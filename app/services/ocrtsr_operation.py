from app.utils import *

class OcrtsrProcessor:
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
                (self.result_dir, f"{self.filename}_surya_tsr_*.json")
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
                
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_tsr")
                with PrintUtils().show_spinner(f"Surya(tsr) 실행중 (page {page_index+1})"):
                    subprocess.run(
                        ["surya_table", file_path, "--output_dir", json_path, "--images"],
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
                json_path = os.path.join(self.result_dir, f'{self.filename}_surya_tsr', f'{self.filename}_{page_index}', 'results.json')
                if not os.path.exists(json_path):
                    raise Exception("tsr detection file error occurred ")

                ## layout을 탐지한 결과
                with open(json_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                json_value = [] ## 페이지별로 json 파일 만들기
                for file_name, data_info in data.items():
                    try:
                        for table_index in range(len(data_info)):
                            small_data_info = data_info[table_index]
                            for cell_index in small_data_info['cells']:
                                json_value_tmp = {}
                                json_value_tmp['page_index'] = page_index ## pdf파일 페이지 번호
                                json_value_tmp['table_index'] = table_index ## 테이블 번호
                                json_value_tmp['row_id'] = cell_index['row_id'] ## row 아이디
                                json_value_tmp['col_id'] = cell_index['col_id'] ## col 아이디
                                json_value_tmp['bbox'] = cell_index['bbox'] ## bbox 정보
                                json_value.append(json_value_tmp)

                    except Exception as e:
                        continue
                json_path = os.path.join(self.result_dir, f'{self.filename}_surya_layout_{page_index}.json')
                if not os.path.exists(json_path):
                    raise Exception("can't find surya table result file(.json)")
                
                with open(json_path, 'r', encoding='utf-8') as file:
                    table_data = json.load(file)

                for cell_info in json_value:
                    table_bbox = table_data['output'][f'{self.filename}_{page_index}'][cell_info['table_index']]['bbox']
                    table_x, table_y = table_bbox[0], table_bbox[1]

                    ## 테이블 위치 기반 셀 위치 이동
                    cell_info['bbox'] = [
                        cell_info['bbox'][0] + table_x,
                        cell_info['bbox'][1] + table_y,
                        cell_info['bbox'][2] + table_x,
                        cell_info['bbox'][3] + table_y
                    ]

                ## json 저장부
                json_path = os.path.join(self.result_dir, f"{self.filename}_surya_tsr_{page_index}.json")
                with open(json_path, "a", encoding="utf-8") as f:
                    json.dump({"output": json_value}, f, ensure_ascii=False, indent=4)

                # """surya 이미지 생성부"""
                try:
                    image_path = os.path.join(self.dataset_tmp, f"{self.filename}_{page_index}.jpg")
                    if not os.path.exists(image_path):
                        raise Exception("can't find image file(.jpg)")
                    image = cv2.imread(image_path)

                    for record in json_value:
                        x1, y1, x2, y2 = map(int, [record["bbox"][0], record["bbox"][1], record["bbox"][2], record["bbox"][3]])
                        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    boxed_image_path = os.path.join(self.dataset_tmp, f'{self.filename}_surya_tsr_{page_index}.jpg')
                    cv2.imwrite(boxed_image_path, image)
                except Exception as e:
                    print("-"*50)
                    print("surya tsr warning:", e)
                    print("-"*50)
                    continue
                # """+"""

            json_dir_path = os.path.join(self.result_dir, f'{self.filename}_surya_tsr')
            shutil.rmtree(json_dir_path)
            return None
        
        except Exception as e:
            raise Exception(e)