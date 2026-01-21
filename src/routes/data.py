# this for upload 
from fastapi import FastAPI,APIRouter,Depends,UploadFile #as file have a spatial class in fast api
import os
from helpers.config import get_settings,settings
data_router=APIRouter( # end point
   prefix="/api/v1/data",
   tags=["api_v1","data"],
)
# project id : when make procces like upload file i (user) should tell system what is project id 
@data_router.post("/upload/{project_id}")# end point , recieve file then upload it to the system
async def upload_data(project_id:str)#function for end point 
      