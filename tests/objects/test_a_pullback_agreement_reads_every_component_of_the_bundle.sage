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

The specimen is the equatorial embedding $S^1 \to S^2$, with coordinate
representations $x \mapsto (x,0)$ in the north charts and $y \mapsto (y,0)$
in the south charts. On the overlap $y=1/x$ and the target inversion
$I(z)=z/|z|^2$ sends $(x,0)$ to $(1/x,0)$, so these are one global smooth map,
including both poles. Its derivative of the target coordinate change is
$dI_{(x,0)}=\operatorname{diag}(-1/x^2,1/x^2)$. Consequently the section with
north coefficients $(x,1)$ has south coefficients $(-y,y^2)$, smooth on the
whole south chart. The bundle has rank two over a one-dimensional base.
"""

import pytest

from sage_extensions.all import *


def _the_pullback_over_the_circle():
    r"""The equatorial embedding, expressed in both pairs of stereographic charts."""
    circle = SmoothManifolds().sphere(1)
    north = circle.atlas()["U_N"]
    south = circle.atlas()["U_S"]
    sphere = SmoothManifolds().sphere(2)
    x = north.coordinate(0)
    y = south.coordinate(0)
    mapping = circle.Mor(sphere)(
        {
            ("U_N", "U_N"): (x, north.function_ring().zero()),
            ("U_S", "U_S"): (y, south.function_ring().zero()),
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
    r"""The north tuple $(x,1)$ and south tuple $(-y,y^2)$ agree by the target Jacobian."""
    circle, north, south, _sphere, pulled = _the_pullback_over_the_circle()
    y = south.coordinate(0)

    section = pulled.sections().section(
        {
            "U_N": (north.coordinate(0), north.function_ring().one()),
            "U_S": (-y, y**2),
        }
    )

    at = circle.point((2,), "U_N")
    assert section.components()["U_N"][1](at) == RR(1)
    assert tuple(section.components_at(at, "U_N")) == (RR(2), RR(1))
    assert tuple(section.components_at(at, "U_S")) == (-RR(1)/2, RR(1)/4)
    assert tuple(section.components_at(circle.point((0,), "U_N"), "U_N")) == (RR(0), RR(1))
    assert tuple(section.components_at(circle.point((0,), "U_S"), "U_S")) == (RR(0), RR(0))


def test_a_disagreement_in_the_second_component_is_refused() -> None:
    r"""The first component transforms correctly, but $y$ is not $y^2$ on the overlap.

    At $y=1/2$ the transported second coefficient is $1/4$, not $1/2$.
    Checking only as many rows as the base dimension would miss the defect.
    """
    circle, north, south, _sphere, pulled = _the_pullback_over_the_circle()
    y = south.coordinate(0)

    with pytest.raises(AssertionError):
        pulled.sections().section(
            {
                "U_N": (north.coordinate(0), north.function_ring().one()),
                "U_S": (
                    -y,
                    y,
                ),
            }
        )


def test_a_nested_rational_cut_does_not_exclude_the_ambient_pole() -> None:
    r"""A reciprocal is a smooth guard on the cut t != 0, not at t=0.

    The ambient origin must remain a point after registering the nested
    cut, while the cut contains 2 and excludes 0.
    """
    line = SmoothManifolds()(1, "nested rational cuts")
    chart = line.chart("U", "t")
    t = chart.coordinate(0)
    first = line.restricted_chart("U", (t,))
    reciprocal = first.section_ratio(first.function_ring().one(), first.coordinate(0))
    second = line.restricted_chart("U", (t, reciprocal))
    assert line.point((0,), "U").coordinates()[0] == RR(0)
    assert second.domain().point((2,), second.label()).coordinates()[0] == RR(2)
    with pytest.raises((ValueError, AssertionError)):
        second.domain().point((0,), second.label())


def test_restricting_the_same_chart_on_the_same_domain_retains_the_chart() -> None:
    r"""A chart restricted by the same defining nonvanishing datum has the same domain.

    Reading the reciprocal guard on x != 0 imposes no further condition.
    A different cut x != 1 must not be identified with the first cut.
    """
    line = SmoothManifolds()(1, "retained open restriction")
    chart = line.chart("U", "x")
    x = chart.coordinate(0)
    first = line.restricted_chart("U", (x,))
    assert line.restricted_chart("U", (x,)) is first
    reciprocal = first.section_ratio(first.function_ring().one(), first.coordinate(0))
    assert line.restricted_chart("U", (x, reciprocal)) is first
    other = line.restricted_chart("U", (x-chart.function_ring().one(),))
    assert other is not first
    assert first.domain().point((1,), first.label()).coordinates()[0] == RR(1)
    with pytest.raises((ValueError, AssertionError)):
        other.domain().point((1,), other.label())
