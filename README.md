# agent-scroll (Python)

[![CI](https://github.com/p-vbordei/agent-scroll-py/actions/workflows/ci.yml/badge.svg)](https://github.com/p-vbordei/agent-scroll-py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agent-scroll)](https://pypi.org/project/agent-scroll/)
[![Spec](https://img.shields.io/badge/spec-v0.1-blue)](./SPEC.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)

> **Idiomatic Python port of [`@p-vbordei/agent-scroll`](https://github.com/p-vbordei/agent-scroll).** Canonical byte-deterministic transcript format for AI-agent conversations. Same RFC 8785 JCS bytes, same SHA-256 hashes, same Ed25519 signatures as the TypeScript reference — verified by 20 byte-equality vectors plus mutation, roundtrip, and chain-tamper tests.

A scroll is an ordered chain of *sealed turns*. Each turn is a normalized JSON object (`{version, turn, role, model, params, messages, ..., timestamp_ns, prev_hash?}`) that gets serialized via JCS, SHA-256 hashed, optionally Ed25519-signed, and linked to its predecessor by `prev_hash`. Any byte flip — in body, hash, signature, or chain order — is detectable.

## What's in the box

- `canonical(value)` — RFC 8785 JCS bytes
- `hash_canonical(value)` — `sha256:<hex>` string
- `seal(turn, sign=None)` — produce a `SealedTurn` (hash + optional Ed25519 signature)
- `seal_chain(turns, sign=None)` — chain-linked sealed turns, each carrying `prev_hash`
- `verify(chain, pubkey=None)` — schema + hash + chain link + signature
- `serialize` / `deserialize` — round-trip via canonical bytes
- `validate_turn` / `validate_sealed_turn` — explicit role / tool-call schema checks

## Install

```bash
pip install agent-scroll
```

Requires Python 3.10+. Runtime deps: `jcs`, `cryptography`.

## Quickstart

See [`examples/quickstart.py`](examples/quickstart.py) for the full script. Build three turns, seal-and-sign as a chain, verify, then mutate a byte and watch verify fail:

```bash
python examples/quickstart.py
```

Expected output:

```
sealed 3 turns, all hashes set
verify clean: ok=True
verify tampered: ok=False reason=BadHash
```

## How it relates

| Port | Source | Same vectors |
|---|---|---|
| [`agent-scroll`](https://github.com/p-vbordei/agent-scroll) | TypeScript reference | — |
| [`agent-scroll`](https://pypi.org/project/agent-scroll/) (this repo) | Python | C1–C4 + 20 byte-equality |
| [`agent-scroll-rs`](https://github.com/p-vbordei/agent-scroll-rs) | Rust | C1–C4 + 20 byte-equality |

## Conformance

This port is verified against the same fixture set as the TypeScript reference:

- **C1** — byte equality across 20 vectors (the gold standard). Canonical bytes of each fixture must hex-match the TS output.
- **C2** — single-byte mutation in hash or body MUST fail `verify`.
- **C3** — `serialize` → `deserialize` roundtrip is byte-stable.
- **C4** — chain tamper / reorder MUST fail `verify`.

```bash
pip install -e ".[dev]"
pytest -v
```

Fixtures in [`fixtures/`](fixtures/) (`c1-hex.json` carries the expected hex per vector) and the 20 wire-format vectors in [`vectors/`](vectors/) are copied verbatim from the [TS conformance suite](https://github.com/p-vbordei/agent-scroll/tree/main/conformance).

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for module map, dependency choices, and byte-determinism invariants.

## Development

```bash
git clone https://github.com/p-vbordei/agent-scroll-py
cd agent-scroll-py
pip install -e ".[dev]"
pytest -v
python examples/quickstart.py
```

## License

Apache-2.0 — see [LICENSE](./LICENSE).
