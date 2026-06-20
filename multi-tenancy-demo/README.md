# multi-tenancy-demo

Multi-tenant contract analyst agent on GCP, demonstrating OAuth 2.0-based
per-customer data isolation. One Operator publishes the agent; Customer A
and Customer B each interact with it using only their own Google Drive
documents.

## Structure

```
agent/        ADK agent, deployed to Vertex AI Agent Engine.
              Tenant-agnostic by construction - one deployment serves all
              customers. Isolation is enforced by Agent Identity resolving
              a credential scoped to the calling session's user_id.

frontend/     FastAPI app: Firebase Auth login, role-based routing
              (Operator console vs customer chat), and the OAuth
              continue_uri that Agent Identity redirects to after a
              customer grants Drive access.
```

## Setup

**For the full step-by-step walkthrough (commands included, Windows-aware),
see [`SETUP.md`](./SETUP.md).** The summary below is the short version.

## Build order

1. **`agent/`** - follow `agent/README.md`: bootstrap the GCP project,
   register OAuth clients, create Agent Identity auth providers, deploy the
   agent via ADK. End with a `reasoningEngine` resource name.
2. **`frontend/`** - follow `frontend/README.md`: enable Firebase Auth,
   set the Operator claim on your own account, configure `.env` with the
   agent's resource name from step 1, run `uvicorn app.main:app`.

## Where tenant isolation actually lives

Not in either app's prompts or business logic - those are a backstop, not
the mechanism. It lives in:

- `frontend/app/auth.py` - the only place a `CurrentUser` (and therefore a
  `user_id`) can be constructed, and only from a verified Firebase session
  cookie. No route anywhere in `frontend/` accepts a tenant/customer
  identifier from a request body or query param.
- `agent/agent/tools/*.py` - Drive credentials are resolved per active
  session via Agent Identity's 3LO auth provider, never passed as a
  model-visible function argument.
- IAM bindings - only the specific deployed reasoning engine is granted
  `roles/iamconnectors.user` on the auth providers.

Same agent code path, same frontend code path, for both customers. Only the
resolved credential differs per request.

## Known gaps before this is production-grade

See `agent/README.md` and `frontend/README.md`'s respective "before you
treat this as production" / "known gaps" sections - notably: several
`gcloud alpha agent-identity` / `agent-registry` commands are preview-stage
and should be re-verified against current docs, and the OAuth popup wiring
in `frontend/app/templates/chat.html` is stubbed pending confirmation of the
live ADK `auth_request` event shape.
