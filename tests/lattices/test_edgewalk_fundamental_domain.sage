r"""The edgewalk of the pinned port, through the owning public call.

`sage-indefinite-port` is paused at `991b88b0`, and its entry point is
`sage_indefinite_port.indefinite.edgewalk.edgewalk_fundamental_domain(lattice)`:
one lattice, no start vertex, no root-norm filter, no termination switch, and no
isometry route.  ``allcock_edgewalk`` on a hyperbolic lattice is the owning public
call for that walk (#344); the options an earlier revision of it advertised --
``option_norms="K3"``, ``initial_vertex``, ``early_termination`` and
``edgewalk_isometry`` -- have no engine in the pinned port, are not part of the
API, and are not tested here.  What is tested is what the walk decides.

U+<2n> are in Nikulin's rank-three classification: U+<46> is non-reflective.  In
U+<4> the vector x of norm 4 pairs evenly with L, so it is a wall of the full
walk: the walk is over every root, and that is the invariant the first test
states.
"""

from sage_extensions.all import *


def _hyperbolic_plus(square):
    summand = Lattices(ZZ)("A1").twist(-square // 2)
    return HyperbolicLattices(ZZ)(Lattices(ZZ)("U") + summand)


def test_the_walk_is_over_every_root_so_the_norm_four_wall_is_one():
    r"""In ``U + <4>`` the walk returns the norm-four wall beside the norm-two ones.

    The vector ``x`` of norm 4 pairs evenly with the lattice — ``b(x, L)`` is even —
    so a reflection in it is an isometry and its hyperplane is a wall of the full
    walk.  A walk restricted to the norm-two roots would not return it, and no such
    restriction is asked for here.
    """
    lattice = _hyperbolic_plus(4)
    x = tuple(lattice.module_generators())[2]
    assert lattice.q(x) == 4

    walls = tuple(lattice.allcock_edgewalk().simple_roots())

    assert x in walls or -x in walls
    assert sorted({int(root.q()) for root in walls}) == [2, 4]


def test_the_walk_certifies_the_reflectivity_of_the_chamber_it_finds():
    r"""``U + <2>`` is reflective, and the certificate comes with a nonempty chamber.

    The report's ``reason_non_reflective`` is ``None`` for a reflective verdict,
    which the pinned port records by not setting it; the simple roots it returns
    are roots of the lattice, of the norm-two kind this one has.
    """
    lattice = _hyperbolic_plus(2)
    report = lattice.allcock_edgewalk()

    assert report.is_reflective() is True
    assert report.reason_non_reflective() is None
    assert report.vertices().cardinality() > 0
    assert all(lattice.q(root) == 2 for root in report.simple_roots())


def test_a_non_reflective_lattice_is_reported_and_no_reason_is_recorded():
    r"""``U + <46>`` is non-reflective: the walk stops without a certificate.

    The pinned port reports the verdict and the vertices it enumerated, and records
    no reason string, so ``reason_non_reflective`` is ``None`` on this side too —
    asserted as the engine's behaviour, not as a claim that nothing stopped it.
    """
    lattice = _hyperbolic_plus(46)
    report = lattice.allcock_edgewalk()

    assert report.is_reflective() is False
    assert report.reason_non_reflective() is None
    assert report.vertices().cardinality() > 0
