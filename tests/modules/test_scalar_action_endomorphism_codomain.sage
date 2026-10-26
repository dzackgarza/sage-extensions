"""The scalar-action morphism lands in endomorphisms of the additive group.

The codomain is End_Ab(U(M)), not End_R(M); the former is needed even
when a scalar acts additively but is not itself an R-linear endomorphism.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_free_module_scalar_action_has_additive_endomorphism_codomain():
    M = ZZ.free_module(2)
    rho = M.scalar_action()
    U = M.underlying_additive_group()
    assert rho.domain() is ZZ
    assert rho.codomain() is AdditiveGroups().AdditiveCommutative().End(U)
    e0, e1 = M.module_generator(0), M.module_generator(1)
    for n in (-3, 0, 1, 4):
        f = rho(ZZ(n))
        assert f(e0 + e1) == n * e0 + n * e1
        assert f(U.zero()) == U.zero()
