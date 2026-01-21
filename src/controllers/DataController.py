# this file for data logic (validation)
from fastapi import UploadFile
from .BaseController import BaseController #. as BaseController is a file in same folder of DataControler
class DataController(BaseController):#here DataController inheret BaseController so can access app_settings
    def __init__(self):
        super() .__init__()#here we force BaseController call it's __init__ (app_settings)
        self.size_scale=1048567

    def validate_uploaded_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False,"type not supported"
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, "size is too big your limit is 10M"
        
        return True ,"succes"