import ctypes
from pathlib import Path
from typing import Callable, Dict, Optional

# Import the Python wrapper
from wrappers.python.eels_wrapper import EELSWrapper

# Constants for output sizes
G1_MAX_OUTPUT_SIZE = 256  # For G1 operations
G2_MAX_OUTPUT_SIZE = 512  # For G2 operations
PAIRING_MAX_OUTPUT_SIZE = 32  # For pairing operations


class LibCallerWrapper:
    """
    Enhanced wrapper class for calling functions in shared libraries.
    Provides functionality for loading libraries and calling multiple C functions.
    """

    def __init__(self, lib_path: str):
        """
        Initialize the wrapper with a library path.

        Args:
            lib_path: Path to the shared library
        """
        self.lib = ctypes.CDLL(lib_path)
        self.lib_path = lib_path
        self._function_cache: Dict[str, Callable] = {}

    def register_function(
        self,
        function_name: str,
        max_output_size: int,
        method_name: Optional[str] = None,
    ):
        """
        Register a C function from the library and create a corresponding Python method.

        Args:
            function_name: Name of the C function in the library
            max_output_size: Maximum size of the output buffer
            method_name: Name of the Python method to create (defaults to function_name without '_wrapper')
        """
        if method_name is None:
            method_name = function_name.replace("_wrapper", "")

        # Get the function from the library
        function = getattr(self.lib, function_name)

        # Define common function signature
        function.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),  # input
            ctypes.c_size_t,  # input_len
            ctypes.POINTER(ctypes.c_uint8),  # output
            ctypes.c_size_t,  # output_capacity
            ctypes.POINTER(ctypes.c_size_t),  # output_len
        ]
        function.restype = ctypes.c_int

        # Create a closure to capture the function and max_output_size
        def call_function(input_bytes: bytes) -> bytes:
            input_len = len(input_bytes)
            input_array = (ctypes.c_uint8 * input_len)(*input_bytes)
            output_buffer = (ctypes.c_uint8 * max_output_size)()
            output_len = ctypes.c_size_t()

            result = function(
                input_array,
                input_len,
                output_buffer,
                max_output_size,
                ctypes.byref(output_len),
            )

            if result != 0:
                raise RuntimeError(f"{function_name} failed with error code: {result}")

            return bytes(output_buffer[: output_len.value])

        # Store the function in the cache
        self._function_cache[method_name] = call_function

        # Add the method to the instance
        setattr(self, method_name, call_function)

    def __getattr__(self, name):
        """
        Handle attribute access for methods that haven't been registered yet.

        Args:
            name: Name of the attribute being accessed

        Returns:
            The requested attribute

        Raises:
            AttributeError: If the attribute doesn't exist
        """
        if name in self._function_cache:
            return self._function_cache[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


def get_lib_path(lib_name: str) -> str:
    """
    Helper function to get the path to a shared library.
    """
    build_dir = Path(__file__).parent.parent / "build"
    return str(build_dir / lib_name)


# Create the shared wrapper instances (but don't register functions yet)
_rust_wrapper = LibCallerWrapper(get_lib_path("librevm_wrapper.so"))
_go_wrapper = LibCallerWrapper(get_lib_path("libgo_ethereum_wrapper.so"))

# Register all the functions for the Rust wrapper
_rust_wrapper.register_function("g1_add_wrapper", G1_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("g2_add_wrapper", G2_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("g1_msm_wrapper", G1_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("g2_msm_wrapper", G2_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("map_fp_to_g1_wrapper", G1_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("map_fp2_to_g2_wrapper", G2_MAX_OUTPUT_SIZE)
_rust_wrapper.register_function("pairing_wrapper", PAIRING_MAX_OUTPUT_SIZE)

# Register all the functions for the Go wrapper
_go_wrapper.register_function("g1_add_wrapper", G1_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("g2_add_wrapper", G2_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("g1_msm_wrapper", G1_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("g2_msm_wrapper", G2_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("map_fp_to_g1_wrapper", G1_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("map_fp2_to_g2_wrapper", G2_MAX_OUTPUT_SIZE)
_go_wrapper.register_function("pairing_wrapper", PAIRING_MAX_OUTPUT_SIZE)
