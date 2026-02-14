from .BaseController import BaseController
# here iam trynig to control vectors db like reset and get info
# i know that i made this frunctions in the provider but lets see why we call it again here
from models.db_schemes import project, data_chunk
from stores.llm.LLMEnums import DocumentTypeEnum
class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
    def create_collection_name(self, project_id):
        return f"collection_{project_id}"
    
    def reset_vector_db_collection(self,project=project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self,project=project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        return collection_info

    def index_into_vector_db(self,project=project,chunks:List[DataChunk],do_reset:bool = False):
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [c.chunk_text for c in chunks]
        metadata =[c.chunk_metadata for c in chunks]
        vectors=[self.embedding_client.embed_text(text=text,document_type=DocumentTypeEnum.DOCUMENT.value) for text in texts] # object from LLMProviderFactory which mean object from CohereProvider which contain embed_text
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,)


        _ = self.vectordb_client.insert_many(
            collection_name = collection_name,
            text = texts,
            metadata=metadata,
            vectors = vectors,

        )

        return True