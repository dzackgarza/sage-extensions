r"""``primitive_orbit_series`` on ``L_d``: its ``constant`` term is the primitive isotropic line count.

``L_d = U ⊕ U ⊕ ⟨-2d⟩`` has rank five and signature ``(2, 3)``.  The series of
orbits attached to it has one meaningful term on an indefinite lattice: the
``constant`` term, which ``lattice-database`` reads as ``c_Γ(0)``.  This module
asserts that term for the three groups the derivation pins -- ``O``, ``Otilde``
and ``Otilde+`` -- against the counts derived and verified in
``tests/lattices/test_isotropic_line_orbits_of_small_indefinite_lattices.sage``
(1, 1, 2, 2, 4 for each of them), and that the bounded terms are empty:

* ``O`` and ``Otilde`` contain ``-id`` or not, so a vector and its negative are
  one point or two, which is the distinction between counting vectors and
  counting lines; ``z`` and ``w`` are empty because no positive or negative norm
  is bounded on an indefinite lattice.
* ``primitive_orbit_series`` documents its ``constant`` term as the number of
  ``Γ``-orbits of primitive isotropic **lines** -- rank-one isotropic
  sublattices -- because that is the count a Baily-Borel cusp is made of.  The
  owner contract test lives here rather than in the lattice-database card: the
  card's field text is that repository's work this cycle.
"""

from sage_extensions.all import *  # noqa: F401,F403

_CASES = (
    (1, 1),
    (2, 1),
    (4, 2),
    (9, 2),
    (36, 4),
)


def _lattice(d):
    r"""``U ⊕ U ⊕ ⟨-2d⟩``, rank five and signature ``(2, 3)``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2 * ZZ(d)]])


def test_the_constant_term_of_the_series_is_the_primitive_isotropic_line_count() -> None:
    r"""``O``, ``Otilde`` and ``Otilde+`` on the five lattices: the derived line counts."""
    for d, derived in _CASES:
        series = _lattice(d).primitive_orbit_series()
        for group in ("O", "Otilde", "Otilde+"):
            assert series[group]["constant"] == derived


def test_the_series_bounds_nothing_on_an_indefinite_lattice() -> None:
    r"""``z`` and ``w`` empty: a bounded fibre is infinite here, so only the constant term exists."""
    series = _lattice(9).primitive_orbit_series()
    for group in ("O", "Otilde", "Otilde+"):
        assert series[group]["z"] == []
        assert series[group]["w"] == []
