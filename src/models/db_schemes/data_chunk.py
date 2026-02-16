from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId


    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[("chunk_project_id",1)], # we make list as we could include one or more key  project_id ia the field or column we will apply indedxing on it 1 -> desc
                "name": "chunk_project_id_index_1",
                "unique": False # chunk_project_id_ coulsn't be unique each project id related to many ununique chunks 

            }
        ]
    
class RetrievedDocument(BaseModel):
    text:str
    score : float