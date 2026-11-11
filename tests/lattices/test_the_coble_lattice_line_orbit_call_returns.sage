r"""The `T_Co` line-orbit call is a single public call, and it does not list a module's elements.

`T_Co` is built from the cited formula, Dolgachev--Kondo, Izv. Math. 77:3 (2013),
section 3, eq. (3.6), printed p. 513: `N = <2> + E(2)` with `E = U + E8(-1)`.

The call exercised here is `L.Aut().isotropic_orbit_representatives(1)` on that
lattice, the consumer of sage-extensions#286 and the subject of sage-extensions#322.
Its line classes reach the port's marked reduction, which asks this library for the
integral members of one marked-line lift locus; the residue locus of that locus
(`isotropic_lifts.IsotropicReductionLiftTorsors.integral_parameter_classes`) must be
computed from the parameter module's structure, not by listing that module's elements.

This file asks for the line orbit only, and it asserts the one thing the paper proof
fixes without a computation: that the call returns and that every returned
representative is a primitive isotropic line of `T_Co`.  No count is asserted: the
`O(T_Co)` and `Õ⁺(T_Co)` counts of `T_Co` are lattice-database card values
(lattice-database#7) and are not available yet, so there is nothing to pin.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)


def _is_primitive_isotropic_line(lattice, subobject) -> bool:
    r"""Whether ``subobject`` is a rank-one primitive totally isotropic subobject of ``lattice``."""
    if subobject.module_rank() != cardinal(1):
        return False
    if subobject.is_primitive() is not True:
        return False
    for label in subobject.module_generating_set():
        vector = subobject.inclusion()(subobject.module_generator(label))
        if lattice.q(vector) != lattice.base_ring().zero():
            return False
        if lattice.b(vector, vector) != lattice.base_ring().zero():
            return False
    return True


def test_the_coble_lattice_line_orbit_call_returns_primitive_isotropic_lines() -> None:
    r"""``L.Aut().isotropic_orbit_representatives(1)`` returns on ``T_Co``."""
    lattice = _coble_lattice()

    lines = lattice.Aut().isotropic_orbit_representatives(1)

    assert lines.is_empty() is False
    assert all(
        _is_primitive_isotropic_line(lattice, representative) for representative in lines
    )
