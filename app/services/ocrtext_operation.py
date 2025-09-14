from app.utils import *

class OcrtextProcessor:
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
                (self.result_dir, f"{self.filename}_surya_ocr_*.json")
            ]
            Fileutils().resultfile_delete(delete_patterns)
            return {"success": True, "error_message": None}
        
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    """데이터 생성"""
    def generation(self):
        try:
            for i, img in enumerate(self.file_info['images']):
                max_width = 1024
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size)
                    
                img_path = os.path.join(self.dataset_tmp, f"{self.filename}_{i}.jpg")
                if os.path.exists(img_path): os.remove(img_path)
                img.save(img_path, "JPEG")            

            for page_index in range(int(self.file_info['page_count'])):
                file_path  = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                if not os.path.exists(file_path):
                    raise Exception("image processing error occurred")
                
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_ocr")
                with PrintUtils().show_spinner(f"Surya(ocr) 실행중 (page {page_index+1})"):
                    subprocess.run(
                        ["surya_ocr", file_path, "--output_dir", json_path, "--images"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True
                    )
            return None
        
        except Exception as e:
            raise Exception(e)

    """결과 데이터 파싱"""
    def parsing(self):
        try:
            for page_index in range(int(self.file_info['page_count'])):
                json_path = os.path.join(self.result_dir, f'{self.filename}_surya_ocr', f'{self.filename}_{page_index}', 'results.json')
                if not os.path.exists(json_path):
                    raise Exception("ocr detection file error occurred ")

                ## layout을 탐지한 결과
                with open(json_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                json_value = []
                for doc_id, pages in data.items():
                    for page in pages:
                        for line in page.get("text_lines", []):
                            bbox = line.get("bbox", [])
                            text = line.get("text", "")
                            if len(bbox) == 4 and text.strip():
                                json_value.append({
                                    "x1": bbox[0],
                                    "y1": bbox[1],
                                    "x2": bbox[2],
                                    "y2": bbox[3],
                                    "text": text
                                })
                                
                ## json 저장부
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_ocr_{page_index}.json")
                with open(json_path, "a", encoding="utf-8") as f:
                    json.dump({"output": json_value}, f, ensure_ascii=False, indent=4)

                # """surya 이미지 생성부"""
                try:
                    image_path = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                    if not os.path.exists(image_path):
                        raise Exception("can't find image file(.jpg)")
                    image = cv2.imread(image_path)

                    for record in json_value:
                        x1, y1, x2, y2 = map(int, [record["x1"], record["y1"], record["x2"], record["y2"]])
                        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    boxed_image_path = os.path.join(self.dataset_tmp, f'{self.filename}_surya_ocr_{page_index}.jpg')
                    cv2.imwrite(boxed_image_path, image)
                except Exception as e:
                    print("-"*50)
                    print("surya tsr warning:", e)
                    print("-"*50)
                    continue
                # """+"""

            json_dir_path = os.path.join(self.result_dir, f'{self.filename}_surya_ocr')
            shutil.rmtree(json_dir_path)
            return None
        
        except Exception as e:
            raise Exception(e)