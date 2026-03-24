from fastapi import APIRouter, HTTPException
from starlette import status

from app.dependencies import db_dependency, user_dependency
from app.models.agents import Agents
from app.schemas.agents import AgentCreate, AgentResponse
from loguru import logger

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AgentResponse)
async def add_agent(agent: AgentCreate, db: db_dependency, user: user_dependency):
    logger.info(f"Adding agent: {agent}")
    agent_model = Agents(
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        first_message=agent.first_message,
        voice_id=agent.voice_id,
        owner_id=user["id"],  # comes from the JWT token, not from the request
    )
    logger.info(f"Agent model: {agent_model}")
    db.add(agent_model)
    db.commit()
    db.refresh(agent_model)
    logger.info(f"Agent added: {agent_model}")
    return agent_model

@router.get("/", response_model=list[AgentResponse])
async def get_agents(db: db_dependency, user: user_dependency):
    # only return groceries belonging to the logged-in user
    agents = db.query(Agents).filter(Agents.owner_id == user["id"]).all()
    return agents

