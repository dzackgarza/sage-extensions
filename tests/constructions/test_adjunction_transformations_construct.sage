r"""The identity-slice adjunction exposes its unit and counit as natural transformations."""

from sage_extensions.all import *  # noqa: F401,F403


def _identity_slice_adjunction():
    line = AffineSpaces(QQ)(1)
    identity = line.categorical_identity_morphism()
    slices = Schemes(QQ).SliceOver(line)
    obj = slices(identity)
    return obj, identity.slice_base_change_adjunction()


def test_identity_slice_adjunction_unit_transformation_has_identity_component_endpoints() -> None:
    obj, adjunction = _identity_slice_adjunction()
    component = adjunction.unit_transformation().component(obj)

    assert component.domain() is obj
    assert component.codomain() is obj


def test_identity_slice_adjunction_counit_transformation_has_identity_component_endpoints() -> None:
    obj, adjunction = _identity_slice_adjunction()
    component = adjunction.counit_transformation().component(obj)

    assert component.domain() is obj
    assert component.codomain() is obj
