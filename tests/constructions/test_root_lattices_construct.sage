r"""ADE root lattices with their chosen simple-root systems.

For ``A2`` the selected simple system has two roots, Coxeter number three and
highest root of height two.  The two simple reflections generate the Weyl group
of order six, while root signs and coroots are intrinsic element operations.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _a2_root_lattice():
    return Lattices(ZZ)("A2")


def test_a2_retains_its_simple_system_cartan_type_and_fundamental_weights() -> None:
    lattice = _a2_root_lattice()
    simple = lattice.simple_roots()
    reflections = lattice.simple_reflections()
    weights = lattice.fundamental_weights()

    assert lattice in RootLattices()
    assert simple.cardinality() == cardinal(2)
    assert reflections.cardinality() == cardinal(2)
    assert weights.cardinality() == cardinal(2)
    assert lattice.cartan_type().module_rank() == 2
    assert lattice.coxeter_number() == 3
    assert isinstance(simple[0], lattice.ElementType)


def test_a2_highest_root_has_height_two_and_is_positive() -> None:
    lattice = _a2_root_lattice()
    highest = lattice.highest_root()

    assert highest in lattice.roots()
    assert highest.height() == 2
    assert highest.is_positive_root()
    assert not highest.is_negative_root()


def test_a2_simple_root_sign_height_and_coroot_are_the_standard_ones() -> None:
    lattice = _a2_root_lattice()
    root = lattice.simple_roots()[0]
    negative = -root
    coroot = root.coroot()

    assert root.height() == 1
    assert root.is_positive_root()
    assert not root.is_negative_root()
    assert negative.height() == -1
    assert negative.is_negative_root()
    assert not negative.is_positive_root()
    assert lattice.b(root, coroot) == 2


def test_a2_simple_reflections_generate_the_weyl_group_of_order_six() -> None:
    lattice = _a2_root_lattice()

    assert lattice.weyl_group().order() == 6
    assert all(reflection in lattice.O() for reflection in lattice.simple_reflections())


def test_root_lattice_morphisms_have_identity() -> None:
    lattice = _a2_root_lattice()
    identity = lattice.Mor(lattice).identity()

    assert identity(lattice.simple_roots()[0]) == lattice.simple_roots()[0]
    assert identity * identity == identity
