r"""The singleton identity family is a Zariski cover of every scheme."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_cover_of_the_projective_line() -> None:
    line = ProjectiveSpaces(QQ)(1)
    coverage = zariski_coverage(line)
    cover = coverage.an_object()

    assert cover in coverage
    assert coverage.site_category().base_object() is line
    assert cover.target().arrow() == line.categorical_identity_morphism()
