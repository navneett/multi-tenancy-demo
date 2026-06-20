"""
Step 5: Deploy the contract analyst agent to Vertex AI Agent Engine.

Run from the project root with the venv active:
    python setup/05_deploy_agent.py

This is a one-time (or per-update) operator action - customers never run this.
"""

import os

import vertexai
from vertexai import agent_engines

from agent.agent import root_agent

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.environ["STAGING_BUCKET"]  # e.g. gs://your-project-agent-staging

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

app = agent_engines.AdkApp(agent=root_agent, enable_tracing=True)

print(">> Deploying contract analyst agent to Vertex AI Agent Engine...")
remote_agent = agent_engines.create(
    agent_engine=app,
    requirements="agent/requirements.txt",
    extra_packages=["agent"],
    env_vars={
        "GOOGLE_CLOUD_PROJECT": PROJECT_ID,
        "GOOGLE_CLOUD_LOCATION": LOCATION,
        "OAUTH_CONTINUE_URI": os.environ.get(
            "OAUTH_CONTINUE_URI", "https://YOUR_FRONTEND_DOMAIN/oauth/validateUserId"
        ),
    },
    display_name="contract-analyst-agent",
)

print("")
print("Deployed.")
print(f"  Resource name:    {remote_agent.resource_name}")
print(f"  Reasoning engine: {remote_agent.resource_name.split('/')[-1]}")
print("")
print("Next:")
print("  1. Copy the reasoning engine ID above.")
print("  2. Re-run setup/03_create_auth_providers.sh with REASONING_ENGINE_ID=<id>")
print("     to grant this deployed agent access to the auth providers.")
print("  3. Your frontend calls this agent via remote_agent.async_stream_query(")
print("     user_id=<customer's authenticated user id>, message=...)")
