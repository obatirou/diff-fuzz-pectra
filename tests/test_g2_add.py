import pytest
from hypothesis import given
from hypothesis import strategies as st

from .strategies import (
    invalid_size_bytes,
    non_bls12_381_g2_points_bytes,
    two_bls12_381_g2_points_bytes,
)


@given(input_data=two_bls12_381_g2_points_bytes())
def test_g2_add(rust_wrapper, go_wrapper, python_wrapper, input_data):
    rust_result = rust_wrapper.g2_add(input_data)
    go_result = go_wrapper.g2_add(input_data)
    python_result = python_wrapper.g2_add(input_data)

    assert rust_result == go_result == python_result


# Keep the original test with random data to test error handling
@given(input_data=st.binary(min_size=512, max_size=512))
def test_g2_add_error_handling(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """Test that all implementations handle invalid inputs consistently."""
    try:
        rust_result = rust_wrapper.g2_add(input_data)
        go_result = go_wrapper.g2_add(input_data)
        python_result = python_wrapper.g2_add(input_data)

        assert rust_result == go_result == python_result
    except RuntimeError:
        # All implementations should fail in the same way
        try:
            rust_wrapper.g2_add(input_data)
            pytest.fail("Rust implementation should have failed")
        except RuntimeError:
            pass

        try:
            go_wrapper.g2_add(input_data)
            pytest.fail("Go implementation should have failed")
        except RuntimeError:
            pass

        try:
            python_wrapper.g2_add(input_data)
            pytest.fail("Python implementation should have failed")
        except RuntimeError:
            pass


@given(input_data=invalid_size_bytes(expected_size=512))
def test_invalid_size_input(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        rust_wrapper.g2_add(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.g2_add(input_data)
    with pytest.raises(RuntimeError):
        python_wrapper.g2_add(input_data)


@given(input_data=non_bls12_381_g2_points_bytes())
def test_g2_add_invalid_points(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        python_wrapper.g2_add(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.g2_add(input_data)
    with pytest.raises(RuntimeError):
        rust_wrapper.g2_add(input_data)
