# Production Architecture

This service is a payment gateway adapter. External systems should integrate with
our stable API, not directly with a bank-specific API.

## Layers

```text
1C / site / POS / future frontend
        |
        v
FastAPI public API
        |
        v
PaymentGateway
        |
        +-- MKassaProvider -> MKassa API
        +-- FutureBankProvider -> another bank API
        |
        v
PaymentStore -> PostgreSQL in production, SQLite in tests/local demo
```

## Database Choice

Production database: PostgreSQL.

SQLite is kept only for tests and quick local runs. The application talks to the
database through SQLAlchemy, so switching storage is only a `DATABASE_URL`
change.

Local/test:

```env
DATABASE_URL=sqlite:///./data/payment_gateway.db
```

Production:

```env
DATABASE_URL=postgresql+psycopg://payments:<password>@postgres:5432/payment_gateway
```

For local and demo environments, `AUTO_CREATE_SCHEMA=true` can create tables on
startup. For stricter production deploys, run Alembic first and start the app
with `AUTO_CREATE_SCHEMA=false`.

```bash
DATABASE_URL=postgresql+psycopg://payments:<password>@postgres:5432/payment_gateway \
  .venv/bin/python -m alembic upgrade head
```

## Provider Boundary

Bank-specific logic must stay behind `PaymentProvider`.

Current provider:

```text
src/payment_gateway/api.py      -> HTTP-only FastAPI layer
src/payment_gateway/service.py  -> business use cases
src/payment_gateway/gateway.py          -> provider registry
src/payment_gateway/providers/mkassa.py -> low-level MKassa HTTP client and adapter
src/payment_gateway/store.py            -> SQL persistence
```

The intended dependency direction is:

```text
api -> service -> gateway/provider -> bank client
api -> service -> store
```

This keeps the design close to SOLID:

- Single responsibility: routes, use cases, provider clients, and persistence are separate.
- Open/closed: a new bank is added as a new provider without rewriting existing MKassa code.
- Dependency inversion: business flows depend on the provider protocol, not one concrete bank API.

When adding another bank:

1. Add a bank client that knows only that bank's HTTP API.
2. Add a provider implementing the `PaymentProvider` protocol.
3. Register it in `PaymentGateway`.
4. Keep public API payloads stable unless a new business capability is required.

## Public API Rule

External clients should use our API and `X-Integration-Key`.

Do not expose:

- MKassa API key;
- bank-internal auth;
- bank-specific webhook secret;
- raw bank endpoint URLs.

## Audit

The service persists:

- transactions;
- webhook events with duplicate detection;
- API access events by `integration_name`.

These tables are intentionally provider-aware, so future banks can reuse the
same operational and frontend screens.

## Frontend Readiness

Frontend should use the same API as 1C/site/POS:

- create QR;
- render QR PNG;
- check transaction status;
- read local audit/debug data for support screens.

Do not build frontend logic around MKassa field names directly. Treat MKassa as
one provider under the gateway.
