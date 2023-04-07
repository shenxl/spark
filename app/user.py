import redis
import json
from enum import Enum
from logs.logger import Logger

from logs.logger import Logger


# 设置日志
logger = Logger(__name__)
# 创建一个 Redis 实例
redis_client = redis.Redis(host='localhost', port=6379, db=0)
class UserMode(Enum):
    NORMAL = "NORMAL"
    ARTS = "ARTS"
    FILE = "FILE"
    ONLINE = "ONLINE"

def default(obj):
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def object_hook(obj):
    if 'mode' in obj:
        obj['mode'] = UserMode[obj['mode']]
    return obj
class User:
    
    def __init__(self, user_id,status="active",
                mode=UserMode.NORMAL, 
                arts_role=None,arts_template=None, arts_answer=None,
                file_type=None,file_name=None,file_id=None):
        
        self.id = user_id
        self.status = status
        self.mode = mode
        self.arts_role = arts_role
        self.arts_template = arts_template
        self.arts_answer = arts_answer  
        self.file_type = file_type
        self.file_name = file_name
        self.file_id = file_id
        
    def to_dict(self):
        return {
            'status': self.status,
            'mode': self.mode,
            'arts_role': self.arts_role,
            'arts_template': self.arts_template,
            'arts_answer': self.arts_answer,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_id': self.file_id,
        }
        
        
    @staticmethod
    def init(user_id):
        user = User(user_id)
        redis_data = json.dumps(user.to_dict(), default=default)
        redis_client.set(user_id, redis_data)
    
    @staticmethod
    def clear_redis(user_id):
        keys = redis_client.keys(f'message_store:{user_id}_*')
        for key in keys:
            redis_client.delete(key)
        
    @staticmethod
    def get_user(user_id):
        user = redis_client.get(user_id)
        if user is None:
            user = User(user_id)
            redis_data = json.dumps(user.to_dict(), default=default)
            redis_client.set(user_id, redis_data)
        else:
            user_dict = json.loads(user.decode(), object_hook=object_hook)
            user = User(user_id, **user_dict)
        return user
   
    @staticmethod
    def update_arts_mode(user_id, role, prompt, answer):
        user = User.get_user(user_id)
        user.mode = UserMode.ARTS
        user.file_type = None
        user.file_id = None
        user.file_name = None
        user.arts_template = prompt
        user.arts_role = role
        user.arts_answer = answer
        redis_data = json.dumps(user.to_dict(), default=default)
        redis_client.set(user_id, redis_data)
    
    @staticmethod   
    def update_files_mode(user_id,fileid, filename, filetype):
        user = User.get_user(user_id)
        user.mode = UserMode.FILE
        user.arts_template = None
        user.arts_role = None
        user.arts_answer = None
        user.file_id = fileid
        user.file_name = filename
        user.file_type = filetype
        
        redis_data = json.dumps(user.to_dict(), default=default)
        redis_client.set(user_id, redis_data)