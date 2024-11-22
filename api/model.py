from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field
class BettingInfoCreate(BaseModel):
    username: str
    game_id: int
    bet_amount: int = Field(..., gt=0, description="Bet amount must be greater than 0")
    bet_side: Literal["home", "away"]
    end_time: datetime  

class BettingInfoUpdate(BaseModel):
    username: str
    game_id: int
    bet_amount: int = Field(..., gt=0, description="Bet amount must be greater than 0")
    bet_side: Literal["home", "away"]