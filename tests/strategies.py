from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.strategies import composite
from py_ecc.bls12_381.bls12_381_curve import G1, G2, curve_order, multiply

# BLS12-381 base field prime (Fp)
BLS12_381_PRIME = 0x1A0111EA397FE69A4B1BA7B6434BACD764774B84F38512BF6730D2A0F6B0F6241EABFFFEB153FFFFB9FEFFFFFFFFAAAB

LENGTH_PER_PAIR_G1 = 160  # 128 bytes for G1 point, 32 bytes for scalar
LENGTH_PER_PAIR_G2 = 288  # 256 bytes for G2 point, 32 bytes for scalar

# BLS12-381 scalar field size
BLS12_381_SCALAR_FIELD = (
    0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001
)
# BLS12-381 G1 generator point
BLS12_381_G1_GENERATOR_X = 0x17F1D3A73197D7942695638C4FA9AC0FC3688C4F9774B905A14E3A3F171BAC586C55E83FF97A1AEFFB3AF00ADB22C6BB
BLS12_381_G1_GENERATOR_Y = 0x08B3F481E3AAA0F1A09E30ED741D8AE4FCF5E095D5D00AF600DB18CB2C04B3EDD03CC744A2888AE40CAA232946C5E7E1

# BLS12-381 G2 generator point (x and y coordinates in Fp2 representation)
BLS12_381_G2_GENERATOR_X_C0 = 0x024AA2B2F08F0A91260805272DC51051C6E47AD4FA403B02B4510B647AE3D1770BAC0326A805BBEFD48056C8C121BDB8
BLS12_381_G2_GENERATOR_X_C1 = 0x13E02B6052719F607DACD3A088274F65596BD0D09920B61AB5DA61BBDC7F5049334CF11213945D57E5AC7D055D042B7E
BLS12_381_G2_GENERATOR_Y_C0 = 0x0CE5D527727D6E118CC9CDC6DA2E351AADFD9BAA8CBDD3A76D429A695160D12C923AC9CC3BACA289E193548608B82801
BLS12_381_G2_GENERATOR_Y_C1 = 0x0606C4A02EA734CC32ACD2B02BC28B99CB3E287E85A763AF267492AB572E99AB3F370D275CEC1DA1AAA9075FF05F79BE


@composite
def valid_fp_field_element_bytes(draw):
    """
    Generate a random valid field element in Fp as bytes.
    The element must be less than the BLS12_381_PRIME.
    """
    # Generate a random element in Fp
    field_element = draw(st.integers(min_value=0, max_value=BLS12_381_PRIME - 1))

    # Convert to big-endian bytes representation
    field_bytes = field_element.to_bytes(64, byteorder="big")

    return field_bytes


@composite
def invalid_fp_field_element_bytes(draw):
    """
    Generate invalid field element bytes (not in Fp).
    These are values greater than or equal to the BLS12_381_PRIME.
    """
    # Generate a random element >= BLS12_381_PRIME
    field_element = draw(
        st.integers(
            min_value=BLS12_381_PRIME,
            max_value=2 ** (64 * 8) - 1,  # Maximum possible value in 64 bytes
        )
    )

    # Convert to big-endian bytes representation
    field_bytes = field_element.to_bytes(64, byteorder="big")

    return field_bytes


@composite
def valid_fp2_field_element_bytes(draw):
    """
    Generate a random valid field element in Fp2 as bytes.
    Fp2 is represented as two Fp elements (c0, c1) where the element is c0 + c1*u
    and u^2 = -1.
    """
    # Generate two random elements in Fp
    c0 = draw(st.integers(min_value=0, max_value=BLS12_381_PRIME - 1))
    c1 = draw(st.integers(min_value=0, max_value=BLS12_381_PRIME - 1))

    # Convert to big-endian bytes representation
    c0_bytes = c0.to_bytes(64, byteorder="big")
    c1_bytes = c1.to_bytes(64, byteorder="big")

    # Concatenate the two components
    return c0_bytes + c1_bytes


