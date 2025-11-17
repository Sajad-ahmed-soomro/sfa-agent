# app/main.py
from fastapi import FastAPI
from app.model import AgentRequest, AgentResponse, Status
from app.langgraph_adapter import SfaLangGraphAgent
from typing import Dict, Any

app = FastAPI(title="Sustainability Footprint Agent (SFA) - LangGraph")

# Instantiate the agent (graph)
sfa_agent = SfaLangGraphAgent()

@app.get("/health")
def health():
    return {"status": "ok", "message": "I'm up and ready"}

@app.post("/analyze", response_model=AgentResponse)
def analyze(req: AgentRequest):
    try:
        # Convert Pydantic messages into plain dicts for the graph runner
        messages = [m.dict() for m in req.messages]
        data = sfa_agent.run(messages)
        if data is None:
            raise Exception("Agent returned no data")
        return AgentResponse(agent_name="sfa-agent", status=Status.SUCCESS, data=data, error_message=None)
    except Exception as e:
        return AgentResponse(agent_name="sfa-agent", status=Status.ERROR, data=None, error_message=str(e))
