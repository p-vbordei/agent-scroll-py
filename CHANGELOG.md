# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-19

Initial Python port of [`@p-vbordei/agent-scroll`](https://github.com/p-vbordei/agent-scroll) v0.1. Published to PyPI as [`agent-scroll`](https://pypi.org/project/agent-scroll/).

### Added
- Public API: `canonical`, `hash_canonical`, `seal`, `seal_chain`, `verify`, `serialize`, `deserialize`.
- Types: `Turn`, `SealedTurn`, `Sig`, `SignOpts`, `VerifyResult`, `VerifyFailure`.
- Schema validation: `validate_turn`, `validate_sealed_turn` — hand-rolled to mirror the TS Zod schema (role, model, params, messages, tool_calls, tool_results, timestamp_ns, prev_hash).
- 20 byte-equality vectors (`fixtures/c1-hex.json` + `fixtures/c1-turns.json`) imported verbatim from the TS conformance suite.
- C1–C4 conformance suite (`tests/test_conformance.py`): byte equality, mutation detection, serialize/deserialize roundtrip, chain tamper.
- Wire-format vectors `001`–`020` in `vectors/` — each must parse as a valid `SealedTurn` array.
- Runnable quickstart at `examples/quickstart.py` — build a 3-turn signed chain, verify, tamper, observe `BadHash`.
- Architecture notes at `docs/architecture.md`.

[Unreleased]: https://github.com/p-vbordei/agent-scroll-py/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/p-vbordei/agent-scroll-py/releases/tag/v0.1.0
