from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.analyze_service import analyze_xml
import os

router = APIRouter()

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        file_location = f"{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        
        log = analyze_xml(file_location)
        
        return {"log": log}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
