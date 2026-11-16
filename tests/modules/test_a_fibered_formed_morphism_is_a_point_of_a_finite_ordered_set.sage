r"""A formed module and a formed-module morphism as points of a finite ordered set.

A category's own object is built by the category, so the symmetric even witness
``BilinearFormModules(ZZ).an_object()`` is an object of ``Symmetric().Even()``:
the Gram matrix of ``U`` is ``[[0, 1], [1, 0]]``, which is symmetric with zero
diagonal, hence even.  A formed-module morphism over a ring map is an arrow of
the Mor set the domain's ``fibered_formed_mor`` returns, and its equality
compares the semilinear module component and the value component.

Both classes decide equality, so both owe the hash :class:`Sets` states: equal
elements hash alike and a finite ordered set holds them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_symmetric_even_witness_is_an_object_of_the_category_it_names() -> None:
    r"""``BilinearFormModules(ZZ).an_object()`` is ``U``, symmetric and even.

    The object the category states for itself is the plane with the hyperbolic
    form: its Gram matrix is symmetric, and its diagonal is zero, so the form is
    even as well.  A construction establishes the properties it is asked for,
    so the witness is an object of both branches at once, and it is a point of a
    finite ordered set.
    """
    witness = BilinearFormModules(ZZ).an_object()

    assert witness in BilinearFormModules(ZZ)
    assert witness in BilinearFormModules(ZZ).Symmetric()
    assert witness in BilinearFormModules(ZZ).Even()
    assert witness in BilinearFormModules(ZZ).Symmetric().Even()
    assert witness.module_rank() == 2
    assert FiniteOrderedSets()((witness,)).cardinality() == 1


def test_two_presentations_of_one_fibered_formed_morphism_are_one_point() -> None:
    r"""The identity of one endomorphism set, and the same pair of components again.

    The ring map is the identity of ``ZZ``, so the endomorphism set of the
    witness over it has an identity arrow.  Its module and value components
    define a second arrow of the same set, which is why the two are equal; the
    first is not the second, so what the finite ordered set counts is the
    equality and not the identity of the objects.
    """
    witness = BilinearFormModules(ZZ).an_object()
    identity_map = Rings().Mor(ZZ, ZZ).identity()
    arrows = witness.fibered_formed_mor(witness, identity_map)
    identity = arrows.identity()
    rebuilt = arrows((identity.module_morphism(), identity.value_morphism()))

    assert rebuilt is not identity
    assert rebuilt == identity
    assert hash(rebuilt) == hash(identity)
    assert FiniteOrderedSets()((rebuilt, identity)).cardinality() == 1
