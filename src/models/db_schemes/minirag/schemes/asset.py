from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column , Integer , DateTime , func ,String , ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID , JSONB
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLAlchemyBase):
    __tablename__ = "assets"
    asset_id = Column(Integer,primary_key=True,autoincrement = True) #sql alchemy by defult apply index on clomn with UUID or primary key
    asset_uuid = Column(UUID(as_uuid=True),default = uuid.uuid4,unique=True,nullable=False)# for seacurity and user access i don.t need anyone to know that i have 10 project
  
    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column (Integer, nullable=False)
    asset_config = Column (JSONB, nullable=True)# JSONB because we want to read(retrive data) as it'd latency is low

    asset_project_id = Column(Integer,ForeignKey("projects.project_id"),nullable=False)
   
    created_at = Column(DateTime(timezone=True),server_default = func.now(),nullable = False)
    update_at = Column(DateTime(timezone=True),onupdate= func.now(),nullable=True)

   
    project = relationship("Project",back_populates="assets") # you have class or model named with project i will take data from it to put in assets
    chunks = relationship("DataChunk", back_populates="asset")

    __tabel_args__ = (
        Index('ix_asset_project_id',asset_project_id), # apply index on asset_progect_id  
        Index('ix_asset_type',asset_type) # apply index on asset_progect_id  
    )


