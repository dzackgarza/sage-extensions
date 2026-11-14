r"""``|Hom(Rings)(R[x], R)| = |R|`` for a rigid coefficient ring.

A unital ring map out of ``R[S]`` is determined by a unital ring endomorphism
of ``R`` and the images of the generators, and those images are arbitrary.  When
``R`` is rigid -- ``ZZ`` and ``QQ`` have only the identity unital endomorphism,
since such a map fixes ``1``, hence ``ZZ``, hence inverses -- the coefficient
part contributes one choice, so the hom set is in bijection with ``A^S`` and

    |Hom(Rings)(R[S], A)| = |A|^|S|.

For ``A = QQ`` that is ``aleph_0^k = aleph_0`` for every finite ``k >= 1``, and
``1`` for ``k = 0``: with no variables the only map is the coefficient map.

The rule is stated with its hypotheses and refuses the rest; the last test pins
that boundary, so an undecided hom set is never silently counted.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_the_ring_maps_from_qq_x_to_qq_are_countably_many() -> None:
    r"""``x`` may go anywhere, and the coefficients cannot move: ``aleph_0`` maps."""
    assert QQ["x"].Mor(QQ).cardinality() == aleph0


def test_two_variables_do_not_change_the_count() -> None:
    r"""``aleph_0^2 = aleph_0``: the pair of generator images ranges over ``QQ^2``."""
    assert QQ.polynomial_ring(("x", "y")).Mor(QQ).cardinality() == aleph0


def test_a_polynomial_ring_in_no_variables_has_one_map_to_its_coefficient_ring() -> None:
    r"""``QQ[()] = QQ``, and a rigid ring has one unital endomorphism."""
    assert QQ.polynomial_ring(()).Mor(QQ).cardinality() == cardinal(1)


def test_a_hom_set_this_rule_does_not_decide_stays_undecided() -> None:
    r"""The unital-algebra hom set ``ZZ[x] -> ZZ`` is not decided by this rule.

    It is a different set -- maps preserving the scalar action, not all ring
    maps -- and no rule here counts it.  Refusing keeps the boundary visible:
    an undecided cardinality must not be answered with a plausible number.
    """
    with pytest.raises(AssertionError):
        ZZ["x"].Mor(ZZ).cardinality()
