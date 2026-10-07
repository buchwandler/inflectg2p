---
schema_version: 2
object_type: release_entry
versioning:
  schema_version: 1
  revision: 1
entry_id: entry-0002
release_version: v0.1.0
kind: added
summary:
  Added configurable eSpeak runtime modes and optional pronunciation lexicons
  with traceable pronunciation hits
status: accepted
audience: null
scopes: []
source_refs:
  - git:9f87640a0099e32d98ce9dfc0e7b5fdc42f17168
paths:
  - .github/workflows/python-publish.yml
  - .github/workflows/test.yml
  - .ledger/ledger.toml
  - .ledger/releaseledger/.ledger-project.toml
  - .ledger/releaseledger/config.toml
  - .ledger/releaseledger/data/.ledger-project.toml
  - .ledger/taskledger/.ledger-project.toml
  - .ledger/taskledger/config.toml
  - LICENSE
  - MANIFEST.in
  - NOTICE
  - README.md
  - docs/Makefile
  - docs/api.md
  - docs/architecture.md
  - docs/backends.md
  - docs/changelog.md
  - docs/cli.md
  - docs/codec.md
  - docs/compatibility.md
  - docs/conf.py
  - docs/index.md
  - docs/installation.md
  - docs/lexicons.md
  - docs/make.py
  - docs/prepared-text.md
  - docs/quickstart.md
  - docs/requirements.txt
  - examples/README.md
  - examples/backend_modes.py
  - examples/basic_usage.py
  - examples/custom_backend.py
  - examples/direct_g2lex.py
  - examples/lexicon_selection.py
  - examples/lexicon_usage.py
  - examples/result_inspection.py
  - inflectg2p/__init__.py
  - inflectg2p/__main__.py
  - inflectg2p/api.py
  - inflectg2p/backends/__init__.py
  - inflectg2p/backends/base.py
  - inflectg2p/backends/espeak.py
  - inflectg2p/codec.py
  - inflectg2p/config.py
  - inflectg2p/errors.py
  - inflectg2p/frontend.py
  - inflectg2p/lexicons/__init__.py
  - inflectg2p/lexicons/base.py
  - inflectg2p/lexicons/g2lex.py
  - inflectg2p/lexicons/lexphon.py
  - inflectg2p/lexicons/overlay.py
  - inflectg2p/lexicons/registry.py
  - inflectg2p/lexicons/spans.py
  - inflectg2p/types.py
  - pyproject.toml
  - tests/goldens/inflect_v2_en_us.json
  - tests/test_api.py
  - tests/test_backend.py
  - tests/test_cli.py
  - tests/test_codec.py
  - tests/test_dependency_contract.py
  - tests/test_espeak_integration.py
  - tests/test_examples.py
  - tests/test_goldens.py
  - tests/test_lexicon_adapters.py
  - tests/test_lexicon_overlay.py
  - tests/test_lexicon_spans.py
  - tests/test_normalize_no_numbers.py
  - tests/test_packaging.py
  - tests/test_semantic_boundary.py
  - tests/test_symbols.py
  - tools/check_release_artifacts.py
issues: []
prs: []
sources:
  - git:9f87640a0099e32d98ce9dfc0e7b5fdc42f17168
contributors:
  - "@holgern"
breaking: false
internal: false
order: 2
---
