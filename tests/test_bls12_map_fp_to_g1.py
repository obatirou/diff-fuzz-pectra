import pytest
from hypothesis import given
from hypothesis import strategies as st

from .strategies import (
    invalid_fp_field_element_bytes,
    invalid_size_bytes,
    valid_fp_field_element_bytes,
)


@given(input_data=valid_fp_field_element_bytes())
def test_map_fp_to_g1(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """
    Test that all implementations agree on the result of mapping
    a valid field element to a G1 point.
    """
    rust_result = rust_wrapper.map_fp_to_g1(input_data)
    go_result = go_wrapper.map_fp_to_g1(input_data)
    python_result = python_wrapper.map_fp_to_g1(input_data)

    assert rust_result == go_result == python_result
    # Output should be a properly formatted G1 point (128 bytes)
    assert len(rust_result) == 128


@given(input_data=invalid_fp_field_element_bytes())
def test_map_fp_to_g1_invalid_element(
    rust_wrapper, go_wrapper, python_wrapper, input_data
):
    """
    Test handling of invalid field elements (>= BLS12_381_PRIME).
    All implementations should either reject these or map them consistently.
    """
    try:
        rust_result = rust_wrapper.map_fp_to_g1(input_data)
        go_result = go_wrapper.map_fp_to_g1(input_data)
        python_result = python_wrapper.map_fp_to_g1(input_data)

        # If all implementations accept the invalid input,
        # they should at least agree on the result
        assert rust_result == go_result == python_result
    except RuntimeError:
        # It's acceptable for implementations to reject invalid inputs
        pass


@given(input_data=invalid_size_bytes(expected_size=64))
def test_invalid_size_input(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """
    Test handling of inputs with invalid size (not 64 bytes).
    All implementations should reject these inputs.
    """
    with pytest.raises(RuntimeError):
        rust_wrapper.map_fp_to_g1(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.map_fp_to_g1(input_data)
    with pytest.raises(RuntimeError):
        python_wrapper.map_fp_to_g1(input_data)


@given(input_data=st.binary(min_size=64, max_size=64))
def test_map_fp_to_g1_error_handling(
    rust_wrapper, go_wrapper, python_wrapper, input_data
):
    """
    Test that all implementations handle arbitrary 64-byte inputs consistently.
    They should either all succeed or all fail with a similar error.
    """
    implementations = [
        ("rust", rust_wrapper.map_fp_to_g1),
        ("go", go_wrapper.map_fp_to_g1),
        ("python", python_wrapper.map_fp_to_g1),
    ]

    results = []
    errors = []

    for name, func in implementations:
        try:
            results.append((name, func(input_data)))
        except RuntimeError as e:
            errors.append((name, str(e)))

    # Check for consistency: all should succeed or all should fail
    if results and errors:
        pytest.fail(f"Inconsistent behavior: {results} succeeded but {errors} failed")

    # If all succeeded, verify they return the same result
    if results:
        first_name, first_result = results[0]
        for name, result in results[1:]:
            assert first_result == result, f"{first_name} and {name} disagree on result"
