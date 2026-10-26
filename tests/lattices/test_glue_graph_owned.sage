r"""The glue of the primitive extension cut out by an involution of ``U``."""

from sage_extensions.all import *


def test_swap_on_u_glues_invariant_and_coinvariant_parts_along_index_two() -> None:
    r"""The swap ``e <-> f`` of ``U`` has invariant lattice ``ZZ(e+f) = <2>`` and
    coinvariant lattice ``ZZ(e-f) = <-2>``.  Their sum has determinant ``-4``
    against ``-1`` for ``U``, so its index in ``U`` is ``2``; the glue graph is
    the graph of an anti-isometry between the two ``ZZ/2`` discriminant groups
    and has ``2`` elements, the nonzero one being the class of ``e = (e+f)/2 +
    (e-f)/2``.  Derived by hand.
    """
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()
    swap = plane.Aut()({e: f, f: e})
    extension = swap.primitive_extension()

    assert extension.index() == 2
    assert extension.glue_graph().cardinality() == 2
