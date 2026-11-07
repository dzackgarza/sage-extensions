r"""Isotropic subobjects of a finite quadratic module, with their orbit and stabilizer.

``A.isotropic_subobject(generators)`` returns the submodule spanned by the given
classes when ``q`` vanishes on it, refusing a family that is not isotropic.
``O(q).orbit(J)`` and ``O(q).stabilizer(J)`` give the orbit and the setwise
stabilizer of such a submodule ``J``: the orbit is the closure of ``J`` under the
selected generators of ``O(q)``, taken in the owned finite action
``O(q).subobject_orbit_action(J)``, and the stabilizer is the subgroup Schreier's
lemma produces from that walk's own transversals.  Both are computed, and
``|Stab(J)| * |orbit(J)| = |O(q)|`` is the orbit-stabilizer identity checked on
the returned subgroup: its order is the engine's order of that subgroup, not a
quotient of orders.

Two specimens.

**``T_Co = B(2)`` with ``B = U ⊕ U ⊕ I_{0,7}``.**  ``A_{B(2)} = B/2B ≅ F_2^{11}``
and ``J = ⟨[1], [3]⟩`` is the image of the totally isotropic plane
``P = ⟨e₁, e₂⟩`` of the #295 specimen: the divided discriminant classes of its
two generators.  The orbit is large (|orbit| = 23715 here, one walk, no
enumeration of the submodules of ``A``), so the identity at this size is what the
Schreier family has to be able to answer.

**``A_{U ⊕ U(2)} ≅ F_2²`` with ``J = ⟨[e/2]⟩``.**  The form has
``q(e/2) = q(f/2) = 0`` and ``b(e/2, f/2) = 1/2``, so *two* of the three nonzero
classes are isotropic, ``⟨[e/2]⟩`` and ``⟨[f/2]⟩``, and the third, ``[e/2] + [f/2]``,
is not.  ``|O(q)| = 2``: the two isotropic lines are interchanged and each has a
trivial stabilizer.  This specimen exists to keep the trivial-group trap out —
``J`` is not the zero submodule, ``|O(q)| > 1``, and ``O(q)`` moves ``J`` to the
other line rather than fixing it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _elements_of(subobject):
    r"""The element set of a submodule inside its ambient form."""
    inclusion = subobject.inclusion()
    return frozenset(inclusion(element) for element in subobject.elements())


def _fixes_every_element(isometry, elements):
    r"""Whether one automorphism of the ambient form fixes a set of its elements."""
    return frozenset(isometry(element) for element in elements) == elements


def _tco_specimen():
    r"""``T_Co = B(2)``, its discriminant form, and ``J`` the image of the plane ``⟨e₁, e₂⟩``."""
    base = Lattices(ZZ)("U") + Lattices(ZZ)("U") + (Lattices(ZZ)([[-1]]) ** 7)
    lattice = base.twist(2)
    labels = tuple(lattice.module_generating_set())
    plane = lattice.subobject_on(
        [lattice.module_generator(labels[0]), lattice.module_generator(labels[2])]
    )
    images = tuple(
        lattice.divided_discriminant_class(vector) for vector in plane.embedded_module_generators()
    )
    form = lattice.discriminant_quadratic_form()
    return lattice, plane, form, form.isotropic_subobject(images), images


def test_the_small_specimen_checks_the_orbit_stabilizer_identity() -> None:
    r"""``A_{U ⊕ U(2)}``: ``|Stab(J)| * |orbit(J)| = |O(q)|`` on the returned subgroup.

    The two isotropic lines are interchanged by ``O(q)``, so the orbit of ``J`` is
    the other line and the stabilizer is a real subgroup of ``O(q)``, of order one.
    The identity is read from ``orbit(J)``, ``stabilizer(J)`` and ``O(q)``
    themselves, and the orbit is asserted to contain the other line.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2)
    form = lattice.discriminant_quadratic_form()
    group = form.orthogonal_group()

    zero = form.quadratic_value_module().zero()
    isotropic = tuple(element for element in form.elements() if form.q(element) == zero)
    classes = [element for element in isotropic if element != form.zero()]
    assert classes

    subobject = form.isotropic_subobject([classes[0]])
    other = form.isotropic_subobject([classes[1]])
    assert subobject.cardinality() > 1
    assert other != subobject
    assert int(group.cardinality()) > 1

    orbit = group.orbit(subobject)
    stabilizer = group.stabilizer(subobject)
    assert orbit.cardinality() > 1
    assert other in orbit

    assert stabilizer.supergroup() is group
    element_set = _elements_of(subobject)
    for isometry in stabilizer.group_generators():
        assert _fixes_every_element(isometry, element_set)
    assert int(stabilizer.cardinality()) * int(orbit.cardinality()) == int(group.cardinality())

    # the action's orbit and the submodule orbit name the same points
    action = group.subobject_orbit_action(subobject)
    assert int(action.point_set().cardinality()) == int(orbit.cardinality())
    assert subobject in orbit


def test_the_tco_plane_gives_an_isotropic_subobject_with_orbit_and_stabilizer() -> None:
    r"""``J`` on ``A_{B(2)}``: the orbit of the plane's image and its setwise stabilizer.

    Every figure is computed.  The orbit is the owned finite action's point set —
    the walk itself evaluates every selected generator's image of every point, so
    its closure is that sweep and not a second pass — and the stabilizer is a
    subgroup of ``O(q)`` whose generators fix ``J``.  The stabilizer's order and
    the orbit's therefore multiply to the group's order, which is the
    orbit-stabilizer theorem on the returned objects; nothing here reads a
    submodule enumeration of ``A``, a stored count, or a stabilizer index.
    """
    lattice, plane, form, subobject, images = _tco_specimen()
    group = form.orthogonal_group()

    assert int(form.cardinality()) > 1
    assert subobject.cardinality() > 1

    action = group.subobject_orbit_action(subobject)
    points = action.point_set()

    orbit = group.orbit(subobject)
    assert int(orbit.cardinality()) == int(points.cardinality())
    assert int(group.orbit_points(subobject).cardinality()) == int(orbit.cardinality())
    assert subobject in orbit

    stabilizer = group.stabilizer(subobject)
    assert stabilizer.supergroup() is group
    element_set = _elements_of(subobject)
    for isometry in stabilizer.group_generators():
        assert _fixes_every_element(isometry, element_set)

    total = int(group.cardinality())
    order = int(stabilizer.cardinality())
    count = int(orbit.cardinality())
    assert order * count == total

    # one orbit point, built from the orbit itself: the same order and still isotropic
    neighbour = next(iter(orbit))
    assert neighbour.cardinality() == subobject.cardinality()
    assert form.form_vanishes_on(_elements_of(neighbour))
