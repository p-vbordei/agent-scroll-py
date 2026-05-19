# agent-scroll (Python)

[![CI](https://github.com/p-vbordei/agent-scroll-py/actions/workflows/ci.yml/badge.svg)](https://github.com/p-vbordei/agent-scroll-py/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](./LICENSE)

> **Python port of [`@p-vbordei/agent-scroll`](https://github.com/p-vbordei/agent-scroll).** Canonical byte-deterministic transcript format for AI-agent conversations. Byte-identical canonical bytes and Ed25519 signatures vs. the TypeScript reference; passes the same C1–C4 conformance suite.

## Install

```bash
pip install agent-scroll
```

## Conformance

```bash
pip install -e ".[dev]"
pytest -v
```

Fixtures in `fixtures/` (C1 byte-equality expected hex) and vectors in `vectors/` are copied verbatim from the [TS conformance suite](https://github.com/p-vbordei/agent-scroll/tree/main/conformance).

## License

Apache-2.0
