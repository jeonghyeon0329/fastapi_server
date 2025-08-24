from fastapi import HTTPException, UploadFile
from typing import List, Tuple, Union, Optional, Iterable
from pathlib import Path

def _safe_filename(name: str) -> str: 
    """
        사용자가 파일명으로 파일경로를 집어넣는 경우를 막음
    """
    return Path(name).name

def _normalize_extensions(exts: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(exts, str): exts = [exts]
    out = []
    for e in exts:
        e = (e or "").strip().lower()
        if not e: continue
        out.append(e if e.startswith(".") else f".{e}")
    return out

class FileManager:
    UPLOAD_ROOT = Path("uploads")
    def __init__(self, user_id: str, affiliation: str):
        self.user_id: str = user_id
        self.affiliation: str = (affiliation or "anonymous").strip() or "anonymous"
        self.base_dirname: str = f"{self.affiliation}_{self.user_id}"
        self.subdirs: List[str] = ["dataset", "dataset_tmp", "result"]
        
        self.base_path: Path = self._ensure_user_dirs()
        self.dataset_dir: Path = self.base_path / "dataset"
        self.dataset_tmp: Path = self.base_path / "dataset_tmp"
        self.result_dir: Path = self.base_path / "result"
        self.filename_stem: Optional[str] = None
        self.saved_fullpath: Optional[Path] = None #dataset_dir + filename.확장자
        
    def _ensure_user_dirs(self) -> Path:
        base_path = self.UPLOAD_ROOT / self.base_dirname
        base_path.mkdir(parents=True, exist_ok=True)
        for name in self.subdirs:
            (base_path / name).mkdir(parents=True, exist_ok=True)
        return base_path

    async def save_file_to_dataset(self, file: UploadFile, chunk_size: int = 1024 * 1024) -> Path:
        
        if not file or not getattr(file, "filename", None):
            raise HTTPException(status_code=422, detail="file is required")

        safe_name = _safe_filename(file.filename)
        self.filename_stem = Path(safe_name).stem ## 확장자 제외
        self.saved_fullpath = self.dataset_dir / safe_name

        with open(self.saved_fullpath, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
        return self.saved_fullpath

    @staticmethod
    def require_file_count(files: List[UploadFile], expected_count: int) -> Union[UploadFile, Tuple[UploadFile, ...]]:
        if not isinstance(files, list):
            raise HTTPException(status_code=422, detail="files must be a list")
        if len(files) != expected_count:
            raise HTTPException(status_code=422, detail=f"expected {expected_count} files, got {len(files)}")

        names = [getattr(f, "filename", "") for f in files]
        if any(not n for n in names):
            raise HTTPException(status_code=422, detail="file without filename detected")
        if len(names) != len(set(names)):
            raise HTTPException(status_code=422, detail="duplicated filenames detected")

        return files[0] if expected_count == 1 else tuple(files)

    @staticmethod
    def validate_extensions(files: Union[UploadFile, List[UploadFile]], allowed_extensions: Union[str, List[str]]) -> None:
        exts = _normalize_extensions(allowed_extensions) ## 확장자 정규화
        file_list = files if isinstance(files, list) else [files]

        for f in file_list:
            name = getattr(f, "filename", "") or ""
            if not name:
                raise HTTPException(status_code=422, detail="file without filename detected")
            lower = name.lower()
            if not any(lower.endswith(e) for e in exts):
                raise HTTPException(status_code=422, detail=f"unsupported file extension: {name}")