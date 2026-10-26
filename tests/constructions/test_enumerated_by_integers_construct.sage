r"""Laurent monomials are enumerated by integer exponent."""

from sage_extensions.all import *  # noqa: F401,F403


def test_laurent_monomials_are_enumerated_by_integers() -> None:
    functions = EnumeratedByIntegers().an_object()

    assert functions in EnumeratedByIntegers()
    assert functions.index_set() is ZZ
    assert functions.function(-2) in functions
    assert functions.cardinality() == aleph0
