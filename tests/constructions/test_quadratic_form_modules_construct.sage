r"""Quadratic-form modules retain the quadratic map and its polarization.

For ``q(x,y)=x^2+xy+y^2``, the associated bilinear form has
``b(e_0,e_1)=1`` and is recovered from the same selected quadratic datum.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _binary_quadratic_form():
    return ZZ.free_module(2).equip_quadratic_form(ZZ, [[1, 1], [0, 1]])


def test_quadratic_form_exposes_q_and_its_associated_bilinear_module() -> None:
    quadratic = _binary_quadratic_form()
    e0, e1 = quadratic.module_generator(0), quadratic.module_generator(1)
    bilinear = quadratic.associated_bilinear_module()

    assert quadratic in QuadraticFormModules(ZZ)
    assert quadratic.q(e0) == ZZ.one()
    assert quadratic.q(e1) == ZZ.one()
    assert quadratic.q(e0 + e1) == ZZ(3)
    assert bilinear in BilinearFormModules(ZZ)
    assert bilinear.b(bilinear.module_generator(0), bilinear.module_generator(1)) == ZZ.one()
    assert isinstance(e0, quadratic.ElementType)


def test_quadratic_form_module_morphisms_have_identity() -> None:
    quadratic = _binary_quadratic_form()
    identity = quadratic.Mor(quadratic).identity()

    assert identity(quadratic.module_generator(0)) == quadratic.module_generator(0)
    assert identity * identity == identity
