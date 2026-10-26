"""Zeta-factor data for affine quadrics attached to integral lattices.

Migrated from the formula formerly implemented by ``latticedb.site.zeta_tex`` of
dzackgarza/lattice-database, since removed.
The preamble owns the mathematical factorization; presentation layers may
render the returned factors in TeX or another notation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuadraticCharacterDiscriminant:
    """The discriminant parameter ``coefficient`` or ``coefficient * n``."""

    coefficient: int
    times_norm_parameter: bool = False


@dataclass(frozen=True)
class PartialLFactor:
    """One partial Dirichlet L-factor with shift and quadratic character."""

    shift: int
    character: QuadraticCharacterDiscriminant


@dataclass(frozen=True)
class QuadraticHypersurfaceZetaFactorization:
    """Numerator and denominator factors of one partial affine-quadric zeta function."""

    numerator: tuple[PartialLFactor, ...]
    denominator: tuple[PartialLFactor, ...] = ()


def quadratic_hypersurface_zeta_factorization(lattice, *, cone: bool):
    """Return the partial zeta factorization of the zero or nonzero quadric level.

    The bad-prime set Sigma is external to the factorization: for the cone it
    is the bad-reduction set of ``lattice``; for a nonzero level it is enlarged
    by the primes dividing the represented norm parameter n.
    """
    rank = int(lattice.module_rank())
    determinant = lattice.determinant()
    if determinant == 0:
        raise ValueError(
            f"the affine-quadric zeta factorization requires a nondegenerate lattice, not {lattice}"
        )
    m = rank // 2
    trivial = QuadraticCharacterDiscriminant(1)
    if rank % 2 == 1:
        first = PartialLFactor(2 * m, trivial)
        if cone:
            return QuadraticHypersurfaceZetaFactorization((first,))
        coefficient = (-1) ** m * int(determinant)
        varying = PartialLFactor(
            m, QuadraticCharacterDiscriminant(coefficient, times_norm_parameter=True)
        )
        return QuadraticHypersurfaceZetaFactorization((first, varying))

    character = QuadraticCharacterDiscriminant(
        int(lattice.discriminant_character_discriminant())
    )
    first = PartialLFactor(2 * m - 1, trivial)
    denominator = PartialLFactor(m - 1, character)
    if cone:
        return QuadraticHypersurfaceZetaFactorization(
            (first, PartialLFactor(m, character)), (denominator,)
        )
    return QuadraticHypersurfaceZetaFactorization((first,), (denominator,))
