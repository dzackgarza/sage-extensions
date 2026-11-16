r"""A field whose engine is inexact answers primitivity, and states what it cannot compute.

``RR`` is an owned exact field whose selected linear-algebra parent is the field
itself, so no Sage matrix ring backs it and no Smith form exists there.  A
morphism of its free modules is still read by the definition: an injective map
is primitive because every submodule of a vector space is saturated, and a map
with a kernel is not.  The saturation of an image over ``RR`` is the whole
codomain, which the exact Smith computation of the presented owner cannot
supply, so it is refused with that hypothesis named.

Over a field of any kind the inclusions of the basis of $R^2$ are injective, and
$e_0 \mapsto e_0$, $e_1 \mapsto 0$ is not.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_an_injective_endomorphism_of_the_real_plane_is_primitive() -> None:
    r"""$e_0 \mapsto e_0$, $e_1 \mapsto e_0 + e_1$ is an isomorphism of $RR^2$."""
    plane = RR**2
    first, second = tuple(plane.module_generators())

    inclusion = plane.Mor(plane)({0: first, 1: first + second})

    assert inclusion.is_injective() is True
    assert inclusion.is_primitive() is True


def test_an_endomorphism_of_the_real_plane_with_a_kernel_is_not_primitive() -> None:
    r"""$e_0 \mapsto e_0$, $e_1 \mapsto 0$ kills the kernel's line."""
    plane = RR**2
    first, _second = tuple(plane.module_generators())

    projection = plane.Mor(plane)({0: first, 1: plane.zero()})

    assert projection.is_injective() is False
    assert projection.is_primitive() is False
    assert projection.kernel().module_rank() == NN(1)


def test_the_real_planes_saturation_names_the_missing_smith_computation() -> None:
    r"""$\operatorname{coker}$ over $RR$ is computed by the presented owner's exact Smith form."""
    plane = RR**2
    first, second = tuple(plane.module_generators())

    inclusion = plane.Mor(plane)({0: first, 1: first + second})

    with pytest.raises(AssertionError):
        inclusion.saturation()
