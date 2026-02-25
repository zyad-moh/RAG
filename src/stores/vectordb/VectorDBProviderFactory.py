from .provider import QdrantDBProvider,PGVectorProvider
from.VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:
    def __init__(self, config,db_client: sessionmaker = None):#config to take the config fo DB
        self.config=config
        self.BaseController =BaseController()
        self.db_client = db_client
    def create(self, provider:str):
        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client=self.BaseController.get_database_path(self.config.VECTOR_DB_PATH)# note that self.config.VECTOR_DB_PATH is refer to the db name npt path # it was named with db_path
            return QdrantDBProvider(
                
                db_client=qdrant_db_client,# it was named with db_path
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
               
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
            )

        if provider == VectorDBEnums.PGVECTOR.value:
            return PGVectorProvider(
                
                db_client=self.db_client,
                defult_vector_size = self.config.EMBEDDING_MODEL_SIZE,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
            )
        return None
