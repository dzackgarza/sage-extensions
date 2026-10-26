r"""Finite noncrystallographic root lattices over their exact coefficient order.

The ``H3`` root system is defined over the ring of integers of
``QQ(sqrt(5))``.  It has rank three, thirty roots, Coxeter number ten and full
reflection group of order 120; its three chosen simple roots generate that
reflection group.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _h3_root_lattice():
    coefficient_order = QuadraticField(5, "s").ring_of_integers()
    return coefficient_order, NoncrystallographicRootLattices(coefficient_order)(["H", 3])


def test_h3_retains_its_exact_coefficient_order_and_root_system() -> None:
    coefficient_order, lattice = _h3_root_lattice()
    roots = lattice.roots()
    simple = lattice.simple_roots()

    assert lattice in NoncrystallographicRootLattices(coefficient_order)
    assert lattice in Lattices(coefficient_order)
    assert lattice.base_ring() is coefficient_order
    assert lattice.module_rank() == 3
    assert roots.cardinality() == cardinal(30)
    assert simple.cardinality() == cardinal(3)
    assert isinstance(simple[0], lattice.ElementType)
    assert all(root in roots for root in simple)


def test_h3_has_coxeter_number_ten_and_three_simple_reflections() -> None:
    _coefficient_order, lattice = _h3_root_lattice()
    coxeter_type = lattice.coxeter_type()
    reflections = lattice.simple_reflections()

    assert lattice.coxeter_number() == 10
    assert reflections.cardinality() == cardinal(3)
    assert Groups.Coxeter(coxeter_type).order() == 120


def test_h3_root_lattice_morphisms_have_identity() -> None:
    _coefficient_order, lattice = _h3_root_lattice()
    identity = lattice.Mor(lattice).identity()

    assert identity(lattice.module_generator(0)) == lattice.module_generator(0)
    assert identity * identity == identity
