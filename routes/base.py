from fastapi import FastAPI,APIRouter
base_router=APIRouter()
@base_router.get("/")#dicorator
def welcome():
   return {"message": "Hello World!"}