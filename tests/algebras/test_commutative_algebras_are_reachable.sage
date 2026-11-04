r"""The commutative-algebra category is reachable and carries its de Rham data.

Research asked for ``CommutativeAlgebras.de_rham_adjunction``.  This library has
no ``CommutativeAlgebras`` name: commutative algebras are the refinement
``Algebras(R).Associative().Unital().Commutative()``, and that refinement is what
carries ``de_rham``, ``de_rham_adjunction`` and ``de_rham_cohomology``.  The base
``Algebras`` was itself unexported, which is why the chain was unreachable from a
session; it is exported now, and these tests pin the maintained spelling and the
two functors it answers.
"""

from sage_extensions.all import Algebras, ZZ


def _commutative_algebras():
    return Algebras(ZZ).Associative().Unital().Commutative()


def test_the_commutative_algebra_category_is_reachable() -> None:
    category = _commutative_algebras()

    assert repr(category) == "Category of commutative algebras"
    assert category.base_ring() is ZZ


def test_the_de_rham_functor_and_adjunction_answer() -> None:
    category = _commutative_algebras()

    functor = category.de_rham()
    adjunction = category.de_rham_adjunction()

    assert "de Rham" in repr(functor)
    assert "adjunction" in repr(adjunction)
    assert "Integer Ring" in repr(adjunction)


def test_de_rham_cohomology_is_indexed_by_degree() -> None:
    category = _commutative_algebras()

    assert repr(category.de_rham_cohomology(1)).startswith("H^{1}_dR")
