r"""A pullback's components are read in the bundle's frame, so the law that relates two charts is the codomain's chart change, not the derivative of the map.

A section of $f^*E$ over a chart $W$ of the base takes its values in the fibre at $f(q)$,
and its tuple is read in the frame of a chart $V$ of the codomain that $W$ is represented
in (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  Two base charts $W_s, W_t$
carry two such frames, $V_s$ and $V_t$, and the tuples are related by the codomain's
coordinate change evaluated at the image point:

$$a_t(x) = J_{V_s \to V_t}\big(T_s(x)\big)\,a_s(x),$$

with no derivative of $f$ in it.  For $f = \mathrm{id}$ the codomain's change is the base's
own, which is why the identity-map and reflection specimens pass either way; for a map
between different manifolds the two laws differ, and the tuple's length is the bundle's
**rank**, not the base's dimension.

The specimen is $S^1 \to S^2$, $x \mapsto (x, 0)$ in the north chart, stated on both charts
of the circle: a rank-two bundle over a one-dimensional base.
"""

import pytest

from sage_extensions.all import *


def _the_pullback_over_the_circle():
    r"""$S^1$, its two charts, the map $x \mapsto (x, 0)$ into the sphere's north chart, and $f^*TS^2$."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    sphere = SmoothManifolds().sphere(2)
    x = north.coordinate(0)
    y = south.coordinate(0)
    mapping = circle.Mor(sphere)(
        {
            ("U_N", "U_N"): (x, north.function_ring().zero()),
            ("U_S", "U_N"): (
                south.section_ratio(south.function_ring().one(), y),
                south.function_ring().zero(),
            ),
        }
    )
    return circle, north, south, sphere, sphere.tangent_bundle().pullback_along(mapping)


def test_the_pullback_has_the_bundle_s_rank_over_a_one_dimensional_base() -> None:
    r"""$f^*TS^2$ is rank two over the circle, whose dimension is one."""
    circle, _north, _south, _sphere, pulled = _the_pullback_over_the_circle()

    assert pulled.base_manifold() is circle
    assert pulled.rank() == 2
    assert circle.dimension() == 1


def test_a_family_that_agrees_in_both_components_is_a_section() -> None:
    r"""$(x, 1)$ on both charts is one section: the first component is the base coordinate the law fixes, the second is constant.

    The image chart is the sphere's north chart on both base charts, so the two frames are
    the same frame and the law asks the tuples to agree as functions on the base: the first
    component is the image's own first coordinate, $x$ on the north chart and $1/y$ on the
    south one, and the second is the constant $1$.
    """
    circle, north, south, _sphere, pulled = _the_pullback_over_the_circle()
    south_ring = south.function_ring()

    section = pulled.sections().section(
        {
            "U_N": (north.coordinate(0), north.function_ring().one()),
            "U_S": (south.section_ratio(south_ring.one(), south.coordinate(0)), south_ring.one()),
        }
    )

    at = circle.point((2,), "U_N")
    assert section.components()["U_N"][1](at) == RR(1)


def test_a_disagreement_in_the_second_component_is_refused() -> None:
    r"""Two tuples whose second components are $1$ and $x$ are not one section, and the check reads that component.

    The first component is the image's first coordinate on both charts, so it agrees; the
    second is $1$ on the north chart and $y$ on the south one, which are different
    functions, so the family is not a section.  A check that read only as many rows as the
    base has dimensions would compare component zero alone and accept it.
    """
    circle, north, south, _sphere, pulled = _the_pullback_over_the_circle()
    south_ring = south.function_ring()

    with pytest.raises(AssertionError):
        pulled.sections().section(
            {
                "U_N": (north.coordinate(0), north.function_ring().one()),
                "U_S": (
                    south.section_ratio(south_ring.one(), south.coordinate(0)),
                    south.coordinate(0),
                ),
            }
        )
