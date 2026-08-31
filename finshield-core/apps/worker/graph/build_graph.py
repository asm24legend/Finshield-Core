from langgraph.graph import StateGraph, END
from graph.state import CaseState
from graph.nodes.kyc_agent import kyc_agent
from graph.nodes.sanctions_agent import sanctions_agent
from graph.nodes.market_risk_agent import market_risk_agent
from graph.nodes.aggregator_agent import aggregator_agent


def build_case_graph():
    graph = StateGraph(CaseState)

    graph.add_node("kyc_agent", kyc_agent)
    graph.add_node("sanctions_agent", sanctions_agent)
    graph.add_node("market_risk_agent", market_risk_agent)
    graph.add_node("aggregator_agent", aggregator_agent)

    graph.set_entry_point("kyc_agent")
    graph.add_edge("kyc_agent", "sanctions_agent")
    graph.add_edge("sanctions_agent", "market_risk_agent")
    graph.add_edge("market_risk_agent", "aggregator_agent")
    graph.add_edge("aggregator_agent", END)

    return graph.compile()