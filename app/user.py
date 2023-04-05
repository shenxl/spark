from flask import session
from enum import Enum

class UserMode(Enum):
    NORMAL = 0
    ARTS = 1
    FILE = 2
    ONLINE = 3


class User:
    
    def __init__(self, user_id):
        self.id = user_id
        self.status = "active"
        self.mode = UserMode.NORMAL
        self.arts_role = None
        self.arts_template = None
        self.arts_answer = None
        
    @staticmethod
    def get_user(user_id):
        if "users" not in session:
            session["users"] = {}
        if user_id not in session["users"]:
            session["users"][user_id] = User(user_id)
        return session["users"][user_id]
    
    def update_arts_mode(self, role, prompt, answer):
        self.mode = UserMode.ARTS
        self.arts_template = prompt
        self.arts_role = role
        self.arts_answer = answer
        session.modified = True
        session["users"][self.id] = self