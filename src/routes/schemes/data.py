from pydantic import BaseModel
from typing import Optional
class ProcessRequest(BaseModel):# for endpoint requests
    file_id:str #scheme ensure thst fileid is str
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0 # must go to routes/ data as do_reset could came in request
