r"""ADE log pairs retain the selected Dynkin type, polygon, and distinguished point."""

from sage_extensions.all import *  # noqa: F401,F403


def test_e6_log_pair_retains_its_ade_data() -> None:
    pair = ADELogPairs(QQ)("E", 6)

    assert pair in ADELogPairs(QQ)
    assert pair in ToricLogPairs(QQ)
    assert pair.dynkin_letter() == "E"
    assert pair.dynkin_rank() == 6
    assert not pair.is_affine_type()
    assert pair.distinguished_point() in pair.polygon().vertices()
    assert pair.blue_divisor() + pair.complementary_divisor() == pair.log_scheme().toric_boundary_divisor()
