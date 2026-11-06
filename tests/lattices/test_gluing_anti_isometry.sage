r"""The anti-isometry a primitive gluing induces, as a morphism of torsion forms.

For a finite-index embedding ``j: M = S ⊥ T -> L`` of integral lattices with
both summands primitive in ``L``, the glue ``L/M`` is the graph of an
anti-isometry ``gamma: A_S -> A_T`` (Nikulin, Prop. 1.5.1).  ``gluing_subgroup()``
returns the glue as a subgroup of ``A_M``; ``gluing_anti_isometry(S)`` returns
``gamma`` itself, with codomain ``A_T`` carrying the negated form, because ``L``
being integral is exactly ``q_S(s) + q_T(t) = 0`` on the graph.

What is asserted is the object the consumer needs and the certificate its issue
states: the witness is a typed torsion-form isometry, ``q`` agrees on the
domain's generators, the inverse pair holds, and its order is the embedding's
own index and the glue's own order.

Two specimens.  The first is the index-two even overlattice of
``⟨2⟩ ⊥ ⟨-2⟩`` inside ``U``: the two summands each have discriminant group
``Z/2`` and ``gamma`` carries the class of order two to the class of order two.
The second is the consumer's: ``S_En ⊥ T_En ⊂ II_{3,19}`` with
``S_En = U(2) ⊕ E8(-2)`` and ``T_En = U ⊕ U(2) ⊕ E8(-2)``, as the invariant
lattice and its orthogonal complement of the Enriques involution.  Each has
``(Z/2)^10`` as discriminant group and the index is 1024, so there the glue is
the whole of both discriminant forms and ``gamma`` lives on all 1024 classes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _index_two_overlattice_in_u():
    r"""``diag(2, -2) -> U``: the isotropic class of ``A_M`` of order two."""
    summands = Lattices(ZZ)([[2, 0], [0, -2]])
    discriminant = summands.discriminant_group()
    glue_class = sum(discriminant.module_generators(), discriminant.zero())
    return summands.overlattice(glue_class)


def _enriques_extension():
    r"""``S_En ⊥ T_En -> II_{3,19}``, the primitive extension of the Enriques involution."""
    return Involutions.I_En.primitive_extension()


def test_the_index_two_overlattice_inside_u_has_an_anti_isometry_onto_its_complement() -> None:
    r"""Specimen 1: the class of order two goes to the class of order two."""
    inclusion = _index_two_overlattice_in_u()
    summands = inclusion.domain()
    labels = tuple(summands.module_generating_set())
    left = summands.subobject_on([summands.module_generator(labels[0])])

    assert inclusion.index() == ZZ(2)
    assert inclusion.codomain().is_unimodular() is True

    witness = inclusion.gluing_anti_isometry(left)

    assert witness.is_quadratic() is True
    assert witness.domain().cardinality() == 2
    assert witness.codomain().cardinality() == 2
    # the summands are the whole of the embedding's domain, so their glue is it
    assert witness.domain().cardinality() == inclusion.gluing_subgroup().cardinality()
    assert witness.domain().cardinality() == inclusion.index()
    for element in witness.domain().elements():
        image = witness(element)
        assert witness.domain().q(element) == witness.codomain().q(image)
        assert witness.inverse()(image) == element
        assert image.additive_order() == element.additive_order()
    assert max(
        witness(element).additive_order() for element in witness.domain().elements()
    ) == 2


def test_the_enriques_gluing_is_an_anti_isometry_on_all_1024_classes() -> None:
    r"""Specimen 2: ``A_{S_En} -> A_{T_En}(-1)``, the whole of both, index 1024."""
    extension = _enriques_extension()
    lattice = extension.lattice
    invariant = extension.invariant
    complement = extension.orthogonal_complement
    inclusion = extension.orthogonal_sum_inclusion()
    summands = inclusion.domain()

    assert lattice is NamedLattices.LK3
    assert extension.index() == ZZ(1024)
    assert summands.module_rank() == 22
    assert invariant.module_rank() == 10 and complement.module_rank() == 12
    assert invariant.discriminant_group().cardinality() == 1024

    # the invariant lattice is a primitive sublattice of the overlattice itself
    assert invariant.is_primitive() is True

    witness = inclusion.gluing_anti_isometry(invariant)

    assert witness.is_quadratic() is True
    # the glue is the whole of both discriminant forms, so the anti-isometry
    # lives on all 1024 classes of each, not only on a generating family
    assert witness.domain().cardinality() == 1024
    assert witness.codomain().cardinality() == 1024
    assert witness.domain().cardinality() == inclusion.index()

    for generator in witness.domain().module_generators():
        image = witness(generator)
        assert witness.domain().q(generator) == witness.codomain().q(image)
        assert witness.inverse()(image) == generator
