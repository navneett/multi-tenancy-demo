"""
Local smoke test - run the agent on your machine before deploying, simulating
Customer A and Customer B as two different ADK sessions/user_ids.

Note: this still requires real Agent Identity auth providers to exist (step 3),
since AuthenticatedFunctionTool resolves credentials through that service even
in local runs - there's no local-only stub for the 3LO flow.

Usage:
    python setup/06_local_test.py
"""

import asyncio

from vertexai import agent_engines

from agent.agent import root_agent


async def run_as(user_id: str, message: str):
    app = agent_engines.AdkApp(agent=root_agent)
    print(f"\n--- session for user_id={user_id} ---")
    async for event in app.async_stream_query(user_id=user_id, message=message):
        print(event)


async def main():
    # Simulates Customer A's user logging in and asking about their contracts.
    await run_as(
        user_id="customerA-alice",
        message="Find any vendor agreements in my Drive and summarize the termination clause.",
    )

    # Simulates Customer B's user, in a separate session/user_id.
    # This should NEVER see Customer A's documents - if it does, that's a
    # credential-resolution bug, not a prompt-engineering issue, and should
    # be fixed in the auth provider / binding config, not by adding more
    # instructions to the agent.
    await run_as(
        user_id="customerB-bob",
        message="What contracts do I have in Drive related to onboarding?",
    )


if __name__ == "__main__":
    asyncio.run(main())
