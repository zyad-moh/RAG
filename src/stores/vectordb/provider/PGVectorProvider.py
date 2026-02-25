from ..VectorDBInerface import VectorDBInerface
from ..VectorDBEnums import PgvectorTableSchemaEnum,PgVectorDistanceMethodEnums,PgVectorIndexTypeEnums,DistanceMethodEnums
import logging
from models.db_schemes import RetrievedDocument
from typing import List
from sqlalchemy.sql import text as sql_text
import json
import logging
class PGVectorProvider(VectorDBInerface):
    def __init__(self,db_client,defult_vector_size = 384,distance_method:str = None,index_threshold:int = 100):
        self.db_client = db_client
        self.defult_vector_size = defult_vector_size
        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value: 
            distance_method = PgVectorDistanceMethodEnums.DOT.value    
        self.distance_method = distance_method
        self.index_threshold = index_threshold
        self.pgvector_table_prefix = PgvectorTableSchemaEnum._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name:f"{collection_name}_vector_idx"


    async def connect(self):
       async with self.db_client() as session:
        async with session.begin():
            await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()

    async def disconnect(self):
        pass

    async def is_collection_existed(self,collection_name:str)->bool:
        record = None
        async with self.db_client() as session:
         async with session.begin():
            list_tbl=sql_text(f"SELECT * FROM pg_tables WHERE tablename = :collection_name")
            results = await session.execute(list_tbl,{"collection_name": collection_name})
            record = results.scalar_one_or_none()#nither the value nor the none
        return record

    async def list_all_collection(self)->list:
        record = []
        async with self.db_client() as session:
         async with session.begin():
            list_tbl=sql_text("SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix ")#tablename is column contain all tables_name like asset , chunk,....
            results = await session.execute(list_tbl,{"prefix":self.pgvector_table_prefix})
            records = results.scalars().all()
        return records

    async def get_collection_info(self,collection_name:str)->dict:
        async with self.db_client() as session:
         async with session.begin():
            list_tbl=sql_text(f"SELECT schemaname,tablename,tableowner,tablespace,hasindexes FROM pg_tables WHERE tablename = :collection_name ")#tablename is column contain all tables_name like asset , chunk,....
            count_sql=sql_text(f"SELECT COUNT(*) FROM {collection_name}") # count all records in that collaction
            list_tbl = await session.execute(list_tbl,{"collection_name":collection_name})
            count_sql = await session.execute(count_sql)
            
            table_data = list_tbl.fetchone()# well return tuble of values ("","",...) عشان كدا طلع انه بيرجع 6 و المفروض انه يرجع 2 بس
        if not table_data:
            return None
        
        return {
            "table_info": {
            "schemaname": table_data[0],
            "tablename": table_data[1],
            "tableowner": table_data[2],
            "tablespace": table_data[3],
            "hasindexes": table_data[4],
            },
            "record_count":count_sql.scalar_one()
        }

    
    async def create_collection(self, collection_name:str,embedding_size:int,do_reset:bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name)
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collaction:{collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(f'CREATE TABLE {collection_name}('
                        f'{PgvectorTableSchemaEnum.ID.value} bigserial PRIMARY KEY,'
                        f'{PgvectorTableSchemaEnum.TEXT.value} text,'
                        f'{PgvectorTableSchemaEnum.VECTOR.value} vector({embedding_size}),'
                        f'{PgvectorTableSchemaEnum.METADATA.value} jsonb DEFAULT \'{{}}\','
                        f'{PgvectorTableSchemaEnum.CHUNK_ID.value} integer,'
                        f'FOREIGN KEY({PgvectorTableSchemaEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                    ')'
                )
                    await session.execute(create_sql)
                    await session.commit()

            return True
        return False

    async def delete_collection(self,collection_name:str):
        async with self.db_client() as session:
         async with session.begin():
            self.logger.info(f"Deleting collection:{collection_name}")
            delete_sql = sql_text(f"DROP TABLE IF EXISTS {collection_name}")
            await session.execute(delete_sql)
            await session.commit()# i make commit when change happen on db like insert update delete
        return True    


    async def is_index_existed(self,collection_name:str)-> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(
                   f"""SELECT 1 FROM pg_indexes WHERE tablename=:collection_name AND indexname=:indexname""" 
                )
                results = await session.execute(search_sql,{"collection_name":collection_name,"indexname":index_name})
                return bool(results.scalar_one_or_none())
    async def create_vector_index(self,collection_name:str,index_type:str = PgVectorIndexTypeEnums.HNSW):
        is_index_existed = await self.is_index_existed(collection_name=collection_name)
        if is_index_existed:
            return False
        
        async with self.db_client() as session:
            async with session.begin():
               count_sql=sql_text(f"SELECT COUNT(*) FROM {collection_name}") # count all records in that collaction
               result = await session.execute(count_sql)
               records_count = result.scalar_one()
               if records_count < self.index_threshold:
                    return False

               self.logger.info(f"start : creating vector index for collection :{collection_name}")
               index_name = self.default_index_name(collection_name) 
               create_idx_sql = sql_text(
                                            f'CREATE INDEX {index_name} ON {collectoin_name}'
                                            f'USING {index_type} ({PgvectorTableSchemaEnum.VECTOR.value} {self.distance_method})'
               ) 
               await session.execute(create_idx_sql)
               await session.commit()
               self.logger.info(f"end : created vector index for collection :{collection_name}")


    async def reset_vector_index(self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value) ->bool:
            index_name = self.default_index_name(collection_name)
            async with self.db_client() as session:
                async with session.begin():
                    drop_sql = sql_text(f"DROP INDEX IF EXISTS {index_name}")
                    await session.execute(drop_sql)
            return self.create_vector_index(collection_name,index_type)        
                    
   
   
    async def insert_one(self,collection_name:str,text:str,vector:list,metadata:dict =None,record_id:str=None):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Error collaction :{collection_name} not exist to insert ")
            return False

        if not record_id:
            self.logger.info(f"record_id is empty")
            return False

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name}'
                f'({PgvectorTableSchemaEnum.TEXT.value},{PgvectorTableSchemaEnum.VECTOR.value},{PgvectorTableSchemaEnum.METADATA.value},{PgvectorTableSchemaEnum.CHUNK_ID.value})'
                'VALUES (:text,:vector,:metadata,:chunk_id)'
                )
                metadata_json = json.dumps(metadata,ensure_ascii = False) if metadata is not None else "{}" 
                await session.execute(insert_sql,
                {"text":text,
                 "vector":"[" + ",".join([str(v) for v in vector]) + "]",# because sql want "[1,2,3,4]" not [1,2,3,4]
                 "metadata":metadata_json,
                 "chunk_id":record_id,
                })
                await session.commit()
                await self.create_vector_index(collection_name=collection_name)
        return True


    async def insert_many(self,collection_name:str,texts:list,vectors:list,metadata:list =None,record_ids:list=None,
    batch_size:int=50):
        
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Error collaction :{collection_name} not exist to insert ")
            return False
        

        if len(vectors) != len(record_ids):
            self.logger.info(f"Error num of vectors  not num of equal record_ids for collection {collection_name} ")
            return False

        
        if not metadata or len(metadata)==0:
            metadata =[None]*len(texts)

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0,len(texts),batch_size):
                    batch_end = i + batch_size

                    batch_texts = texts[i:batch_end]
                    batch_vectors = vectors[i:batch_end]
                    batch_metadata = metadata[i:batch_end]
                    batch_record_ids = record_ids[i:batch_end]
                    values = []
                    for _text,_vector,_metadata,_record_id in zip(batch_texts,batch_vectors,batch_metadata,batch_record_ids):
                        # metadata(dict by default) must be passed to sql as json 

                        metadata_json = json.dumps(_metadata,ensure_ascii = False) if _metadata is not None else "{}" 
                        values.append(
                          {"text":_text,
                        "vector":"[" + ",".join([str(v) for v in _vector]) + "]",# because sql want "[1,2,3,4]" not [1,2,3,4]
                        "metadata":metadata_json,
                        "chunk_id":_record_id,
                        }  
                        )
                                         
                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name}'
                    f'({PgvectorTableSchemaEnum.TEXT.value},'
                    f'{PgvectorTableSchemaEnum.VECTOR.value},'
                    f'{PgvectorTableSchemaEnum.METADATA.value},'
                    f'{PgvectorTableSchemaEnum.CHUNK_ID.value})'
                    'VALUES (:text,:vector,:metadata,:chunk_id)'
                    ) 
                    await session.execute(batch_insert_sql,values)
        await self.create_vector_index(collection_name=collection_name)# i called create_vector_index here in PGVectorProvider not in nlp_controller because create_vector_index is spetial for PGVectorProvider and doesn't exist into other providers
        return True


    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Error collaction :{collection_name} not exist to insert ")
            return False
        
        vector = "[" + ",".join([str(v) for v in vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(f'SELECT {PgvectorTableSchemaEnum.TEXT.value} as text , 1-({PgvectorTableSchemaEnum.VECTOR.value} <=> :vector) as score'
                f' FROM {collection_name}'
                ' ORDER BY SCORE DESC '
                f'LIMIT {limit}'
                )
        
                result = await session.execute(search_sql,{"vector" : vector})
                records = result.fetchall()
                return[ RetrievedDocument(text = r.text,score = r.score) for r in records]
"""values= [{"name": "Ali","text","hfkjknkl","_vector":"[1,2,3,4]","_metadata":"2ni3f4"},
                                {"name": "Omar","text","hfkjknkl","_vector":"[1,2,3,4]","_metadata":"2ni3f4"},
                                {"name": "Zyad","text","hfkjknkl","_vector":"[1,2,3,4]","_metadata":"2ni3f4"},
                                                    ...
                                                    ...
                                                    ...
                                {"name": "Zyad","text","hfkjknkl","_vector":"[1,2,3,4]","_metadata":"2ni3f4"}->50]  """ 



#we made  (as text) in search fun because if i changed column name in future 
#  <=>  to calc cosin similarity and it return the cos(x) so we made 1 - ()
# in search_by_vector func i said in query order(desc) the text column based on the score 
# problem when insert vector it make a new cluster solve apply indexing after all insertion or after specific num of insertion to apply hnsw on all vectors , and under that spacific number we could use greedy search