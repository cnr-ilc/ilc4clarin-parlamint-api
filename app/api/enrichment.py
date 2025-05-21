from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
import os
import aiofiles
from app.services.enrich_service import enrich_xml
from app.core.nlp import get_nlp

router = APIRouter()

@router.post("/enrich")
async def enrich_file(file: UploadFile = File(...), nlp = Depends(get_nlp)):
    try:
        file_location = f"{file.filename}"
        async with aiofiles.open(file_location, "wb") as f:
            content = await file.read()
            await f.write(content)
        
        zip_file_path = await enrich_xml(file_location, nlp)
        
        async def iterfile(file_path):
            async with aiofiles.open(file_path, mode='rb') as f:
                while chunk := await f.read(1024):
                    yield chunk
            os.remove(file_path)

        return StreamingResponse(iterfile(zip_file_path), media_type='application/zip', headers={
            'Content-Disposition': f'attachment; filename="{os.path.basename(zip_file_path)}"'
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
