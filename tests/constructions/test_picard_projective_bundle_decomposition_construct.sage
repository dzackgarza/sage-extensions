r"""Pic(P^n_S) splits as Pic(S) plus the hyperplane class when the base Picard group is supplied."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_line_picard_group_retains_base_and_hyperplane_summands() -> None:
    line = ProjectiveSpaces(ZZ)(1)
    base = line.base_scheme()
    base_picard = PicardGroups().trivial(base)
    picard = PicardGroups().projective_bundle(line, base_picard)

    assert picard.picard_scheme() is line
    assert picard.projective_base_picard_group() is base_picard
    assert picard.projective_hyperplane_factor().module_rank() == 1
    assert picard.base_picard_inclusion().domain() is base_picard
    assert picard.base_picard_inclusion().codomain() is picard
    assert picard.hyperplane_class() != picard.zero()
