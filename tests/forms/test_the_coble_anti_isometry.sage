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

    ``S = <2> + <-2>^{10}`` and ``T = <2> + 2U + 2*(-E_8 Cartan)``, the Gram
    matrices of the report, written out as integers so that the specimen depends
    only on the numbers it states.
    """
    diagonal = [2] + [-2] * 10
    s_gram = [
        [diagonal[row] if index == row else 0 for index in range(11)]
        for row in range(11)
    ]
    # The E8 Cartan matrix as Sage's combinatorics states it, negated: the
    # specimen's 2*(-E8 Cartan).  It is unimodular; a Bourbaki relabelling would
    # be the same lattice, but a diagram of the wrong shape (the affine one, for
    # instance) is not, and its discriminant form has a radical.
    cartan_e8 = [
        [-2, 0, 1, 0, 0, 0, 0, 0],
        [0, -2, 0, 1, 0, 0, 0, 0],
        [1, 0, -2, 1, 0, 0, 0, 0],
        [0, 1, 1, -2, 1, 0, 0, 0],
        [0, 0, 0, 1, -2, 1, 0, 0],
        [0, 0, 0, 0, 1, -2, 1, 0],
        [0, 0, 0, 0, 0, 1, -2, 1],
        [0, 0, 0, 0, 0, 0, 1, -2],
    ]
    t_gram = _block_diagonal(
        [
            [[2]],
            [[0, 2], [2, 0]],
            [[2 * entry for entry in row] for row in cartan_e8],
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
    r"""``q_T(gamma x) = -q_S(x)`` on every generator, and the inverse composes."""
    source, plain, twisted = _coble_discriminant_forms()
    witness = source.isometry_to(twisted)

    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is True
    assert witness.domain() is source
    assert witness.codomain() is twisted

    generators = tuple(source.module_generators())
    assert len(generators) == 11
    for generator in generators:
        image = witness.forward()(generator)
        assert twisted.q(image) == source.q(generator)
        assert plain.q(image) == -source.q(generator)
        assert witness.inverse()(image) == generator
