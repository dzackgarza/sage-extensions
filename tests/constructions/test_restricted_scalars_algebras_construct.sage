r"""Restriction of algebra scalars retains the extension algebra and scalar map.

The polynomial algebra ``QQ(i)[x]`` restricted along ``QQ -> QQ(i)`` remains
the same ring, now regarded as a ``QQ``-algebra with the extension and its
selected scalar/algebra generator labels retained separately.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_gaussian_polynomial_algebra_restricted_to_qq_retains_extension_data() -> None:
    extension = QuadraticField(-1, "i")
    algebra = extension["x"]
    ring_map = QQ.Mor(extension)(lambda rational: extension(rational))
    restricted = algebra.restrict_scalars(ring_map)

    assert restricted in RestrictedScalarsAlgebras(QQ)
    assert restricted.algebra_over_extension() is algebra
    assert restricted.extension_ring() is extension
    assert restricted.ring_map() is ring_map
    assert restricted.restricted_algebra_generator_labels().cardinality() == cardinal(1)
    assert restricted.restricted_scalar_generator_labels().cardinality() == cardinal(1)
    assert isinstance(restricted.one(), restricted.ElementType)