@composite
def invalid_fp2_field_element_bytes(draw):
    """
    Generate invalid field element bytes (not in Fp2).
    These are values where at least one component is greater than or equal to the BLS12_381_PRIME.
    """
    # Decide which component(s) to make invalid
    invalid_c0 = draw(st.booleans())
    invalid_c1 = draw(st.booleans())

    # Ensure at least one component is invalid
    if not invalid_c0 and not invalid_c1:
        invalid_c0 = True

    # Generate the components
    if invalid_c0:
        c0 = draw(
            st.integers(
                min_value=BLS12_381_PRIME,
                max_value=2 ** (64 * 8) - 1,  # Maximum possible value in 64 bytes
            )
        )
    else:
        c0 = draw(st.integers(min_value=0, max_value=BLS12_381_PRIME - 1))

    if invalid_c1:
        c1 = draw(
            st.integers(
                min_value=BLS12_381_PRIME,
                max_value=2 ** (64 * 8) - 1,  # Maximum possible value in 64 bytes
            )
        )
    else:
        c1 = draw(st.integers(min_value=0, max_value=BLS12_381_PRIME - 1))

    # Convert to big-endian bytes representation
    c0_bytes = c0.to_bytes(64, byteorder="big")
    c1_bytes = c1.to_bytes(64, byteorder="big")

    # Concatenate the two components
    return c0_bytes + c1_bytes


@composite
def invalid_size_bytes(draw, expected_size):
    max_size = max(expected_size * 2, 1024)

    # Generate random bytes with size other than expected_size
    size = draw(st.integers(0, max_size).filter(lambda x: x != expected_size))
    return draw(st.binary(min_size=size, max_size=size))


@composite
def invalid_size_bytes_multiple_of(draw, multiple_of):
    # Invalid sizes are anything that's not a multiple of 160 bytes (128+32)
    # Each valid pair consists of a 128-byte G1 point and a 32-byte scalar
    length = draw(
        st.integers(min_value=1, max_value=1000).filter(
            lambda x: x % multiple_of != 0 or x == 0
        )
    )
    return bytes(
        draw(
            st.lists(
                st.integers(min_value=0, max_value=255),
                min_size=length,
                max_size=length,
            )
        )
    )


