from __future__ import annotations

from typing import Protocol

from payment_gateway.models import (
    BranchListResponse,
    CancelResponse,
    DynamicQRCreate,
    DynamicQRResponse,
    StaticQRCreate,
    StaticQRResponse,
    Transaction,
    TransactionDetailListResponse,
    TransactionListResponse,
)


class PaymentProvider(Protocol):
    name: str

    async def create_dynamic_qr(self, payload: DynamicQRCreate) -> DynamicQRResponse: ...

    async def create_static_qr(self, payload: StaticQRCreate) -> StaticQRResponse: ...

    async def get_transaction(self, transaction_id: str) -> Transaction: ...

    async def cancel_transaction(self, transaction_id: str) -> CancelResponse: ...

    async def list_transactions(self, **filters: object) -> TransactionListResponse: ...

    async def transaction_details(self, **filters: object) -> TransactionDetailListResponse: ...

    async def branches(self, **filters: object) -> BranchListResponse: ...


class PaymentGateway:
    def __init__(self, providers: list[PaymentProvider], *, default_provider: str) -> None:
        self.providers = {provider.name: provider for provider in providers}
        self.default_provider = default_provider
        if default_provider not in self.providers:
            raise ValueError(f"Unknown default payment provider: {default_provider}")

    def provider(self, name: str | None = None) -> PaymentProvider:
        provider_name = name or self.default_provider
        try:
            return self.providers[provider_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported payment provider: {provider_name}") from exc
