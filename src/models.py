from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


#This file stores all models used for validation or the business logic
            
#this model is only used for validation purposes, it does not interact with the database
#no distinction between the type of sensor, this can be found from the fields that are present
class Measurement(BaseModel):
    entry_timestamp: datetime
    sensor_id: int = Field(ge=0)
    temperature: float = Field (ge = -40, le = 70)
    humidity: float = Field (ge = 0, le = 1)
    wetness: Optional[float] = Field (ge = 0, le = 1, default = None)

