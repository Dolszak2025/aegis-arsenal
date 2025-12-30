import os
import asyncio
import base64
import json
import functions_framework
from google.cloud import logging as cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

from database import init_db_pool, get_db_pool, CustomAsyncPostgresSaver

# LangGraph and LangChain imports
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

# Configure Google Cloud Logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging_client.logger("genesis-proof-of-life")

# Configure OpenTelemetry
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
trace.set_tracer_provider(provider)

# Global DB pool
db_initialized = False

async def ensure_db_pool():
    global db_initialized
    if not db_initialized:
        supabase_conn_string = os.environ.get("SUPABASE_CONN_STRING")
        if not supabase_conn_string:
            raise ValueError("SUPABASE_CONN_STRING not set")
        await init_db_pool(supabase_conn_string)
        db_initialized = True

# LangGraph Agent State
class AgentState(TypedDict):
    input: str
    chat_history: list
    next_step: str
    agent_outcome: str
    security_analysis: dict  # For security bot
    sub_agent: str  # For swarm routing

# Import specialized agents
from security_agent import SECURITY_NODES, security_analyze, security_recommend
from devops_agent import DEVOPS_NODES, devops_analyze, devops_report, devops_execute
from financial_guard import FINANCIAL_GUARD, verify_budget_ceiling

# Supervisor Router
def supervisor_router(state: AgentState):
    """
    Initiative: Determines which specialized bot in the swarm
    is best suited for the incoming Pub/Sub signal.
    """
    intent = state['input'].lower()
    if "iam" in intent or "permission" in intent or "security" in intent:
        state['sub_agent'] = "security_bot"
        return "security_analyze"
    elif "deploy" in intent or "build" in intent or "terraform" in intent or "health" in intent:
        state['sub_agent'] = "devops_bot"
        return "devops_analyze"
    else:
        state['sub_agent'] = "general_bot"
        return "model"

# LangGraph Nodes
def call_model(state: AgentState):
    """LLM reasoning node."""
    # Initialize LLM inside the node to ensure API key is available
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    prompt = f"Process this input: {state['input']}\nHistory: {state['chat_history']}"
    response = llm.invoke(prompt)
    state['agent_outcome'] = response.content
    state['next_step'] = "action"
    return state

def execute_tool(state: AgentState):
    """Technical action node for Agent Bots."""
    # Example: Execute some tool based on outcome
    logger.log_text(f"Executing tool with outcome: {state['agent_outcome']}")
    # Placeholder for actual tool execution
    state['next_step'] = "end"
    return state

def reflect_node(state: AgentState):
    """Self-reflective node for quality control."""
    outcome = state.get('agent_outcome', '')
    # Simple reflection: check for security keywords
    security_issues = []
    if 'password' in outcome.lower() or 'secret' in outcome.lower():
        security_issues.append("Potential secret exposure detected")
    if len(outcome) > 1000:
        security_issues.append("Response too verbose - consider summarization")
    
    if security_issues:
        state['reflection_issues'] = security_issues
        state['agent_outcome'] = "REFLECTED: " + outcome + " | ISSUES: " + str(security_issues)
    else:
        state['reflection_issues'] = []
    
    return state

# Build the LangGraph workflow with routing
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_router)
workflow.add_node("model", call_model)
workflow.add_node("reflect", reflect_node)
workflow.add_node("action", execute_tool)
workflow.add_node("security_analyze", security_analyze)
workflow.add_node("security_recommend", security_recommend)
workflow.add_node("devops_analyze", devops_analyze)
workflow.add_node("devops_report", devops_report)
workflow.add_node("devops_execute", devops_execute)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", lambda x: x.get("next_step", "model"))
workflow.add_edge("model", "reflect")
workflow.add_edge("reflect", "action")
workflow.add_edge("action", END)
workflow.add_edge("security_analyze", "security_recommend")
workflow.add_edge("security_recommend", END)
workflow.add_edge("devops_analyze", "devops_report")
workflow.add_edge("devops_report", "devops_execute")
workflow.add_edge("devops_execute", END)

# Note: Graph is compiled with checkpointer inside the function

async def process_message_with_langgraph(data: str, message_id: str):
    """Process the message using LangGraph."""
    await ensure_db_pool()

    # Financial Hard-Stop: Check budget before processing
    budget_check = await verify_budget_ceiling()
    if budget_check["status"] == "LOCKDOWN":
        logger.log_text(f"Financial lockdown triggered: {budget_check}")
        return  # Exit early without processing

    # Get DB pool
    pool = get_db_pool()

    # Create checkpointer
    checkpointer = CustomAsyncPostgresSaver.from_pool(pool)

    logger.log_text(f"Processing message with LangGraph: {data}")

    # Initial state
    initial_state = AgentState(
        input=data,
        chat_history=[],
        next_step="",
        agent_outcome=""
    )

    # Compile the graph with checkpointer
    agent_graph = workflow.compile(checkpointer=checkpointer)

    # Run the graph with checkpointer
    config = {"configurable": {"thread_id": message_id}}
    result = await agent_graph.ainvoke(initial_state, config=config)

    logger.log_text(f"LangGraph result: {result['agent_outcome']}")

    # Here you can publish the result back to Pub/Sub or take further actions

@functions_framework.cloud_event
def genesis_proof_of_life_function(cloud_event):
    """Cloud Function triggered by Pub/Sub message."""
    # Start a trace
    with trace.get_tracer(__name__).start_as_current_span("genesis_proof_of_life_function"):
        try:
            # Decode the Pub/Sub message
            if 'message' in cloud_event.data:
                message_data = cloud_event.data['message']
                data = base64.b64decode(message_data['data']).decode('utf-8')
                message_id = message_data.get('messageId', 'unknown')
            else:
                # Fallback for different event format
                data = base64.b64decode(cloud_event.data.get('data', '')).decode('utf-8')
                message_id = cloud_event.data.get('messageId', 'unknown')

            logger.log_text(f"Received Pub/Sub message: {message_id} - {data}")

            # Check for resilience drill
            if "$$SSC_RESILIENCE_DRILL_ACTIVE" in data:
                logger.log_text("Resilience drill activated - simulating failure for checkpointer test")
                # Simulate a failure that should be retried
                raise Exception("Simulated resilience drill failure")

            # Run async processing
            asyncio.run(process_message(data, message_id))

            return "Processed successfully"

        except Exception as e:
            logger.log_text(f"Error processing message: {e}", severity="ERROR")
            raise

async def process_message(data: str, message_id: str):
    """Process the message asynchronously."""
    await process_message_with_langgraph(data, message_id)
