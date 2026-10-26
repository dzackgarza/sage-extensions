r"""Scalar-extended module morphisms retain their source map and extension functor."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rationalized_doubling_retains_scalar_extension_provenance() -> None:
    line = ZZ.free_module(("e",))
    e = line.module_generator("e")
    doubling = line.Mor(line)({"e": 2 * e})
    scalar_map = ZZ.Mor(QQ)(lambda value: QQ(value))
    extension = Modules(ZZ).scalar_extension(scalar_map)
    changed = extension(doubling)

    assert changed.scalar_extension_of() is doubling
    assert changed.scalar_extension_functor() is extension
