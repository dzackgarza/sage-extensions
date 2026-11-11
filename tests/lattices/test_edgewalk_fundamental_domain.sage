r"""The edgewalk's verdict on card 0026's lattice, read by tag.

`sage-indefinite-port` is paused at `991b88b0`, and its entry point is
`sage_indefinite_port.indefinite.edgewalk.edgewalk_fundamental_domain(lattice)`:
one lattice, no start vertex, no root-norm filter, no termination switch, and no
isometry route.  ``allcock_edgewalk`` on a hyperbolic lattice is the owning public
call for that walk (#344), and this module asks it one question on one lattice.

The expected verdict is not typed here.  Card `0026` of
`dzackgarza/lattice-database` is ``U + A1(-1)`` with Gram
`[[0,1,0],[1,0,0],[0,0,-2]]` and signature `(1, 2)`, and its ``hyperbolic`` block
states ``reflective: true`` with ``certifications`` stamping
``hyperbolic.reflective``: the value is the database's own decision, read by tag
through the digest, and the card's ``references`` names the source it cites for
it.  The lattice is built from that card's ``gram_tensor``, so the test's lattice
and the card's are the same matrix, and its `(1, n)` signature exercises the
wrapper's twist transport rather than the direct `(n, 1)` route.

Two lattices of the earlier version of this module are gone, and their absence is
deliberate: `U + <4>` and `U + <46>` have no card in `dzackgarza/lattice-database`
-- the catalogue's rank-three lattices of signature `(1, 2)` with `|det| = 4` are
eight odd forms and none is the even `U + <4>`, and it holds no such lattice of
`|det| = 46` at all -- and no source with a numbered statement and a printed page
was found for their reflectivity verdicts.  An expected verdict with no card and
no citation is not kept.
"""

from sage_extensions.all import *


def test_the_walk_returns_the_reflective_verdict_card_0026_certifies() -> None:
    r"""`U + A1(-1)` is reflective by its card, and the walk says so.

    The card's Gram is the lattice's Gram, so the comparison is about the
    database's lattice and not a lookalike; the verdict comes back through the
    `(1, n)` transport of the wrapper.
    """
    stated = card("hyperbolic_reflectivity", "0026")
    lattice = HyperbolicLattices(ZZ)(Lattices(ZZ)(stated["gram"]))
    basis = tuple(lattice.module_generators())

    assert [
        [int(lattice.b(left, right)) for right in basis] for left in basis
    ] == stated["gram"]
    assert [int(entry) for entry in lattice.signature()] == [
        int(entry) for entry in stated["signature"]
    ]
    assert lattice.allcock_edgewalk().is_reflective() is bool(stated["reflective"])
