r"""Group algebras retain their group, basis inclusion, centre and regular representation.

For ``QQ[S3]`` the group inclusion is multiplicative, the centre has dimension
three (one basis vector per conjugacy class), Maschke gives semisimplicity, and
the left regular representation has dimension six.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_s3_group_algebra_retains_group_inclusion_center_and_regular_representation() -> None:
    group = Groups.S(3)
    algebra = QQ[group]
    inclusion = algebra.group_inclusion()
    regular = algebra.regular_representation()
    generator = group.group_generators()[0]

    assert algebra in GroupAlgebras(QQ)
    assert algebra.group() is group
    assert isinstance(algebra.one(), algebra.ElementType)
    assert inclusion(generator * generator) == inclusion(generator) * inclusion(generator)
    assert algebra.center().dimension() == 3
    assert regular.module_rank() == 6
    assert algebra.is_semisimple()


def test_group_algebra_maschke_boundary_and_augmentation() -> None:
    group = Groups.S(3)
    rational = QQ[group]
    modular = GF(3)[group]

    assert rational.augmentation()(rational(group.one())) == QQ.one()
    assert rational.is_semisimple()
    assert not modular.is_semisimple()
