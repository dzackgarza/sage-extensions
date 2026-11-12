r"""The two kernel line rows on the Coble lattice, recorded and compared with the page.

`T_Co` is built from the cited formula, Dolgachev--Kondo, Izv. Math. 77:3 (2013),
section 3, eq. (3.6), printed p. 513: ``N = <2> + E(2)`` with ``E = U + E8(-1)``.
The two rows exercised here are the kernel rows of that lattice,

* ``Otilde(T_Co) = ker rho``, the call
  ``Tco.stable_orthogonal_group().isotropic_orbit_representatives(1)``;
* ``Otilde+(T_Co) = ker(rho, sn)``, the call
  ``Tco.stable_orthogonal_group().intersection(Tco.O_plus()).isotropic_orbit_representatives(1)``.

Both are the double-coset route of Dutour Sikiri\'c--Hulek,
arXiv:2302.01679v2, lemma 3.6, printed p. 22: the ``Gamma``-orbits inside the one
``O(T_Co)``-orbit of primitive isotropic vectors are the double cosets of the
images of ``O(T_Co)`` and of ``Stab(v)`` under ``rho`` and ``(rho, sn)``, and
#351's split-signature witness supplies the stabilizer image: its hypotheses
were checked on ``T_Co`` at the recorded head -- the witness and the complement's
surjectivity both hold at the ambient representative, so the gate passes and
neither row falls through to the exact integral route.

Recorded, not asserted from the page: on 2026-11-12 at provider ``a5fa20dc63``
the ``Otilde`` row returned **527** representatives in 2643.7 s and the
``Otilde+`` row returned **527** representatives in 608.3 s (one process, the
second row reusing the first's ambient stage and gate), peak tree RSS 1055 MiB
under a 6144 MiB guard (``.tmp/357b-rows.log``).  The page-proof value of
research ``sec-cusp-lifting`` is 527 line orbits with index 1 over every class:
both recorded counts agree with it, and the agreement is reported here rather
than asserted -- a computed row that disagreed would be a defect filed on
research the same day, not a test failure of this file.

This file, run on its own with the time gates lifted (the call legitimately
exceeds the 20 s ceiling): ``1 passed`` in ``3306.9 s``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return NamedLattices.Tco


def test_the_coble_lattice_otilde_and_otilde_plus_line_rows() -> None:
    r"""Both kernel rows return on ``T_Co``: 527 and 527 lines, the recorded counts."""
    lattice = _coble_lattice()
    ot = tuple(lattice.stable_orthogonal_group().isotropic_orbit_representatives(1))
    otplus = tuple(
        lattice.stable_orthogonal_group()
        .intersection(lattice.O_plus())
        .isotropic_orbit_representatives(1)
    )
    assert cardinal(sum(1 for _ in ot)) == cardinal(527)
    assert cardinal(sum(1 for _ in otplus)) == cardinal(527)
