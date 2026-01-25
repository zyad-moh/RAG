# this for upload 
from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request #as file have a spatial class in fast api
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,settings
from controllers import DataController,ProjectController,ProcessController #don't forget i accessed them easly because of __init__ files
import aiofiles                                          
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
logger = logging.getLogger('uvicorn.error')
data_router=APIRouter( # prefix for end point
   prefix="/api/v1/data",
   tags=["api_v1","data"],
)
# project id : when make procces like upload file i (user) should tell system what is project id 
#function for end point 
@data_router.post("/upload/{project_id}")# end point , recieve file then upload it to the system
async def upload_data(request:Request,project_id:str,file:UploadFile,
                     app_settings:settings=Depends(get_settings)): 
   
   project_model=ProjectModel(db_client=request.app.db_client)
   project=await project_model.get_project_or_create_one( #await to able to collect results
      project_id=project_id
   )#here we store project_id in mongodb using projectmodel based on db_scheme (project)
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
           "file id": file_id,
           #"project_id":str(project._id)
         }
         )

@data_router.post("/process/{project_id}")
async def procces_endpoint(project_id:str , Proccess_Request: ProcessRequest):#Proccess_Request it's like (file_id) but it's processed
   file_id=Proccess_Request.file_id 
   chunk_size=Proccess_Request.chunk_size
   overlap_size=Proccess_Request.overlap_size
   Process_Controller=ProcessController(project_id=project_id)
   file_content=Process_Controller.get_file_content(file_id=file_id)
   file_chunks =Process_Controller.procces_file_content(file_content=file_content,file_id=file_id,chunk_size=chunk_size,overlap_size=overlap_size)
   
   if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )

   return file_chunks
# note here (async def upload_data) i get uploaded file , i need to validate it (logic -> controller )
# chunk by chunk it's similar data augmantation you know !!!
#Lazy loading , Streaming data instead of loading all at once
#raise TypeError(f'Object of type {o.__class__.__name__} '
#   TypeError: Object of type ResponseSignal is not JSON serializable 
# return {"signal": ResponseSignal.FILE_TYPE_NOT_SUPPORTED} should be FILE_TYPE_NOT_SUPPORTED.value
""""1️⃣ mongo_data:/data/db

This is the Docker named volume.

It tells Docker where MongoDB stores its data inside the container.

Example from docker-compose.yml:

volumes:
  - mongo_data:/data/db


✅ This has nothing to do with the connection URL.
It is purely for persistent storage inside Docker.

2️⃣ MONGODB_URL

This is the connection string your app uses to talk to MongoDB.

It does not refer to the volume name.

It refers to where MongoDB is listening, which depends on your host or Docker network."""
#request:Request:you need to know each info about comming request ,and contain the app in main
