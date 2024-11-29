from fastapi import HTTPException
from pathlib import Path

from pydantic import BaseModel, field_validator


#Classe per gestire l'input della richiesta di POST per generare la documentazione da file locale
class DocInputPaths(BaseModel):
    project_path: str
    result_path: str

    #Verifica che i paramentri in input siano corretti
    @field_validator("result_path")
    @classmethod
    def result_path_validator(cls,v: str):
        if len(v.strip()) == 0:
            error_response = {
                "msg": "project_path and/or result_path cannot be empty"
            }
            print(f"Validation error: {error_response['msg']}")
            raise HTTPException(status_code=422, detail=error_response)

        if type(v) is not str:
            error_response = {
                "msg": f"project_path and/or result_path must be str, not {type(v).__name__}"
            }
            print(f"Validation error: {error_response['msg']}")
            raise HTTPException(status_code=422, detail=error_response)

        if not ((Path(v).exists()) or (Path(v).is_dir())):
            error_response = {
                "msg": "project_path and/or result_path must be a path of a folder"
            }
            print(f"Validation error: {error_response['msg']}")
            raise HTTPException(status_code=422, detail=error_response)
        return v

    @field_validator("project_path")
    @classmethod
    def project_path_validator(cls, v: str):
        if len(v.strip()) == 0:
            error_response = {
                "msg": "project_path and/or result_path cannot be empty"
            }
            print(f"Validation error: {error_response['msg']}")
            raise HTTPException(status_code=422, detail=error_response)

        if type(v) is not str:
            error_response = {
                "msg": f"project_path and/or result_path must be str, not {type(v).__name__}"
            }
            print(f"Validation error: {error_response['msg']}")
            raise HTTPException(status_code=422, detail=error_response)

        return v

