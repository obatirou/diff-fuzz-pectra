import pytest
from hypothesis import given, settings

from .strategies import (
    LENGTH_PER_PAIR_G1,
    g1_msm_input_bytes,
    g1_msm_invalid_subgroup_input_bytes,
    g1_msm_valid_subgroup_input_bytes,
    g1_msm_valid_subgroup_with_zero_scalar,
    g1_msm_with_zero_scalar,
    invalid_size_bytes_multiple_of,
)


@given(input_data=g1_msm_input_bytes())
@settings(deadline=500)
def test_g1_msm(rust_wrapper, go_wrapper, python_wrapper, input_data):
    try:
        python_result = python_wrapper.g1_msm(input_data)
        rust_result = rust_wrapper.g1_msm(input_data)
        go_result = go_wrapper.g1_msm(input_data)

        assert rust_result == go_result == python_result
    except RuntimeError as e:
        if "Sub-group check failed" in str(e):
            # All implementations should fail with subgroup check failure
            with pytest.raises(RuntimeError):
                python_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                rust_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                go_wrapper.g1_msm(input_data)
        else:
            # For other errors, re-raise
            raise


@given(input_data=invalid_size_bytes_multiple_of(multiple_of=LENGTH_PER_PAIR_G1))
def test_invalid_size_input(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        rust_wrapper.g1_msm(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.g1_msm(input_data)
    with pytest.raises(RuntimeError):
        python_wrapper.g1_msm(input_data)


# Add specific test cases for MSM with 1 pair (equivalent to multiplication)
@given(input_data=g1_msm_input_bytes(min_pairs=1, max_pairs=1))
@settings(deadline=1000)
def test_g1_msm_single_pair(rust_wrapper, go_wrapper, python_wrapper, input_data):
    try:
        python_result = python_wrapper.g1_msm(input_data)
        rust_result = rust_wrapper.g1_msm(input_data)
        go_result = go_wrapper.g1_msm(input_data)

        assert rust_result == go_result == python_result
    except RuntimeError as e:
        if "Sub-group check failed" in str(e):
            # All implementations should fail with subgroup check failure
            with pytest.raises(RuntimeError):
                python_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                rust_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                go_wrapper.g1_msm(input_data)
        else:
            # For other errors, re-raise
            raise


@given(input_data=g1_msm_with_zero_scalar())
@settings(deadline=500)
def test_g1_msm_with_zero_scalar(rust_wrapper, go_wrapper, python_wrapper, input_data):
    try:
        python_result = python_wrapper.g1_msm(input_data)
        rust_result = rust_wrapper.g1_msm(input_data)
        go_result = go_wrapper.g1_msm(input_data)

        assert rust_result == go_result == python_result
    except RuntimeError as e:
        if "Sub-group check failed" in str(e):
            # All implementations should fail with subgroup check failure
            with pytest.raises(RuntimeError):
                python_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                rust_wrapper.g1_msm(input_data)
            with pytest.raises(RuntimeError):
                go_wrapper.g1_msm(input_data)
        else:
            # For other errors, re-raise
            raise


@given(input_data=g1_msm_valid_subgroup_input_bytes())
@settings(deadline=1000)
def test_g1_msm_valid_subgroup(rust_wrapper, go_wrapper, python_wrapper, input_data):
    python_result = python_wrapper.g1_msm(input_data)
    rust_result = rust_wrapper.g1_msm(input_data)
    go_result = go_wrapper.g1_msm(input_data)

    assert rust_result == go_result == python_result


@given(input_data=g1_msm_invalid_subgroup_input_bytes())
@settings(deadline=1000)
def test_g1_msm_invalid_subgroup(rust_wrapper, go_wrapper, python_wrapper, input_data):
    with pytest.raises(RuntimeError):
        python_wrapper.g1_msm(input_data)
    with pytest.raises(RuntimeError):
        rust_wrapper.g1_msm(input_data)
    with pytest.raises(RuntimeError):
        go_wrapper.g1_msm(input_data)


@given(input_data=g1_msm_valid_subgroup_with_zero_scalar())
@settings(deadline=1000)
def test_g1_msm_valid_subgroup_with_zero_scalar(
    rust_wrapper, go_wrapper, python_wrapper, input_data
):
    python_result = python_wrapper.g1_msm(input_data)
    rust_result = rust_wrapper.g1_msm(input_data)
    go_result = go_wrapper.g1_msm(input_data)

    assert rust_result == go_result == python_result
