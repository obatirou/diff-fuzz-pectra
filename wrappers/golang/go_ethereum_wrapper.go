package main

/*
#include <stdint.h>
#include <stdlib.h>

typedef int32_t error_code_t;
*/
import "C"
import (
	"unsafe"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/vm"
)

// Helper function to handle common wrapper logic
func runPrecompiledContract(
	input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t,
	contractAddress byte) C.error_code_t {

	// Check for null pointers
	if input == nil || output == nil || outputLen == nil {
		return -1
	}

	// Convert input to Go slice
	inputSlice := C.GoBytes(unsafe.Pointer(input), C.int(inputLen))

	// Call go-ethereum's implementation
	contract := vm.PrecompiledContractsPrague[common.BytesToAddress([]byte{contractAddress})]
	result, err := contract.Run(inputSlice)
	if err != nil {
		return -4 // Invalid input format or computation error
	}

	// Check output buffer capacity
	if len(result) > int(outCap) {
		return -2
	}

	// Copy result to output buffer
	outSlice := (*[1 << 30]byte)(unsafe.Pointer(output))[:len(result):len(result)]
	copy(outSlice, result)
	*outputLen = C.size_t(len(result))

	return 0
}

//export g1_add_wrapper
func g1_add_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x0b)
}

func main() {} // Required for building as C shared library

//export g1_msm_wrapper
func g1_msm_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x0c)
}

//export map_fp_to_g1_wrapper
func map_fp_to_g1_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x10)
}

//export g2_add_wrapper
func g2_add_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x0d)
}

//export g2_msm_wrapper
func g2_msm_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x0e)
}

//export map_fp2_to_g2_wrapper
func map_fp2_to_g2_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x11)
}

//export pairing_wrapper
func pairing_wrapper(input *C.uint8_t, inputLen C.size_t,
	output *C.uint8_t, outCap C.size_t,
	outputLen *C.size_t) C.error_code_t {

	return runPrecompiledContract(input, inputLen, output, outCap, outputLen, 0x0f)
}
