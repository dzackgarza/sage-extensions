r"""Every owned object exposes its selected-resolution registry at the root category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_polynomial_algebra_retains_its_selected_algebra_resolution() -> None:
    algebra = QQ.polynomial_ring("x")
    owner = algebra.algebra_framing_owner()
    labels = algebra.algebra_generating_set()

    assert algebra in Objects()
    assert algebra.has_selected_resolution(owner)
    assert algebra.selected_resolution_generating_set(owner) is labels
    assert algebra.selected_resolution(owner).generating_set() is labels
