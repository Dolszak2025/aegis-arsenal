"""
Security Architect Bot - Specialized Agent for IAM and Security Automation
Part of the Aegis Arsenal Swarm Engine
"""

import os
import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from google.cloud import iam_v1, resourcemanager_v3
from google.auth import default

# Initialize GCP clients
credentials, project = default()
iam_client = iam_v1.IAMClient(credentials=credentials)
resource_client = resourcemanager_v3.ProjectsClient(credentials=credentials)

# Initialize LLM for security analysis
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.1,  # Lower temperature for security decisions
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

@tool
def analyze_iam_policy(project_id: str) -> Dict[str, Any]:
    """
    Analyze IAM policies for a project to identify potential security risks.
    Returns a summary of roles, bindings, and recommendations.
    """
    try:
        # Get project IAM policy
        request = iam_v1.GetIamPolicyRequest(
            resource=f"projects/{project_id}"
        )
        policy = iam_client.get_iam_policy(request)

        analysis = {
            "total_bindings": len(policy.bindings),
            "roles_found": [binding.role for binding in policy.bindings],
            "high_privilege_roles": [],
            "recommendations": []
        }

        # Check for high-privilege roles
        dangerous_roles = [
            "roles/owner",
            "roles/editor",
            "roles/iam.securityAdmin",
            "roles/resourcemanager.projectIamAdmin"
        ]

        for binding in policy.bindings:
            if binding.role in dangerous_roles:
                analysis["high_privilege_roles"].append({
                    "role": binding.role,
                    "members": list(binding.members)
                })

        # Generate recommendations
        if len(analysis["high_privilege_roles"]) > 0:
            analysis["recommendations"].append(
                "Consider implementing least privilege: Replace broad roles with specific permissions"
            )

        if analysis["total_bindings"] > 50:
            analysis["recommendations"].append(
                "High number of bindings detected. Consider role consolidation."
            )

        return analysis

    except Exception as e:
        return {"error": f"Failed to analyze IAM policy: {str(e)}"}

@tool
def check_service_account_permissions(service_account_email: str) -> Dict[str, Any]:
    """
    Check permissions granted to a specific service account.
    """
    try:
        # This would require listing all resources and checking IAM
        # For simplicity, we'll check project-level permissions
        project_id = os.environ.get("PROJECT_ID")
        request = iam_v1.GetIamPolicyRequest(
            resource=f"projects/{project_id}"
        )
        policy = iam_client.get_iam_policy(request)

        sa_permissions = []
        for binding in policy.bindings:
            if f"serviceAccount:{service_account_email}" in binding.members:
                sa_permissions.append(binding.role)

        return {
            "service_account": service_account_email,
            "granted_roles": sa_permissions,
            "assessment": "Review roles for least privilege compliance"
        }

    except Exception as e:
        return {"error": f"Failed to check service account: {str(e)}"}

@tool
def generate_security_recommendation(analysis_data: Dict[str, Any]) -> str:
    """
    Use LLM to generate detailed security recommendations based on analysis.
    """
    try:
        prompt = f"""
        Based on this IAM security analysis, provide detailed recommendations:

        Analysis Data: {analysis_data}

        Focus on:
        1. Principle of Least Privilege violations
        2. Potential security risks
        3. Remediation steps
        4. Best practices for GCP IAM

        Provide actionable, prioritized recommendations.
        """

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Failed to generate recommendations: {str(e)}"

# Define the Security Architect's specialized workflow
def security_analyze(state):
    """Security analysis node for the agent."""
    input_text = state['input']

    # Determine analysis type from input
    if "iam" in input_text.lower() or "policy" in input_text.lower():
        project_id = os.environ.get("PROJECT_ID", "default-project")
        analysis = analyze_iam_policy(project_id)
        state['security_analysis'] = analysis
        state['next_action'] = "recommend"
    elif "service account" in input_text.lower() or "sa" in input_text.lower():
        # Extract service account email from input (simplified)
        sa_email = "aegis-bot-sa@" + os.environ.get("PROJECT_ID", "project") + ".iam.gserviceaccount.com"
        analysis = check_service_account_permissions(sa_email)
        state['security_analysis'] = analysis
        state['next_action'] = "recommend"
    else:
        state['security_analysis'] = {"message": "No specific security analysis requested"}
        state['next_action'] = "end"

    return state

def security_recommend(state):
    """Generate security recommendations."""
    analysis = state.get('security_analysis', {})
    recommendations = generate_security_recommendation(analysis)
    state['agent_outcome'] = recommendations
    state['next_action'] = "end"
    return state

# Export the nodes and tools for integration with main swarm
SECURITY_NODES = {
    "security_analyze": security_analyze,
    "security_recommend": security_recommend
}

SECURITY_TOOLS = [
    analyze_iam_policy,
    check_service_account_permissions,
    generate_security_recommendation
]

async def jit_elevation_analysis(error_log: str) -> str:
    """
    Action: Detects missing IAM roles and proposes a Terraform fix.
    """
    try:
        # Parse error for permission issues
        if "403" in error_log or "Forbidden" in error_log:
            # Extract missing permission (simplified parsing)
            if "iam.serviceAccounts.get" in error_log:
                suggested_role = "roles/iam.serviceAccountUser"
            elif "pubsub.topics.publish" in error_log:
                suggested_role = "roles/pubsub.publisher"
            elif "storage.objects.get" in error_log:
                suggested_role = "roles/storage.objectViewer"
            else:
                suggested_role = "roles/viewer"  # Default fallback

            tf_fix = f"""
resource "google_project_iam_member" "jit_elevation" {{
  project = "{os.environ.get('PROJECT_ID')}"
  role    = "{suggested_role}"
  member  = "serviceAccount:aegis-bot-sa@{os.environ.get('PROJECT_ID')}.iam.gserviceaccount.com"
}}

# Note: This is a JIT elevation. Review and apply manually or via approval workflow.
"""
            return f"Flag: $$SSC_DESIGN_PROTOCOLS_PENDING\nJIT Recommendation: {tf_fix}"
        else:
            return "No IAM elevation needed - error not permission-related"
    except Exception as e:
        return f"Failed to analyze JIT elevation: {str(e)}"