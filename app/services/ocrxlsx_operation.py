from app.utils import *

class OcrxlsxProcessor:
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
                # (self.result_dir, f"{self.filename}_surya_info_*.json"),
                # (self.result_dir, f"{self.filename}.xlsx")
            ]
            Fileutils().resultfile_delete(delete_patterns)
            return {"success": True, "error_message": None}
        
        except Exception as e:
            return {"success": False, "error_message": str(e)}

    """데이터 생성"""
    def generation(self):
        try:
            for page_index in range(int(self.file_info['page_count'])):

                file_path = os.path.join(self.result_dir, f"{self.filename}_surya_ocr_{page_index}.json")
                if not os.path.exists(file_path):
                    raise Exception("can't find ocr result")    
                with open(file_path, 'r', encoding='utf-8') as file:
                    text_data = pd.DataFrame(json.load(file)['output'])

                file_path = os.path.join(self.result_dir, f"{self.filename}_surya_tsr_{page_index}.json")
                if not os.path.exists(file_path):
                    raise Exception("can't find tsr result")    
                with open(file_path, 'r', encoding='utf-8') as file:
                    table_data = pd.DataFrame(json.load(file)['output'])
                print("?")
                ## 탐지된 결과가 전혀 없는 경우
                if text_data.empty or table_data.empty : 
                    print("??")
                    continue
                
                ## table에 대한 정보
                table_data[['x1', 'y1', 'x2', 'y2']] = table_data['bbox'].apply(lambda x: pd.Series(x))
                text_data = text_data.sort_values(by=["y1", "x1", "y2", "x2"]).reset_index(drop=True)
                print("?")
                # 레코드 신뢰도 계산
                # cells[["page_index", "table_index", "row_id", "col_id"]]
                text_data['cell_id'] = text_data.apply(lambda x : credit(x, table_data, self.overlap_threshold), axis=1)
                text_data = text_data.dropna(subset=['cell_id'])
                if text_data.empty: continue

                split_cols = text_data["cell_id"].str.split("_", expand=True)

                # 앞 4개는 다시 cell_id로 합쳐서 cell_id로 활용
                text_data["cell_id"] = split_cols[[0, 1, 2, 3]].agg("_".join, axis=1)
                # 뒤 4개는 분리해서 box 정보로 활용
                text_data[["box_x1", "box_y1", "box_x2", "box_y2"]] = split_cols[[4, 5, 6, 7]].astype(float)
                ## 데이터 형 변환(가끔 string으로 잡히는 경우가 있음)
                text_data[["box_x1", "box_y1", "box_x2", "box_y2"]] = text_data[["box_x1", "box_y1", "box_x2", "box_y2"]].astype(float)
                
                ## 중복되는 부분 하나로 통합처리
                final_df = (
                    text_data
                    .groupby(["cell_id"], as_index=False)
                    .agg({
                        "text": lambda x: " ".join(dict.fromkeys(x)), # 공백이 필요없으면 스페이스바 제거
                        "x1": "min",
                        "y1": "min",
                        "x2": "max",
                        "y2": "max",
                        "box_x1": "min",
                        "box_y1": "min",
                        "box_x2": "max",
                        "box_y2": "max"
                        }) 
                    .reset_index(drop=True)
                )
                print("???")
                print(final_df)
                if not final_df.empty:
                    final_df[["page_index", "table_index", "row_id", "col_id"]] = final_df["cell_id"].str.split("_", expand=True)
                    
                    file_path = os.path.join(self.result_dir, f"{self.filename}_surya_info_{page_index}.json")
                    final_df.to_json(file_path, orient="records", force_ascii=False, indent=4)

                    ## 엑셀 파일 만들기
                    excel_output_path = os.path.join(self.result_dir, f"{self.filename}.xlsx")
                    grouped = final_df.groupby(["page_index", "table_index"])
                    
                    table_number = 0
                    for (page_idx, table_idx), group in grouped:
                        max_row = group["row_id"].astype(int).max()
                        max_col = group["col_id"].astype(int).max()
                        
                        sheet_df = pd.DataFrame("", index=range(max_row + 1), columns=range(max_col + 1))

                        for _, row in group.iterrows():
                            r = int(row["row_id"])
                            c = int(row["col_id"])
                            text = row["text"] if pd.notnull(row["text"]) else ""
                            sheet_df.iat[r, c] = text

                        ## 빈칸채우기 기능
                        try:
                            if str(self.para.get("fullfill", "")).lower().strip() == "true":
                                sheet_df = sheet_df.replace("", np.nan).ffill()
                        except: pass
                            
                        sheet_name = f"{page_index+1}page_{table_number+1}table_matrix"
                        table_number += 1
                    
                        if os.path.exists(excel_output_path):
                            with pd.ExcelWriter(excel_output_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:        
                                sheet_df.to_excel(writer, sheet_name=sheet_name, index=True)
                        else:
                            with pd.ExcelWriter(excel_output_path, engine='openpyxl', mode='w') as writer:
                                sheet_df.to_excel(writer, sheet_name=sheet_name, index=True)   
                else: continue                    
            return None
        
        except Exception as e:
            raise Exception(e)

    """결과 데이터 파싱"""
    def parsing(self):
        try:
            return None        
        except Exception as e:
            raise Exception(e)