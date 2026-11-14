r"""An integral lattice quotients by its radical as a lattice, not as a formed module.

``P/rad(P)`` for an integral lattice keeps the lattice owner's construction: the
quotient is ``I^perp/I`` with the isotropic reduction's inclusion, orthogonal
complement, ``quotient_lattice`` and parabolic data, so it supports the lattice
operations (``primitive_isotropic_subobject`` among them).  The generic
formed-module descent is the route for formed modules that are not lattices; for
an integral lattice it returned a relationful presented module whose generators
outnumber its rank.
"""

from sage_extensions.all import *


def _degenerate_lattice():
    return Lattices(ZZ)([[2, 0, 0], [0, 0, 0], [0, 0, 6]])


def test_a_degenerate_integral_lattice_quotients_by_its_radical_as_a_lattice() -> None:
    lattice = _degenerate_lattice()
    quotient = lattice.radical_quotient()

    assert quotient in Lattices(ZZ)
    assert quotient.rank() == 2
    assert hasattr(quotient, "primitive_isotropic_subobject")
    assert quotient.quotient_lattice() is quotient
    assert quotient.is_nondegenerate() is True

    gram = quotient.gram_matrix()
    diagonal = sorted([gram[0, 0], gram[1, 1]], key=int)
    assert diagonal == [ZZ(2), ZZ(6)]
    assert gram[0, 1] == ZZ.zero()


def test_the_radical_projection_kills_the_radical_and_keeps_the_coordinates() -> None:
    lattice = _degenerate_lattice()
    quotient = lattice.radical_quotient()
    projection = lattice.radical_quotient_projection()
    first, radical_generator, last = tuple(lattice.module_generators())

    assert projection.codomain() is quotient
    assert projection(radical_generator) == quotient.zero()
    assert projection(first) != quotient.zero()
    assert projection(last) != quotient.zero()


def test_the_exported_isotropic_reduction_ingress_agrees_with_the_quotient() -> None:
    lattice = _degenerate_lattice()
    ingress = IsotropicReductions(ZZ)(lattice.radical().inclusion())
    quotient = lattice.radical_quotient()

    assert ingress in Lattices(ZZ)
    assert ingress.rank() == quotient.rank() == 2
    ingress_gram = ingress.gram_matrix()
    quotient_gram = quotient.gram_matrix()
    for row in range(2):
        for column in range(2):
            assert ingress_gram[row, column] == quotient_gram[row, column]


def test_a_rank_twenty_four_radical_five_lattice_quotients_to_rank_nineteen() -> None:
    r"""The consumer's shape: a rank-24 lattice whose radical has rank 5.

    The Gram is two E8 blocks, three A1 blocks and five zero coordinates — the
    consumer's shape, not its ``G24``, whose Gram lives in the research
    repository and is not vendored here.
    """
    from sage_extensions.catalogue import _E8g, _block_gram

    a1 = tensor(ZZ, (), (1, 1), [[2]])
    zero = tensor(ZZ, (), (5, 5), [[ZZ.zero() for _ in range(5)] for _ in range(5)])
    lattice = Lattices(ZZ)(_block_gram(_E8g(), _E8g(), a1, a1, a1, zero))

    assert lattice.rank() == 24
    assert lattice.radical().rank() == 5
    assert lattice.is_nondegenerate() is False

    quotient = lattice.radical_quotient()
    assert quotient in Lattices(ZZ)
    assert quotient.rank() == 19
    assert quotient.is_nondegenerate() is True
    assert hasattr(quotient, "primitive_isotropic_subobject")
    assert quotient.quotient_lattice() is quotient
    assert lattice.radical_quotient_projection().codomain() is quotient
