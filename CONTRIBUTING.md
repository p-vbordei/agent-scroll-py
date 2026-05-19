# Contributing to agent-scroll-py

Thanks for considering a contribution. The bar is high because **this repo implements a format**: any change to canonical encoding, hashing, or signing semantics breaks every existing scroll. Please read this file before opening a PR.

## Orientation

- **The TS reference is the source of truth.** This port must produce byte-identical canonical bytes and hashes. If you find a divergence, it's a bug here.
- **Conformance vectors are the contract.** The 20 byte-equality vectors in `fixtures/c1-hex.json` (and the 20 wire-format files in `vectors/`) come from the TS suite. Do not edit them. If a vector needs to change, change it upstream in [`agent-scroll`](https://github.com/p-vbordei/agent-scroll) first and copy it here.
- **Idiomatic Python is welcome.** The port should look like Python, not transpiled TypeScript. TypedDicts, dataclasses, and stdlib types over custom wrappers.
- **One logical change per PR.** Easier to review, easier to revert.

## Dev setup

```bash
git clone https://github.com/p-vbordei/agent-scroll-py
cd agent-scroll-py
pip install -e ".[dev]"
# or, with uv:
uv sync --extra dev
```

## Run tests

```bash
pytest -v                          # full suite (C1–C4 + 20 schema-parse vectors)
pytest -v tests/test_conformance.py::test_c1_byte_equality   # just C1
ruff check .                       # lint
python examples/quickstart.py      # smoke the example
```

A healthy tree: `pytest` green, `ruff check` clean, and `examples/quickstart.py` prints `verify clean: ok=True` followed by `verify tampered: ok=False reason=BadHash`.

## Release process

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` — move items from `[Unreleased]` to a new dated section.
3. Tag: `git tag v0.x.y && git push --tags`.
4. Build + publish: `python -m build && twine upload dist/*` (PyPI name: `agent-scroll`).
5. GitHub release notes mirror the CHANGELOG entry.

## Code style

- Ruff config in `pyproject.toml`; line length 100.
- Type hints required on public API.
- No new runtime deps without strong justification — current deps are `jcs` and `cryptography`. Anything else is a no.
