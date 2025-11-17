# app/langgraph_adapter.py

from typing import List, Dict, Any, Optional, TypedDict
import re
from app import analysis

# -------------------------
# Real LangGraph Imports
# -------------------------
from langgraph.graph import StateGraph, START, END


# -------------------------
# LangGraph State Definition
# -------------------------
class SFAState(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    days: int
    household: Optional[str]
    readings: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    recommendations: List[str]
    response: Dict[str, Any]
    used_simulator: bool


# -------------------------
# Node Implementations
# -------------------------
def node_start(state: SFAState) -> SFAState:
    messages = state.get("messages", [])
    text = " ".join(m.get("content", "") for m in messages)

    # default
    days = 7
    household = None

    m = re.search(r"last\s+(\d+)\s+days", text, flags=re.I)
    if m:
        days = int(m.group(1))

    m2 = re.search(r"household[-_ ]?(\w+)", text, flags=re.I)
    if m2:
        household = m2.group(1)

    state["days"] = days
    state["household"] = household
    return state


def node_ingest(state: SFAState) -> SFAState:
    if "readings" in state:
        state["used_simulator"] = False
    else:
        days = state.get("days", 7)
        state["used_simulator"] = True
        state["readings"] = analysis.simulate_hourly_readings(days=days)

    return state


def node_analyze(state: SFAState) -> SFAState:
    readings = state.get("readings", [])
    metrics = analysis.aggregate_readings(readings)
    metrics["estimated_co2_kg"] = analysis.estimate_co2(metrics["energy_kwh_total"])
    metrics["efficiency_score"] = analysis.efficiency_score(metrics)

    state["metrics"] = metrics
    return state


def node_recommend(state: SFAState) -> SFAState:
    metrics = state.get("metrics", {})
    recs = analysis.generate_recommendations(metrics)
    state["recommendations"] = recs
    return state


def node_respond(state: SFAState) -> SFAState:
    days = state.get("days", 7)
    metrics = state.get("metrics", {})

    summary = (
        f"Energy usage over last {days} days: "
        f"{metrics.get('energy_kwh_total', 0)} kWh "
        f"(CO2: {metrics.get('estimated_co2_kg', 0)} kg)."
    )

    state["response"] = {
        "message": summary,
        "metrics": metrics,
        "recommendations": state.get("recommendations", [])
    }
    return state


# -------------------------
# Main Agent Class
# -------------------------
class SfaLangGraphAgent:
    def __init__(self):
        self.graph_builder = StateGraph(SFAState)

        # Add nodes
        self.graph_builder.add_node("start", node_start)
        self.graph_builder.add_node("ingest", node_ingest)
        self.graph_builder.add_node("analyze", node_analyze)
        self.graph_builder.add_node("recommend", node_recommend)
        self.graph_builder.add_node("respond", node_respond)

        # Edges
        self.graph_builder.add_edge(START, "start")
        self.graph_builder.add_edge("start", "ingest")
        self.graph_builder.add_edge("ingest", "analyze")
        self.graph_builder.add_edge("analyze", "recommend")
        self.graph_builder.add_edge("recommend", "respond")
        self.graph_builder.add_edge("respond", END)

        # Compile graph
        self.graph = self.graph_builder.compile()

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        state = {"messages": messages}
        result = self.graph.invoke(state)
        return result.get("response", {})
