r"""The coordinate frame of one chart trivializes the tangent bundle of a two-chart chart domain.

The tangent bundle of an open submanifold of $S^2$ is trivial, and the frame that states
it is the coordinate frame of one of the charts it carries: the coordinate vector fields
of a chart are a basis of the tangent space at every point of that chart, and on the
submanifold they are a basis everywhere the chart reaches (Lee, *Introduction to Smooth
Manifolds*, 2nd ed., Ch. 3 and Ch. 10).  In a chart where that frame is not the
coordinate frame its components are the derivative of the coordinate change, and their
determinant may vanish somewhere -- but only where the chart itself ends.  On the south
chart of $S^2$ the frame is $\partial/\partial x$ written in $y$-coordinates, whose
determinant is $-\lvert y\rvert^4$: its only zero is the north pole $y = 0$, which is
not in the south chart's domain, since that domain is the overlap where
$\lvert y\rvert^2 \ne 0$.  So the frame is a basis of every fibre of $TV$, and the
decision is: the determinant, divided by the overlap functions that cut the chart, takes
no zero.

The specimen is $S^2$ minus the north pole with both stereographic charts read on it --
two charts, a transition between them, and a frame whose determinant is a polynomial in
two variables.
"""

import pytest

from sage_extensions.all import *


def _the_two_chart_chart_domain():
    r"""$S^2$ minus the north pole, with the north and south charts on it, and its tangent bundle's sections."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    submanifold = sphere.open_submanifold(sphere.open_submanifold_inclusion(north.domain()))
    return submanifold, submanifold.atlas()["U_N"], submanifold.tangent_bundle().sections()


def test_the_coordinate_frame_trivializes_the_two_chart_chart_domain() -> None:
    r"""$TV$ is free of rank two, with the north chart's coordinate frame as its basis.

    The frame's determinant on the south chart is $-\lvert y\rvert^4$, and the south
    chart is the subset where $\lvert y\rvert^2 \ne 0$; dividing the determinant by that
    overlap function twice leaves $-1$, which takes no zero.  So the family is a basis of
    every fibre, and the frame trivializes the bundle.
    """
    submanifold, north, sections = _the_two_chart_chart_domain()
    frame = tuple(sections.coordinate_vector_field(north, index) for index in range(2))

    trivialized = sections.trivialized_by(frame)

    assert trivialized.module_rank() == 2
    assert trivialized.basis() == frame
    assert trivialized.vector_bundle().base_manifold() is submanifold
    assert trivialized.trivialization().frame() == frame


def test_the_trivialization_reads_a_pair_of_functions_at_a_point_of_either_chart() -> None:
    r"""$\sum_i a_i \partial_{x_i}$ is read back as $(a_1, a_2)$ at a point given in the south chart too.

    The functions are stated on both charts -- $x_1$ on the north chart is $y_1/\lvert
    y\rvert^2$ on the south one -- and so is the section they state; reading the section
    back at the point of the south chart with coordinates $(2/13, 3/13)$, which is the
    point of the north chart with coordinates $(2, 3)$, returns the two values.
    """
    submanifold, north, sections = _the_two_chart_chart_domain()
    south = submanifold.atlas()["U_S"]
    frame = tuple(sections.coordinate_vector_field(north, index) for index in range(2))
    trivialization = sections.trivialized_by(frame).trivialization()
    first = submanifold.smooth_function(
        {
            "U_N": north.coordinate(0),
            "U_S": south.section_ratio(
                south.coordinate(0), south.coordinate(0) ** 2 + south.coordinate(1) ** 2
            ),
        }
    )
    second = submanifold.smooth_function(
        {
            "U_N": north.coordinate(1),
            "U_S": south.section_ratio(
                south.coordinate(1), south.coordinate(0) ** 2 + south.coordinate(1) ** 2
            ),
        }
    )
    at_south = submanifold.atlas()["U_S"].domain()((RR(2) / RR(13), RR(3) / RR(13)))

    section = trivialization.forward((first, second))
    back = trivialization.inverse(section)

    assert back[0](at_south) == RR(2)
    assert back[1](at_south) == RR(3)
    assert trivialization.forward(back) == section
