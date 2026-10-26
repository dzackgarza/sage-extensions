r"""The free resolution of a cyclic module over the integers."""

from sage_extensions.all import *  # noqa: F401,F403


def test_Z_mod_2_has_the_length_one_resolution_by_multiplication_by_two() -> None:
    r"""``0 -> Z --2--> Z -> Z/2 -> 0`` resolves ``Z/2``; ``Ext^1(Z/2, Z) = Z/2``.

    Over the principal ideal domain ``Z`` every finitely generated module has
    a free resolution of length at most one (Weibel, *An Introduction to
    Homological Algebra*, 4.1).
    """
    line = Modules(ZZ)(ZZ**1)
    (e,) = line.basis()
    module = line.Mor(line)({e: 2 * e}).cokernel()

    resolution = module.free_resolution()
    first = resolution.differential(1)

    assert module.cardinality() == 2
    assert first.kernel().cardinality() == 1
    assert first.cokernel().cardinality() == 2
    assert module.ext(line, 1).cardinality() == 2
    assert module.ext(line, 2).cardinality() == 1
