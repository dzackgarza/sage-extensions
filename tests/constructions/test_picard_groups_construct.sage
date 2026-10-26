r"""A represented rank-three free module supplies a small Picard-group specimen."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rank_three_picard_group_specimen() -> None:
    free = ZZ.free_module(Set(("p", "q", "r")))
    picard = PicardGroups()(free)

    assert picard in PicardGroups()
    assert picard.module_rank() == 3
