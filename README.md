# Diff testing precompiles Pectra

```
diff_testing/
├── README.md
├── docs/
│   └── design.md            # Detailed design decisions and protocols
├── python/
│   └── tests/               # Hypothesis-based fuzz tests
├── wrappers/
│   ├── rust/                # Rust implementation
│   ├── python/              # EELS implementation
│   └── golang/              # Go implementation
├── pyproject.toml           # Python project configuration
├── .trunk/trunk.yaml        # Quality tools configuration
└── build/                   # Compiled shared libraries
```

## Prerequisites

- Python 3.10+
- Rust (latest stable)
- Go 1.19+
- A C compiler (for shared library compilation)
- [Trunk](https://trunk.io) for code quality tools

## Setup

1. Install Python dependencies:

   ```bash
   uv sync
   ```

2. Install Ethereum execution specs:

   ```bash
   uv pip install git+https://github.com/ethereum/execution-specs.git@forks/prague
   ```

3. Create libraries:

   ```bash
   make all
   ```

4. Run tests:

   ```bash
   uv run pytest -n logical tests
   ```

## Development Workflow

### Code Quality

```bash
trunk check        # Run linters and static analysis
trunk fmt          # Format code according to style guidelines
```

To set up pre-commit hooks:

```bash
trunk install-hook
```

## Notes

- C-compatible shared libraries for each language implementation
- Each wrapper exposes a consistent API for cryptographic operations
- Hypothesis-based property testing

## Adding New Language Implementations

1. Create a new wrapper in the `wrappers/` directory
2. Implement the standard API defined in `docs/design.md`
3. Build a shared library exposing the required functions
4. Add the implementation to the pytest fixtures
5. Run the existing test suite to verify compatibility

## TODO

- add other clients
- check for gas
- fix unreliable tests (pairing / test_g2_add)
