r"""The diagonal sign action on a product of projective lines is a C2 action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_diagonal_sign_action_on_two_projective_lines_is_an_involution() -> None:
    line = ProjectiveSpaces(QQ)(1)
    surface = Schemes(QQ).product((line, line))
    action = surface.c2_diagonal_sign_action()
    group = action.acting_group()
    generator = group.group_generators()[0]
    involution = action.action_of(generator)

    assert group.order() == 2
    assert involution * involution == surface.categorical_identity_morphism()
