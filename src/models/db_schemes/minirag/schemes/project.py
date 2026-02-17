from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column , Integer , DateTime , func
from sqlalchemy.dialects.postgresql import UUID
import uuid
class Project(SQLAlchemyBase):
    __tablename__ = "projects"
    project_id = Column(Integer,primary_key=True,autoincrement = True)
    project_uuid = Column(UUID(as_uuid=True),default = uuid.uuid4,unique=True,nullable=False)# for seacurity and user access i don.t need anyone to know that i have 10 project
    created_at = Column(DateTime(timezone=True),server_default = func.now(),nullable = False)#server_default to automaticlly put the time when record created 
    update_at = Column(DateTime(timezone=True),onupdate= func.now(),nullable=True)