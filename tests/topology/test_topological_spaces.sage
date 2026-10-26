r"""Continuity between the indiscrete and the Sierpinski topologies on two points.

Derivation: on `\{0, 1\}` the Sierpinski topology has opens `\emptyset, \{1\},
\{0, 1\}` and the indiscrete topology has opens `\emptyset, \{0, 1\}`.  Each space
is its own set, with a point at each point of `\{0, 1\}`.  The map that sends the
point of the indiscrete space at `s` to the point of the Sierpinski space at `s`
pulls the open `\{1\}` back to `\{1\}`, which is not open, so it is not continuous;
the map in the other direction pulls every open back to an open, so it is
continuous.
"""

from sage_extensions.all import *


def test_the_identity_on_points_is_continuous_from_sierpinski_to_indiscrete_but_not_back() -> None:
    points = Sets.Δ[1]
    spaces = TopologicalSpaces()
    indiscrete = spaces(points, ((), points))
    sierpinski = spaces(points, ((), (points(1),), points))
    forward = Sets().Mor(sierpinski, indiscrete)(
        lambda point: indiscrete(0) if point == sierpinski(0) else indiscrete(1)
    )
    backward = Sets().Mor(indiscrete, sierpinski)(
        lambda point: sierpinski(0) if point == indiscrete(0) else sierpinski(1)
    )

    assert forward in spaces.Mor(sierpinski, indiscrete)
    assert backward not in spaces.Mor(indiscrete, sierpinski)
    assert sierpinski.open_subsets().cardinality() == 3
