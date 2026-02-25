from .BaseController import BaseController
# here iam trynig to control vectors db like reset and get info
# i know that i made this frunctions in the provider but lets see why we call it again here , answer: i use the function made in PGVectorProvider here like i used function insert one in index_into_vector_db
# i could say that here i (بظبط) parameter which will go to functoins in PGVectorProvider and use it's return (output) in assign or something else 
# instate of write the whole below code in routes i wrote it here in separated file
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
import json 

class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client,template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
    def create_collection_name(self, project_id):
        return f"collection_{self.vectordb_client.defult_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self,project=Project):
        collection_name = self.create_collection_name(project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vector_db_collection_info(self,project=Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)
        return json.loads(#to convert string to dict
            json.dumps(collection_info , default =lambda x: x.__dict__)
        )

    async def index_into_vector_db(self,project:Project,chunks:list[DataChunk],chunks_ids:list[int],do_reset:bool = False):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [c.chunk_text for c in chunks]
        metadata =[c.chunk_metadata for c in chunks]
        vectors=self.embedding_client.embed_text(text=texts,document_type=DocumentTypeEnum.DOCUMENT.value) # object from LLMProviderFactory which mean object from CohereProvider which contain embed_text ,here i have deleted comberihention loop aand passed texts direcly because i modified text:union[str,List[str]] in embd text as it could take list 
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,)


        _ = await self.vectordb_client.insert_many(
            collection_name = collection_name,
            texts = texts,
            metadata=metadata,
            vectors = vectors,
            record_ids=chunks_ids,
        )

        

        return True
    async def search_vector_db_collection(self,project:Project,text:str,limit:int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        query_vector = None
        vectors=self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnum.QUERY.value)# المكان اللى جوا الموديل اللى بعمل بيه الفيكتورس
        if not vectors or len(vectors)==0:
            return False 
  
        # note we have modified text:union[str,List[str]] in embd text function as it could take and return list so now vector is a list contain one vector
        if isinstance(vectors,list) and len(vectors)>0:
            query_vector=vectors[0]
       
        if not query_vector:
            return False 
       
        result = await self.vectordb_client.search_by_vector(# result is similar to collection info as it contain many diff objects but after apply schema it became a document or dict
            collection_name = collection_name,
            vector = query_vector,# because search_by_vector wait List[float] not List[List[float]]
            limit=limit,
        )

        if not result:
            return False

        return result
    async def answer_rag_question(self,project:Project,query:str,limit:int = 10):
        
        answer , full_prompt , chat_history = None , None , None

        retrieved_documents = await self.search_vector_db_collection(project=project,text=query,limit = limit)# المكان اللى متخزن جوا الفيكتورز
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer , full_prompt , chat_history
        
        system_prompt = self.template_parser.get("rag","system_prompt")
        """document_prompt = []
        for i,doc in enumerate(retrieved_documents):
        document_prompt.append(self.template_parser.get("rag","document_prompt",{
            "doc_num" : i+1 ,
            "chunk_text" : doc.text,
            }))"""

        documents_prompts="\n".join ([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunck_text": self.generation_client.process_text (doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag","footer_prompt", {
                    "query":query,
                   
            })
        
        chat_history = [self.generation_client.construct_prompt(
            prompt = system_prompt,
            role = self.generation_client.enums.SYSTEM.value # instate fo writing coher or open ai enum and i don't know which one is used 
            )]

        full_prompt = "\n\n".join([documents_prompts,footer_prompt])

        answer = self.generation_client.generate_text(
            prompt = full_prompt,
            chat_history = chat_history
        )

        return answer , full_prompt , chat_history