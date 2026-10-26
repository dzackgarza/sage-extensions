r"""The identity scheme morphism acts identically on affine quasi-coherent sheaves."""

from sage_extensions.all import *  # noqa: F401,F403


def _affine_line_structure_module_sheaf():
    line = AffineSpaces(QQ)(1, names=("x",))
    algebra = line.coordinate_algebra()
    sheaves = QuasiCoherentSheaves(line)
    sheaf = sheaves.associated_sheaf(algebra.free_module(1))
    return line, sheaves, sheaf


def test_identity_scheme_pullback_and_direct_image_fix_a_quasi_coherent_sheaf() -> None:
    line, _sheaves, sheaf = _affine_line_structure_module_sheaf()
    identity = line.categorical_identity_morphism()

    assert identity.module_pullback(sheaf) == sheaf
    assert identity.direct_image(sheaf) == sheaf


def test_identity_scheme_pullback_and_direct_image_are_endofunctors_on_qcoh() -> None:
    line, sheaves, _sheaf = _affine_line_structure_module_sheaf()
    identity = line.categorical_identity_morphism()
    pullback = identity.module_pullback_functor()
    direct_image = identity.direct_image_functor()

    assert pullback.domain() is sheaves
    assert pullback.codomain() is sheaves
    assert direct_image.domain() is sheaves
    assert direct_image.codomain() is sheaves


def test_identity_scheme_quasi_coherent_adjunction_uses_pullback_and_direct_image() -> None:
    line, _sheaves, _sheaf = _affine_line_structure_module_sheaf()
    identity = line.categorical_identity_morphism()
    adjunction = identity.quasi_coherent_adjunction()

    assert adjunction.left_adjoint() == identity.module_pullback_functor()
    assert adjunction.right_adjoint() == identity.direct_image_functor()
