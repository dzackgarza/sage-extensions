r"""Framed free modules retain the canonical basis map and its consequences.

The standard module ``ZZ^2`` is countable, torsion-free, and rank two.  Its
selected basis defines diagonal Gram tensors, full and generated subobjects,
and the canonical scalar extension to ``QQ^2``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_standard_plane_has_rank_cardinality_and_torsion_free_framing() -> None:
    module = ZZ.free_module(2)

    assert module in FramedFreeModules(ZZ)
    assert module.module_rank() == 2
    assert module.cardinality() == aleph0
    assert not module.is_finite()
    assert module.is_torsion_free()
    assert isinstance(module.module_generator(0), module.ElementType)


def test_framed_basis_builds_diagonal_gram_and_subobjects() -> None:
    module = ZZ.free_module(2)
    e0 = module.module_generator(0)
    gram = module.diagonal_gram({}, default=1)
    line = module.subobject_on((e0,))
    whole = module.whole_subobject()

    assert gram[0, 0] == ZZ.one()
    assert gram[1, 1] == ZZ.one()
    assert gram[0, 1] == ZZ.zero()
    assert line.module_rank() == 1
    assert whole.inclusion().domain() is whole
    assert whole.inclusion().codomain() is module
    assert whole.index() == 1


def test_framed_free_module_base_change_and_vector_space_have_expected_rank() -> None:
    module = ZZ.free_module(2)
    inclusion = ZZ.Mor(QQ)(lambda integer: QQ(integer))
    changed = module.base_change(inclusion)
    generic = module.vector_space()

    assert changed in FramedFreeModules(QQ)
    assert changed.module_rank() == 2
    assert generic in VectorSpaces(QQ)
    assert generic.module_rank() == 2


def test_framed_free_module_morphisms_have_identity() -> None:
    module = ZZ.free_module(2)
    identity = module.Mor(module).identity()

    assert identity(module.module_generator(0)) == module.module_generator(0)
    assert identity * identity == identity
