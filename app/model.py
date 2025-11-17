from pydantic import BaseModel
from typing import List,Any,Dict,Optional
from enum import Enum


class Role(str,Enum):
    USER="user"
    ASSISTANT="assistant"
    SYSTEM="system"


class Message(BaseModel):
    role:Role
    content:str

class AgentRequest(BaseModel):
    messages:List[Message]



class Status(str,Enum):
    SUCCESS = "success"
    ERROR = "error"


class AgentResponse(BaseModel):
    agent_name:str
    status:Status
    data:Optional[Dict[str,any]]=None
    error_message:Optional[str]=None



