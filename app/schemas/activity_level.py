from pydantic import BaseModel, ConfigDict
from typing import Optional

class ActivityLevelBase(BaseModel):
    code: str
    name: str
    factor: float

class ActivityLevelCreate(ActivityLevelBase):
    pass

class ActivityLevelResponse(ActivityLevelBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ActivityLevelUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    factor: Optional[float] = None