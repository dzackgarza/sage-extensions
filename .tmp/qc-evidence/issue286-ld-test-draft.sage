r"""The orbit splitting on small indefinite lattices, against counts derived by hand.

The tests here are the first indefinite ones whose answers are known independently
of the library: ``L_d = U + U + <-2d>`` has rank five and signature ``(2, 3)``, and
the number of primitive isotropic orbits can be written down from two theorems.

*Derivation.*  ``A_{L_d} = Z/2d``.  A primitive isotropic ``v`` has divisibility
``e`` dividing ``2d``, and ``v/e`` is an isotropic class of ``A_{L_d}`` of order
``e``; the class has ``q = v^2/(2e^2) = 0``, and the rank-one summand's
discriminant contributes ``-x^2/2d``, which forces ``e^2 | d``.  For each such
``e`` the isotropic classes of order ``e`` are the ``phi(e)`` primitive residues
``x`` modulo ``e``.  By the Eichler criterion (Gritsenko--Hulek--Sankaran,
*Abelianisation of orthogonal groups and the fundamental group of modular
varieties*, J. Algebra 322 (2009), Prop. 3.3: in a lattice containing
``U + U``, two primitive vectors of the same norm and the same class
``v/div(v)`` lie in one ``Otilde(L)``-orbit, with
``Otilde(L) <= SO^+(L)``) the ``Otilde``-orbits are in bijection with those
classes, so their number is ``sum_{e^2 | d} phi(e)``.  ``O(L)`` acts on a class
only through its order, so its orbits are one per ``e``, numbering
``#{e : e^2 | d}`` -- Scattone, *On the compactification of moduli spaces for
algebraic K3 surfaces*, Mem. AMS 374 (1987), for the 0-cusps of ``F_{2d}``.

The derivation was checked against the lattice before the test was written: the
isotropic classes of ``A_{L_d}`` by order are, for d = 1, 2, 4, 9, 36,
``{1: 1}``, ``{1: 1}``, ``{1: 1, 2: 1}``, ``{1: 1, 3: 2}`` and
``{1: 1, 2: 1, 3: 2, 6: 2}``, whose totals are ``1, 1, 2, 3, 6`` and whose orders
number ``1, 1, 2, 2, 4``.

``Otilde^+`` is ``Otilde(L) cap O^+(L)``, and since ``Otilde <= SO^+`` the two
counts coincide; both are asserted so that a disagreement shows which one moved.
"""

from sage_extensions.all import *  # noqa: F401,F403

_CASES = (
    (1, 1, 1),
    (2, 1, 1),
    (4, 2, 2),
    (9, 2, 3),
    (36, 4, 6),
)


def _lattice(d):
    r"""``U + U + <-2d>``, rank five and signature ``(2, 3)``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2 * ZZ(d)]])


def test_the_isotropic_class_orders_are_the_divisibility_condition() -> None:
    r"""``e^2 | d``, ``phi(e)`` classes of order ``e``, checked on the lattice itself."""
    for d, order_count, class_count in _CASES:
        discriminant = _lattice(d).discriminant_group()
        zero = discriminant.q(discriminant.zero())
        orders = {}
        for element in discriminant.elements():
            if discriminant.q(element) != zero:
                continue
            order = int(element.additive_order())
            orders[order] = orders.get(order, 0) + 1
        admissible = [e for e in range(1, 2 * d + 1) if (d % (e * e)) == 0]
        assert sorted(orders) == admissible
        assert sum(orders.values()) == class_count
        assert len(orders) == order_count


def test_the_primitive_isotropic_orbits_of_l_d_are_one_per_class() -> None:
    r"""``O(L_d)`` gives one orbit per admissible ``e``; ``Otilde`` and ``Otilde^+`` one per class."""
    for d, order_count, class_count in _CASES:
        lattice = _lattice(d)
        representatives = lattice.Aut().isotropic_orbit_representatives(1)
        assert representatives.cardinality() == order_count
        for line in representatives:
            vector = line.inclusion()(line.module_generator(0))
            assert vector.is_primitive() is True
            assert vector.q() == ZZ(0)

        stable = lattice.stable_orthogonal_group()
        assert stable.isotropic_orbit_representatives(1).cardinality() == class_count

        stable_plus = stable.intersection(lattice.O_plus())
        assert stable_plus.isotropic_orbit_representatives(1).cardinality() == class_count
