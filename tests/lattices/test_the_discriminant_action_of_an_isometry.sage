r"""The discriminant action of an isometry, and one contract for its two constructors.

An isometry ``s`` of an integral lattice ``L`` acts on ``A_L = L^∨/L``.  The two
constructors that raise that automorphism used to state different contracts:
between two forms it is ``TorsionFormIsometryMor``, whose element constructor
takes a mutually inverse pair of base morphisms ``(forward, inverse=None, *,
check=False)``; on the diagonal the family is the orthogonal group
``O(A_L)``, whose element constructor took one engine datum, so the pair form
raised ``TypeError`` there.  Both now take the same call, and an automorphism
is a group element on either route — not a bare core arrow.

The action is asserted where the mathematics is: on the class in ``L^∨/L`` of a
dual vector, compared with the class of the isometry's image of that same dual
vector.  For ``<2> + <2>`` the swap sends ``e_1/2`` to ``e_2/2`` and the two
classes generate the quotient; for the Enriques coinvariant shape
``T = <2> + U(2) + E8(-2)`` the reflection negates the first summand, so it
negates the class of its primitive dual.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_pair():
    r"""``<2> + <2>``: even, and ``A_L`` is the two-elementary group of order four."""
    lattice = Lattices(ZZ)([[2, 0], [0, 2]])
    labels = tuple(lattice.module_generating_set())
    return lattice, labels


def test_the_swap_acts_on_dual_classes_as_it_does_on_the_lattice() -> None:
    lattice, labels = _plane_pair()
    e_1 = lattice.module_generator(labels[0])
    e_2 = lattice.module_generator(labels[1])
    swap = lattice.O()({labels[0]: e_2, labels[1]: e_1})
    discriminant = swap.discriminant_morphism()
    projection = lattice.discriminant_projection()

    assert discriminant.parent() is lattice.discriminant_group().orthogonal_group()
    assert discriminant(projection(lattice.primitive_dual(e_1))) == projection(lattice.primitive_dual(e_2))
    assert discriminant(projection(lattice.primitive_dual(e_2))) == projection(lattice.primitive_dual(e_1))
    # the two classes are distinct, so the two assertions above are not one
    assert projection(lattice.primitive_dual(e_1)) != projection(lattice.primitive_dual(e_2))


def test_the_representation_returns_the_same_automorphism_as_the_morphism() -> None:
    lattice, labels = _plane_pair()
    e_1 = lattice.module_generator(labels[0])
    e_2 = lattice.module_generator(labels[1])
    swap = lattice.O()({labels[0]: e_2, labels[1]: e_1})
    representation = lattice.discriminant_representation()

    assert representation(swap) == swap.discriminant_morphism()
    assert representation(swap).parent() is lattice.discriminant_group().orthogonal_group()


def test_a_reflection_of_the_enriques_coinvariant_shape_negates_its_dual_class() -> None:
    r"""``T = <2> + U(2) + E8(-2)``: the first summand's reflection on ``A_T``."""
    e8_cartan = [
        [2, -1, 0, 0, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0, 0, 0],
        [0, -1, 2, -1, 0, 0, 0, -1],
        [0, 0, -1, 2, -1, 0, 0, 0],
        [0, 0, 0, -1, 2, -1, 0, 0],
        [0, 0, 0, 0, -1, 2, -1, 0],
        [0, 0, 0, 0, 0, -1, 2, 0],
        [0, 0, -1, 0, 0, 0, 0, 2],
    ]
    lattice = (
        Lattices(ZZ)([[2]])
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-2 * entry for entry in row] for row in e8_cartan])
    )
    assert lattice.is_even()
    labels = tuple(lattice.module_generating_set())
    images = {
        label: (-lattice.module_generator(label) if label == labels[0] else lattice.module_generator(label))
        for label in labels
    }
    reflection = lattice.O()(images)
    discriminant = reflection.discriminant_morphism()
    projection = lattice.discriminant_projection()
    class_of_first_dual = projection(lattice.primitive_dual(lattice.module_generator(labels[0])))

    assert discriminant(class_of_first_dual) == -class_of_first_dual
    assert lattice.discriminant_representation()(reflection) == discriminant


def test_the_group_constructor_takes_a_pair_and_keeps_its_own_elements() -> None:
    r"""One contract: a pair, an element of the group, or the engine datum.

    The pair form is what the isometry route hands this constructor; an element
    already in the group is its own normalization image, so a caller that has
    one does not have to know which route built it; and the single engine
    datum keeps its own meaning.
    """
    lattice, labels = _plane_pair()
    first, second = (lattice.module_generator(label) for label in labels)
    swap = lattice.O()({labels[0]: second, labels[1]: first})
    discriminant = swap.discriminant_morphism()

    form = lattice.discriminant_group()
    values = form.value_module()
    identity = values.module_category().Mor(values, values).identity()
    classes = tuple(form.module_generating_set())
    component = form.module_category().Mor(form, form)(
        {classes[0]: form.module_generator(classes[1]), classes[1]: form.module_generator(classes[0])}
    )
    formed_forward = form.category().Mor(form, form)((component, identity))
    formed_inverse = form.category().Mor(form, form)((component, identity))

    by_pair = form.O()(formed_forward, formed_inverse, check=True)
    assert by_pair.parent() is form.orthogonal_group()
    assert by_pair == discriminant
    assert by_pair(form.module_generator(classes[0])) == form.module_generator(classes[1])
    # an element of the group is its own normalization image
    assert form.O().from_morphism(discriminant) == discriminant
    # and the single-datum contract still answers
    assert form.O()(discriminant) == discriminant
