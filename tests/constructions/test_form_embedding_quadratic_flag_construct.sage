r"""A lattice embedding records that its preserved datum is bilinear, not a separate quadratic form."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a1_into_a2_form_embedding_is_not_marked_quadratic() -> None:
    a1 = NamedLattices.A1
    a2 = NamedLattices.A2
    embedding = a1.Mono(a2)([a2.module_generator(0)])

    assert not embedding.is_quadratic()
