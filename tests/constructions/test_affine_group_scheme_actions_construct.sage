r"""The category of actions of an affine group scheme has represented objects."""

from sage_extensions.all import *  # noqa: F401,F403


def test_mu_two_action_retains_the_acting_group_scheme() -> None:
    mu = AffineGroupSchemes(QQ).roots_of_unity(2)
    acted = AffineGroupSchemeActions(mu).an_object()

    assert acted in AffineGroupSchemeActions(mu)
    assert acted.group_scheme() is mu
