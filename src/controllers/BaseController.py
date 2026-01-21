#all controller may want to see app settings (.env,config) , 
#so we will load it in base controller as rest controoler will see it
from helpers.config import get_settings , settings 
# we will but get_settings as a constractor as when base controller is called then the caller (any other controoler ) get acces get_settings
class BaseController():
    
    def __init__(self):
        self.app_settings=get_settings()