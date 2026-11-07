"""Generated signed-pair permutations admit their words and exclude a shear."""

from sage_extensions.all import *


def test_generated_subgroup_membership_respects_its_full_finite_group():
    lattice = Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    space = lattice.base_change(ZZ.fraction_field_map())
    labels = tuple(space.module_generating_set())
    e, f, x, y = tuple(space.module_generators())
    exchange = space.Isom(space)(dict(zip(labels, (x, y, e, f), strict=True)))
    sign = space.Isom(space)(dict(zip(labels, (-e, -f, x, y), strict=True)))
    group = space.O().subgroup((exchange, sign))
    ring = space.base_ring()
    unit = ring(2) / ring(2)
    rebuilt = space.Isom(space)({
        label: space.scalar_multiple(unit, image)
        for label, image in zip(labels, (x, y, e, f), strict=True)
    })
    shear = space.Isom(space)(dict(zip(labels, (e, f - y, x + e, y), strict=True)))

    assert group.membership_decision(exchange) is True
    assert group.membership_decision(rebuilt) is True
    assert group.membership_decision(~exchange) is True
    assert group.membership_decision(exchange * sign) is True
    assert group.membership_decision(shear) is False


def test_lattice_group_unit_and_free_word_images_have_their_exact_actions():
    space = Lattices(QQ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    labels = tuple(space.module_generating_set())
    e, f, x, y = tuple(space.module_generators())
    exchange = space.O()(dict(zip(labels, (x, y, e, f), strict=True)))
    sign = space.O()(dict(zip(labels, (-e, -f, x, y), strict=True)))
    unit = space.O().one()
    for element in (exchange, sign, exchange * sign):
        assert all((unit * element)(point) == element(point) for point in (e, f, x, y))
        assert all((element * unit)(point) == element(point) for point in (e, f, x, y))
    free = Groups.Free(2)
    free_labels = tuple(free.free_basis())
    s, t = tuple(free.free_generator(label) for label in free_labels)
    augmentation = free.Mor(space.O())(dict(zip(free_labels, (exchange, sign), strict=True)))
    square = augmentation((s * t)**2)
    fourth = augmentation((s * t)**4)
    assert all(square(point) == -point for point in (e, f, x, y))
    assert all(fourth(point) == point for point in (e, f, x, y))


def test_an_inverse_unipotent_generator_is_an_arrow_of_its_classifying_category():
    space = Lattices(QQ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    labels = tuple(space.module_generating_set())
    e, f, x, y = tuple(space.module_generators())
    shear = space.O()({labels[0]: e, labels[1]: f + x, labels[2]: x, labels[3]: y - e})
    group = space.O().subgroup((shear,))
    inverse = ~shear
    assert group.membership_decision(inverse) is True
    category = group.classifying_category()
    point = category.an_object()
    arrow = category.Mor(point, point)(inverse)
    assert arrow.group_element()(f) == f - x
    assert arrow.group_element()(y) == y + e
    assert all((~arrow).group_element()(arrow.group_element()(vector)) == vector for vector in (e, f, x, y))
