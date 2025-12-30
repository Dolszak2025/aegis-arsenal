"""
DevOps Agent - Specialized Platform Engineer Bot
Part of the Aegis Arsenal Swarm Engine
Handles deployment, IaC, and platform health monitoring
"""

import os
import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from google.cloud import run_v2, functions_v2
from google.auth import default

# Initialize GCP clients
credentials, project = default()
run_client = run_v2.ServicesAsyncClient(credentials=credentials)
functions_client = functions_v2.FunctionServiceAsyncClient(credentials=credentials)

# Initialize LLM for DevOps reasoning
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.2,  # Lower temperature for precise operations
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

async def check_deployment_health(service_name: str, service_type: str = "cloud_run") -> Dict[str, Any]:
    """
    Check the health of a deployed service (Cloud Run or Cloud Functions).
    """
    try:
        if service_type == "cloud_run":
            request = run_v2.GetServiceRequest(
                name=f"projects/{os.environ.get('PROJECT_ID')}/locations/europe-central2/services/{service_name}"
            )
            service = await run_client.get_service(request)
            health_status = {
                "status": "healthy" if service.conditions[0].state == "CONDITION_SUCCEEDED" else "unhealthy",
                "latest_revision": service.latest_ready_revision,
                "traffic_split": service.traffic
            }
        elif service_type == "cloud_functions":
            request = functions_v2.GetFunctionRequest(
                name=f"projects/{os.environ.get('PROJECT_ID')}/locations/europe-central2/functions/{service_name}"
            )
            function = await functions_client.get_function(request)
            health_status = {
                "status": "healthy" if function.state == functions_v2.Function.State.ACTIVE else "unhealthy",
                "runtime": function.runtime,
                "entry_point": function.entry_point
            }
        else:
            return {"error": f"Unsupported service type: {service_type}"}

        return health_status

    except Exception as e:
        return {"error": f"Failed to check deployment health: {str(e)}"}

async def analyze_terraform_plan(plan_output: str) -> str:
    """
    Analyze a Terraform plan output and provide recommendations.
    """
    try:
        prompt = f"""
        Analyze this Terraform plan output and provide a summary of changes,
        potential risks, and recommendations:

        {plan_output}

        Focus on:
        1. Resources being created/modified/destroyed
        2. Security implications
        3. Cost impacts
        4. Best practices compliance
        """
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Failed to analyze Terraform plan: {str(e)}"

async def execute_deployment_command(command: str) -> Dict[str, Any]:
    """
    Simulate or log deployment commands (in production, this would execute via secure APIs).
    """
    # In a real implementation, this would use GCP APIs or secure execution
    # For now, return a simulation
    return {
        "command": command,
        "status": "simulated_success",
        "output": f"Simulated execution of: {command}",
        "recommendation": "In production, execute via approved CI/CD pipeline only."
    }

# Define the DevOps Bot's specialized workflow
def devops_analyze(state):
    """DevOps analysis node for deployment and IaC queries."""
    input_text = state['input']

    # Determine analysis type from input
    if "health" in input_text.lower() or "status" in input_text.lower():
        # Extract service name (simplified)
        service_name = "aegis-arsenal"  # Default, could be parsed from input
        asyncio.run(check_deployment_health(service_name))
        state['devops_analysis'] = f"Health check initiated for {service_name}"
        state['next_action'] = "report"
    elif "terraform" in input_text.lower() or "iac" in input_text.lower():
        # Placeholder for Terraform analysis
        state['devops_analysis'] = "Terraform analysis requested"
        state['next_action'] = "plan"
    elif "deploy" in input_text.lower():
        # Deployment command
        command = "gcloud run deploy aegis-arsenal --source=."  # Example
        asyncio.run(execute_deployment_command(command))
        state['devops_analysis'] = f"Deployment command prepared: {command}"
        state['next_action'] = "execute"
    else:
        state['devops_analysis'] = {"message": "No specific DevOps action requested"}
        state['next_action'] = "end"

    return state

def devops_report(state):
    """Report DevOps findings."""
    analysis = state.get('devops_analysis', {})
    # Use LLM to generate report
    llm = ChatOpenAI(model="gpt-4", openai_api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = f"Generate a DevOps report based on: {analysis}"
    response = llm.invoke(prompt)
    state['agent_outcome'] = response.content
    state['next_action'] = "end"
    return state

async def route_to_optimized_provider(task: dict):
    """
    Initiative: Determines if a task is cheaper/faster on GCP vs. Edge.
    Returns the recommended provider for execution.
    """
    try:
        # Analyze task characteristics
        latency_critical = task.get('latency_critical', False)
        compute_intensive = task.get('compute_intensive', False)
        data_sensitive = task.get('data_sensitive', False)

        if latency_critical:
            # Low latency reasoning - prefer Supabase Edge Functions
            return "supabase_edge"
        elif compute_intensive:
            # Heavy lifting - use GCP Functions Gen2
            return "gcp_functions_gen2"
        elif data_sensitive:
            # Sensitive data - keep in GCP VPC
            return "gcp_cloud_run"
        else:
            # Default to cost-effective option
            return "supabase_edge"
    except Exception as e:
        print(f"Failed to route provider: {e}")
        return "gcp_functions_gen2"  # Safe fallback

async def execute_on_supabase_edge(function_name: str, payload: dict):
    """
    Execute a task on Supabase Edge Functions.
    Placeholder for actual Supabase API integration.
    """
    # In production, this would call Supabase Edge Runtime
    print(f"Simulating execution on Supabase Edge: {function_name} with {payload}")
    return {"status": "simulated_success", "provider": "supabase_edge"}

async def execute_on_vercel(function_name: str, payload: dict):
    """
    Execute a task on Vercel serverless functions.
    Placeholder for Vercel API integration.
    """
    # In production, this would call Vercel API
    print(f"Simulating execution on Vercel: {function_name} with {payload}")
    return {"status": "simulated_success", "provider": "vercel"}

# Update the devops_execute function to use multi-cloud routing
def devops_execute(state):
    """Execute DevOps actions with multi-cloud routing."""
    analysis = state.get('devops_analysis', {})

    # Determine optimal provider
    task = {"latency_critical": "health" in str(analysis).lower()}
    provider = asyncio.run(route_to_optimized_provider(task))

    if provider == "supabase_edge":
        result = asyncio.run(execute_on_supabase_edge("aegis-task", analysis))
    elif provider == "vercel":
        result = asyncio.run(execute_on_vercel("aegis-task", analysis))
    else:
        # Default GCP execution
        result = f"Executed on GCP: {analysis}"

    state['agent_outcome'] = f"Multi-cloud execution: {result}"
    state['next_action'] = "end"
    return state

# Export the nodes for integration with main swarm
DEVOPS_NODES = {
    "devops_analyze": devops_analyze,
    "devops_report": devops_report,
    "devops_execute": devops_execute
}