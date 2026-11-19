r"""A section of a pullback is stated on the pullback's own charts, and its components obey the pullback's law.

A section of $f^*E$ over $N$ assigns to $q$ an element of the fibre $E_{f(q)}$ (Lee,
*Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  On a chart $W_1$ of $N$ whose
representation of $f$ lands in a chart $V_1$ of $M$ it is a tuple of functions, and on a
second chart $W_2$ the tuple is related to the first by the derivative of the composite
$T$, which carries a point of $W_1$ to the coordinates of $f$ in $V_2$:
$a_{W_2}(T(x)) = J_T(x)\,a_{W_1}(x)$.  So the sections of a pullback are not only the
pullbacks of sections of $E$: stating one is a computation on the map's own chart
representations, and a family that does not obey the law is a different object on each
chart.

The specimen is the reflection of $S^2$ in its equator, stated on both stereographic
charts by $x \mapsto x/\lvert x\rvert^2$.  Composed with the coordinate change that is the
identity, so its law reads $a_{U_S}(x) = a_{U_N}(x)$: the same expressions on both charts.
"""

import pytest

from sage_extensions.all import *


def _the_reflection_and_its_pullback():
    r"""$S^2$, its two charts, the reflection in the equator, and the pullback of $TS^2$ along it."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    def reflected(chart):
        coordinates = tuple(chart.coordinates())
        norm_squared = coordinates[0] ** 2 + coordinates[1] ** 2
        return tuple(
            chart.section_ratio(coordinate, norm_squared) for coordinate in coordinates
        )

    reflection = sphere.Mor(sphere)(
        {
            ("U_N", "U_N"): reflected(north),
            ("U_S", "U_S"): reflected(south),
        }
    )
    return sphere, north, south, reflection, sphere.tangent_bundle().pullback_along(reflection)


def test_a_section_of_a_pullback_is_stated_by_components_that_obey_its_law() -> None:
    r"""The same constant tuple on both charts is one section, and its components are read in either chart.

    The reflection composed with the coordinate change is the identity, so the law asks
    for the two tuples to be equal as functions; the constant $(1, 0)$ is.
    """
    _sphere, north, south, _reflection, pulled = _the_reflection_and_its_pullback()
    north_ring = north.function_ring()
    south_ring = south.function_ring()

    section = pulled.sections().section(
        {
            "U_N": (north_ring.one(), north_ring.zero()),
            "U_S": (south_ring.one(), south_ring.zero()),
        }
    )

    assert section.parent() is pulled.sections()
    assert section.components()["U_N"][0](north.domain()((2, 3))) == RR(1)
    assert section.components()["U_S"][1](south.domain()((RR(1) / RR(2), RR(0)))) == RR(0)


def test_a_family_that_does_not_obey_the_pullback_law_is_refused() -> None:
    r"""$(1, 0)$ on the north chart and $(0, 1)$ on the south one are two different objects, not one section.

    The law asks the two tuples to agree as functions; these differ everywhere, so the
    family describes a different element of the fibre on each chart.
    """
    _sphere, north, south, _reflection, pulled = _the_reflection_and_its_pullback()
    north_ring = north.function_ring()
    south_ring = south.function_ring()

    with pytest.raises(AssertionError):
        pulled.sections().section(
            {
                "U_N": (north_ring.one(), north_ring.zero()),
                "U_S": (south_ring.zero(), south_ring.one()),
            }
        )
