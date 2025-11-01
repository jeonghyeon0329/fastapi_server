from fastapi import HTTPException, UploadFile
from typing import List, Tuple, Union, Optional, Iterable
from rich.console import Console
from pathlib import Path
from PIL import Image
import pandas as pd
import tempfile
import os, io, glob, itertools, time, threading

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
        self.affiliation: str = affiliation
        self.base_dir = f"{self.affiliation}_{self.user_id}" if self.user_id and self.affiliation else None
        self.subdirs: List[str] = ["dataset", "dataset_tmp", "result"]
        self.filename = None
        self.full_path = None
        self.file_info = None

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

        for subdirs in self.subdirs:
            sub_path = base_path / subdirs
            if not sub_path.exists():
                sub_path.mkdir(parents=True)
        return base_path
    
    async def save_file_to_dataset(self, file: UploadFile, chunk_size: int = 1024 * 1024) -> Path:
        
        if not file or not getattr(file, "filename", None):
            raise HTTPException(
                status_code=422, 
                detail={
                    "error_code" : "C001",
                    "message" : "File required",
            })
        safe_name = _safe_filename(file.filename)
        self.filename = Path(safe_name).stem ## 확장자 제외
        self.full_path = self.dataset_dir / safe_name
        with open(self.full_path, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)

        self.file_info = Fileutils().pdf_info(self.full_path)
        return self.full_path

    @staticmethod # self 영향 없이 진행
    def require_file_count(files: List[UploadFile], expected_count: int) -> Union[UploadFile, Tuple[UploadFile, ...]]:
        if not isinstance(files, list):
            raise HTTPException(
                status_code=422, 
                detail={
                    "error_code" : "C002",
                    "message" : "Files format error",
            })
            
        if len(files) != expected_count:
            raise HTTPException(
                status_code=422, 
                detail={
                    "error_code" : "C003",
                    "message" : "Files count error",
            })

        names = [getattr(f, "filename", "") for f in files]
        if any(not n for n in names):
            raise HTTPException(
                status_code=422, 
                detail={
                    "error_code" : "C004",
                    "message" : "Files name error",
            })

        if len(names) != len(set(names)):
            raise HTTPException(
                status_code=422, 
                detail={
                    "error_code" : "C005",
                    "message" : "Files duplicate error",
            })

        return files[0] if expected_count == 1 else tuple(files)

    @staticmethod
    def validate_extensions(files: Union[UploadFile, List[UploadFile]], allowed_extensions: Union[str, List[str]]) -> None:
        exts = _normalize_extensions(allowed_extensions) ## 확장자 정규화
        file_list = files if isinstance(files, list) else [files]

        for f in file_list:
            name = getattr(f, "filename", "") or ""
            if not name:
                raise HTTPException(
                    status_code=422, 
                    detail={
                        "error_code" : "C006",
                        "message" : "Files name error",
                })
            lower = name.lower()
            if not any(lower.endswith(e) for e in exts):
                raise HTTPException(
                    status_code=422, 
                    detail={
                        "error_code" : "C007",
                        "message" : f"Files extension error : {name}",
                })
        
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
        
    def extract_files_by_count(self, files, expected_count):
        if len(files) != expected_count:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code" : "F001",
                    "message" : "wrong file count",
                })

        filenames = [file.filename for file in files]
        if len(filenames) != len(set(filenames)):
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code" : "F002",
                    "message" : "Failed to count files",
                })

        return files[0] if expected_count == 1 else tuple(files)
    
    def validate_file_extensions(self, files, allowed_extensions):

        ## 허용하는 파일 확장자 목록
        if isinstance(allowed_extensions, str):
            allowed_extensions = [allowed_extensions]

        ## 파일 리스트 부분은 list 형태
        if not isinstance(files, list): files = [files]
        for file in files:
            if not any(file.filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error_code" : "F003",
                        "message" : "unexpected Files-format",
                })

    def convert_images_to_pdf(self, files):
        try:
            is_single_file = not isinstance(files, list)
            if is_single_file:
                files = [files]

            converted = []
            for f in files:
                ext = f.filename.lower()
                if ext.endswith((".jpg", ".jpeg", ".png")):
                    image = Image.open(f.file).convert("RGB")
                    pdf_stream = io.BytesIO()
                    image.save(pdf_stream, format="PDF")
                    pdf_stream.seek(0)

                    # SpooledTemporaryFile로 감싸기
                    temp = tempfile.SpooledTemporaryFile()
                    temp.write(pdf_stream.read())
                    temp.seek(0)

                    # UploadFile 객체 생성 (content_type 없이)
                    pdf_file = UploadFile(
                        filename=ext.rsplit(".", 1)[0] + ".pdf",
                        file=temp
                    )
                    converted.append(pdf_file)
                else:
                    converted.append(f)

            return converted[0] if is_single_file else converted
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code" : "F003",
                    "message" : "unexpected Files-format",
                    "errors" : str(e)
                })
    
    def pdf_info(self, pdf_path: str):
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        images = []
        for i in range(len(pdf)):
            page = pdf[i]
            pil_image = page.render(scale=100/72).to_pil() # 200dpi
            images.append(pil_image)

        return {"images": images, "page_count": len(images)}
    
class PrintUtils:
    def __init__(self):
        self.console = Console()

    def show_spinner(self, message: str = "작업중", interval: float = 0.1):
        console = self.console
        interval = interval

        class SpinnerCtx:
            def __enter__(self):
                self._spinner = itertools.cycle(["-", "\\", "|", "/"])
                self._running = True
                self._thread = threading.Thread(target=self._spin_loop, daemon=True)
                self._thread.start()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self._running = False
                self._thread.join()
                if exc_type is None:
                    console.log(f"{message} [bold green]완료 ✅[/]")
                else:
                    console.log(f"{message} [bold red]실패 ❌[/]")

            def _spin_loop(self):
                while self._running:
                    console.print(f"{message} {next(self._spinner)}", end="\r", style="cyan")
                    time.sleep(interval)

        return SpinnerCtx()