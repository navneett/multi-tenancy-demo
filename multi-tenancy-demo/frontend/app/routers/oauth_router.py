"""
Hosts the `continue_uri` registered with Agent Identity's 3LO auth provider
(see agent repo's agent/config.py: OAUTH_CONTINUE_URI, and
setup/02_create_oauth_clients.md for where this exact path must also be
registered with Google's OAuth client config).

IMPORTANT - what this endpoint does NOT do: it does not see, store, or
exchange any access/refresh token. By the time the browser lands here,
Agent Identity has already completed the token exchange server-side. This
endpoint's only job is to let the in-flight agent session resume.

Confirm the exact query params Agent Identity appends to this redirect
against current docs before wiring this for real - the example below
assumes a `state` param that round-trips your session_id, which is the
standard OAuth pattern but the precise param names here may differ.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/oauth/validateUserId")
async def oauth_continue(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
):
    params = dict(request.query_params)
    session_id = params.get("state")  # adjust to whatever param actually carries this

    # A tiny page that closes itself / signals the chat tab to resume polling.
    # If your chat UI is a single page (no popup), redirect straight to /chat
    # instead of rendering this.
    return HTMLResponse(
        """
        <html><body style="font-family: sans-serif; padding: 2rem;">
          <p>Access granted. You can close this window and return to the chat.</p>
          <script>
            if (window.opener) { window.opener.postMessage('oauth-complete', '*'); window.close(); }
          </script>
        </body></html>
        """
    )
