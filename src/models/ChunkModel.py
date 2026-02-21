# responsble for the chunk collection
from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne # type of action(insert_one)
from sqlalchemy.future import select
from sqlalchemy import func , delete
class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super() .__init__(db_client=db_client) #here i pass db_clients to BaseDataModel (عشان يفضل شغال) 
        self.db_client=self.db_client    
  
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init 
        #await  instance.init_collection()# to create indices
        return instance   
# c_post(comment on postgres update) i don't need init_collection as it's done automatic with alimbic

    async def create_chunk(self,chunk:DataChunk):#take model with type DataChunk and insert in DB
       async with self.db_client() as session:# session maker which create session
            async with session.begin(): # here open session (connection)
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk) # because data come without create and update ,,,رجعلي القيم اللي اتولدت تلقائيًا
       return chunk
       
       
       
       
       """result=await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))#we will take convert to dict to be able to get into DB
       chunk._id=result.inserted_id
       return chunk
    """
    
    
    async def get_chunk(self,chunk_id:str):#
        async with self.db_client() as session:
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
            chunk = result. scalar_one_or_none()
        return chunk
                    
        
        """ 
        result=await self.collection.find_one({

            "_id":ObjectId(chunk_id)
        })
        if result is None:
            return None
        return DataChunk(**result)"""
   
   
   
    # if i insert chunk step by step it is not memory effeiciant sol batch write i pass data in form of batches 
    async def insert_many_chunks(self,chunks:list,batch_size:int=100):
        async with self.db_client() as session:# session maker which create session
            async with session.begin():
               for i in range(0,len(chunks),batch_size):
                   batch=chunks[i:i+batch_size]
                   session.add_all(batch)
            await session.commit()
        return len(chunks)
        """for i in range(0,len(chunks),batch_size):
          batch=chunks[i:i+batch_size]# at each itire batch contain diff chunks with size 100 
          operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
          ] 
          await self.collection.bulk_write(operations)#??
       return len(chunks)  
   """
   
   
    async def delete_chunk_by_project_id(self,project_id:ObjectId):#delet chunk by project id
       async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
       return result.rowcount
      
       """ result=await self.collection.delete_many(
            { "chunk_project_id" : project_id}
        )
        return result.deleted_count"""    
   
   
   
   
    async def get_project_chunk(self,project_id:ObjectId,page_no:int=1,page_size:int=50):
        async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records
        
        
        
        """records = await self.collection.find( # i have to make skip to prevent 
            {"chunk_project_id" : project_id}
        ).skip(
                (page_no-1) * page_size
                ).limit(page_size).to_list(length=None)
        
        return [
            DataChunk(**record)
            for record in records
        ]"""
        #So record is coming from an async function but is being used without await.

"""
❓ السؤال المهم:

إزاي هيعمل indexing على collection مش موجودة؟

✅ الإجابة:

👉 MongoDB بيخلق collection تلقائيًا عند أول عملية write أو index

"""

