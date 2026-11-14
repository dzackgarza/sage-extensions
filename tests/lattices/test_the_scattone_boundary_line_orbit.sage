r"""The Scattone boundary line count, compared with the card's own row.

``6JRX`` and ``6JRY`` each state, on the line row and with Scattone's citation, *one*
primitive isotropic line orbit under $O^+(L)$ (§6, p. 94: the Baily–Borel compactification of
$D_k/O_-(L_k)$ adds one zero-dimensional component, and $\Gamma_k$'s is one by Theorem 4.0.1,
p. 55).  The row is the card's; the count asserted here comes from the public orbit call, and
the card is what the call is compared against.

Harness: the classification is the indefinite port's
``sage_indefinite_port.indefinite.marked_lattices.primitive_marking_classes``, reached from
this repository's ``isotropic_orbit_representatives``
(``categories/lattice_morphisms.py:4085`` and ``categories/isotropic_orbits.py:933``).  It
must be measured with the port under development bound at ``/repos/sage-indefinite-port``
(``991b88b0``); the image also ships a stale copy at that path, so the run that produced these
numbers is ``.scratch/sage-python-port`` and it printed the imported provenance.

Measured: one call, $\Lambda_2$ under $O$, `1 orbit in 115.06 s`.  That is the known-family
comparison this batch owes, and it is six times the declared 20 s call ceiling, so the test
below cannot pass the gate as written; the ceiling is not raised for it.  The record of
that cost is ``results/issue294-batch.md`` and issue #306, and the run is kept because the
assertion is the deliverable — a count derived from the call, not from the docstring.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _period_lattice(k):
    r"""$U \oplus U \oplus E_8(-1) \oplus E_8(-1) \oplus \langle -2k\rangle$, from the cards."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


def test_the_degree_two_card_states_one_primitive_isotropic_line_orbit_under_o_plus() -> None:
    r"""``6JRX``'s line row: one orbit, under the group the row names ($O^+$).

    The row is the card's, keyed ``O+`` → ``constant: 1`` (§6, p. 94 with §1, p. 3); the
    expected value asserted below is that certified row, read from the card, not derived
    here.  The comparison therefore uses that subgroup, not the whole orthogonal group: a
    single $O$-orbit is one $O^+$-orbit only when some element *outside* $O^+$ lies in its
    stabilizer, and in signature $(2,19)$ that is not something $-\mathrm{id}$ settles --
    $-\mathrm{id}$ fixes an isotropic line and would split nothing, but whether it lies in
    $O^+$ here is exactly the convention that must not be assumed.  An $O$-count is a valid
    run result and is not this row's comparison.
    """
    lattice = _period_lattice(1)
    lines = lattice.O_plus().isotropic_orbit_representatives(1)

    assert lines.cardinality() == cardinal(1)
    for line in lines:
        vector = line.inclusion()(line.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True
