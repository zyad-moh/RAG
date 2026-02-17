from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column , Integer , DateTime , func ,String , ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID , JSONB
from sqlalchemy.orm import relationship
import uuid
from pydantic import BaseModel
class DataChunk(SQLAlchemyBase):

    __tablename__ = "chunks"

    chunk_id = Column(Integer,primary_key=True,autoincrement = True) #sql alchemy by defult apply index on clomn with UUID or primary key
    chunk_uuid = Column(UUID(as_uuid=True),default = uuid.uuid4,unique=True,nullable=False)# for seacurity and user access i don.t need anyone to know that i have 10 project

    chunk_text = Column(String,nullable = False)
    chunk_metadata= Column(JSONB,nullable = False)
    chunk_order= Column(Integer,nullable = False)
    
    chunk_project_id = Column(Integer,ForeignKey("projects.project_id"),nullable = False)
    chunk_asset_id = Column(Integer,ForeignKey("assets.asset_id"),nullable = False)

    created_at = Column(DateTime(timezone=True),server_default = func.now(),nullable = False)#server_default to automaticlly put the time when record created 
    update_at = Column(DateTime(timezone=True),onupdate= func.now(),nullable=True)

    project = relationship("Project",back_populates = "chunks")
    asset = relationship("Asset",back_populates = "chunks")

    __tabel_args__ = (
        Index('ix_chunk_project_id',chunk_project_id), # apply index on asset_progect_id  
        Index('ix_chunk_asset_id',chunk_asset_id) # apply index on asset_progect_id  
    )
class RetrievedDocument(BaseModel):
    text:str
    score : float