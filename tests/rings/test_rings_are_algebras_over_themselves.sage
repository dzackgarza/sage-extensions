r"""The augmentation of a group algebra over a number field."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_augmentation_ideal_of_the_symmetric_group_algebra_has_codimension_one() -> None:
    r"""For ``K[G]`` with ``|G| = n``, the augmentation ``sum a_g g |-> sum a_g`` is a
    surjective ``K``-algebra morphism onto ``K`` whose kernel, the augmentation
    ideal, is spanned by the ``g - 1`` and has dimension ``n - 1``
    (Serre, *Linear Representations of Finite Groups*, 6.2).  For ``S_3`` over
    ``QQ(i)``: dimension 6 and augmentation ideal of dimension 5."""
    field = QuadraticField(-1, "i")
    group = Groups.S(3)
    group_algebra = Algebras(field)(group)
    augmentation = group_algebra.augmentation()
    g = group_algebra(next(iter(group.group_generators())))
    one = group_algebra.one()

    assert group_algebra.module_rank() == 6
    assert augmentation(g + 3 * one) == field(4)
    assert augmentation(g - one) == field.zero()
    assert augmentation(g * g) == field.one()
    assert augmentation.kernel().module_rank() == 5
    assert not group_algebra.is_commutative()
