r"""The selected subfamily is read from the announced family, and generates the stabilizer.

`L.Aut().discriminant_point_stabilizer(point)` presents `rho_L^-1(P)` for `P`
the stabilizer of a finite set of classes of `A_L`; its family is the Schreier
family of the point's orbit, `|S| * |orbit|` members, and
`discriminant_point_stabilizer_image_generators` selects a subfamily of it whose
images in `O(A_L)` generate `P`.  The selection reads the members in the
family's own order and stops at the first one that would not enlarge the
subgroup their images have generated, so it visits a prefix of the family and
never realizes the rest: for a large discriminant group the family itself is the
expensive datum, and this route pays for the members it reaches rather than for
all of them.

What the two tests assert is that these are still two routes to one answer.  The
selection's members lie in the preimage, preserve the point, and each one's
discriminant image occurs among the announced family's images -- so the
selection is a subfamily of that family and not a family of its own.  And the
images of the selection generate a subgroup of `O(A_L)` of order
`|O(A_L)| / |orbit|`, which is `|P|` by the index-stabilizer identity: the
order is computed here from the two public calls, not taken from the selection.

The specimen is `U + U(2)` (rank four, `A_L = (Z/2)^4`, small enough that the
announced family is built here as well) at the four classes of `A_{U(2)}`.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$U \oplus U(2)$ and the four classes of $A_{U(2)}$ inside $A_L$."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])
    form = lattice.discriminant_group()
    basis = tuple(lattice.module_generators())
    first = lattice.discriminant_class(lattice.primitive_dual(basis[2]))
    second = lattice.discriminant_class(lattice.primitive_dual(basis[3]))
    return lattice, frozenset({form.zero(), first, second, first + second})


def test_the_selection_is_a_subfamily_of_the_announced_family() -> None:
    r"""Each selected member is in the preimage, fixes the point, and is one of the family's."""
    lattice, point = _specimen()
    group = lattice.Aut()
    preimage = group.discriminant_point_stabilizer(point)
    family = tuple(preimage.group_generators())
    selection = tuple(group.discriminant_point_stabilizer_image_generators(point))

    assert selection
    assert cardinal(sum(1 for _ in selection)) < cardinal(sum(1 for _ in family))
    assert all(member in preimage for member in selection)
    assert all(
        frozenset(member.discriminant_morphism()(class_) for class_ in point) == point
        for member in selection
    )
    family_images = tuple(member.discriminant_morphism() for member in family)
    assert all(
        any(member.discriminant_morphism() == image for image in family_images)
        for member in selection
    )


def test_the_selections_images_generate_the_points_stabilizer() -> None:
    r"""`|<selection>|` in `O(A_L)` is `|O(A_L)| / |orbit of point|`, the point's stabilizer."""
    lattice, point = _specimen()
    group = lattice.Aut()
    image_group = lattice.discriminant_group().orthogonal_group()
    orbit = group.discriminant_point_orbit(point)
    selection = tuple(group.discriminant_point_stabilizer_image_generators(point))
    generated = image_group.subgroup(
        tuple(image_group(member.discriminant_morphism()) for member in selection)
    )

    assert generated.cardinality() == cardinal(
        int(image_group.cardinality()) // int(orbit.cardinality())
    )
