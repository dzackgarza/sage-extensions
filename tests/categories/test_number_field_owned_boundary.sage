r"""The ring of integers of the real quadratic field of discriminant 5."""

from sage_extensions.all import *  # noqa: F401,F403


def test_ring_of_integers_of_QQ_sqrt5_is_Z_golden_ratio() -> None:
    r"""``O_K = Z[(1 + sqrt 5)/2]`` for ``K = Q(sqrt 5)``: discriminant 5, class number 1.

    ``phi = (1 + sqrt 5)/2`` is a root of ``x^2 - x - 1``, whose discriminant
    ``5`` is squarefree, so ``Z[phi]`` is maximal.  ``sqrt 5 / 2`` has minimal
    polynomial ``x^2 - 5/4`` and is not integral.  ``K`` is totally real.
    """
    field = QuadraticField(5, "a")
    a = field.primitive_element()
    order = field.ring_of_integers()
    golden = (1 + a) / 2

    assert golden**2 - golden - 1 == 0
    assert order.discriminant() == 5
    assert field.class_number() == 1
    assert golden in order
    assert a / 2 not in order
    assert field.embeddings(AA).cardinality() == 2
    assert order.integral_basis().cardinality() == 2
