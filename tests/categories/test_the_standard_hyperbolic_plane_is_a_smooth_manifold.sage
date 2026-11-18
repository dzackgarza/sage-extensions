r"""The standard ``HH^2``: the hyperboloid of ``I_{1,2}`` in its reference component."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_standard_hyperbolic_plane_is_an_object_of_its_category() -> None:
    r"""``HH^2`` is the hyperboloid of the lattice ``I_{1,2}``, so ``dim = rank - 1 = 2``.

    Its points are those of one chosen component of ``{q > 0}``, which is
    what ``positive_cone_component`` returns.
    """
    space = HyperbolicSpaces(2).an_object()

    assert space.category() is HyperbolicSpaces(2)
    assert space.dimension() == 2
    assert space.lattice().module_rank() == 3
    assert space.lattice().signature_pair().first() == 1
    assert space.lattice().signature_pair().second() == 2
    assert space.positive_cone_component() in PositiveConeComponents(space.lattice())


def test_the_hyperboloid_carries_the_smooth_structure_of_its_engine_manifold() -> None:
    r"""The metric ``-b`` of ``HH^2`` is smooth, and the atlas is one global chart.

    The chart ``hyperboloid`` is the diffeomorphism ``t^perp_RR -> HH(C^+)``,
    so it has one coordinate per dimension of the hyperboloid.
    """
    space = HyperbolicSpaces(2).an_object()

    assert space.is_smooth() is True
    assert space.chart_labels().cardinality() == 1
    assert space.atlas()["hyperboloid"].coordinates().cardinality() == space.dimension()


def test_the_origin_of_the_hyperboloid_chart_is_the_normalized_timelike_vector() -> None:
    r"""``y = 0`` is the point ``x = t / sqrt(q(t))``, the center of the hyperboloid.

    ``x = s t + y`` with ``s = sqrt((1 - q(y))/q(t))``, so ``y = 0`` gives
    ``x`` on the ray of the timelike vector ``t`` of the component and its
    chart coordinates are again zero.
    """
    space = HyperbolicSpaces(2).an_object()
    chart = space.atlas()["hyperboloid"]
    origin = space.point((0, 0), "hyperboloid")

    assert tuple(chart(origin)) == (0, 0)
