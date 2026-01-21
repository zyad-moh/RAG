# this for upload 
from fastapi import FastAPI,APIRouter,Depends,UploadFile #as file have a spatial class in fast api
import os
from helpers.config import get_settings,settings
from controllers import DataController
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
   return isvalid,res
         
# note here (async def upload_data) i get uploaded file , i need to validate it (logic -> controller )