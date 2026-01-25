from fastapi import FastAPI
from routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app=FastAPI()
@app.on_event("startup")
async def startup_dp_client():
    settings = get_settings()# equal to i take obj from class  don't write get_settings.MONGODB_URL

    app.mongo_conn=AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client =app.mongo_conn[settings.MONGODB_DATABASE]

#Case A — 1 user uploads a file Only 1 connection is used at a time, but it is reused for multiple requests.

@app.on_event("shutdown")#closes all connections when FastAPI shuts down.
async def shutdown_dp_client():
   app.mongo_conn.close()


app.include_router(base.base_router)
app.include_router(data.data_router)






#v7:
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
#In a long-running app or containerized deployment, 
#leaving connections open can cause MongoDB to refuse new connections after a while.
#If you restart FastAPI multiple times during dev without closing, you can hit “too many connections” on Mongo.
"""
Case B — Many users uploading files simultaneously (without restarting FastAPI) :FastAPI does NOT open a new connection for each user, it reuses the pool.
Case C — FastAPI is restarted repeatedly without closing the client

Each restart creates a new connection pool

Old pools are left open → MongoDB sees many open connections

Eventually you may hit the MongoDB max connection limit

⚠ This is the danger of not calling mongo_conn.close() — it’s only relevant when the app is restarted, not during normal user requests.
"""