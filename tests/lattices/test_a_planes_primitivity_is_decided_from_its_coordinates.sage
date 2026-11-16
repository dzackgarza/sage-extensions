r"""A lattice subobject's primitivity is read from its coordinates, not from a quotient.

`primitive_isotropic_subobject` admits a plane only when the span of its basis is
saturated, and it reads that decision off the span's inclusion.  Over the integers
with both endpoints finitely generated and free, the cokernel of an inclusion is
the quotient of the ambient framing by the row lattice of its coordinate matrix,
and its torsion is that matrix's elementary divisors: the decision is one Smith
form of the matrix the inclusion already retains, so nothing constructs the
quotient module.  The first count below is that construction; the last assertions
are the decision itself, at saturated spans and at a span that misses a factor
two in each of two directions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_subobjects_primitivity_builds_no_quotient_module() -> None:
    r"""Decide primitivity of \(\langle e_1, f_2\rangle\), \(\langle e_1, 2f_2\rangle\) and lines.

    \(U\oplus U\) has basis \(e_1,f_1,e_2,f_2\) with \(b(e_i,f_i)=1\).  The span
    of \(e_1\) and \(f_2\) is primitive, while the span of \(e_1\) and \(2f_2\)
    has \(f_2\) outside it and twice \(f_2\) inside, so its quotient carries a
    torsion class of order two;
    the line spanned by \(2e_1\) has a quotient of the same kind and the line
    spanned by \(f_1 - e_1\) does not.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    span = lattice.subobject_on((e1, f2))
    inclusion = span.inclusion()

    decided, quotients = cokernels_built_by(span.is_primitive, inclusion)

    assert decided is True
    assert quotients == 0
    assert lattice.subobject_on((e1, 2 * f2)).is_primitive() is False
    assert lattice.subobject_on((2 * e1,)).is_primitive() is False
    assert lattice.subobject_on((f1 - e1,)).is_primitive() is True
    assert lattice.subobject_on(()).is_primitive() is True
