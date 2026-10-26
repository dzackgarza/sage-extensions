r"""A small Euclidean ball around a point of (mathbf Q^2) can contain one lattice point."""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.definite_lattices import _ExactCVPEngine
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ


def test_square_lattice_close_vectors_at_radius_squared_one_eighth() -> None:
    lattice = Lattices(ZZ)(ZZ^2)
    first = lattice.basis_vector(0)
    close = lattice.close_vectors((QQ(3) / 4, QQ(1) / 4), QQ(1) / 8)

    assert close.cardinality() == cardinal(1)
    assert close[first] == QQ(1) / 8


def test_close_vectors_is_invariant_under_large_integral_target_translation() -> None:
    lattice = Lattices(ZZ)([[2]])
    (generator,) = lattice.module_generators()
    shift = ZZ(10**6)
    target = (QQ(shift) + QQ(1) / 2,)

    close = lattice.close_vectors(target, ZZ(1))

    left = lattice.scalar_multiple(shift, generator)
    right = lattice.scalar_multiple(shift + 1, generator)
    assert close.cardinality() == cardinal(2)
    assert Set(close.index_set()) == Set((left, right))
    assert close[left] == QQ(1) / 2
    assert close[right] == QQ(1) / 2
    assert lattice.closest_vector(target) in close.index_set()
    assert lattice._has_close_vector(target, ZZ(1))
    assert not lattice._has_close_vector(target, QQ(1) / 4)

    lowered = lattice._exact_cvp_engine().close_vector_coordinates(target, ZZ(1))
    payload = tuple(
        (
            tuple(int(entry) for entry in coordinates),
            (int(square.numerator()), int(square.denominator())),
        )
        for coordinates, square in lowered
    )
    assert tuple(sorted(payload)) == (
        ((10**6,), (1, 2)),
        ((10**6 + 1,), (1, 2)),
    )


def test_affine_cvp_scale_search_finds_first_feasible_multiplier_exactly() -> None:
    lattice = Lattices(ZZ)([[2]])

    scale, shell = lattice._exact_cvp_engine().first_close_vector_scale_coordinates(
        (QQ(1) / 3,),
        QQ(1) / 10,
        5,
    )
    assert scale == 2
    assert tuple(int(entry) for entry in shell[0][0]) == (1,)
    assert (int(shell[0][1].numerator()), int(shell[0][1].denominator())) == (2, 9)
    assert lattice._first_close_vector_scale(
        (QQ(1) / 3,),
        QQ(1) / 10,
        5,
    ) == 2
    assert lattice._first_close_vector_scale(
        (QQ(1) / 2,),
        QQ(1) / 2,
        5,
        exact_distance=True,
    ) == 1


def test_coordinate_cvp_engine_can_be_prepared_from_an_exact_positive_gram() -> None:
    engine = _ExactCVPEngine._from_positive_engine_gram(
        ZZ,
        sage_matrix(SageZZ, [[SageZZ.one() + SageZZ.one()]]),
    )

    assert engine.lattice is None
    assert engine.rank == 1
    assert int(engine.engine_gram[0, 0]) == 2
    assert engine._engine_target_coordinates((QQ(1) / 2,)) == (
        SageQQ.one() / (SageQQ.one() + SageQQ.one()),
    )
