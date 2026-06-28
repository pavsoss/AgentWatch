"""Tests for server-side premium entitlement enforcement (issue #462)."""

from __future__ import annotations

import importlib
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException


@pytest.fixture(scope="module")
def keypair() -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


def _token(private_pem: str, **claims) -> str:
    payload = {
        "sub": "user@example.com",
        "tier": "enterprise",
        "exp": datetime.now(UTC) + timedelta(days=30),
        "features": ["compliance"],
        **claims,
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


def _reload(monkeypatch, public_key: str | None, *, env: str | None = None):
    if public_key is None:
        monkeypatch.delenv("AGENTWATCH_LICENSE_PUBLIC_KEY", raising=False)
        monkeypatch.delenv("AGENTWATCH_LICENSE_PUBLIC_KEY_FILE", raising=False)
    else:
        monkeypatch.setenv("AGENTWATCH_LICENSE_PUBLIC_KEY", public_key)
    if env is None:
        monkeypatch.delenv("AGENTWATCH_ENV", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
    else:
        monkeypatch.setenv("AGENTWATCH_ENV", env)
    import agentwatch.api.entitlement as ent

    importlib.reload(ent)
    return ent


def test_disabled_without_key(monkeypatch):
    ent = _reload(monkeypatch, None)
    assert ent.entitlement_enforcement_enabled() is False
    assert ent.authenticate_entitlement(x_entitlement_token=None) is None
    assert ent.require_entitlement("compliance")(entitlement=None) is None


def test_production_without_key_fails_closed(monkeypatch):
    ent = _reload(monkeypatch, None, env="production")
    with pytest.raises(HTTPException) as exc:
        ent.require_entitlement("compliance")(entitlement=None)
    assert exc.value.status_code == 500


def test_valid_token_grants_feature(monkeypatch, keypair):
    private_pem, public_pem = keypair
    ent = _reload(monkeypatch, public_pem)
    entitlement = ent.authenticate_entitlement(x_entitlement_token=_token(private_pem))
    assert ent.require_entitlement("compliance")(entitlement=entitlement) is entitlement


def test_missing_token_rejected(monkeypatch, keypair):
    _, public_pem = keypair
    ent = _reload(monkeypatch, public_pem)
    with pytest.raises(HTTPException) as exc:
        ent.authenticate_entitlement(x_entitlement_token=None)
    assert exc.value.status_code == 402


def test_invalid_token_rejected(monkeypatch, keypair):
    _, public_pem = keypair
    ent = _reload(monkeypatch, public_pem)
    with pytest.raises(HTTPException) as exc:
        ent.authenticate_entitlement(x_entitlement_token="bad.token.value")  # noqa: S106
    assert exc.value.status_code == 402


def test_feature_not_granted_rejected(monkeypatch, keypair):
    private_pem, public_pem = keypair
    ent = _reload(monkeypatch, public_pem)
    entitlement = ent.authenticate_entitlement(
        x_entitlement_token=_token(private_pem, features=["sso"])
    )
    with pytest.raises(HTTPException) as exc:
        ent.require_entitlement("compliance")(entitlement=entitlement)
    assert exc.value.status_code == 402


def test_machine_bound_token_checked_against_header(monkeypatch, keypair):
    private_pem, public_pem = keypair
    ent = _reload(monkeypatch, public_pem)
    bound = _token(private_pem, machine_id="client-fp")
    assert ent.authenticate_entitlement(x_entitlement_token=bound, x_machine_id="client-fp")
    with pytest.raises(HTTPException) as exc:
        ent.authenticate_entitlement(x_entitlement_token=bound, x_machine_id="other")
    assert exc.value.status_code == 402


def test_eu_ai_act_report_gated(monkeypatch, keypair):
    private_pem, public_pem = keypair
    from fastapi.testclient import TestClient

    import agentwatch.api.entitlement as ent
    from agentwatch.api.server import app

    monkeypatch.setattr("agentwatch.api.server._API_KEY", None)
    monkeypatch.setattr(ent, "_LICENSE_PUBLIC_KEY", public_pem)
    client = TestClient(app)

    assert client.get("/api/v1/governance/eu-ai-act-report").status_code == 402
    ok = client.get(
        "/api/v1/governance/eu-ai-act-report",
        headers={"X-Entitlement-Token": _token(private_pem)},
    )
    assert ok.status_code == 200
    assert ok.json()["article"] == "EU AI Act Article 15"
