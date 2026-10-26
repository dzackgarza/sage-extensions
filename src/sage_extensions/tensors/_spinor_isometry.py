r"""Exact indefinite isometry decisions through improper spinor genera.

This is Hecke ``e2ab5716135292294f5d5d9d34ed707b91e98b88``,
``QuadForm/IntegerLattices/ZLatticeMorphism.jl:755--916`` and
``PadicLift.jl:329--403``.  The input consists of integral Gram matrices
of nondegenerate indefinite lattices of rank at least three.  Rational
space isometry and local normal forms are supplied by Sage.  Reflection
decomposition and CRT give the rational weak approximation used by the
source; the index of the resulting intersection decides the improper
spinor genus [Conway--Sloane, Chapter 15, Theorems 14--15].

Only the decision is returned.  The rational approximation is not an
integral isometry and is never offered as one.
"""

from sage.arith.misc import CRT, gcd
from sage.matrix.constructor import matrix
from sage.modules.free_module import span
from sage.modules.free_module_element import vector
from sage.quadratic_forms.genera.genus import Genus
from sage.quadratic_forms.genera.normal_form import p_adic_normal_form
from sage.quadratic_forms.quadratic_form import QuadraticForm
from sage.rings.infinity import infinity
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


def _valuation(entries, prime):
    r"""The minimum valuation of a matrix or vector, including zero."""
    return min((entry.valuation(prime) for entry in entries.list()), default=infinity)


def _reflection(gram, direction):
    r"""The row action of the reflection in a nonisotropic direction."""
    square = direction * gram * direction
    return matrix.identity(QQ, gram.nrows()) - (
        QQ(2) / square
    ) * gram * direction.column() * direction.row()


def _reflection_approximation(gram, approximation, prime):
    r"""Hecke ``_decompose_in_reflections`` in a diagonal rational frame.

    The two choices ``g-e`` and ``g+e`` control denominator loss at each
    prime, including the extra factor of two in the dyadic case.  Return
    both the ordered reflection directions and the actual error valuation.
    """
    rank = gram.nrows()
    identity = matrix.identity(QQ, rank)
    remainder = approximation
    directions = []
    delta = 1 if prime == 2 else 0
    for index in range(rank):
        standard = identity.row(index)
        minus = remainder.row(index) - standard
        square = minus * gram * minus
        if square.valuation(prime) <= gram[index, index].valuation(prime) + 2 * delta:
            directions.append(minus)
            remainder = remainder * _reflection(gram, minus)
        else:
            plus = remainder.row(index) + standard
            directions.extend((plus, standard))
            remainder = remainder * _reflection(gram, plus) * _reflection(gram, standard)
    directions.reverse()
    exact = identity
    for direction in directions:
        exact = exact * _reflection(gram, direction)
    return directions, _valuation(approximation - exact, prime)


def _weak_approximation(gram, targets):
    r"""Hecke ``weak_approximation``: approximate finitely many local SO maps.

    Return ``None`` only when the supplied local approximations need more
    precision.  Otherwise reflection vectors are combined by CRT, with
    increasing precision until the exact rational product has every stated
    local accuracy.  No fixed precision cutoff is used.
    """
    identity = matrix.identity(QQ, gram.nrows())
    decompositions = []
    for approximation, prime, precision in targets:
        if (approximation.det() - 1).valuation(prime) < precision:
            return None
        directions, error = _reflection_approximation(gram, approximation, prime)
        if error < precision:
            return None
        assert len(directions) % 2 == 0, "a local SO map must have even reflection length"
        decompositions.append([
            vector(ZZ, direction.denominator() * direction)
            for direction in directions
        ])
    length = max(map(len, decompositions), default=0)
    standard = vector(ZZ, identity.row(0))
    for directions in decompositions:
        directions[:0] = [standard] * (length - len(directions))

    extra = 2 * gram.nrows() + 10
    while True:
        moduli = [prime ** (precision + extra) for _, prime, precision in targets]
        exact = identity
        for index in range(length):
            direction = vector(QQ, [
                CRT([directions[index][coordinate] for directions in decompositions], moduli)
                for coordinate in range(gram.nrows())
            ])
            if direction * gram * direction == 0:
                break
            exact = exact * _reflection(gram, direction)
        else:
            if all(
                _valuation(exact - approximation, prime) >= precision
                for approximation, prime, precision in targets
            ):
                return exact
        extra += 10


def _lift_matrix(padic_matrix):
    r"""Retain chosen rational representatives of finite-precision entries."""
    return matrix(
        QQ, padic_matrix.nrows(), padic_matrix.ncols(),
        [entry.lift() for entry in padic_matrix.list()],
    )


