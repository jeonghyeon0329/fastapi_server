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
                (self.result_dir, f"{self.filename}_surya_layout_*.json")
            ]
            Fileutils().resultfile_delete(delete_patterns)
            return {"success": True, "error_message": None}
        
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    """데이터 생성"""
    def generation(self):
        try:
            for i, img in enumerate(self.file_info['images']):
                img_path = os.path.join(self.dataset_tmp, f"{self.filename}_{i}.jpg")
                if os.path.exists(img_path): os.remove(img_path)
                img.save(img_path, "JPEG")            

            for page_index in range(int(self.file_info['page_count'])):
                file_path  = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                if not os.path.exists(file_path):
                    raise Exception("image processing error occurred")
                
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_layout")
                with PrintUtils().show_spinner(f"Surya(layout) 실행중 (page {page_index+1})"):
                    subprocess.run(
                        ["surya_layout", file_path, "--output_dir", json_path, "--images"],
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
                json_path = os.path.join(self.result_dir, f'{self.filename}_surya_layout', f'{self.filename}_{page_index}', 'results.json')
                if not os.path.exists(json_path):
                    raise Exception("layout detection file error occurred ")

                ## layout을 탐지한 결과
                with open(json_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                table_filtering = {}
                for file_name, data_info in data.items():
                    try:
                        table_filtering_tmp = []
                        data_info = data_info.pop()['bboxes'] #list format
                        for data_index in data_info:
                            if data_index['label'] == 'Table':
                                table_filtering_tmp.append(data_index)
                            else: pass

                        table_filtering[file_name] = table_filtering_tmp
                    except Exception as e:
                        continue

                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_layout_{page_index}.json")
                with open(json_path, "a", encoding="utf-8") as f:
                    json.dump({"output": table_filtering}, f, ensure_ascii=False, indent=4)

                # """surya 이미지 생성부"""
                try:
                    image_path = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                    if not os.path.exists(image_path):
                        raise Exception("can't find image file(.jpg)")
                    image = cv2.imread(image_path)
                    if table_filtering != []:
                        
                        for key, value in table_filtering.items():
                            if value == []: pass
                            else:
                                for value_index in value:
                                    x1, y1, x2, y2 = map(int, [value_index["bbox"][0], value_index["bbox"][1], value_index["bbox"][2], value_index["bbox"][3]])
                                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    else: pass 

                    boxed_image_path = os.path.join(self.dataset_tmp, f'{self.filename}_surya_layout_{page_index}.jpg')
                    cv2.imwrite(boxed_image_path, image)
                # """+"""
                except Exception as e:
                    print("-"*50)
                    print("surya layout warning:", e)
                    print("-"*50)
                    continue
                
            json_dir_path = os.path.join(self.result_dir, f'{self.filename}_surya_layout')
            shutil.rmtree(json_dir_path)
            return None
        
        except Exception as e:
            raise Exception(e)