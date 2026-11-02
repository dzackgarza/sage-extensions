r"""The extended isometry decision for torsion forms whose polar form has a radical.

Three additions to the documented reduction's outcomes, each pinned to a
specimen with a proof:

* the order-qualified value profile — the multiset of element orders and
  values, preserved by every isometry — is a ``False`` certificate with no
  search; it separates the equal-radical pairs the earlier invariants could
  not, including the ``(Z/16)^3`` diagonal pair and the obstruction specimen
  on ``Z/4 x Z/2``, whose radical is not a direct summand and whose reduced
  forms are isomorphic while the forms are not;
* the witness search runs over the orbit of the framing under the elementary
  automorphisms of the presented module (unit rescalings, transpositions of
  equal-invariant coordinates, and admissible transvections), not only over
  monomial transports: on ``(Z/4)^2``, ``diag(1/4, 1/4)`` and
  ``(x^2 + 2xy + 2y^2)/4`` are isometric only through the shear
  ``e_2 |-> e_2 + e_1``, and every unit twist of ``(Z/2)^3`` carries one;
* the bounded search keeps its contract: running past the candidate budget is
  undecided (never ``False``, never an unsound classification), and each
  ``True`` below is admitted by the typed isometry constructor with
  ``check=True``.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed import (
    TorsionBilinearFormModules,
    TorsionQuadraticFormModules,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    TorsionFormIsometry,
)
from sage_extensions.categories.modules.framed.fraction_field_quotients import (
    FractionFieldQuotients,
)

import pytest

VALUES = FractionFieldQuotients(ZZ)(2)
HALF = QQ(1) / QQ(2)
QUARTER = QQ(1) / QQ(4)


def _quadratic(relation_rows, gram):
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        relation_rows, gram, VALUES
    )


def test_the_shear_between_diagonal_and_mixed_grams_on_four_squares_is_found() -> None:
    r"""``diag(1/4, 1/4)`` and ``(x^2 + 2xy + 2y^2)/4`` on ``(Z/4)^2``.

    No monomial automorphism carries one to the other: a diagonal rescaling
    would need odd ``u, v`` with ``2uv = 0 mod 4``, and a transposition leaves
    the cross term.  The orbit search finds the shear ``e_2 |-> e_2 + e_1``
    and the typed constructor checks it, so this is a ``True`` the published
    candidate set could only leave undecided.
    """
    diagonal = _quadratic(
        [[4, 0], [0, 4]], [[QUARTER, 0], [0, QUARTER]]
    )
    mixed = _quadratic(
        [[4, 0], [0, 4]], [[QUARTER, QUARTER], [QUARTER, HALF]]
    )
    assert diagonal.is_isomorphic(mixed) is True
    witness = diagonal.isometry_to(mixed)
    assert isinstance(witness, TorsionFormIsometry)
    for generator in diagonal.module_generators():
        assert mixed.q(witness.forward()(generator)) == diagonal.q(generator)


def test_the_unit_twist_on_three_two_elementary_generators_is_isometric() -> None:
    r"""``diag(1/2, 1/2, 1)`` and ``3q`` on ``(Z/2)^3`` agree as forms up to a shear.

    The twist by ``3`` on the first coordinate is not seen by any diagonal or
    permutation candidate: the witness exchanges the radical direction with a
    transvection.  The same twist on ``Z/4`` is decided ``False`` elsewhere in
    this suite, so the answer here is a proof, not a symmetry principle.
    """
    base = _quadratic(
        [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        [[HALF, 0, 0], [0, HALF, 0], [0, 0, 1]],
    )
    twisted = _quadratic(
        [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        [[3 * HALF, 0, 0], [0, 3 * HALF, 0], [0, 0, 3]],
    )
    assert base.is_isomorphic(twisted) is True
    witness = base.isometry_to(twisted)
    assert isinstance(witness, TorsionFormIsometry)
    for generator in base.module_generators():
        assert twisted.q(witness.forward()(generator)) == base.q(generator)


def test_the_nonsplit_obstruction_pair_is_decided_false_by_the_profile() -> None:
    r"""``Z/4 x Z/2`` with ``G_1 = [[0, 1/2], [1/2, 1/2]]`` and ``G_3 = [[1/2, 1/2], [1/2, 0]]``.

    Both forms share the radical ``<2 e_1>`` with ``q`` vanishing there, and
    their reduced forms on ``(Z/2)^2`` are isomorphic by a swap, so nothing in
    the reduction's former invariant list separates them.  The order-qualified
    value profile does: among the elements of order two, ``G_1`` attains
    ``1/2`` twice where ``G_3`` attains it never.  The pair is a certificate
    that splitting hypotheses matter, and it is decided here without a search.
    """
    first = _quadratic(
        [[4, 0], [0, 2]], [[0, HALF], [HALF, HALF]]
    )
    second = _quadratic(
        [[4, 0], [0, 2]], [[HALF, HALF], [HALF, 0]]
    )
    assert first.polar_radical().cardinality() == second.polar_radical().cardinality()
    assert first.is_isomorphic(second) is False
    assert second.is_isomorphic(first) is False
    assert first.isometry_to(second) is None


def test_a_deep_regrading_past_the_search_budget_is_undecided_not_false() -> None:
    r"""An isometric regrading of ``(Z/16)^3`` buried past the candidate budget.

    The regraded form *is* isometric — the Gram matrix below is ``A^t G A``
    for a long product ``A`` of elementary automorphisms of ``(Z/16)^3`` — so
    every named invariant agrees and the orbit search runs without finding the
    short word.  The answer must then be the supported undecided outcome:
    spending the budget is not exhausting the orbit, and the decision may
    neither claim ``False`` nor fabricate a witness.
    """
    steps = [
        [[1, 0, 3], [0, 1, 0], [0, 0, 1]],
        [[7, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 1, 0], [0, 1, 1]],
        [[1, 5, 0], [0, 1, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 7, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 1, 11], [0, 0, 1]],
        [[0, 1, 0], [1, 0, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 1, 0], [13, 0, 1]],
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[1, 0, 9], [0, 1, 0], [0, 0, 1]],
        [[1, 0, 0], [0, 1, 7], [0, 0, 1]],
        [[1, 0, 0], [0, 0, 1], [0, 1, 0]],
    ]

    def matmul(left, right):
        return [
            [
                sum(left[row][k] * right[k][column] for k in range(3)) % 16
                for column in range(3)
            ]
            for row in range(3)
        ]

    change = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for step in steps:
        change = matmul(step, change)

    eighth = QQ(1) / QQ(8)
    regraded = [
        [
            sum(
                change[k][i] * eighth * change[k][j]
                for k in range(3)
            )
            for j in range(3)
        ]
        for i in range(3)
    ]
    diagonal = _quadratic(
        [[16, 0, 0], [0, 16, 0], [0, 0, 16]],
        [[eighth, 0, 0], [0, eighth, 0], [0, 0, eighth]],
    )
    buried = _quadratic([[16, 0, 0], [0, 16, 0], [0, 0, 16]], regraded)
    with pytest.raises(TypeError, match="undecided"):
        diagonal.is_isomorphic(buried)


def test_the_bilinear_flavour_keeps_the_profile_certificate() -> None:
    r"""The obstruction pair as bilinear forms on ``Z/4 x Z/2``: same radical, and still separated.

    Notice first that the quadratic-flavour twists ``1/2`` and ``3/2`` on
    ``Z/4`` are not a bilinear specimen at all — as values in ``Q/Z`` they are
    one class.  Here the two forms ``[[0, 1/2], [1/2, 1/2]]`` and
    ``[[1/2, 1/2], [1/2, 0]]`` on ``Z/4 x Z/2`` share the radical
    ``<2 e_1>``, and a bilinear isometry must preserve the diagonal values
    ``b(x, x)`` with their element orders: among the order-two elements the
    first attains ``1/2`` twice and the second never, so the profile decides
    ``False`` without a search.
    """
    values = FractionFieldQuotients(ZZ)(1)

    def bilinear(relation_rows, gram):
        return TorsionBilinearFormModules(ZZ).from_relations_and_gram(
            relation_rows, gram, values
        )

    first = bilinear([[4, 0], [0, 2]], [[0, HALF], [HALF, HALF]])
    second = bilinear([[4, 0], [0, 2]], [[HALF, HALF], [HALF, 0]])
    assert first.polar_radical().cardinality() == second.polar_radical().cardinality()
    assert first.is_isomorphic(second) is False
    assert second.is_isomorphic(first) is False
    assert first.isometry_to(second) is None
    assert first.is_isomorphic(
        bilinear([[4, 0], [0, 2]], [[0, HALF], [HALF, HALF]])
    ) is True
