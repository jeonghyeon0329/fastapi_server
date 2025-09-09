from fastapi import HTTPException, UploadFile
from typing import List, Tuple, Union, Optional, Iterable
from pathlib import Path
import glob
import os

def _safe_filename(name: str) -> str: 
    """ 사용자가 파일명으로 파일경로를 집어넣는 경우를 막음"""
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
        self.affiliation = affiliation
        self.base_dir = f"{self.affiliation}_{self.user_id}" if self.user_id and self.affiliation else None
        self.subdirs: List[str] = ["dataset", "dataset_tmp", "result"]
        self.filename = None
        self.full_path = None

        if self.user_id and self.affiliation:
            self.base_path = self._init_user_folder()
            self.dataset_dir = self.base_path / "dataset"
            self.dataset_tmp = self.base_path / "dataset_tmp"
            self.result_dir = self.base_path / "result"
        else:
            self.base_path = None
            self.dataset_dir = None
            self.dataset_tmp = None
            self.result_dir = None

    ## 유저별로 폴더가 없는 경우 폴더 생성    
    def _init_user_folder(self) -> Path:
        base_path = self.UPLOAD_ROOT / self.base_dir

        if not base_path.exists():
            base_path.mkdir(parents=True)

        for subfolder in self.subfolder:
            sub_path = base_path / subfolder
            if not sub_path.exists():
                sub_path.mkdir(parents=True)
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

    @staticmethod # self 영향 없이 진행
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
        
class Fileutils:

    def __init__(self):
        pass

    def resultfile_delete(self, delete_patterns):
        try:
            for dir_path, pattern in delete_patterns:
                full_pattern = os.path.join(dir_path, pattern)
                for file_path in glob.glob(full_pattern):
                    if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            raise Exception(e)