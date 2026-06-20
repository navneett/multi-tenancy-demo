"""
Google Drive tool for the contract analyst agent.

Isolation guarantee: this tool never receives a customer ID or a token as a
function argument that the model could be tricked into supplying. The
credential is resolved by the ADK auth framework from the ACTIVE SESSION's
identity, via the google-drive-3lo auth provider binding. The LLM only ever
sees document names and content - never the underlying access token.
"""

import io

import googleapiclient.discovery
import googleapiclient.http
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools import AuthenticatedFunctionTool, ToolContext

from .. import config

_drive_auth_scheme = GcpAuthProviderScheme(
    name=config.GOOGLE_DRIVE_AUTH_PROVIDER,
    continue_uri=config.OAUTH_CONTINUE_URI,
)


def _drive_client(access_token: str):
    credentials = googleapiclient.discovery.build(
        "drive",
        "v3",
        credentials=_bearer_credentials(access_token),
    )
    return credentials


def _bearer_credentials(access_token: str):
    # Lightweight credentials object - googleapiclient just needs something
    # with a valid .token and .apply(); we don't refresh here because
    # Agent Identity already handed us a live, refreshed access token.
    from google.oauth2.credentials import Credentials

    return Credentials(token=access_token)


async def search_contract_documents(
    query: str,
    tool_context: ToolContext,
) -> dict:
    """Searches the logged-in customer's own Google Drive for contract documents.

    Args:
        query: Free-text search, e.g. "MSA Acme Corp" or "vendor agreement 2025".

    Returns:
        A dict with a list of matching files (id, name, mimeType, modifiedTime).
        Only files the CURRENT customer has access to in their own Drive are
        ever returned - this tool call is scoped by the resolved credential,
        not by any tenant/customer value passed in the prompt.
    """
    access_token = tool_context.get_auth_response().get("access_token")
    if not access_token:
        return {"error": "Drive access not yet authorized for this user."}

    drive = _drive_client(access_token)
    safe_query = query.replace("'", "\\'")
    results = (
        drive.files()
        .list(
            q=(
                f"name contains '{safe_query}' and "
                "mimeType != 'application/vnd.google-apps.folder' and trashed = false"
            ),
            fields="files(id, name, mimeType, modifiedTime)",
            pageSize=10,
        )
        .execute()
    )
    return {"files": results.get("files", [])}


async def fetch_document_text(
    file_id: str,
    tool_context: ToolContext,
) -> dict:
    """Fetches the text content of a specific Drive file by ID, for analysis.

    Args:
        file_id: The Drive file ID returned by search_contract_documents.

    Returns:
        A dict with the extracted text content of the file, truncated if very long.
    """
    access_token = tool_context.get_auth_response().get("access_token")
    if not access_token:
        return {"error": "Drive access not yet authorized for this user."}

    drive = _drive_client(access_token)
    meta = drive.files().get(fileId=file_id, fields="mimeType,name").execute()
    mime_type = meta["mimeType"]

    if mime_type == "application/vnd.google-apps.document":
        request = drive.files().export_media(fileId=file_id, mimeType="text/plain")
    else:
        request = drive.files().get_media(fileId=file_id)

    buffer = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    text = buffer.getvalue().decode("utf-8", errors="ignore")
    return {"name": meta["name"], "text": text[:50_000]}


def build_drive_tools() -> list[AuthenticatedFunctionTool]:
    """Wraps the Drive functions as ADK tools bound to the 3LO Drive auth scheme."""
    return [
        AuthenticatedFunctionTool(func=search_contract_documents, auth_scheme=_drive_auth_scheme),
        AuthenticatedFunctionTool(func=fetch_document_text, auth_scheme=_drive_auth_scheme),
    ]
