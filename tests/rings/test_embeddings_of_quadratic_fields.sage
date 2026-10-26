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
    field = GF(4)

    assert field.Mor(field).embeddings().cardinality() == 2
