r"""The automorphism group of S3 has order six and identity the identity map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_automorphisms_of_symmetric_three_form_a_group() -> None:
    group = Groups.S(3)
    automorphisms = group.Aut()
    identity = automorphisms.one()
    element = group.group_generators()[0]

    assert automorphisms in Groups()
    assert automorphisms.order() == 6
    assert identity(element) == element
    assert identity * identity == identity

