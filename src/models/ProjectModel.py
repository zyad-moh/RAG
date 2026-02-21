# responsble for the project collection
from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func,delete
#from models.db_schemes.minirag.schemes import Project
class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super() .__init__(db_client=db_client) #here i pass db_clients to BaseDataModel (عشان يفضل شغال) 
        self.db_client=self.db_client # c_post : allow me create session and close it , function should be asynv 
# now i have the collectoin lets make some process 1-creat project field
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init  
        #await  instance.init_collection()# to create indices
        return instance   
# c_post(comment on postgres update) i don't need init_collection as it's done automatic with alimbic
 

    async def  create_project(self,project:Project):# let'ss use the scheme this function will take object from project(pydantic) to insert it
        async with self.db_client() as session:# session maker which create session
            async with session.begin(): # here open session (connection)
                session.add(project)
            await session.commit()
            await session.refresh(project) # because data come without create and update ,,,رجعلي القيم اللي اتولدت تلقائيًا
        return project
        """result=await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))#await for motor , each document in collectoin have extra _id or could say inserted with id 
        project.project_id=result.inserted_id  # when insert data _id musn't be there as if he exist it's prevent mongo to create _id
        return project""" # what if _id doesn't exist in result.inserted_id sol (get/create)

    async def get_project_or_create_one(self,project_id:str):# let'ss use the scheme this function will take object from project(pydantic) to insert it
        async with self.db_client() as session: 
            async with session.begin():  
                print("Project object:", Project)
                print("Type:", type(Project))
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project is None:
                   project = Project(project_id=project_id) 
                   session.add(project)
                   await session.flush() 
                
                return project



        """ record= await self.collection.find_one({
            "project_id":project_id # field named project_id with type project_id
        })

        if record is None:
            project=Project(project_id=project_id)#دا كله عشان اقوله خزن ال بروجكت اى دى بس تبع ال scheme 
            project=await self.create_project(project=project)
            return project
        return Project(**record)#record is dict but i need it to be from project type
        """        

    #don't use get_all without paggination # like in google split all 100 search result in 10 pages 
    async def get_all_projects(self, page: int=1, page_size: int=10):#number of pages and page_size    
        async with self.db_client() as session:
            async with session.begin():

                total_documents = await session.execute(select(
                func.count( Project.project_id )

                ))

                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                 total_pages += 1

                query = select(Project).offset((page -1) * page_size ).limit(page_size)
                projects = await session.execute(query).scalars().all()
                return projects, total_pages
       
        """# count total number of documents
        total_documents = await self.collection.count_documents({})
        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
           total_pages += 1
        cursor = self.collection.find().skip((page-1)* page_size).limit(page_size)#cursor(is a list) for payload and memory efficient
        projects = []
        async for document in cursor:
           projects.append(
           Project( ** document)
           )
        return projects, total_pages #!!!!!!!!!!!!
"""
"""Short, clear answer

MongoDB will generate 10 DIFFERENT _id values
even if:

all 10 files are uploaded

in the same request

with the same project_id = 1

_id is per document, not per request, not per project."""