r"""Composing identity-slice adjunctions yields the same endoadjunction shape."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_slice_adjunction_composes_with_itself() -> None:
    line = AffineSpaces(QQ)(1)
    slices = Schemes(QQ).SliceOver(line)
    adjunction = line.categorical_identity_morphism().slice_base_change_adjunction()
    composite = adjunction.then(adjunction)

    assert composite.left_adjoint().domain() is slices
    assert composite.left_adjoint().codomain() is slices
    assert composite.right_adjoint().domain() is slices
    assert composite.right_adjoint().codomain() is slices
