r"""A represented rank-three free module supplies a small divisor-class-group specimen."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_three_class_group_specimen() -> None:
    free = ZZ.free_module(Set(("p", "q", "r")))
    classes = ClassGroups()(free)

    assert classes in ClassGroups()
    assert classes.module_rank() == 3
