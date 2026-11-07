r"""Isotropic subobjects of a finite quadratic module, with their orbit and stabilizer.

``A.isotropic_subobject(generators)`` returns the submodule spanned by the given
classes when ``q`` vanishes on it, refusing a family that is not isotropic.
``O(q).orbit(J)`` and ``O(q).stabilizer(J)`` give the orbit and the setwise
stabilizer of such a submodule ``J`` through the owned subobject action, and
``|Stab(J)| * |orbit(J)| = |O(q)|`` is the caller's check — computed here from
the library's own cardinalities, never written as a number.

Two specimens.

**``T_Co = B(2)`` with ``B = U ⊕ U ⊕ I_{0,7}``.**  ``A_{B(2)} = B/2B ≅ F_2^{11}``
and ``J = ⟨[1], [3]⟩`` is the image of the totally isotropic plane
``P = ⟨e₁, e₂⟩`` of the #295 specimen: the divided discriminant classes of its
two generators.  The 119 discriminant images of the setwise stabilizer of ``P``
fix ``J``, so the group they generate is inside ``Stab(J)`` and its order
divides ``|Stab(J)|`` — computed, not asserted as a number.

**``A_{U ⊕ U(2)} ≅ F_2²`` with ``J = ⟨[e/2]⟩``.**  Here ``q(e/2) = 0`` while
``q((e+f)/2) = 1``, so exactly half the nonzero classes are isotropic: ``J`` is
the unique isotropic line, ``|O(q)| = 2``, the orbit has size 2 and the
stabilizer is trivial.  This specimen exists to keep the trivial-group trap out:
the test asserts ``J`` is not the zero submodule and ``|O(q)| > 1``.
"""

from sage_extensions.all import *  # noqa: F401,F403


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


def test_the_tco_plane_gives_an_isotropic_subobject_with_orbit_and_stabilizer() -> None:
    r"""``J`` on ``A_{B(2)}``: the product law, and the 119 images fix ``J``."""
    lattice, plane, form, subobject, images = _tco_specimen()
    group = form.orthogonal_group()

    assert int(form.cardinality()) > 1
    assert subobject.cardinality() > 1

    stabilizer = group.stabilizer(subobject)
    orbit = group.orbit(subobject)
    assert int(stabilizer.cardinality()) * int(orbit.cardinality()) == int(group.cardinality())

    rho = lattice.discriminant_representation()
    setwise = lattice.Isom(lattice).stabilizer(plane, action="setwise")
    stabilizer_images = tuple(rho(generator) for generator in setwise.group_generators())
    for image in stabilizer_images:
        for element in images:
            assert image(element) == element
    generated = int(group.subgroup_on(stabilizer_images).cardinality())
    assert int(stabilizer.cardinality()) % generated == 0


def test_the_small_specimen_keeps_the_trivial_group_out() -> None:
    r"""``A_{U ⊕ U(2)} ≅ F_2²`` with the unique isotropic line: ``|O(q)| = 2`` and the product law."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2)
    form = lattice.discriminant_quadratic_form()
    group = form.orthogonal_group()

    isotropic = tuple(
        element
        for element in form.elements()
        if form.q(element) == form.quadratic_value_module().zero()
    )
    generators = [element for element in isotropic if element != form.zero()]
    assert generators

    subobject = form.isotropic_subobject([generators[0]])
    assert subobject.cardinality() > 1
    assert int(group.cardinality()) > 1

    stabilizer = group.stabilizer(subobject)
    orbit = group.orbit(subobject)
    assert int(stabilizer.cardinality()) * int(orbit.cardinality()) == int(group.cardinality())
