from app.utils import *

class OcrclnProcessor:
    def __init__(self, task_info, operate_parameter):
        self.task_info = task_info
        self.operate_parameter = operate_parameter
        for key, value in task_info.__dict__.items():
            setattr(self, key, value)
        self.condition = self.condition()
        self.overlap_threshold = 0.3 # 겹쳐지는 부분의 최소 면적 비율

    """조건 검색"""
    def condition(self):
        try:
            delete_patterns = [
                (self.data_path, f"{self.filename}.pdf"),
                (self.jpg_path, f"{self.filename}_*.jpg"),
                (self.result_path, f"{self.filename}_*.json"),
                # (self.result_path, f"{self.filename}.xlsx") ## 완성된 xlsx파일
            ]
            Fileutils().resultfile_delete(delete_patterns)
            return {"success": True, "error_message": None}
        
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    """데이터 생성"""
    def generation(self):
        try:
            return None
        
        except Exception as e:
            raise Exception(e)

    """결과 데이터 파싱"""
    def parsing(self):
        try:
            return None        
        except Exception as e:
            raise Exception(e)