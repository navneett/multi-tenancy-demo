"""
Thin client wrapper for calling the deployed contract analyst agent.

Single chokepoint rule: every call into the agent goes through `ask_agent`,
and `ask_agent` takes a `CurrentUser`, never a bare string user_id. This
makes it structurally awkward to ever pass an unverified or client-supplied
identity into the agent - you'd have to manufacture a CurrentUser, which
only auth.py's verified paths do.
"""

from collections.abc import AsyncIterator

import vertexai
from vertexai import agent_engines

from . import config
from .auth import CurrentUser

vertexai.init(project=config.PROJECT_ID, location=config.LOCATION)

_remote_agent = agent_engines.get(config.AGENT_ENGINE_RESOURCE_NAME)


async def ask_agent(
    user: CurrentUser,
    message: str,
    session_id: str | None = None,
) -> AsyncIterator[dict]:
    """Streams events from the agent for the given verified user.

    user.uid becomes the agent_engine `user_id` - this is the value Agent
    Identity and Agent Engine Sessions both key off internally. Customer A's
    uid and Customer B's uid resolve to entirely separate credential sets;
    nothing in this function (or anywhere upstream of it) lets one bleed
    into the other.
    """
    async for event in _remote_agent.async_stream_query(
        user_id=user.uid,
        session_id=session_id,
        message=message,
    ):
        yield event
