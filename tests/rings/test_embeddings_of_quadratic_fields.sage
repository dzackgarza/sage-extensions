r"""Embeddings between number fields, and the maps they induce on rings of integers.

A field map ``Q(sqrt 5) -> L`` is determined by the image of ``sqrt 5``, which must
be a square root of ``5`` in ``L``.  So ``Q(sqrt 5)`` has exactly two automorphisms,
the identity and the conjugation ``sigma: sqrt 5 -> -sqrt 5``, with
``sigma^2 = 1``.  The Gauss sum ``zeta - zeta^2 - zeta^3 + zeta^4`` squares to ``5``
in ``Q(zeta_5)``, so ``Q(sqrt 5)`` has exactly two embeddings there, exchanged by
precomposition with ``sigma``.  A field automorphism preserves integrality, so
``sigma`` restricts to the ring of integers, sending the golden ratio
``(1 + sqrt 5)/2`` to ``(1 - sqrt 5)/2``.  ``F_4`` has exactly two automorphisms,
the identity and Frobenius ``a -> a^2``.

An algebra endomorphism is more than a field automorphism: it must fix what the
retained structure map marks.  ``F_4`` is presented as ``F_2[z_2]/(z_2^2 + z_2 +
1)``, so its algebra Mor is taken over that presentation ring and its only
endomorphism is the identity, while Frobenius remains a ring automorphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_conjugation_is_the_nontrivial_automorphism_of_q_root_five() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()
    automorphisms = field.Mor(field)
    conjugation = automorphisms(-root)

    assert conjugation(root) == -root
    assert conjugation(root * root) == 5
    assert conjugation(1 + root) == 1 - root
    assert conjugation * conjugation == automorphisms.identity()
    assert conjugation != automorphisms.identity()
    assert conjugation.is_injective()


def test_q_root_five_has_exactly_two_automorphisms() -> None:
    field = QuadraticField(5)

    assert field.Mor(field).embeddings().cardinality() == 2


def test_q_root_five_embeds_twice_in_the_fifth_cyclotomic_field() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()
    conjugation = field.Mor(field)(-root)
    cyclotomic = CyclotomicField(5)
    embeddings = field.Mor(cyclotomic).embeddings()

    assert all(embedding(root) ** 2 == 5 for embedding in embeddings)
    assert all((embedding * conjugation)(root) == -embedding(root) for embedding in embeddings)
    assert all((embedding * conjugation) != embedding for embedding in embeddings)


def test_conjugation_restricts_to_the_ring_of_integers() -> None:
    field = QuadraticField(5)
    root = field.primitive_element()
    conjugation = field.Mor(field)(-root)
    integers = field.ring_of_integers()
    restricted = integers.Mor(integers)(conjugation)
    golden = integers((1 + root) / 2)

    assert restricted.field_embedding() == conjugation
    assert restricted.is_injective()
    assert restricted(golden) == integers((1 - root) / 2)
    assert restricted(golden) + golden == integers.one()
    assert restricted(golden) * golden == -integers.one()
    assert integers.Mor(integers).identity()(golden) == golden


def test_frobenius_is_the_nontrivial_automorphism_of_the_field_with_four_elements() -> None:
    from sage_extensions.categories.rings.ring_foundation import OwnedRings

    field = GF(4)
    automorphisms = OwnedRings().Mor(field, field).embeddings()

    assert automorphisms.cardinality() == 2
    identity = OwnedRings().Mor(field, field).identity()
    frobenius = tuple(e for e in automorphisms if e != identity)[0]
    assert frobenius * frobenius == identity


def test_a_presented_field_has_only_the_identity_as_an_algebra_endomorphism() -> None:
    r"""``F_4 = F_2[z_2]/(z_2^2 + z_2 + 1)`` remembers the class of ``z_2``.

    ``Mor(F_4, F_4)`` is the unital algebra Mor over the presentation ring
    ``F_2[z_2]``, so its arrows are the maps fixing the class of ``z_2``.  That
    class generates the field, so only the identity qualifies; Frobenius is a
    ring automorphism (the test above), not an algebra endomorphism of this
    presented structure, because it sends the class of ``z_2`` to ``z_2 + 1``
    and so fails \(f \circ \rho = \rho\).
    """
    from sage_extensions.categories.rings.ring_foundation import OwnedRings

    field = GF(4)
    structure = field.algebra_structure_morphism()
    base_generator = tuple(field.algebra_base_ring().algebra_generating_set())[0]
    structural_element = structure(base_generator)
    endomorphisms = field.Mor(field).embeddings()

    assert endomorphisms.cardinality() == 1
    identity = tuple(endomorphisms)[0]
    assert identity is field.Mor(field).identity()
    assert identity.linearity_decision() is True
    assert identity(structural_element) == structural_element

    identity_ring_map = OwnedRings().Mor(field, field).identity()
    frobenius = tuple(
        embedding
        for embedding in OwnedRings().Mor(field, field).embeddings()
        if embedding != identity_ring_map
    )[0]
    assert frobenius(structural_element) != structural_element
    assert frobenius * structure != structure


def test_the_presentation_of_the_field_with_eight_elements_fixes_its_generator_too() -> None:
    from sage_extensions.categories.rings.ring_foundation import OwnedRings

    field = GF(8)
    structure = field.algebra_structure_morphism()
    base_generator = tuple(field.algebra_base_ring().algebra_generating_set())[0]

    assert OwnedRings().Mor(field, field).embeddings().cardinality() == 3
    assert field.Mor(field).embeddings().cardinality() == 1
    assert tuple(field.Mor(field).embeddings())[0](structure(base_generator)) == structure(base_generator)
