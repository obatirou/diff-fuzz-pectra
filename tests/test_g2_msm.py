import pytest
from hypothesis import given, settings

from .strategies import (
    LENGTH_PER_PAIR_G2,
    g2_msm_input_bytes,
    g2_msm_valid_subgroup_with_zero_scalar,
    g2_msm_with_zero_scalar,
    invalid_size_bytes_multiple_of,
)


@given(input_data=g2_msm_input_bytes())
@settings(deadline=10000)
def test_g2_msm(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """
    Test that all implementations agree on the result of G2 MSM using valid inputs.
    """
    try:
        rust_result = rust_wrapper.g2_msm(input_data)
        go_result = go_wrapper.g2_msm(input_data)
        python_result = python_wrapper.g2_msm(input_data)

        assert rust_result == go_result == python_result
        assert len(rust_result) == 256
    except RuntimeError:
        # If one fails, then all should fail in a consistent manner.
        with pytest.raises(RuntimeError):
            rust_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            go_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            python_wrapper.g2_msm(input_data)


@given(input_data=invalid_size_bytes_multiple_of(multiple_of=LENGTH_PER_PAIR_G2))
def test_invalid_size_input(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        rust_wrapper.g2_msm(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.g2_msm(input_data)
    with pytest.raises(RuntimeError):
        python_wrapper.g2_msm(input_data)


@given(input_data=g2_msm_input_bytes(min_pairs=1, max_pairs=1))
@settings(deadline=2000)
def test_g2_msm_single_pair(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """
    Test G2 MSM with a single point-scalar pair.
    This is a special case that should be handled correctly by all implementations.
    """
    try:
        rust_result = rust_wrapper.g2_msm(input_data)
        go_result = go_wrapper.g2_msm(input_data)
        python_result = python_wrapper.g2_msm(input_data)

        assert rust_result == go_result == python_result
        # Output should be a properly formatted G2 point (256 bytes)
        assert len(rust_result) == 256
    except RuntimeError:
        # If one implementation fails, they should all fail
        with pytest.raises(RuntimeError):
            rust_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            go_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            python_wrapper.g2_msm(input_data)


@given(input_data=g2_msm_with_zero_scalar())
@settings(deadline=3000)
def test_g2_msm_with_zero_scalar(rust_wrapper, go_wrapper, python_wrapper, input_data):
    """
    Test G2 MSM with at least one zero scalar.
    All implementations should handle zero scalars correctly.
    """
    try:
        rust_result = rust_wrapper.g2_msm(input_data)
        go_result = go_wrapper.g2_msm(input_data)
        python_result = python_wrapper.g2_msm(input_data)

        assert rust_result == go_result == python_result
        # Output should be a properly formatted G2 point (256 bytes)
        assert len(rust_result) == 256
    except RuntimeError:
        # If one implementation fails, they should all fail
        with pytest.raises(RuntimeError):
            rust_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            go_wrapper.g2_msm(input_data)
        with pytest.raises(RuntimeError):
            python_wrapper.g2_msm(input_data)


@given(input_data=g2_msm_valid_subgroup_with_zero_scalar())
@settings(deadline=10000)
def test_g2_msm_valid_subgroup_with_zero_scalar(
    rust_wrapper, go_wrapper, python_wrapper, input_data
):
    rust_result = rust_wrapper.g2_msm(input_data)
    go_result = go_wrapper.g2_msm(input_data)
    python_result = python_wrapper.g2_msm(input_data)

    assert rust_result == go_result == python_result
