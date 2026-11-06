r"""``discriminant_representation`` on the setwise stabilizer of a plane in ``T_Co = B(2)``.

``rho_L`` is the discriminant action ``O(L) -> O(A_L)``.  It reads an isometry as
an element of ``Aut(L)``, as a matrix, or as a morphism from an equal copy of
``L``, all through the constructor that builds ``Aut(L)``, so its image is the
discriminant action of an actual isometry.

**The specimen is ``T_Co = B(2)`` with ``B = U ⊕ U ⊕ I_{0,7}``**, not ``B``: ``B``
is unimodular, so ``A_B = 0`` and ``O(A_B)`` is the trivial group — a map into it
proves nothing.  Twisting by two gives ``A_{B(2)} = B/2B ≅ F_2^{11}`` with a
nondegenerate quadratic form, whose orthogonal group is large, and that is the
lattice stage 1 works with.  The isometries of ``B`` and of ``B(2)`` are the same
integer matrices, so the setwise stabilizer of ``P`` in ``O(B(2))`` is the one
``B`` carries.

``P = ⟨e₁, e₂⟩`` is spanned by the first basis vector of each copy of ``U(2)``:
both are null and ``b(e₁, e₂) = 0``, so ``P`` is totally isotropic and the
marked-lattice route accepts it.

The test asserts that the calls return, that every image lands in ``O(A_L)`` and
preserves ``q``, that the generated order divides ``|O(A_L)|`` computed by the
library in the same test, and that ``|O(A_L)|`` is not 1 — the trivial-group
specimen is precisely the mistake this file replaces.  No count is asserted as a
literal: expected values are lattice-database cards, and there is no card for
this one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``T_Co = B(2)`` with ``B = U ⊕ U ⊕ I_{0,7}``, and the totally isotropic plane ``⟨e₁, e₂⟩``."""
    base = Lattices(ZZ)("U") + Lattices(ZZ)("U") + (Lattices(ZZ)([[-1]]) ** 7)
    lattice = base.twist(2)
    labels = tuple(lattice.module_generating_set())
    plane = lattice.subobject_on(
        [lattice.module_generator(labels[0]), lattice.module_generator(labels[2])]
    )
    return lattice, plane


def test_the_setwise_stabilizer_generators_pass_through_rho() -> None:
    r"""Every generator's image lies in ``O(A_{B(2)})``, preserves ``q``, and generates a subgroup of it."""
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
    # the orthogonal group of A_{B(2)} is not the trivial group: A_{B(2)} is
    # F_2^11 with a nondegenerate form, so a map into it is a real test
    assert int(target.cardinality()) > 1
    assert int(target.cardinality()) % order == 0


def test_an_isometry_given_by_matrix_or_by_its_own_construction_has_the_same_image() -> None:
    r"""The identity written three ways: as an element of ``Aut(L)``, as a matrix, and by its defining map."""
    lattice, _plane = _specimen()
    rho = lattice.discriminant_representation()
    target = rho.codomain()
    identity = lattice.Aut()(lambda label: lattice.module_generator(label))
    labels = tuple(lattice.module_generating_set())
    unit = [
        [ZZ(1) if left == right else ZZ(0) for right in range(len(labels))]
        for left in range(len(labels))
    ]
    assert rho(identity) == target.one()
    assert rho(lattice.Aut()(unit)) == target.one()
