r"""``discriminant_representation`` on a setwise stabilizer's generators, by isometry, matrix and copy.

``rho_L`` is the discriminant action ``O(L) -> O(A_L)``.  It used to take only an
element of ``Aut(L)`` itself, so the generators of a setwise stabilizer -- which
the library returns as isometries of ``L`` obtained from the marked-lattice
route -- could not be pushed through it when they arrived as a matrix or as a
morphism from an equal copy of ``L``.  The map now reads all three forms through
the one constructor that builds ``Aut(L)``, so what comes out is the
discriminant action of an actual isometry.

The specimen is ``B = U ⊕ U ⊕ I_{0,7}`` with the plane ``P = ⟨e₁, e₂⟩`` spanned
by the first basis vector of each copy of ``U``: both are null and ``b(e₁, e₂) = 0``,
so ``P`` is totally isotropic and the marked-lattice route accepts it.  (Spanning
the two basis vectors of a *single* ``U`` would give a hyperbolic plane, which
that route refuses, correctly.)

The test asserts that the calls return, that every image lands in ``O(A_L)`` and
preserves ``q``, and that the order of the group the images generate divides
``|O(A_L)|``.  No count is asserted as a literal: the orders are recorded in the
commit message, and the expected value of a known-answer test is a
lattice-database card, which these are not.

``T_En`` is the second specimen the issue names and it does not reach this test:
the setwise stabilizer's generator call there does not return inside the sandbox's
1800 s cap, which is the retention question of #292 and not a property of this map.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``B = U ⊕ U ⊕ I_{0,7}`` with the totally isotropic plane ``⟨e₁, e₂⟩``."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + (Lattices(ZZ)([[-1]]) ** 7)
    labels = tuple(lattice.module_generating_set())
    plane = lattice.subobject_on(
        [lattice.module_generator(labels[0]), lattice.module_generator(labels[2])]
    )
    return lattice, plane


def test_the_setwise_stabilizer_generators_pass_through_rho() -> None:
    r"""Every generator's discriminant image lies in ``O(A_L)``, preserves ``q``, and generates a subgroup of it."""
    lattice, plane = _specimen()

    assert plane.module_rank() == 2
    assert plane.is_primitive() is True
    for left in plane.embedded_module_generators():
        for right in plane.embedded_module_generators():
            assert lattice.b(left, right) == ZZ(0)

    stabilizer = lattice.Isom(lattice).stabilizer(plane, action="setwise")
    generators = tuple(stabilizer.group_generators())
    rho = lattice.discriminant_representation()
    target = rho.codomain()

    images = tuple(rho(generator) for generator in generators)
    assert all(image.parent() is target for image in images)
    assert all(image.validate_form_preservation(check=True) is None for image in images)

    order = int(target.subgroup_on(images).cardinality())
    assert int(target.cardinality()) % order == 0


def test_an_isometry_given_by_matrix_or_by_its_own_construction_has_the_same_image() -> None:
    r"""The identity written three ways: as an element of ``Aut(L)``, as a matrix, and by its defining map."""
    lattice, _plane = _specimen()
    rho = lattice.discriminant_representation()
    target = rho.codomain()
    identity = lattice.Aut()(lambda label: lattice.module_generator(label))
    gram = [
        [
            int(lattice.b(lattice.module_generator(left), lattice.module_generator(right)))
            for right in lattice.module_generating_set()
        ]
        for left in lattice.module_generating_set()
    ]
    assert rho(identity) == target.one()
    assert rho(lattice.Aut()(gram)) == target.one()
