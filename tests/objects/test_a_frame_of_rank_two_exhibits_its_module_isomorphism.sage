r"""A frame of rank $r$ exhibits the module isomorphism $M \times \mathbb R^r \to E$, not only its basis.

A frame is a family $E_1,\dots,E_r$ of sections that is a basis of every fibre, and
that is what states the isomorphism: a family of smooth functions $(a_1,\dots,a_r)$
determines the section $\sum_i a_i E_i$, and a section $V$ determines the family with
$V = \sum_i a_i E_i$, which in a chart is the linear system $V_j = \sum_i a_i (E_i)_j$
(Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  The system is solved by
Cramer's rule, and the determinant that makes it solvable is the one the frame's
being a basis decided: it vanishes nowhere on the chart.

The specimen is the chart domain of $S^2$ -- a proper open submanifold, one chart,
$TV$ of rank two -- read first in its coordinate frame, where the matrix of
components is the identity, and then in a frame that is not the coordinate frame,
$\partial_{x_1}$ and $\partial_{x_1} + \partial_{x_2}$, where the matrix is
$\begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$ and inverting it is real work.
"""

import pytest

from sage_extensions.all import *


def _the_chart_domain(label):
    r"""The open subset of $S^2$ where the stereographic chart's coordinates do not all vanish."""
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    norm_squared = north.coordinate(0) ** 2 + north.coordinate(1) ** 2
    chart = sphere.chart_on_open_subset(label, "x1 x2", "U_N", (norm_squared,))
    return sphere, chart, chart.domain(), sphere.open_submanifold_inclusion(chart.domain())


def _the_sections(label):
    r"""The sections of $TV$, the chart on $V$ whose coordinates are the frame's, and $V$."""
    sphere, chart, domain, inclusion = _the_chart_domain(label)
    sections = sphere.tangent_bundle().pullback_along(inclusion).sections()
    return sections, domain.atlas()[chart.label()], domain


def test_the_trivialization_of_a_rank_two_bundle_states_its_rank_and_its_frame() -> None:
    r"""The module of sections of $TV$ is free of rank two, and the frame is its basis."""
    sections, chart, _domain = _the_sections("R1")
    frame = tuple(
        sections.coordinate_vector_field(chart, index) for index in range(2)
    )

    trivialization = sections.trivialized_by(frame).trivialization()

    assert trivialization.frame() == frame
    assert sections.trivialized_by(frame).module_rank() == 2
    assert sections.trivialized_by(frame).basis() == frame


def test_the_coordinate_frame_carries_a_pair_of_functions_to_a_section_and_back() -> None:
    r"""$\sum_i a_i \partial_{x_i}$ has the components $(a_1, a_2)$, and reading them back gives the functions.

    The coordinate frame's matrix of components is the identity, so the section
    $\sum_i a_i \partial_{x_i}$ has components $(a_1, a_2)$ and the inverse map is
    the pair of components themselves.
    """
    sections, chart, domain = _the_sections("R2")
    frame = tuple(
        sections.coordinate_vector_field(chart, index) for index in range(2)
    )
    trivialization = sections.trivialized_by(frame).trivialization()
    first = domain.smooth_function({chart.label(): chart.coordinate(0)})
    second = domain.smooth_function({chart.label(): chart.coordinate(1)})
    at = chart.domain()((2, 3))

    section = trivialization.forward((first, second))
    back = trivialization.inverse(section)

    assert section.components()[chart.label()][0](at) == RR(2)
    assert section.components()[chart.label()][1](at) == RR(3)
    assert back[0](at) == RR(2)
    assert back[1](at) == RR(3)
    assert trivialization.forward(back) == section


def test_a_frame_that_is_not_the_coordinate_frame_inverts_its_matrix() -> None:
    r"""For $E_2 = \partial_{x_1} + \partial_{x_2}$ the components are $\begin{pmatrix} 1 & 1 \\ 0 & 1\end{pmatrix}$, and inverting it returns the functions.

    With $a_1 = x_1$ and $a_2 = x_2$ the section $\sum_i a_i E_i$ has components
    $(x_1 + x_2,\ x_2)$, and reading the functions back is solving that system: a
    matrix that is not the identity, with coefficients that are not constant.
    """
    sections, chart, domain = _the_sections("R3")
    ring = chart.function_ring()
    label = chart.label()
    first_frame = sections.section({label: (ring.one(), ring.zero())})
    second_frame = sections.section({label: (ring.one(), ring.one())})
    trivialization = sections.trivialized_by(
        (first_frame, second_frame)
    ).trivialization()
    first = domain.smooth_function({label: chart.coordinate(0)})
    second = domain.smooth_function({label: chart.coordinate(1)})
    at = chart.domain()((2, 3))

    section = trivialization.forward((first, second))
    back = trivialization.inverse(section)

    assert section.components()[label][0](at) == RR(5)
    assert section.components()[label][1](at) == RR(3)
    assert back[0](at) == RR(2)
    assert back[1](at) == RR(3)
    assert trivialization.forward(back) == section
