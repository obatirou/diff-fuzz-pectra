use revm_precompile::bls12_381::g1_add::PRECOMPILE as G1_ADD_PRECOMPILE;
use revm_precompile::bls12_381::g1_msm::PRECOMPILE as G1_MSM_PRECOMPILE;
use revm_precompile::bls12_381::g2_add::PRECOMPILE as G2_ADD_PRECOMPILE;
use revm_precompile::bls12_381::g2_msm::PRECOMPILE as G2_MSM_PRECOMPILE;
use revm_precompile::bls12_381::map_fp2_to_g2::PRECOMPILE as MAP_FP2_TO_G2_PRECOMPILE;
use revm_precompile::bls12_381::map_fp_to_g1::PRECOMPILE as MAP_FP_TO_G1_PRECOMPILE;
use revm_precompile::bls12_381::pairing::PRECOMPILE as PAIRING_PRECOMPILE;
use revm_precompile::Bytes;
use revm_precompile::{PrecompileErrors, PrecompileOutput};
use std::slice;

/// Helper function to handle common FFI wrapper logic for BLS12-381 operations
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid data for the specific operation
/// - Output buffer must have sufficient capacity
unsafe fn execute_precompile(
    precompile: fn(&Bytes, u64) -> Result<PrecompileOutput, PrecompileErrors>,
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    // Safety checks
    if input.is_null() || output.is_null() || output_len.is_null() {
        return -1;
    }

    // Convert input to Rust slice
    let input_slice = slice::from_raw_parts(input, input_len);
    let input_bytes = Bytes::copy_from_slice(input_slice);

    // Call the precompile implementation
    let result = match precompile(&input_bytes, u64::MAX) {
        Ok(output) => output.bytes,
        Err(_) => return -4, // Invalid input format or computation error
    };

    // Check output buffer capacity
    if result.len() > output_capacity {
        return -2;
    }

    // Copy result to output buffer
    std::ptr::copy_nonoverlapping(result.as_ptr(), output, result.len());
    *output_len = result.len();

    0 // Success
}

/// FFI wrapper for BLS12-381 G1 point addition.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid BLS12-381 G1 points
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn g1_add_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        G1_ADD_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 G1 multi-scalar multiplication.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid BLS12-381 G1 points and scalar pairs
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn g1_msm_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        G1_MSM_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 map_fp_to_g1 operation.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain a valid BLS12-381 field element (64 bytes)
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn map_fp_to_g1_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        MAP_FP_TO_G1_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 G2 point addition.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid BLS12-381 G2 points
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn g2_add_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        G2_ADD_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 G2 multi-scalar multiplication.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid BLS12-381 G2 points and scalar pairs
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn g2_msm_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        G2_MSM_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 map_fp2_to_g2 operation.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain a valid BLS12-381 Fp2 field element (128 bytes)
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn map_fp2_to_g2_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        MAP_FP2_TO_G2_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}

/// FFI wrapper for BLS12-381 pairing operation.
///
/// # Safety
/// - Input/output pointers must be valid and properly aligned
/// - Input buffer must contain valid BLS12-381 G2 points and G1 points
/// - Output buffer must have sufficient capacity
#[no_mangle]
pub unsafe extern "C" fn pairing_wrapper(
    input: *const u8,
    input_len: usize,
    output: *mut u8,
    output_capacity: usize,
    output_len: *mut usize,
) -> i32 {
    execute_precompile(
        PAIRING_PRECOMPILE.1,
        input,
        input_len,
        output,
        output_capacity,
        output_len,
    )
}
