from ethereum.prague.vm.precompiled_contracts.bls12_381.bls12_381_g1 import (
    bls12_g1_add,
    bls12_g1_msm,
    bls12_map_fp_to_g1,
)
from ethereum.prague.vm.precompiled_contracts.bls12_381.bls12_381_g2 import (
    bls12_g2_add,
    bls12_g2_msm,
    bls12_map_fp2_to_g2,
)
from ethereum.prague.vm.precompiled_contracts.bls12_381.bls12_381_pairing import (
    bls12_pairing,
)
from ethereum_types.numeric import Uint


class MockEvm:
    """Mock EVM class to simulate the EVM environment for precompiles."""

    def __init__(self, data):
        self.message = type("obj", (object,), {"data": data})
        self.output = None
        self.gas_left = Uint(2**256 - 1)  # Max gas

    def charge_gas(self, amount):
        self.gas_left -= amount


class EELSWrapper:
    @staticmethod
    def map_fp_to_g1(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_map_fp_to_g1(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in map_fp_to_g1 operation: {str(e)}") from e

    @staticmethod
    def g1_add(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_g1_add(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in G1 addition: {str(e)}") from e

    @staticmethod
    def g1_msm(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_g1_msm(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in G1 MSM operation: {str(e)}") from e

    @staticmethod
    def g2_add(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_g2_add(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in G2 addition: {str(e)}") from e

    @staticmethod
    def g2_msm(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_g2_msm(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in G2 MSM operation: {str(e)}") from e

    @staticmethod
    def map_fp2_to_g2(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_map_fp2_to_g2(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in map_fp2_to_g2 operation: {str(e)}") from e

    @staticmethod
    def pairing(input_bytes):
        try:
            evm = MockEvm(input_bytes)
            bls12_pairing(evm)
            return evm.output if evm.output is not None else b""
        except Exception as e:
            raise RuntimeError(f"Error in pairing operation: {str(e)}") from e
