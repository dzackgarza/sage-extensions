r"""Absolute Galois groups of number fields are not finitely generated as abstract groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_absolute_galois_groups_of_q_and_q_root_five_have_the_cardinality_of_the_continuum() -> None:
    r"""An infinite profinite group with a countable basis of open subgroups has cardinality $2^{\aleph_0}$.

    So $G_{\mathbb{Q}}$ and $G_{\mathbb{Q}(\sqrt5)}$ are uncountable, hence not
    finitely generated as abstract groups; they surject onto $(\mathbb{Z}/2)^r$
    for every $r$ through multiquadratic extensions.  Source: Ribes–Zalesskii,
    *Profinite Groups*, Prop. 2.3.1.
    """
    for field in (QQ, QuadraticField(5, "a")):
        group = field.absolute_galois_group()

        assert group.cardinality() == continuum
        assert not group.is_finitely_generated()
