r"""A section of a pullback is stated on the pullback's own charts, and its components obey the pullback's law.

A section of $f^*E$ over $N$ assigns to $q$ an element of the fibre $E_{f(q)}$ (Lee,
*Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  On a chart $W_1$ of $N$ whose
representation of $f$ lands in a chart $V_1$ of $M$ it is a tuple of functions, and on a
second chart $W_2$ the tuple is related to the first by the derivative of the target
coordinate transition $g:V_1\to V_2$ at $f(q)$, not the derivative of the map from
$W_1$ to $V_2$.  So the sections of a pullback are not only the
pullbacks of sections of $E$: stating one is a computation on the map's own chart
representations, and a family that does not obey the law is a different object on each
chart.

The specimen is reflection in the equator of $S^2$. It maps the north chart to the
south chart and conversely, with identity coordinate formulas (including the poles).
The change of target coordinates is inversion $I(x)=x/|x|^2$ and
$dI_x(x)=-I(x)$. Thus coefficients $-x$ on the north source chart and $y$ on
the south source chart agree. Same-chart inversion formulas alone would omit
both poles, and constant tuples in different target frames would not agree.
"""

import pytest

from sage_extensions.all import *


def _the_reflection_and_its_pullback():
    r"""$S^2$, its two charts, the reflection in the equator, and the pullback of $TS^2$ along it."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    reflection = sphere.Mor(sphere)(
        {
            ("U_N", "U_S"): tuple(north.coordinates()),
            ("U_S", "U_N"): tuple(south.coordinates()),
        }
    )
    return sphere, north, south, reflection, sphere.tangent_bundle().pullback_along(reflection)


def test_a_section_of_a_pullback_is_stated_by_components_that_obey_its_law() -> None:
    r"""The radial coefficients with opposite signs glue by $dI_x(x)=-I(x)$."""
    _sphere, north, south, _reflection, pulled = _the_reflection_and_its_pullback()
    section = pulled.sections().section(
        {
            "U_N": tuple(-entry for entry in north.coordinates()),
            "U_S": tuple(south.coordinates()),
        }
    )

    assert section.parent() is pulled.sections()
    assert section.components()["U_N"][0](north.domain()((2, 3))) == RR(-2)
    assert section.components()["U_S"][0](south.domain()((RR(1) / RR(2), RR(0)))) == RR(1) / 2
    assert tuple(section.components_at(north.domain()((0, 0)), "U_S")) == (RR(0), RR(0))
    assert tuple(section.components_at(south.domain()((0, 0)), "U_N")) == (RR(0), RR(0))


def test_a_family_that_does_not_obey_the_pullback_law_is_refused() -> None:
    r"""The same-sign radial fields fail the target coordinate transition law."""
    _sphere, north, south, _reflection, pulled = _the_reflection_and_its_pullback()
    with pytest.raises(AssertionError):
        pulled.sections().section(
            {
                "U_N": tuple(north.coordinates()),
                "U_S": tuple(south.coordinates()),
            }
        )
