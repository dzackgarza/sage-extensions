r"""A locally ringed space builds its trivial one-chart covering family."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_line_builds_its_identity_covering_family() -> None:
    line = AffineSpaces(QQ)(1)
    identity = line.categorical_identity_morphism()
    cover = line.covering_family(
        (line,),
        (identity,),
        {},
        ambient_chart_index=0,
    )

    assert cover.covered_object() is line
    assert cover.members().cardinality() == cardinal(1)
    assert cover.member(0) == identity
