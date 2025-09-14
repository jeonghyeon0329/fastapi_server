from fastapi import HTTPException
from app.utils import *
import importlib
import datetime

console = Console()
async def operate_run(operate_parameter, payload, file = None):
    print()
    start_time = datetime.datetime.now()
    console.log(f"start_time : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    """ 파일 처리부 """
    try:
        file_manager = FileManager(
            payload.get("user_id", None),
            payload.get("affiliation", None)
        )
        if file:    
            await file_manager.save_file_to_dataset(file)

    except Exception as e:
        raise HTTPException(
            status_code=422, 
            detail={
                "error_code" : "B001",
                "message" : "Failed to save data",
                "errors" : str(e)
            })
    
    """ 인스턴스 설계부"""
    for model_type, model_kind in operate_parameter.model.items():
        try:
            loaded_module = importlib.import_module(f"app.services.{model_kind}_operation")
            processor_class = getattr(loaded_module, f"{model_kind.capitalize()}Processor", None)
            if processor_class is None:
                raise Exception(f"can't find {model_type} : {model_kind}")
            
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code" : "B002",
                    "message" : "Failed to find module",
                    "errors" : str(e)
                })
        
        """ 인스턴스 오퍼레이터부"""
        try:
            args = [file_manager, operate_parameter]
            processor = processor_class(*args)
            if not processor.condition['success']:
                raise Exception(f"{model_type} : {model_kind}, condition : {str(processor.condition['error_message'])}")
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code" : "B003",
                    "message" : "Failed to operate condition",
                    "errors" : str(e)
                })
        
        try:
            steps = [
                 ("generation", processor.generation),
                ("parsing", processor.parsing)
            ]
                          

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code" : "B004",
                    "message" : "Failed to load processor structure",
                    "errors" : str(e)
                })
        
        for stage_name, func in steps:
            try:
                console.log(f"{model_kind} : {stage_name}")
                func = func()

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error_code" : "B005",
                        "message" : "Failed to operate processor structure",
                        "errors" : f"{model_type} : {model_kind} : {stage_name} : {str(e)}"
                })
    end_time = datetime.datetime.now()
    console.log(f"end_time : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    return { "spending_time(s)" : (end_time - start_time).total_seconds(), "result" : func}