@composite
def bls12_381_point(draw):
    """
    Generate a random point on the BLS12-381 curve defined by
        y^2 = x^3 + 4  (over the field Fq with prime BLS12_381_PRIME)

    This function uses the property that when p ≡ 3 (mod 4), a square root
    modulo p (when it exists) can be computed as a**((p+1)//4) mod p.
    """
    p = BLS12_381_PRIME

    # Draw a random x-coordinate in Fq
    x = draw(st.integers(min_value=0, max_value=p - 1))

    # Compute the right-hand side of the curve equation: x^3 + 4 (mod p)
    rhs = (pow(x, 3, p) + 4) % p

    # Check that rhs is a quadratic residue.
    # For p ≡ 3 mod 4, a nonzero element a is a quadratic residue if and only if:
    #     a^((p-1)//2) ≡ 1 (mod p)
    # Note: 0 is trivially a square (its square root is 0).
    if rhs != 0 and pow(rhs, (p - 1) // 2, p) != 1:
        # If not a quadratic residue, re-draw a valid point.
        # (Hypothesis will discard this draw and try another.)
        return draw(bls12_381_point())

    # Compute the square root using the exponentiation method.
    # When rhs == 0, y is 0.
    y = 0 if rhs == 0 else pow(rhs, (p + 1) // 4, p)

    # Randomize the sign of y (both y and -y are valid square roots).
    if draw(st.booleans()):
        y = (-y) % p

    return (x, y)


@composite
def two_bls12_381_points_bytes(draw):
    """
    Generate two BLS12-381 curve points and return their concatenation as 256 bytes.
    Each point is serialized as (x || y) with each coordinate encoded as a 64-byte big-endian integer.
    """
    # Generate two points.
    point1 = draw(bls12_381_point())
    point2 = draw(bls12_381_point())
    p1x, p1y = point1
    p2x, p2y = point2

    # Convert each coordinate to a 64-byte big-endian representation.
    p1x_bytes = p1x.to_bytes(64, byteorder="big")
    p1y_bytes = p1y.to_bytes(64, byteorder="big")
    p2x_bytes = p2x.to_bytes(64, byteorder="big")
    p2y_bytes = p2y.to_bytes(64, byteorder="big")

    # Concatenate the four coordinates.
    result = p1x_bytes + p1y_bytes + p2x_bytes + p2y_bytes

    # Ensure the final result is exactly 256 bytes.
    assert len(result) == 256, f"Expected 256 bytes, got {len(result)} bytes"
    return result


@composite
def non_bls12_381_points_bytes(draw):
    """
    Generate 256 bytes that are guaranteed not to represent valid BLS12-381 curve points.

    This strategy creates inputs that have the correct size (256 bytes) but contain
    coordinates that don't satisfy the curve equation y^2 = x^3 + 4 mod p.
    """
    # Generate random 256 bytes first
    random_bytes = draw(st.binary(min_size=256, max_size=256))
    assume(random_bytes != b"\x00" * 256)

    # Extract coordinates as if they were points
    p1x_bytes = random_bytes[0:64]
    p1y_bytes = random_bytes[64:128]
    p2x_bytes = random_bytes[128:192]
    p2y_bytes = random_bytes[192:256]

    # Convert to integers
    p = BLS12_381_PRIME
    p1x = int.from_bytes(p1x_bytes, byteorder="big")
    p1y = int.from_bytes(p1y_bytes, byteorder="big")

    # Ensure at least one coordinate doesn't satisfy the curve equation
    # Check if p1y^2 ≡ p1x^3 + 4 (mod p)
    left_side = pow(p1y, 2, p)
    right_side = (pow(p1x, 3, p) + 4) % p

    if left_side == right_side:
        # If it accidentally satisfies the equation, modify y slightly to break it
        p1y = (p1y + 1) % p
        p1y_bytes = p1y.to_bytes(64, byteorder="big")
        return p1x_bytes + p1y_bytes + p2x_bytes + p2y_bytes

    return random_bytes


@composite
def bls12_381_scalar(draw):
    """Generate a random scalar in the BLS12-381 scalar field."""
    return draw(st.integers(min_value=0, max_value=BLS12_381_SCALAR_FIELD - 1))


@composite
def g1_point_scalar_pair_bytes(draw):
    """
    Generate a pair of G1 point and scalar, formatted as 160 bytes:
    - 128 bytes for G1 point (64 bytes for x, 64 bytes for y)
    - 32 bytes for the scalar
    """
    point = draw(bls12_381_point())
    scalar = draw(bls12_381_scalar())

    px, py = point

    # Convert to bytes
    px_bytes = px.to_bytes(64, byteorder="big")
    py_bytes = py.to_bytes(64, byteorder="big")
    scalar_bytes = scalar.to_bytes(32, byteorder="big")

    # Concatenate the components
    result = px_bytes + py_bytes + scalar_bytes
    assert (
        len(result) == LENGTH_PER_PAIR_G1
    ), f"Expected {LENGTH_PER_PAIR_G1} bytes, got {len(result)} bytes"

    return result


@composite
def g1_msm_input_bytes(draw, min_pairs=1, max_pairs=5):
    """
    Generate an input for G1 MSM consisting of multiple point-scalar pairs.
    Each pair is 160 bytes (128 bytes for the point, 32 bytes for the scalar).
    """
    num_pairs = draw(st.integers(min_value=min_pairs, max_value=max_pairs))
    pairs = [draw(g1_point_scalar_pair_bytes()) for _ in range(num_pairs)]
    return b"".join(pairs)


@composite
def g1_subgroup_point_scalar_pair_bytes(draw):
    """
    Generate a G1 point-scalar pair with a valid subgroup point.
    Uses the BLS12-381 G1 generator point, ensuring it's in the correct subgroup.
    """
    # Use the generator point directly (known to be in the correct subgroup)
    px = BLS12_381_G1_GENERATOR_X
    py = BLS12_381_G1_GENERATOR_Y

    # Generate a valid scalar
    scalar = draw(bls12_381_scalar())

    # Convert to bytes
    px_bytes = px.to_bytes(64, byteorder="big")
    py_bytes = py.to_bytes(64, byteorder="big")
    scalar_bytes = scalar.to_bytes(32, byteorder="big")

    # Concatenate the components
    result = px_bytes + py_bytes + scalar_bytes
    assert (
        len(result) == LENGTH_PER_PAIR_G1
    ), f"Expected {LENGTH_PER_PAIR_G1} bytes, got {len(result)} bytes"

    return result


@composite
def g1_msm_valid_subgroup_input_bytes(draw, min_pairs=1, max_pairs=5):
    """
    Generate input for G1 MSM with points guaranteed to be in the correct subgroup.
    """
    num_pairs = draw(st.integers(min_value=min_pairs, max_value=max_pairs))
    pairs = [draw(g1_subgroup_point_scalar_pair_bytes()) for _ in range(num_pairs)]
    return b"".join(pairs)


@composite
def g1_non_subgroup_point_scalar_pair_bytes(draw):
    """
    Generate a G1 point-scalar pair where the point is on the curve
    but NOT in the correct subgroup.
    """
    # Generate a random point on the curve (but not necessarily in the correct subgroup)
    point = draw(bls12_381_point())

    # To ensure it's not in the subgroup, we'll use a point that's definitely on the curve
    # but not processed through cofactor multiplication
    px, py = point

    # Generate a valid scalar
    scalar = draw(bls12_381_scalar())

    # Convert to bytes
    px_bytes = px.to_bytes(64, byteorder="big")
    py_bytes = py.to_bytes(64, byteorder="big")
    scalar_bytes = scalar.to_bytes(32, byteorder="big")

    # Concatenate the components
    result = px_bytes + py_bytes + scalar_bytes
    assert (
        len(result) == LENGTH_PER_PAIR_G1
    ), f"Expected {LENGTH_PER_PAIR_G1} bytes, got {len(result)} bytes"

    return result


@composite
def g1_msm_invalid_subgroup_input_bytes(draw, min_pairs=1, max_pairs=5):
    """
    Generate input for G1 MSM with at least one point NOT in the correct subgroup.
    """
    num_pairs = draw(st.integers(min_value=min_pairs, max_value=max_pairs))
    pairs = []

    # Ensure at least one point is not in the subgroup
    non_subgroup_index = draw(st.integers(min_value=0, max_value=num_pairs - 1))

    for i in range(num_pairs):
        if i == non_subgroup_index:
            # Add a non-subgroup point
            pairs.append(draw(g1_non_subgroup_point_scalar_pair_bytes()))
        else:
            # Add a valid subgroup point
            pairs.append(draw(g1_subgroup_point_scalar_pair_bytes()))

    return b"".join(pairs)


# Test with special case: scalar = 0 (should give point at infinity)
@composite
def g1_msm_with_zero_scalar(draw):
    """Generate G1 MSM input with at least one scalar set to zero."""
    num_pairs = draw(st.integers(min_value=1, max_value=5))
    pairs = []

    # Ensure at least one scalar is zero
    zero_pair_index = draw(st.integers(min_value=0, max_value=num_pairs - 1))

    for i in range(num_pairs):
        point = draw(bls12_381_point())
        px, py = point
        px_bytes = px.to_bytes(64, byteorder="big")
        py_bytes = py.to_bytes(64, byteorder="big")

        if i == zero_pair_index:
            # Create a pair with scalar = 0
            scalar_bytes = (0).to_bytes(32, byteorder="big")
        else:
            # Create a normal pair with non-zero scalar
            scalar = draw(bls12_381_scalar())
            scalar_bytes = scalar.to_bytes(32, byteorder="big")

        pairs.append(px_bytes + py_bytes + scalar_bytes)

    return b"".join(pairs)


@composite
def g1_msm_valid_subgroup_with_zero_scalar(draw):
    """
    Generate G1 MSM input with valid subgroup points and at least one scalar set to zero.
    """
    num_pairs = draw(st.integers(min_value=1, max_value=5))
    pairs = []

    # Ensure at least one scalar is zero
    zero_pair_index = draw(st.integers(min_value=0, max_value=num_pairs - 1))

    for i in range(num_pairs):
        # Use the generator point (known to be in the subgroup)
        px = BLS12_381_G1_GENERATOR_X
        py = BLS12_381_G1_GENERATOR_Y
        px_bytes = px.to_bytes(64, byteorder="big")
        py_bytes = py.to_bytes(64, byteorder="big")

        if i == zero_pair_index:
            # Create a pair with scalar = 0
            scalar_bytes = (0).to_bytes(32, byteorder="big")
        else:
            # Create a normal pair with non-zero scalar
            scalar = draw(bls12_381_scalar())
            scalar_bytes = scalar.to_bytes(32, byteorder="big")

        pairs.append(px_bytes + py_bytes + scalar_bytes)

    return b"".join(pairs)


@composite
def valid_g2_point_bytes(draw):
    """
    Generate a valid G2 point using scalar multiplication and serialize it into 256 bytes.

    A random scalar between 1 and curve_order - 1 is drawn, then multiplied by the
    known generator in G2 (py_ecc.G2). The resulting point is valid by construction.

    The point is serialized as (x.c0 || x.c1 || y.c0 || y.c1) with 64 bytes per coordinate.

    Returns:
        bytes: 256-byte serialized representation of a valid G2 point
    """
    # Generate a valid G2 point
    scalar = draw(st.integers(min_value=1, max_value=curve_order - 1))
    pt = multiply(G2, scalar)

    # Serialize the point
    x, y = pt
    # Extract coefficients from FQ2 objects
    x_c0 = int(x.coeffs[0])
    x_c1 = int(x.coeffs[1])
    y_c0 = int(y.coeffs[0])
    y_c1 = int(y.coeffs[1])

    # Serialize each integer to 64 bytes
    serialized = (
        x_c0.to_bytes(64, byteorder="big")
        + x_c1.to_bytes(64, byteorder="big")
        + y_c0.to_bytes(64, byteorder="big")
        + y_c1.to_bytes(64, byteorder="big")
    )

    assert len(serialized) == 256, f"Expected 256 bytes, got {len(serialized)} bytes"
    return serialized


@composite
def two_bls12_381_g2_points_bytes(draw):
    """
    Generate two valid BLS12-381 G2 points by scalar multiplication and return their serialization as 512 bytes.
    Each point is serialized as (x.c0 || x.c1 || y.c0 || y.c1) with 64 bytes per coordinate.
    """
    point1 = draw(valid_g2_point_bytes())
    point2 = draw(valid_g2_point_bytes())
    p1_bytes = point1
    p2_bytes = point2
    result = p1_bytes + p2_bytes
    assert len(result) == 512, f"Expected 512 bytes, got {len(result)} bytes"
    return result


@composite
def non_bls12_381_g2_points_bytes(draw):
    """
    Generate 512 bytes that are guaranteed not to represent valid BLS12-381 G2 curve points.
    """
    random_bytes = draw(st.binary(min_size=512, max_size=512))
    assume(random_bytes != b"\x00" * 512)
    return random_bytes


def serialize_g2(pt):
    """Serialize G2 point into 256 bytes."""
    x, y = pt
    x_c0 = int(x.coeffs[0])
    x_c1 = int(x.coeffs[1])
    y_c0 = int(y.coeffs[0])
    y_c1 = int(y.coeffs[1])
    return (
        x_c0.to_bytes(64, byteorder="big")
        + x_c1.to_bytes(64, byteorder="big")
        + y_c0.to_bytes(64, byteorder="big")
        + y_c1.to_bytes(64, byteorder="big")
    )


@composite
def valid_g2_point(draw):
    """
    Generate a valid G2 point deterministically via scalar multiplication.
    """
    scalar = draw(st.integers(min_value=1, max_value=curve_order - 1))
    pt = multiply(G2, scalar)
    return pt


@composite
def g2_point_scalar_pair_bytes(draw):
    """
    Generate a pair of G2 point and scalar, formatted as 288 bytes:
    - 256 bytes for the G2 point (obtained deterministically)
    - 32 bytes for the scalar
    """
    point = draw(valid_g2_point())
    # Serialize the point to 256 bytes
    point_bytes = serialize_g2(point)
    scalar = draw(st.integers(min_value=0, max_value=2**256 - 1))
    scalar_bytes = scalar.to_bytes(32, byteorder="big")
    result = point_bytes + scalar_bytes
    assert (
        len(result) == LENGTH_PER_PAIR_G2
    ), f"Expected {LENGTH_PER_PAIR_G2} bytes, got {len(result)} bytes"
    return result


@composite
def g2_msm_input_bytes(draw, min_pairs=1, max_pairs=6):
    """
    Generate an input for G2 MSM consisting of multiple point-scalar pairs.
    """
    num_pairs = draw(st.integers(min_value=min_pairs, max_value=max_pairs))
    pairs = [draw(g2_point_scalar_pair_bytes()) for _ in range(num_pairs)]
    return b"".join(pairs)


@composite
def bls12_381_fp2_element(draw):
    """
    Generate a random element in Fp2, which is represented as a pair of Fp elements (c0, c1)
    where the element is c0 + c1*u and u^2 = -1.
    """
    p = BLS12_381_PRIME
    c0 = draw(st.integers(min_value=0, max_value=p - 1))
    c1 = draw(st.integers(min_value=0, max_value=p - 1))
    return (c0, c1)


@composite
def bls12_381_g2_point(draw):
    """
    Generate a random point on the BLS12-381 G2 curve defined over Fp2.
    The G2 curve equation is y^2 = x^3 + 4(u+1) where u^2 = -1.

    Each point is represented as (x, y) where x and y are elements of Fp2.
    """
    p = BLS12_381_PRIME

    # Draw a random x-coordinate in Fp2
    x_c0, x_c1 = draw(bls12_381_fp2_element())

    # Compute the right-hand side of the curve equation: x^3 + 4(u+1)
    # For G2, the constant term is 4(u+1) = 4 + 4u

    # Calculate x^3 in Fp2
    x_c0_squared = (x_c0 * x_c0) % p
    x_c1_squared = (x_c1 * x_c1) % p

    # (a+bu)^2 = a^2 - b^2 + 2abu
    x_squared_c0 = (x_c0_squared - x_c1_squared) % p
    x_squared_c1 = (2 * x_c0 * x_c1) % p

    # (a+bu)^3 = (a^2-b^2)a + (2ab)bu = a^3-ab^2 + (2a^2b-b^3)u
    x_cubed_c0 = (x_squared_c0 * x_c0 - x_squared_c1 * x_c1) % p
    x_cubed_c1 = (x_squared_c0 * x_c1 + x_squared_c1 * x_c0) % p

    # Add 4(u+1) = 4 + 4u
    rhs_c0 = (x_cubed_c0 + 4) % p
    rhs_c1 = (x_cubed_c1 + 4) % p

    # Check if there's a valid y value (i.e., if rhs is a quadratic residue in Fp2)
    # This is complex for Fp2, so we'll use a simplified approach:
    # We'll draw a random y and check if it satisfies the curve equation
    y_c0, y_c1 = draw(bls12_381_fp2_element())

    # Calculate y^2 in Fp2
    y_c0_squared = (y_c0 * y_c0) % p
    y_c1_squared = (y_c1 * y_c1) % p
    y_squared_c0 = (y_c0_squared - y_c1_squared) % p
    y_squared_c1 = (2 * y_c0 * y_c1) % p

    # Check if y^2 = rhs
    if y_squared_c0 != rhs_c0 or y_squared_c1 != rhs_c1:
        # If not a valid point, re-draw
        return draw(bls12_381_g2_point())

    return ((x_c0, x_c1), (y_c0, y_c1))


@composite
def g2_msm_with_zero_scalar(draw):
    """
    Generate input for G2 MSM with at least one zero scalar using deterministic valid G2 point generation.
    """
    num_pairs = draw(st.integers(min_value=1, max_value=5))
    pairs = []

    # Ensure at least one scalar is zero
    zero_scalar_index = draw(st.integers(min_value=0, max_value=num_pairs - 1))

    for i in range(num_pairs):
        # Use deterministic strategy for a valid G2 point (avoiding recursive random generation)
        point = draw(valid_g2_point())
        # Serialize the point using the serialize_g2 helper
        point_bytes = serialize_g2(point)

        if i == zero_scalar_index:
            scalar = 0
        else:
            scalar = draw(bls12_381_scalar())

        scalar_bytes = scalar.to_bytes(32, byteorder="big")
        pair = point_bytes + scalar_bytes
        pairs.append(pair)

    return b"".join(pairs)


@composite
def g2_msm_valid_subgroup_with_zero_scalar(draw):
    """
    Generate input for G2 MSM with valid subgroup points and at least one zero scalar.
    """
    num_pairs = draw(st.integers(min_value=1, max_value=5))
    pairs = []

    # Ensure at least one scalar is zero
    zero_scalar_index = draw(st.integers(min_value=0, max_value=num_pairs - 1))

    for i in range(num_pairs):
        # Use the generator point (known to be in the correct subgroup)
        x_c0 = BLS12_381_G2_GENERATOR_X_C0
        x_c1 = BLS12_381_G2_GENERATOR_X_C1
        y_c0 = BLS12_381_G2_GENERATOR_Y_C0
        y_c1 = BLS12_381_G2_GENERATOR_Y_C1

        # Convert point to bytes
        x_c0_bytes = x_c0.to_bytes(64, byteorder="big")
        x_c1_bytes = x_c1.to_bytes(64, byteorder="big")
        y_c0_bytes = y_c0.to_bytes(64, byteorder="big")
        y_c1_bytes = y_c1.to_bytes(64, byteorder="big")

        # Generate scalar (zero for the designated index, random otherwise)
        if i == zero_scalar_index:
            scalar = 0
        else:
            scalar = draw(bls12_381_scalar())

        scalar_bytes = scalar.to_bytes(32, byteorder="big")

        # Create the pair
        pair = x_c0_bytes + x_c1_bytes + y_c0_bytes + y_c1_bytes + scalar_bytes
        pairs.append(pair)

    return b"".join(pairs)


@composite
def bls12_381_g1_point(draw):
    """
    Generate a valid G1 subgroup element by taking a random multiple of the G1 generator.
    """
    s = draw(st.integers(min_value=1, max_value=curve_order - 1))
    return multiply(G1, s)


@composite
def bls12_381_g2_point(draw):
    """
    Generate a valid G2 subgroup element by taking a random multiple of the G2 generator.
    """
    s = draw(st.integers(min_value=1, max_value=curve_order - 1))
    return multiply(G2, s)


@composite
def pairing_input_bytes(draw):
    """
    Generate valid input for BLS12-381 pairing operation.
    The input consists of pairs of G1 and G2 points.
    Each pair requires 384 bytes (128 for G1, 256 for G2).
    """
    # Decide how many pairs to generate (1-3 for reasonable test size)
    num_pairs = draw(st.integers(min_value=1, max_value=3))

    result = b""
    for _ in range(num_pairs):
        # Generate a valid G1 point and serialize it.
        g1_point = draw(bls12_381_g1_point())
        g1x = g1_point[0].n
        g1y = g1_point[1].n
        g1x_bytes = g1x.to_bytes(64, byteorder="big")
        g1y_bytes = g1y.to_bytes(64, byteorder="big")

        # Generate a valid G2 point and serialize it.
        # G2 points are represented as tuples of two FQ2 elements: ((x0, x1), (y0, y1))
        g2_point = draw(bls12_381_g2_point())
        g2x_real = g2_point[0].coeffs[0].n
        g2x_imag = g2_point[0].coeffs[1].n
        g2y_real = g2_point[1].coeffs[0].n
        g2y_imag = g2_point[1].coeffs[1].n
        g2x_real_bytes = g2x_real.to_bytes(64, byteorder="big")
        g2x_imag_bytes = g2x_imag.to_bytes(64, byteorder="big")
        g2y_real_bytes = g2y_real.to_bytes(64, byteorder="big")
        g2y_imag_bytes = g2y_imag.to_bytes(64, byteorder="big")

        # Concatenate the serialized coordinates.
        pair_bytes = (
            g1x_bytes
            + g1y_bytes
            + g2x_real_bytes
            + g2x_imag_bytes
            + g2y_real_bytes
            + g2y_imag_bytes
        )
        result += pair_bytes

    return result


@composite
def invalid_size_pairing_bytes(draw):
    """
    Generate byte sequences with lengths that are not multiples of 384 bytes.
    """
    # Generate a valid size first
    valid_size = 384 * draw(st.integers(min_value=1, max_value=3))

    # Then either add or remove some bytes
    if draw(st.booleans()):
        # Add 1-100 extra bytes
        extra_size = draw(st.integers(min_value=1, max_value=100))
        size = valid_size + extra_size
    else:
        # Remove 1-100 bytes (but ensure size > 0)
        missing_size = draw(
            st.integers(min_value=1, max_value=min(100, valid_size - 1))
        )
        size = valid_size - missing_size

    # Generate the actual bytes
    return draw(st.binary(min_size=size, max_size=size))
