r"""The Coble anti-isometry, through the typed torsion-form witness.

The published research specimen (``dzackgarza/research``,
``computations/reports/coble_gluing_discriminants.py``) asks for

.. MATH::

    \gamma\colon A_{S_{Co}} \longrightarrow A_{T_{Co}}(-1),

an isometry from the discriminant form of ``S = 2 + (-2)^{10}`` to the twist by
``-1`` of the discriminant form of ``T = 2 + 2U + 2E_8``; the gluing of
``S_{Co} + T_{Co}`` into ``L_{K3}`` is its graph.  Both forms have order 2048.

Two statements are pinned here, and they are different: the *decision* that the
two forms are anti-isometric, and the *witness* realizing it.  The witness is a
typed form isometry, so it preserves ``q`` of the codomain exactly — and since
the codomain is the twist by ``-1``, the anti-isometry relation
``q_T(gamma x) = -q_S(x)`` holds on the generators.  That relation is checked
here directly, because a witness that preserved ``q_T`` while ignoring the sign
of the twist would be an isometry of the wrong form.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    TorsionFormIsometry,
)



def _coble_discriminant_forms():
    r"""``A_{S_{Co}}`` and the twisted ``A_{T_{Co}}(-1)`` of the published report.

    The construction is the report's own, called directly: ``S`` with Gram
    ``diagonal_matrix(ZZ, [2] + [-2]*10)`` and ``T`` with Gram
    ``block_diagonal_matrix(matrix(ZZ, [[2]]), 2*U, 2*(-E8 Cartan))``, where the
    E8 Cartan matrix comes from ``CartanMatrix(["E", 8])``.  Two spellings are
    forced by this session and change no number: ``int(8)`` because the preparser
    makes the literal a library integer, which Sage's ``CartanMatrix`` rejects,
    and ``int(2)`` for the scalar factors because a library integer has no action
    on a Sage matrix space (recorded in ``TRAPS.md``); Sage's own ``Integer``
    gives exactly these matrices, as the assertions on the assembled Gram show.
    """
    from sage.combinat.root_system.cartan_matrix import CartanMatrix
    from sage.matrix.constructor import (
        block_diagonal_matrix,
        diagonal_matrix,
        matrix,
    )
    from sage.rings.integer_ring import ZZ as SageZZ

    e8 = -CartanMatrix(["E", int(8)])
    assert e8.nrows() == 8 and e8.base_ring() is SageZZ
    hyperbolic = matrix(SageZZ, [[0, 1], [1, 0]])
    s_gram = diagonal_matrix(SageZZ, [int(2)] + [int(-2)] * 10)
    t_gram = block_diagonal_matrix(
        matrix(SageZZ, [[int(2)]]), int(2) * hyperbolic, int(2) * e8
    )
    assert s_gram.nrows() == 11 and t_gram.nrows() == 11

    coble_s = Lattices(ZZ)([list(row) for row in s_gram.rows()])
    coble_t = Lattices(ZZ)([list(row) for row in t_gram.rows()])
    return (
        coble_s.discriminant_group(),
        coble_t.discriminant_group(),
        coble_t.discriminant_group().twist(-1),
    )


def test_the_two_coble_discriminant_forms_are_anti_isometric() -> None:
    r"""``A_{S}`` and ``A_{T}(-1)`` are isometric, and both have order 2048."""
    source, plain, twisted = _coble_discriminant_forms()

    assert source.cardinality() == 2048
    assert plain.cardinality() == 2048
    assert source.is_anti_isometric(plain) is True
    assert source.is_isomorphic(twisted) is True


def test_the_witness_is_a_typed_isometry_realizing_the_anti_isometry() -> None:
    r"""``q`` and ``b`` at once, the sign included, with inverse and composition.

    The source form is ``q``-valued in ``Q/2Z``; the codomain is the twist by
    ``-1``.  A witness is accepted only if it preserves the codomain form
    exactly — ``q`` on generators and on pair sums, ``b`` on every pair of
    generators — and that is what makes
    ``q_T(gamma x) = -q_S(x)`` and ``b_T(gamma x, gamma y) = -b_S(x, y)`` hold
    against the *untwisted* form.
    """
    source, plain, twisted = _coble_discriminant_forms()
    witness = source.isometry_to(twisted)

    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is True
    assert witness.domain() is source
    assert witness.codomain() is twisted

    generators = tuple(source.module_generators())
    assert len(generators) == 11
    images = tuple(witness.forward()(generator) for generator in generators)

    # The codomain form is preserved exactly.
    for generator, image in zip(generators, images, strict=True):
        assert twisted.q(image) == source.q(generator)
    for left in generators:
        for right in generators:
            assert twisted.q(witness.forward()(left + right)) == source.q(left + right)
            assert (
                twisted.b(witness.forward()(left), witness.forward()(right))
                == source.b(left, right)
            )

    # Against the untwisted form this is an anti-isometry, sign included.
    for generator, image in zip(generators, images, strict=True):
        assert plain.q(image) == -source.q(generator)
    for left in generators:
        for right in generators:
            assert plain.q(witness.forward()(left + right)) == -source.q(left + right)
            assert (
                plain.b(witness.forward()(left), witness.forward()(right))
                == -source.b(left, right)
            )

    # The inverse pair and the two composites, on the generators.
    for generator, image in zip(generators, images, strict=True):
        assert witness.inverse()(image) == generator
    for image in images:
        assert witness.forward()(witness.inverse()(image)) == image
    # ``f.then(g)`` is ``g`` after ``f``, so each composite fixes the end it ends at.
    forward_then_inverse = witness.then(witness.inverse())
    inverse_then_forward = witness.inverse().then(witness)
    for generator in generators:
        assert forward_then_inverse(generator) == generator
    for image in images:
        assert inverse_then_forward(image) == image
