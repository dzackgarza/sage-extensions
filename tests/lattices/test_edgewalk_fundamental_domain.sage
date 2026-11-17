r"""The edgewalk's verdict on card 0026's lattice, read by tag.

``allcock_edgewalk`` on a hyperbolic lattice is the owning public call for
the port's walk. Its options and prescribed data use the lattice's own
sign convention.

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


def test_prescribed_k3_vertices_and_isometry_use_the_negative_sign_lattice():
    r"""Twisting U+A1(-1) preserves rays and reverses its wall normals.

    Its K3 walls have square -2. Supplying a reported vertex, either alone
    or with its wall normals, starts the walk at that same ray. The
    edgewalk isometry of the lattice to itself preserves its negative-sign
    form and has an inverse on every basis vector.
    """
    stated = card("hyperbolic_reflectivity", "0026")
    lattice = HyperbolicLattices(ZZ)(Lattices(ZZ)(stated["gram"]))
    report = lattice.allcock_edgewalk(option_norms="K3")
    assert report.is_reflective()
    assert tuple(report.simple_roots())
    assert all(root.q() == -2 for root in report.simple_roots())
    cone = next(iter(report.vertices()))
    (generator,) = tuple(cone.primitive_rays())
    for initial in (generator, (generator, tuple(cone.wall_roots()))):
        prescribed = lattice.allcock_edgewalk(option_norms="K3", initial_vertex=initial)
        assert prescribed.is_reflective()
        first = next(iter(prescribed.vertices()))
        assert tuple(first.primitive_rays()) == (generator,)
        assert all(root.q() == -2 for root in prescribed.simple_roots())
    witness = lattice.edgewalk_isometry(lattice)
    assert witness is not None
    basis = tuple(lattice.module_generators())
    for left in basis:
        assert witness.inverse()(witness(left)) == left
        for right in basis:
            assert lattice.b(witness(left), witness(right)) == lattice.b(left, right)
