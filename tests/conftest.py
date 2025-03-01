import pytest

from .LibCallerWrapper import EELSWrapper, _go_wrapper, _rust_wrapper


@pytest.fixture(scope="module")
def rust_wrapper():
    """Fixture that returns the shared Rust wrapper instance."""
    return _rust_wrapper


@pytest.fixture(scope="module")
def go_wrapper():
    """Fixture that returns the shared Go wrapper instance."""
    return _go_wrapper


@pytest.fixture(scope="module")
def python_wrapper():
    """Fixture that returns the Python wrapper."""
    return EELSWrapper
