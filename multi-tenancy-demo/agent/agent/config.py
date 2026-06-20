"""
Central configuration for the contract analyst agent.

Keep all GCP resource identifiers here so tools and the agent definition
don't hardcode strings in multiple places. Values are read from environment
variables at runtime (set these in your Agent Engine deployment config or
local .env for testing) - nothing here is a secret.
"""

import os

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# Agent Identity connector resource names (created in setup/03_create_auth_providers.sh)
AGENT_SELF_AUTH_PROVIDER = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/connectors/contract-analyst-self"
)
GOOGLE_DRIVE_AUTH_PROVIDER = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/connectors/google-drive-3lo"
)

# This URI must be hosted by YOUR frontend (not this agent) and must match
# the redirect URI registered with both Google and Atlassian OAuth clients.
# It's where the user lands after granting consent; your frontend's handler
# there is responsible for resuming the ADK session.
OAUTH_CONTINUE_URI = os.environ.get(
    "OAUTH_CONTINUE_URI", "https://YOUR_FRONTEND_DOMAIN/oauth/validateUserId"
)

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
