r"""An analytic family over the open unit disc as the restriction of an analytified algebraic family."""

from sage_extensions.all import *


def test_the_disc_family_is_the_restriction_of_the_analytified_algebraic_family() -> None:
    r"""With \(\iota_X, \iota_\Delta\) the inclusions of the total space and of the disc into the
    analytifications, \(\iota_\Delta\circ\pi = \pi^{\mathrm{an}}\circ\iota_X\): the analytic family is the base change of
    \(\pi^{\mathrm{an}}\) to the disc.

    Source: SGA 1, Exposé XII, §1 (analytification commutes with base change).
    """
    family = AnalyticDiscFamily()
    total_inclusion, base_inclusion = family.comparison_maps()

    assert total_inclusion.domain() is family.analytic_total_space()
    assert base_inclusion.domain() is family.analytic_base()
    assert (
        base_inclusion * family.analytic_family_morphism()
        == family.analytified_family_morphism() * total_inclusion
    )
