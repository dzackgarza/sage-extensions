r"""Primitive extensions of two orthogonal integral lattices.

The finite gluing step is the one used by OSCAR's primitive-embedding
algorithms (``QuadFormAndIsom/embeddings.jl`` at ``d135b70b``,
``_overlattice_with_graph`` and ``_primitive_extensions_generic``).
For even lattices ``M`` and ``N``, an even overlattice of ``M + N`` is
specified by an isotropic subgroup of ``A_M + A_N``.  Both summands remain
primitive exactly when that subgroup meets each discriminant summand
trivially, equivalently when it is the graph of an anti-isometry between
subgroups of their discriminant forms.

The routines here retain the two actual embeddings into each extension.
They enumerate the full finite gluing family; callers that classify up to
additional isometries can quotient that family by their stated actions.
"""

from sage_extensions.categories.rings.ring_foundation import (
    _owned_integers,
)


def _orthogonal_sum_embeddings(left, right):
    r"""Return ``(left + right, i_left, i_right)`` with lattice embeddings."""
    total = left + right
    left_injection = total.injection(0)
    right_injection = total.injection(1)
    left_embedding = left.Emb(total)(
        lambda label: left_injection(left.module_generator(label))
    )
    right_embedding = right.Emb(total)(
        lambda label: right_injection(right.module_generator(label))
    )
    return total, left_embedding, right_embedding


def _primitive_extensions(left, right, *, unimodular=False):
    r"""Return all even primitive extensions as pairs of actual embeddings.

    Each pair is ``(left -> V, right -> V)`` with one common codomain,
    orthogonal images, and torsion-free cokernels.  Every even primitive
    extension occurs.  Distinct pairs can have isometric codomains or
    become equivalent under isometries of the summands; no such quotient
    is imposed here.

    The inputs must be nondegenerate even lattices of finite rank over
    ``ZZ``.  If ``unimodular`` is true, only glue groups ``H`` satisfying
    ``|H|^2 = |A_(left + right)|`` are retained.  This is precisely the
    determinant-one condition for the corresponding overlattice.

    Filtering by primitivity of both retained embeddings is the graph
    condition: a nonzero intersection of ``H`` with ``A_left`` enlarges
    ``left`` inside its rational span, and likewise for ``right``.  Thus
    this filter retains exactly the anti-isometry gluings used by the
    pinned primitive-extension routine.
    """
    integers = _owned_integers()
    for lattice in (left, right):
        if (
            lattice.base_ring() is not integers
            or not lattice.module_rank().is_finite()
            or not lattice.is_nondegenerate()
            or not lattice.is_even()
        ):
            raise ValueError(
                f"primitive even extensions require nondegenerate even ZZ-lattices "
                f"of finite rank, but one summand is {lattice}"
            )

    total, left_inclusion, right_inclusion = _orthogonal_sum_embeddings(
        left, right
    )
    discriminant = total.discriminant_group()
    discriminant_order = int(discriminant.cardinality())
    if discriminant_order == 1:
        return ((left_inclusion, right_inclusion),)

    extensions = []
    for subgroup in discriminant.isotropic_subgroups():
        glue_order = int(subgroup.cardinality())
        if unimodular and glue_order**2 != discriminant_order:
            continue
        if glue_order == 1:
            extensions.append((left_inclusion, right_inclusion))
            continue
        extension = discriminant.overlattice_from_isotropic_subobject(subgroup)
        extended_left = extension * left_inclusion
        extended_right = extension * right_inclusion
        if extended_left.is_primitive() and extended_right.is_primitive():
            extensions.append((extended_left, extended_right))
    return tuple(extensions)
