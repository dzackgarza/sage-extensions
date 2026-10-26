r"""Archive reconciliation for algebra scalar extension.

The archived ``AlgebraBaseChangeFunctor(f)`` is now the left adjoint of the
live algebra scalar-extension/restriction adjunction.  This specimen retains
its two essential operations: carrying a finite presentation from ``ZZ`` to
``QQ`` and carrying a nonidentity algebra morphism through the same functor.
"""

from sage_extensions.all import *


ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/functors/algebra_base_change.sage",
    "live_owner": "sage_extensions/categories/functors/algebra_scalar_change.py",
    "disposition": "reconciled-live-owner",
}


def _quadratic_integer_algebra():
    polynomial = ZZ.free_module(("x",)).symmetric_algebra()
    x = polynomial.algebra_generator("x")
    return (polynomial).quotient_by_relations((x**2 - 2,))


def test_archived_algebra_base_change_is_the_live_scalar_extension_functor() -> None:
    algebra = _quadratic_integer_algebra()
    ring_map = ZZ.Mor(QQ)(lambda scalar: QQ(scalar))
    extension = Algebras(ring_map.domain()).Associative().Unital().Commutative().base_change_adjunction(ring_map).left_adjoint()
    extended = extension(algebra)

    assert extended.base_ring() is QQ
    assert extended.algebra_generating_set() is algebra.algebra_generating_set()
    generator = extended.algebra_generator("x")
    assert generator**2 == extended(2)
    assert extended.relations().cardinality() == algebra.relations().cardinality()


def test_archived_algebra_base_change_carries_a_nonidentity_morphism() -> None:
    algebra = _quadratic_integer_algebra()
    involution = algebra.Mor(algebra)(
        {"x": -algebra.algebra_generator("x")}
    )
    ring_map = ZZ.Mor(QQ)(lambda scalar: QQ(scalar))
    extension = Algebras(ring_map.domain()).Associative().Unital().Commutative().base_change_adjunction(ring_map).left_adjoint()
    extended = extension(algebra)
    extended_involution = extension(involution)
    generator = extended.algebra_generator("x")

    assert extended_involution.domain() is extended
    assert extended_involution.codomain() is extended
    assert extended_involution(generator) == -generator




