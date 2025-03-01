import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from .strategies import invalid_size_pairing_bytes, pairing_input_bytes


@given(input_data=pairing_input_bytes())
@settings(deadline=500)
def test_pairing(rust_wrapper, go_wrapper, python_wrapper, input_data):
    python_result = python_wrapper.pairing(input_data)
    rust_result = rust_wrapper.pairing(input_data)
    go_result = go_wrapper.pairing(input_data)

    assert rust_result == go_result == python_result


@given(input_data=st.binary(min_size=384, max_size=384 * 3))
def test_pairing_error_handling(rust_wrapper, go_wrapper, python_wrapper, input_data):
    try:
        rust_result = rust_wrapper.pairing(input_data)
        go_result = go_wrapper.pairing(input_data)
        python_result = python_wrapper.pairing(input_data)

        assert rust_result == go_result == python_result
    except RuntimeError:
        try:
            rust_wrapper.pairing(input_data)
            pytest.fail("Rust implementation should have failed")
        except RuntimeError:
            pass

        try:
            go_wrapper.pairing(input_data)
            pytest.fail("Go implementation should have failed")
        except RuntimeError:
            pass

        try:
            python_wrapper.pairing(input_data)
            pytest.fail("Python implementation should have failed")
        except RuntimeError:
            pass


@given(input_data=invalid_size_pairing_bytes())
def test_invalid_size_input(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        rust_wrapper.pairing(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.pairing(input_data)
    with pytest.raises(RuntimeError):
        python_wrapper.pairing(input_data)
