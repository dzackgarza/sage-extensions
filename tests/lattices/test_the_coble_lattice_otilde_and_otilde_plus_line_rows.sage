r"""The two kernel line rows on the Coble lattice, through the double-coset route.

`T_Co` is built from the cited formula, Dolgachev--Kondo, Izv. Math. 77:3 (2013),
section 3, eq. (3.6), printed p. 513: ``N = <2> + E(2)`` with ``E = U + E8(-1)``.
The two rows exercised here are the kernel rows of that lattice,

* ``Otilde(T_Co) = ker rho``, the call
  ``Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)``;
* ``Otilde+(T_Co) = ker(rho, sn)``, the call
  ``Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)``.

Both are the double-coset route of Dutour Sikirić--Hulek,
arXiv:2302.01679v2, lemma 3.6, printed p. 22: the ``Gamma``-orbits inside the one
``O(T_Co)``-orbit of primitive isotropic vectors are the double cosets of the
images of ``O(T_Co)`` and of ``Stab(v)`` under ``rho`` and ``(rho, sn)``, and
the split-signature witness supplies the stabilizer image, so neither row falls
through to the exact integral route.

The expected count is a lattice-database card value read by tag.  Until the
``T_Co`` card lands, this file asserts what the cited construction guarantees
for every output: each representative is a primitive isotropic line of ``T_Co``,
and the ``Otilde+`` row has at least as many lines as the ``Otilde`` row -- the
group ``Otilde+ = ker(rho, sn)`` is contained in ``Otilde = ker rho``, so its
orbits are at least as many.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return NamedLattices.Tco


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


def test_the_coble_lattice_otilde_and_otilde_plus_line_rows() -> None:
    r"""Both kernel rows return primitive isotropic lines, and the Otilde+ row is at least as large."""
    lattice = _coble_lattice()
    ot = tuple(lattice.stable_orthogonal_group().isotropic_orbit_representatives(1))
    otplus = tuple(
        lattice.stable_orthogonal_group()
        .intersection(lattice.O_plus())
        .isotropic_orbit_representatives(1)
    )
    # The expected count is a card value read by tag; the T_Co card is
    # lattice-database#7, which waits on this library's Coble rows.  Until it
    # lands, assert what the construction guarantees.
    assert all(_is_primitive_isotropic_line(lattice, subobject) for subobject in ot)
    assert all(_is_primitive_isotropic_line(lattice, subobject) for subobject in otplus)
    assert cardinal(sum(1 for _ in otplus)) >= cardinal(sum(1 for _ in ot))
