r"""The identity of a finitely presented module induces the identity on Ext."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_of_z_mod_six_induces_identity_on_ext_one() -> None:
    line = ZZ.free_module(1)
    relations = ZZ.free_module(1)
    six = relations.Mor(line)({0: 6 * line.module_generator(0)}).cokernel()
    identity = six.Mor(six).identity()
    ext = six.ext(ZZ.regular_module(), degree=1)
    induced = identity.ext_map(ZZ.regular_module(), degree=1)

    assert induced.domain() is ext
    assert induced.codomain() is ext
    assert induced == ext.Mor(ext).identity()
