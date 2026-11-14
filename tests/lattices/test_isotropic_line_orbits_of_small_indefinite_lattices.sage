r"""The primitive isotropic line orbits of L_d = U ⊕ U ⊕ ⟨−2d⟩, against hand derivation.

A Baily–Borel 0-cusp is a Γ-orbit of primitive isotropic *lines*, so the count
these tests assert is a count of rank-one isotropic sublattices.  On the five
lattices below the answer can be written down from one theorem and one
identification, and the test asserts the derived numbers through the public call.

*Derivation.*  ``L_d = U ⊕ U ⊕ ⟨−2d⟩`` has rank five and signature ``(2, 3)``,
and ``A_{L_d} = Z/2d``.  A primitive isotropic ``v`` has divisibility ``e``
dividing ``2d``, and ``v/e`` is an isotropic class of ``A_{L_d}`` of order
``e``; the rank-one summand contributes ``-x²/2d`` to the class of ``x·g/2d``,
which forces ``e² | d``, and the classes of order ``e`` are the ``φ(e)``
primitive residues mod ``e``.

By the Eichler criterion (Gritsenko–Hulek–Sankaran, *Abelianisation of
orthogonal groups and the fundamental group of modular varieties*, J. Algebra
322 (2009), Prop. 3.3: in an integral lattice containing ``U ⊕ U``, two
primitive vectors of the same norm and the same class ``v/div(v)`` lie in one
``Ẽ(L)``-orbit, and ``Ẽ(L) ⊆ SÕ⁺(L)``) the ``Õ``-orbits of primitive isotropic
*vectors* are in bijection with those classes, numbering
``Σ_{e²|d} φ(e)``.

*The identification.*  A line identifies ``v ∼ -v``, and the class of ``-v/e``
is ``-[v/e]``; so a class and its negative give one line orbit.  ``-id ∈ Õ(L_d)``
exactly when ``-1`` acts trivially on ``Z/2d``, which happens only for ``2d = 2``.
For every ``d ≥ 2`` the classes of order ``e ≥ 3`` pair as ``{c, -c}``, leaving
``φ(e)/2 = 1`` of them, while orders ``1`` and ``2`` are self-paired.  The line
counts are therefore ``Σ_{e²|d} [φ(e) if e ≤ 2 else φ(e)/2]``, and the three
columns agree because ``φ(e) = 2`` for the admissible ``e ≥ 3`` here:

    d            1  2  4  9  36
    Õ⁺, Õ, O     1  1  2  2   4

*The case where the two readings differ.*  On ``L_9 = U ⊕ U ⊕ ⟨-18⟩``, with
``U = ⟨e, f⟩`` (``e² = f² = 0``, ``e·f = 1``), ``g`` the generator of ``⟨-18⟩``:

    v  = 3e + 3f + g,   v²  = 18 - 18 = 0,  div = 3,  class(v/3)  = 6  in Z/18,
    -v = -3e - 3f - g,  (-v)² = 0,          div = 3,  class(-v/3) = 12,

and ``id`` and ``-id`` are not both in ``Õ(L_9)`` — ``ρ(-id) = -1`` is nontrivial
on ``A_L`` — so the vectors give three orbits where the lines give two.  The
counts asserted here are the line counts, so the two-order-three classes are one
cusp; the vector-level reading is recorded in ``TRAPS.md`` and is not what a
cusp counts.

*The plane count for d = 1.*  Scattone (*On the compactification of moduli
spaces for algebraic K3 surfaces*, Mem. AMS 374 (1987)) gives the degree-two
boundary as four Type II curves and one Type III point, on the degree-two K3
period lattice ``U² ⊕ E8(-1)² ⊕ ⟨-2⟩`` of rank 19.  ``L_1`` is its rank-five
shadow and has one orbit of primitive isotropic planes, the part of that
boundary the shadow can see; the rank-19 module that carries the 4 + 1 is #294's.
"""

from sage_extensions.all import *  # noqa: F401,F403

_CASES = (
    (1, 1),
    (2, 1),
    (4, 2),
    (9, 2),
    (36, 4),
)


def _lattice(d):
    r"""``U ⊕ U ⊕ ⟨-2d⟩``, rank five and signature ``(2, 3)``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2 * ZZ(d)]])


def test_the_line_counts_of_the_three_groups_are_the_derived_ones() -> None:
    r"""``Õ⁺``, ``Õ`` and ``O`` on ``L_d`` for d = 1, 2, 4, 9, 36: the derived line counts."""
    for d, derived in _CASES:
        lattice = _lattice(d)
        orthogonal = lattice.Aut()
        stable = lattice.stable_orthogonal_group()
        stable_plus = stable.intersection(lattice.O_plus())

        assert orthogonal.isotropic_orbit_representatives(1).cardinality() == derived
        assert stable.isotropic_orbit_representatives(1).cardinality() == derived
        assert stable_plus.isotropic_orbit_representatives(1).cardinality() == derived

        for line in orthogonal.isotropic_orbit_representatives(1):
            vector = line.inclusion()(line.module_generator(0))
            assert vector.q() == ZZ(0)
            assert vector.is_primitive() is True


def test_the_two_witness_vectors_of_l_9_are_primitive_isotropic_of_divisibility_three() -> None:
    r"""``v = 3e + 3f + g`` and ``-v``: both attained, classes 6 and 12."""
    lattice = _lattice(9)
    labels = tuple(lattice.module_generating_set())
    e, f = lattice.module_generator(labels[0]), lattice.module_generator(labels[1])
    g = lattice.module_generator(labels[4])

    for sign in (1, -1):
        vector = sign * (3 * e + 3 * f + g)
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True
        assert lattice.div(vector) == ZZ(3)
        assert int(lattice.divided_discriminant_class(vector).additive_order()) == 3

    first = 3 * e + 3 * f + g
    second = -(3 * e + 3 * f + g)
    assert lattice.divided_discriminant_class(first) != lattice.divided_discriminant_class(second)


def test_the_rank_five_shadow_has_one_primitive_isotropic_plane_orbit() -> None:
    r"""``L_1``: the one part of Scattone's degree-two boundary this lattice sees."""
    lattice = _lattice(1)
    planes = lattice.Aut().isotropic_orbit_representatives(2)
    assert planes.cardinality() == 1
    for plane in planes:
        assert plane.module_rank() == 2
        assert plane.is_primitive() is True
