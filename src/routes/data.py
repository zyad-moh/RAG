# this for upload 
from fastapi import FastAPI,APIRouter,Depends,UploadFile,status #as file have a spatial class in fast api
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,settings
from controllers import DataController,ProjectController #don't forget i accessed them easly because of __init__ files
import aiofiles
from models import ResponseSignal
import logging
logger = logging.getLogger('uvicorn.error')
data_router=APIRouter( # prefix for end point
   prefix="/api/v1/data",
   tags=["api_v1","data"],
)
# project id : when make procces like upload file i (user) should tell system what is project id 
#function for end point 
@data_router.post("/upload/{project_id}")# end point , recieve file then upload it to the system
async def upload_data(project_id:str,file:UploadFile,
                     app_settings:settings=Depends(get_settings)): 
   isvalid,res=DataController().validate_uploaded_file(file=file) 
   
   if not isvalid:
      return JSONResponse(# for change 200ok in false response to
         status_code=status.HTTP_400_BAD_REQUEST,
         content={
            "signal":res
         }
      )
   
   file_path,file_id=DataController().generate_unique_filepath(orig_file_name=file.filename,project_id=project_id)
   project_dir_path=ProjectController().get_project_path(project_id=project_id)#for saaaaaaveeeeee storeeeee the file which uploaded from user
   """file_path=os.path.join(
      project_dir_path,
      file.filename
   )"""#path of uploaded file on my disk
   try:
    async with aiofiles.open(file_path,"wb") as f: #If the file does not exist → it is created
       while chunk:=await file.read(app_settings.FILE_DEFULT_CHUNK_SIZE):
         await f.write(chunk) #this code creates an empty file on disk and then fills it chunk by chunk with the contents of the uploaded file.
   except Exception as e:
      logger.error(f"Error while uploading file: {e}")# contain the hidden info (error not showen to user)
      return JSONResponse(# for change 200ok in false response to
         status_code=status.HTTP_400_BAD_REQUEST,
         content={
            "signal":ResponseSignal.FILE_UPLOAD_FAILED.value
         }
      )
   return JSONResponse(
       content={
           "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
           "file id": file_id
         }
         )




# note here (async def upload_data) i get uploaded file , i need to validate it (logic -> controller )
# chunk by chunk it's similar data augmantation you know !!!
#Lazy loading , Streaming data instead of loading all at once
#raise TypeError(f'Object of type {o.__class__.__name__} '
#   TypeError: Object of type ResponseSignal is not JSON serializable 
# return {"signal": ResponseSignal.FILE_TYPE_NOT_SUPPORTED} should be FILE_TYPE_NOT_SUPPORTED.value