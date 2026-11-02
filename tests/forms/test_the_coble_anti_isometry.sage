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



def _block_diagonal(blocks):
    r"""Assemble integer blocks into one Gram matrix, as lists of lists."""
    size = sum(len(block) for block in blocks)
    rows = [[0] * size for _ in range(size)]
    offset = 0
    for block in blocks:
        for row_index, row in enumerate(block):
            for column_index, entry in enumerate(row):
                rows[offset + row_index][offset + column_index] = entry
        offset += len(block)
    return rows


def _coble_discriminant_forms():
    r"""``A_{S_{Co}}`` and the twisted ``A_{T_{Co}}(-1)`` of the published report.

    The report's own construction is used: ``S`` with Gram ``<2> + <-2>^{10}`` and
    ``T`` with Gram ``<2> + 2U + 2*(-E_8 Cartan)``, where the E8 Cartan matrix is
    the one Sage's combinatorics states.  The matrices are assembled as integer
    lists only because Sage's block-diagonal assembly coerces through the owned
    ring's ``matrix_space`` protocol in this session; the *numbers* are the
    published constructor's, not an approximation — a hand-written diagram of the
    wrong shape (the affine one, say) is semidefinite and has a degenerate
    discriminant form, which the polar-radical criterion then refuses.
    """
    from sage.combinat.root_system.cartan_matrix import CartanMatrix

    cartan = [
        [int(entry) for entry in row]
        for row in CartanMatrix(["E", int(8)]).rows()
    ]
    # ``int(8)``: this session's preparser makes the literal a Sage Integer, which
    # Sage's CartanMatrix rejects here; the type argument is the same E8.
    assert len(cartan) == 8
    assert all(cartan[i][i] == 2 for i in range(8))
    assert all(
        cartan[i][j] == cartan[j][i] and cartan[i][j] in (0, -1)
        for i in range(8)
        for j in range(8)
        if i != j
    )
    e8 = [[-entry for entry in row] for row in cartan]
    hyperbolic = [[0, 2], [2, 0]]

    diagonal = [2] + [-2] * 10
    s_gram = [
        [diagonal[row] if index == row else 0 for index in range(11)]
        for row in range(11)
    ]
    t_gram = _block_diagonal(
        [
            [[2]],
            hyperbolic,
            [[2 * entry for entry in row] for row in e8],
        ]
    )

    coble_s = Lattices(ZZ)(s_gram)
    coble_t = Lattices(ZZ)(t_gram)
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
