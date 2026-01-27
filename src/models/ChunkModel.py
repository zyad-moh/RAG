# responsble for the chunk collection
from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne # type of action(insert_one)
class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super() .__init__(db_client=db_client) #here i pass db_clients to BaseDataModel (عشان يفضل شغال) 
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]# to access mongo db
    async def create_chunk(self,chunk:DataChunk):#take model with type DataChunk and insert in DB
       result=await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))#we will take convert to dict to be able to get into DB
       chunk_id=result.inserted_id
       return chunk
    async def get_chunk(self,chunk_id:str):#
        result=await self.collection.find_one({

            "_id":ObjectId(chunk_id)
        })
        if result is None:
            return None
        return DataChunk(**result)
    # if i insert chunk step by step it is not memory effeiciant sol batch write i pass data in form of batches 
    async def insert_many_chunks(self,chunks:list,batch_size:int=100):
       for i in range(0,len(chunks),batch_size):
          batch=chunks[i:i+batch_size]# at each itire batch contain diff chunks with size 100 
          operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
          ] 
          await self.collection.bulk_write(operations)#??
       return len(chunks)  
    async def delete_chunk_by_project_id(self,project_id:ObjectId):#delet chunk by project id
        result=await self.collection.delete_many(
            { "chunk_project_id" : project_id}
        )
        result.deleted_count    



