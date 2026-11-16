r"""A morphism over a field whose engine is inexact has coordinate images.

``RR`` is an owned exact field whose selected linear-algebra parent is the field
itself, so no Sage matrix ring backs it; the coordinates of each image are then
read from ``f`` rather than from a retained matrix.  The projection below sends
$e_0 \mapsto e_0$ and $e_1 \mapsto 0$, whose coordinates in the codomain's own
frame are $(1, 0)$ and $(0, 0)$; a free module has no relations.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_images_of_a_real_endomorphism_are_read_in_its_own_frame() -> None:
    r"""$e_0 \mapsto e_0$, $e_1 \mapsto 0$ over the owned real field."""
    V = RR**2
    first, _second = tuple(V.module_generators())
    projection = V.Mor(V)({0: first, 1: V.zero()})

    assert coordinate_images_of(projection) == ((RR(1), RR(0)), (RR(0), RR(0)))


def test_a_free_module_over_the_real_field_has_no_relations() -> None:
    r"""The zero relation morphism of a zero submodule has no coordinate images."""
    V = RR**2

    assert relation_images_of(V) == ()
