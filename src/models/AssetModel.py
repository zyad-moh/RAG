# for functions
from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Asset
from bson import ObjectId 
from sqlalchemy.future import select

class AssetModel(BaseDataModel):# i need to inheret from base model to access db_client
   def __init__(self, db_client: object):
        super() .__init__(db_client=db_client)# come from db_client=request.app.db_client
        self.db_client=self.db_client# means that self.db_client now points to the "assets" collection in your postgres.  
   
   @classmethod
   async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init 
        #await  instance.init_collection()# to create indices
        return instance   
# c_post(comment on postgres update) i don't need init_collection as it's done automatic with alimbic

   async def create_assets(self,asset:Asset):
        async with self.db_client() as session: 
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset) # because data come without create and update ,,,رجعلي القيم اللي اتولدت تلقائيًا
        return asset

        """result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True)) #Means: “Execute an INSERT query on MongoDB and store the response in result
        asset.asset_id = result.inserted_id

        return asset"""
  
  
  
  
   async def get_all_project_assets(self,asset_project_id:str,asset_type:str):
       async with self.db_client() as sessoin:
        stmt = select(Asset).where(
          Asset.asset_project_id == asset_project_id,
          Asset.asset_type == asset_type,
        )
        ressult = await sessoin.execute(stmt)
        records = ressult.scalars().all()
       return records
      
      
       """ records = await self.collection.find({
          "asset_project_id":ObjectId(asset_project_id )if isinstance(asset_project_id, str) else asset_project_id,
          "asset_type":asset_type,
          }).to_list(length=None)
        return[
          Asset(**record)# return record based on Asset pydantic model
          for record in records
        ]
        #the stringed one refer to the column in the collection but tha variabled one refer to  the project id come from the request , ObjectId(asset_project_id ) casting convert from str to ObjectId 
  
  """
  
   async def get_asset_record(self,asset_project_id:str,asset_name:str):
        async with self.db_client() as session: 
            async with session.begin():  
                query = select(Asset).where(Asset.asset_project_id == asset_project_id,Asset.asset_name == asset_name)
                ressult = await session.execute(query)
                asset = ressult.scalar_one_or_none()
        
        return asset
        
        """record = await self.collection.find_one({
          "asset_project_id":ObjectId(asset_project_id)if isinstance(asset_project_id, str) else asset_project_id,
          "asset_name":asset_name,
          })
        if record:  
          return Asset(**record)# return record based on Asset pydantic model
        return None"""


   