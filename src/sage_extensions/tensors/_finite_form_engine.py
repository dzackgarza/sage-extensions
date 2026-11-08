r"""Private engine (OWN-06): finite-field orthogonal groups.

Consumer: ``torsion_form_modules._engine_orthogonal_group`` for an elementary
odd primary part of a finite quadratic module.  GAP's ``GO(epsilon, n, p)``
is conjugated onto the given Gram matrix by an explicit isometry of
diagonalized forms. Integer-valued elementary two-primary quadratic forms
use GAP Forms to transport the full classical group onto their actual basis.
"""

from sage.libs.gap.libgap import libgap as _engine_libgap
from sage.matrix.constructor import identity_matrix as _engine_identity_matrix
from sage.matrix.constructor import matrix as _engine_matrix
from sage.rings.finite_rings.finite_field_constructor import GF as _engine_GF
from sage.rings.integer_ring import ZZ as SageZZ


def _diagonalize(M):
    r"""``B`` with ``B M B^T`` diagonal, ``M`` symmetric nondegenerate over ``GF(p)``, ``p`` odd."""
    field = M.base_ring()
    n = M.nrows()
    B = _engine_identity_matrix(field, n)
    for k in range(n):
        G = B * M * B.transpose()
        if G[k, k] == 0:
            pivot = next((i for i in range(k + 1, n) if G[i, i] != 0), None)
            if pivot is not None:
                B.swap_rows(k, pivot)
            else:
                j = next(j for j in range(k + 1, n) if G[k, j] != 0)
                B.add_multiple_of_row(k, j, 1)
            G = B * M * B.transpose()
        assert G[k, k] != 0
        for i in range(k + 1, n):
            B.add_multiple_of_row(i, k, -G[i, k] / G[k, k])
    D = B * M * B.transpose()
    assert D.is_diagonal()
    return B


def _normalize_diagonal(D):
    r"""``N`` with ``N D N^T = diag(1, ..., 1, delta)`` for a nondegenerate diagonal ``D`` over ``GF(p)``, ``p`` odd."""
    field = D.base_ring()
    n = D.nrows()
    N = _engine_identity_matrix(field, n)
    current = [D[i, i] for i in range(n)]
    for i in range(n - 1):
        a, b = current[i], current[i + 1]
        x, y = next((x, y) for x in field for y in field if a * x ** 2 + b * y ** 2 == 1)
        step = _engine_identity_matrix(field, n)
        step[i, i], step[i, i + 1] = x, y
        step[i + 1, i], step[i + 1, i + 1] = -b * y, a * x
        N = step * N
        current[i], current[i + 1] = field.one(), a * b
    final = N * D * N.transpose()
    assert final == _engine_matrix.diagonal(field, current)
    return N, current[-1]


def _isometry_between(M, S):
    r"""``X`` with ``X M X^T = S`` for nondegenerate symmetric ``M``, ``S`` of equal discriminant class over ``GF(p)``."""
    B1, B2 = _diagonalize(M), _diagonalize(S)
    N1, d1 = _normalize_diagonal(B1 * M * B1.transpose())
    N2, d2 = _normalize_diagonal(B2 * S * B2.transpose())
    field = M.base_ring()
    t = (d2 / d1).sqrt()
    assert t in field, f"{M} and {S} have different discriminant classes"
    Z = _engine_identity_matrix(field, M.nrows())
    Z[-1, -1] = t
    X = (N2 * B2).inverse() * Z * N1 * B1
    assert X * M * X.transpose() == S
    return X


def _engine_odd_orthogonal_generators(gram, p):
    r"""Generators of ``O(gram)`` over ``GF(p)``, ``p`` odd, as matrices ``g`` with ``g gram g^T = gram``."""
    field = _engine_GF(p)
    n = gram.nrows()
    if n % 2 == 1:
        candidates = [(0, gram), (0, field(_nonsquare(field)) * gram)]
    else:
        candidates = [(1, gram), (-1, gram)]
    for epsilon, form in candidates:
        group = _engine_libgap.GO(epsilon, n, p)
        S = _engine_matrix(field, _engine_libgap.InvariantBilinearForm(group)["matrix"])
        if not (S.det() / form.det()).is_square():
            continue
        X = _isometry_between(form, S)
        Xi = X.inverse()
        gens = [Xi * _engine_matrix(field, g) * X for g in group.GeneratorsOfGroup()]
        assert all(g * gram * g.transpose() == gram for g in gens)
        return gens, SageZZ(group.Size())
    raise AssertionError(f"no orthogonal group of GAP preserves a form isometric to {gram}")


def _nonsquare(field):
    return next(x for x in field if x != 0 and not x.is_square())


def _engine_elementary_two_orthogonal_generators(quadratic):
    r"""Return the full group of a nonsingular quadratic form over GF(2).

    GAP Forms 1.3.0, chapter 5.3.1, supplies ``b`` taking each form to its
    canonical representative. Comparing the supplied form with GAP's GO
    form gives an exact conjugacy, hence the full group with the same order.
    https://gap-packages.github.io/forms/doc/chap5.html
    Quadratic matrices are compared through their quadratic polynomials,
    since congruent matrices in characteristic two need not be identical.
    """
    field = quadratic.base_ring()
    n = quadratic.nrows()
    assert field.cardinality() == 2 and n > 0 and n % 2 == 0
    assert (quadratic + quadratic.transpose()).rank() == n
    assert _engine_libgap.LoadPackage("forms"), "finite quadratic groups over GF(2) require GAP Forms"
    gap_field = _engine_libgap.GF(2)
    form = _engine_libgap.QuadraticFormByMatrix(quadratic, gap_field)
    witt_index = int(_engine_libgap.WittIndex(form))
    assert witt_index in (n // 2, n // 2 - 1)
    group = _engine_libgap.GO(1 if 2 * witt_index == n else -1, n, 2)
    standard = _engine_libgap.QuadraticFormByMatrix(
        _engine_libgap.InvariantQuadraticForm(group)["matrix"], gap_field,
    )
    assert _engine_libgap.GramMatrix(_engine_libgap.IsometricCanonicalForm(form)) == _engine_libgap.GramMatrix(_engine_libgap.IsometricCanonicalForm(standard))
    source_basis = _engine_matrix(field, _engine_libgap.BaseChangeToCanonical(form))
    standard_basis = _engine_matrix(field, _engine_libgap.BaseChangeToCanonical(standard))
    # Q_source = C Q_standard C^t as quadratic polynomials, so C g C^-1
    # transports the full standard group to the supplied generator basis.
    comparison = source_basis.inverse() * standard_basis
    inverse = comparison.inverse()
    generators = [comparison * _engine_matrix(field, generator) * inverse for generator in group.GeneratorsOfGroup()]
    for generator in generators:
        moved = _engine_libgap.QuadraticFormByMatrix(
            generator * quadratic * generator.transpose(), gap_field,
        )
        assert _engine_libgap.GramMatrix(moved) == _engine_libgap.GramMatrix(form)
    return generators, SageZZ(group.Size())