def _norm_generator(normal, prime):
    r"""Hecke ``_norm_generator`` for the first modular Jordan block."""
    row_valuations = [_valuation(row, prime) for row in normal.rows()]
    first_scale = row_valuations[0]
    assert first_scale == 0, "the lattice was scaled to bilinear scale one"
    index = next(
        (position - 1 for position, value in enumerate(row_valuations) if value != first_scale),
        normal.nrows() - 1,
    )
    standard = matrix.identity(QQ, normal.nrows())
    value = normal[index, index]
    if value != 0 and value.valuation(prime) <= 1:
        return standard.row(index)
    assert prime == 2 and index > 0, "the remaining first Jordan block must be dyadic hyperbolic"
    return standard.row(index) + standard.row(index - 1)


def _intersection_index(first, second):
    r"""Return ``[second : first intersect second]`` for rational row lattices."""
    left = span(first.rows(), ZZ)
    right = span(second.rows(), ZZ)
    return ZZ(left.intersection(right).index_in(right))


def _spinor_comparison_index(first, second):
    r"""Hecke ``_is_isometric_indef_approx`` in Sage's rational diagonal frame.

    The returned positive index is prime to ``2 det(first)``.  Its spinor
    operator is the difference of the improper spinor genera.  The input
    Gram matrices are integral of scale one and belong to the same genus.
    """
    first_form = QuadraticForm(QQ, 2 * first)
    diagonal_form, change = first_form.rational_diagonal_form(return_matrix=True)
    diagonal = diagonal_form.Gram_matrix_rational()
    first_basis = change.inverse().transpose()
    second_form = QuadraticForm(QQ, 2 * second)
    rational_map = second_form.is_rationally_isometric(diagonal_form, return_matrix=True)
    assert rational_map is not False, "lattices in one genus have isometric rational spaces"
    second_basis = rational_map.transpose()
    first_inverse = first_basis.inverse()
    second_inverse = second_basis.inverse()
    initial_index = _intersection_index(first_basis, second_basis)
    scale_bound = QQ(8) / gcd(first.inverse().list())
    bad_primes = (2 * ZZ(first.det())).prime_divisors()
    identity = matrix.identity(QQ, first.nrows())
    extra = 10
    while True:
        targets = []
        for prime in bad_primes:
            # The source's scale bound is supplemented by the valuation of
            # the chosen Sage coordinate maps.  This makes the conclusion
            # B_L f B_M^-1 in GL_n(Z_p) independent of the rational
            # diagonalization used by the backend.
            precision = max(
                scale_bound.valuation(prime) + 1,
                1 - _valuation(first_basis, prime) - _valuation(second_inverse, prime),
            )
            if initial_index.valuation(prime) == 0:
                targets.append((identity, prime, precision))
                continue
            local_precision = int(precision + 2 * first.nrows() + extra)
            normal_first, transform_first = p_adic_normal_form(first, prime, precision=local_precision)
            normal_second, transform_second = p_adic_normal_form(second, prime, precision=local_precision)
            assert normal_first == normal_second, "the local normal forms of one genus must agree"
            transform_first = _lift_matrix(transform_first)
            transform_second = _lift_matrix(transform_second)
            approximation = (
                first_inverse * transform_first.inverse() * transform_second * second_basis
            )
            if (approximation.det() - 1).valuation(prime) <= precision:
                direction = _norm_generator(_lift_matrix(normal_first), prime) * transform_first * first_basis
                approximation = _reflection(diagonal, direction) * approximation
            targets.append((approximation, prime, precision))
        exact = _weak_approximation(diagonal, targets)
        if exact is None:
            extra += 5
            continue
        index = _intersection_index(first_basis * exact, second_basis)
        assert all(index.valuation(prime) == 0 for prime in bad_primes), (
            "the weak approximation must identify the two lattices at every bad prime"
        )
        return index


def _isometric_indefinite(first, second):
    r"""Decide integral isometry for indefinite Gram matrices of rank at least 3.

    This uses strong approximation at the real place, so it requires no
    rational isotropic vector and no pair of rational hyperbolic planes.
    """
    content = gcd(second.list())
    first = matrix(QQ, first) / content
    second = matrix(QQ, second) / content
    genus = Genus(first.change_ring(ZZ))
    if genus != Genus(second.change_ring(ZZ)):
        return False
    operators, kernel = genus._improper_spinor_kernel()
    quotient = operators.quotient(kernel)
    if quotient.order() == 1:
        return True
    index = _spinor_comparison_index(first, second)
    return bool(quotient(operators.delta(index)).is_one())
