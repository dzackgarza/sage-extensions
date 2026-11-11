r"""The setwise stabilizer's group generators carry discriminant images (#295).

The consumer is the plane half of #286: `stabilizer_generators` of the divided-class
plane call of #321 takes generators of $G_x$, and the natural source of them is
`Isom(L).stabilizer(P, action="setwise")`.  For that to be usable the stabilizer must
return isometries of $L$ **itself**, and `L.discriminant_representation()` must accept
them.

Two failures stood in the way, both measured on `7858c09d97`:

* `setwise_stabilizer` imported `setwise_transporter` from
  `sage_indefinite_port.indefinite.pairing_slices`, a module the pinned port does not
  ship, so the call raised `ModuleNotFoundError` before producing a generator
  (`.tmp/p295-probe1.log`);
* on the Enriques lattice the port's plane branch evaluates the group's identity, and
  the routing wrapper around `identity` ran `functools.update_wrapper`, whose
  `__doc__` copy runs `sageinspect.sage_getsourcelines` on a dynamically generated
  element class and raises `TypeError` (`.tmp/p295-probe7.log`).

Both are repaired, but the Enriques plane stabilizer is not asserted here: once the
metadata failure is out of the way the call enters the port's rank-two parabolic
computation, which did not return in 3000 s on `T_{\mathrm{En}}`
(`.tmp/p295-gate.log`).  That is the same wall #316 recorded at 1500 s, and it is
recorded in `TRAPS.md` rather than pinned as a test that cannot finish.

The numbers below are measured, not derived.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _coble_ambient():
    r"""$B = U \oplus U \oplus I_{0,7}$, the lattice whose double $B(2)$ is $T_{\mathrm{Co}}$."""
    negative_odd = [[-1 if row == column else 0 for column in range(7)] for row in range(7)]
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)(negative_odd)


def _cross_span_plane(lattice):
    r"""The span of the isotropic generators of the first and second $U$ summand."""
    basis_elements = list(lattice.module_generators())
    return lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])


def _setwise_generator_family(lattice, plane):
    r"""The selected group generators of the setwise stabilizer of ``plane``."""
    return lattice.Aut().stabilizer(plane, action="setwise").group_generators()


def test_every_setwise_stabilizer_generator_has_a_discriminant_image() -> None:
    r"""On $B = U \oplus U \oplus I_{0,7}$ and $P = \langle e_1, e_2\rangle$, all of them do.

    The stabilizer returns its generators as isometries of $B$ itself, and each one
    passes through $B.\mathrm{discriminant\_representation}()$.  $B$ is unimodular, so
    the discriminant group is trivial and the images generate the trivial group: the
    order returned is one.  That is the assertion, not a round number -- the form has
    no nonzero class for an isometry to move.
    """
    lattice = _coble_ambient()
    plane = _cross_span_plane(lattice)
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    assert lattice.determinant() == ZZ(-1)

    family = _setwise_generator_family(lattice, plane)
    assert family.cardinality() != cardinal(0)
    orthogonal = lattice.discriminant_group().orthogonal_group()
    rho = lattice.discriminant_representation()
    for element in family:
        assert rho(element) in orthogonal
    assert orthogonal.cardinality() == cardinal(1)


def test_the_divided_class_plane_call_takes_the_setwise_stabilizer_generators() -> None:
    r"""#321's supplied-generator closure, fed by the setwise stabilizer, on $U \oplus U(2)$.

    The two units connect here: the plane-orbit call needs $\rho(G_x)$, the sandwich
    closes it with generators of $G_x$, and the setwise stabilizer is where those
    generators come from.  The call returns the two plane orbits of $U \oplus U(2)$
    under $\widetilde{O}^+$, the same count its own stabilizer-generator test asserts.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])
    plane = _cross_span_plane(lattice)
    group = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    assert group.contains_character_kernel()

    family = _setwise_generator_family(lattice, plane)
    assert family.cardinality() != cardinal(0)

    orbits = group.isotropic_plane_orbits(
        (plane,), stabilizer_generators={0: tuple(family)}
    )

    assert orbits.cardinality() == cardinal(2)
