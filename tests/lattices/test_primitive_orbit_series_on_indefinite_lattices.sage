r"""``primitive_orbit_series``'s ``constant`` term agrees with the line-orbit call on the same lattice.

``L_d = U ⊕ U ⊕ ⟨-2d⟩`` has rank five and signature ``(2, 3)``.  On an indefinite
lattice the series has one meaningful term: ``constant``, the number of
``Γ``-orbits of primitive isotropic lines.  This module asserts that term against
the same group's own orbit call rather than against a number written here, and
that the bounded terms are empty.

No expected count appears in this file.  A printed count, a docstring or an issue
is not an oracle: the expected value of a known-answer test is a
lattice-database card value named by tag and certified by citation or
computation, and the five ``L_d`` cards do not exist yet.  What is asserted here
holds whatever the count turns out to be — the series and the orbit call are two
routes to one number, and they must agree on every lattice and every group:

* ``constant`` equals ``isotropic_orbit_representatives(1).cardinality()`` for
  the same subgroup of ``O(L)``;
* ``z`` and ``w`` are empty, because no positive or negative norm is bounded on
  an indefinite lattice and the bounded fibre is infinite.
"""

from sage_extensions.all import *  # noqa: F401,F403

_LATTICES = (1, 2, 4, 9, 36)


def _lattice(d):
    r"""``U ⊕ U ⊕ ⟨-2d⟩``, rank five and signature ``(2, 3)``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2 * ZZ(d)]])


def test_the_constant_term_agrees_with_the_line_orbit_call() -> None:
    r"""Two routes to one count, on every ``L_d`` and every subgroup of ``O(L)``."""
    for d in _LATTICES:
        lattice = _lattice(d)
        series = lattice.primitive_orbit_series()
        stable = lattice.stable_orthogonal_group()
        plus = lattice.O_plus()
        subgroups = {
            "O": lattice.Aut(),
            "Otilde": stable,
            "Otilde+": stable.intersection(plus),
        }
        for group, subgroup in subgroups.items():
            assert series[group]["constant"] == subgroup.isotropic_orbit_representatives(1).cardinality()


def test_the_series_bounds_nothing_on_an_indefinite_lattice() -> None:
    r"""``z`` and ``w`` empty: a bounded fibre is infinite here, so only the constant term exists."""
    series = _lattice(9).primitive_orbit_series()
    for group in ("O", "Otilde", "Otilde+"):
        assert series[group]["z"] == []
        assert series[group]["w"] == []
