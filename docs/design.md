## Overview

## Function Signature

All language implementations must provide a C-ABI compatible function with the following signature:

```c
int g1_add_wrapper(
    const uint8_t* input,      // Input buffer
    size_t input_len,          // Length of input
    uint8_t* output,           // Output buffer
    size_t output_capacity,    // Capacity of output buffer
    size_t* output_len         // Actual length of output
);
```

### Return Values

- 0: Success
- -1: Null pointer or invalid input
- -2: Output buffer too small
- -3: Internal error during computation
- -4: Invalid input format

### Buffer Management

- Maximum output buffer size: 256 bytes
- Input format: Raw bytes representing the g1_add operation parameters
- Output format: Raw bytes representing the operation result

## Language-Specific Implementation Details

### Rust Implementation

1. Create a cdylib crate type in Cargo.toml
2. Implement the wrapper using `#[no_mangle]` and `extern "C"`
3. Handle memory safety using Rust's slice types
4. Provide proper error handling

### Go Implementation

1. Use cgo with `//export` directives
2. Build as a shared library with `-buildmode=c-shared`
3. Handle memory management between Go and C
4. Implement proper error handling

## Python Testing Framework

### Components

1. ctypes wrapper for loading shared libraries
2. Hypothesis-based test generation
3. Common test suite for all implementations

## Adding New Language Implementations

### Requirements

1. Implement the common C-ABI interface
2. Build as a shared library
3. Place compiled library in build/ directory
4. Follow error handling conventions

### Steps

1. Create language subdirectory in wrappers/
2. Implement wrapper following C-ABI specification
3. Provide build instructions
4. Add to Python test suite

## Build System

### Requirements

- Rust toolchain
- Go compiler
- Python 3.8+
- C compiler

### Build Process

1. Compile Rust implementation
2. Compile Go implementation
3. Run Python tests
