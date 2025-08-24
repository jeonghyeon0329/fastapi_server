from fastapi import HTTPException
from app.utils import FileManager
import importlib
import traceback
import datetime
import time


async def operate_run(operate_parameter, file, keyword = None):
    """ 파일 처리부 """
    try:
        file_manager = FileManager(operate_parameter.user_id, operate_parameter.affiliation)
        if file:
            await file_manager.save_file_to_dataset(file)
    except Exception as e:
        print(f"[ERROR][{datetime.datetime.now()}] save_file_to_dataset error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=422, detail="failed to save data")

    start_time = time.time()
    print(f"\n[INFO] start_time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    """ 인스턴스 설계부"""
    for model_type, model_kind in operate_parameter.model.items():
        print(f"\n[INFO] ===== {model_kind} operate! =====")
        try:
            loaded_module = importlib.import_module(f"app.services.{model_kind}_operation")
            processor_class = getattr(loaded_module, f"{model_kind.capitalize()}Processor", None)
            if processor_class is None:
                raise ImportError(f"{model_type} : {model_kind}가 없습니다.")
        except Exception as e:
            print(f"[ERROR][{datetime.datetime.now()}] 모듈 로딩 실패: {model_kind}")
            print(f"Exception: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=404, detail = "failed to find module")
        
        """ 인스턴스 오퍼레이터부"""
        try:
            args = [file_manager, operate_parameter]
            if keyword is not None:
                args.append(keyword)

            processor = processor_class(*args)
            if not processor.condition['success']:
                raise Exception(processor.condition['error_message'])
            
        except Exception as e:
            print(f"[ERROR][{datetime.datetime.now()}] 인스턴스 생성 실패: {model_kind}")
            print(f"Exception: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail = "failed to find instance")
        
        try:
            steps = [
                ("generation", processor.generation),
                ("parsing", processor.parsing)
            ]

        except Exception as e:
            print(f"[ERROR][{datetime.datetime.now()}] 단계 구성 실패: {model_kind}")
            print(f"Exception: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail = "failed to find instance-structure")
        
        for stage_name, func in steps:
            try:
                print(f"[INFO] >>> {stage_name} 시작")
                func = func()
                print(f"[INFO] >>> {stage_name} 완료")
            except Exception as e:
                print(f"[ERROR][{datetime.datetime.now()}] {stage_name} 중 오류 발생")
                print(f"Exception: {e}")
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail = str(e))

        print(f"[INFO] ===== {model_kind} finish! =====\n")

    print(f"[INFO] finish_time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[INFO] 소요시간 : {round(time.time() - start_time, 2)}초\n")
    return { "spending_time" : round(time.time() - start_time, 2), "result" : func}
