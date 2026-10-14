from pydantic import BaseModel, Field
class PlayerSubmit(BaseModel):
    mlbb_id: str = Field(min_length=1, max_length=20)
    server_id: str = Field(min_length=1, max_length=10)
    nickname: str = Field(min_length=2, max_length=80)
    role: str = Field(default="flex", max_length=30)
class TournamentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = ""
    mode: str = "5v5"
    map_name: str = "Land of Dawn"
    rules: str = ""
    prize_pool: int = Field(default=0, ge=0)
    max_teams: int = Field(default=16, ge=2, le=256)
    status: str = "draft"
class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
