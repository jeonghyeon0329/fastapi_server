from app.utils import *

class OcrlyProcessor:
    def __init__(self, task_info, operate_parameter):
        self.task_info = task_info
        self.operate_parameter = operate_parameter
        for key, value in task_info.__dict__.items():
            setattr(self, key, value)
        self.condition = self.condition()

    """조건 검색"""
    def condition(self):
        try:
            delete_patterns = [

            ]
            Fileutils().resultfile_delete(delete_patterns)
            return {"success": True, "error_message": None}
        
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    """데이터 생성"""
    def generation(self):
        try:
            image_info = Fileutils().pdf_info(self.full_path)
            for i, img in enumerate(image_info['images']):
                img_path = os.path.join(self.dataset_tmp, f"{self.filename}_{i}.jpg")
                if os.path.exists(img_path): os.remove(img_path)
                img.save(img_path, "JPEG")            

            for page_index in range(int(image_info['page_count'])):
                file_path  = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                if not os.path.exists(file_path):
                    raise Exception("image processing error occurred")
                
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_layout")
                # subprocess.run([
                #     "surya_layout", file_path, "--output_dir", json_path, "--images"
                # ])
            return None
        
        except Exception as e:
            raise Exception(e)

    """결과 데이터 파싱"""
    def parsing(self):
            
        try:
            return None
        
        except Exception as e:
            raise Exception(e)