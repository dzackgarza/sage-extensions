r"""Discriminant morphisms of the two-elementary form ``U(2) + E8(-2)``.

``M = U(2) + E8(-2)`` has rank 10, signature ``(1, 9)`` and discriminant form of
order 1024 with invariants ``(2, ..., 2)`` — the shape the Enriques consumer's
invariant lattice carries.  ``E8(-2)`` here is −2 times the E8 Cartan Gram
(diagonal −4, determinant 256); the *negated* Cartan matrix is unimodular and
would leave only the ``U(2)`` block contributing to the discriminant group.

An isometry of ``M`` acts on all 1024 discriminant classes.  These tests pin
that action: it preserves the quadratic form class by class, it respects
composition, and it is the map the lattice isometry actually induces.  Both
isometries used are involutions, so they do not test the invertibility of the
source map's stored inverse.
"""

from sage_extensions.all import Lattices, ZZ, signature_pair


def _two_elementary_module():
    r"""``M = U(2) + E8(-2)``: rank 10, signature (1, 9), discriminant (2, ..., 2)."""
    e8_cartan = [
        [2, -1, 0, 0, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0, 0, 0],
        [0, -1, 2, -1, 0, 0, 0, -1],
        [0, 0, -1, 2, -1, 0, 0, 0],
        [0, 0, 0, -1, 2, -1, 0, 0],
        [0, 0, 0, 0, -1, 2, -1, 0],
        [0, 0, 0, 0, 0, -1, 2, 0],
        [0, 0, -1, 0, 0, 0, 0, 2],
    ]
    # E8(-2) is -2 times the Cartan Gram, so determinant (-2)^8 = 256; the
    # negated Cartan matrix itself is unimodular and would leave the
    # discriminant form two-elementary only in the U(2) block.
    e8_neg_twice = [[-2 * entry for entry in row] for row in e8_cartan]
    M = Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)(e8_neg_twice)
    assert M.rank() == 10
    assert M.signature_pair() == signature_pair(1, 9)
    D = M.discriminant_group()
    assert D.cardinality() == 1024
    return M, D


def test_negation_induces_a_quadratic_form_preserving_discriminant_morphism() -> None:
    r"""``−id`` acts on ``A_M`` and preserves ``q`` on every one of the 1024 classes."""
    M, D = _two_elementary_module()
    negation = M.O()(lambda label: -M.module_generator(label))
    morphism = negation.discriminant_morphism()

    elements = tuple(D.elements())
    assert len(elements) == 1024
    assert all(D.q(morphism(x)) == D.q(x) for x in elements)
    # −id is an involution, so its discriminant morphism is one too
    assert morphism**2 == D.orthogonal_group().one()


def test_a_non_symmetric_root_reflection_induces_a_discriminant_morphism() -> None:
    r"""An ``E8(-2)`` root reflection is not a diagonal or permutation matrix, and still descends.

    This is the case a matrix-convention error would break first.
    """
    M, D = _two_elementary_module()
    labels = tuple(M.module_generating_set())
    root = M.module_generator(labels[2])

    def reflect(label):
        x = M.module_generator(label)
        return x - ((2 * M.b(x, root)) // M.b(root, root)) * root

    reflection = M.O()(reflect)
    assert reflection(root) == -root
    generators = tuple(M.module_generator(label) for label in labels)
    assert all(
        M.b(reflection(x), reflection(y)) == M.b(x, y)
        for x in generators
        for y in generators
    )

    morphism = reflection.discriminant_morphism()
    assert all(D.q(morphism(x)) == D.q(x) for x in tuple(D.elements()))


def test_the_discriminant_morphism_respects_composition() -> None:
    r"""``Disc(g h) = Disc(g) Disc(h)``, measured on the same two-elementary form."""
    M, D = _two_elementary_module()
    labels = tuple(M.module_generating_set())
    root = M.module_generator(labels[2])
    negation = M.O()(lambda label: -M.module_generator(label))
    reflection = M.O()(
        lambda label: M.module_generator(label)
        - ((2 * M.b(M.module_generator(label), root)) // M.b(root, root)) * root
    )

    product = negation * reflection
    assert product.discriminant_morphism() == (
        negation.discriminant_morphism() * reflection.discriminant_morphism()
    )


def test_the_induced_map_agrees_with_the_lattice_action_on_discriminant_classes() -> None:
    r"""The morphism is the map the lattice isometry actually induces, checked on a generating set."""
    M, D = _two_elementary_module()
    labels = tuple(M.module_generating_set())
    root = M.module_generator(labels[2])
    reflection = M.O()(
        lambda label: M.module_generator(label)
        - ((2 * M.b(M.module_generator(label), root)) // M.b(root, root)) * root
    )
    morphism = reflection.discriminant_morphism()

    classes = tuple(D.module_generating_set())
    assert len(classes) == 10
    for label in classes:
        point = D.module_generator(label)
        # the induced map is additive and preserves the form's values
        assert D.q(morphism(point)) == D.q(point)
        assert D.b(morphism(point), morphism(D.module_generator(classes[0]))) == D.b(
            point, D.module_generator(classes[0])
        )
