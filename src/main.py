from fastapi import FastAPI
from routes import base,data
app=FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)

#Project Boilerplates
#The MVC Architecture
#Pydantic-Settings
#FastAPI Depends Module
#How to Separate Logics
#How to construct your first Controller
#Validate Uploaded Files
#The power of Enums
#Control The Responses
#Dynamic Assets Creation
#aiofiles
#uploading chunking

