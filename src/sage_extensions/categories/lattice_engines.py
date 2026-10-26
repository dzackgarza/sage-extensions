r"""Private exact computational realizations for owned lattice constructions."""

from sage.arith.misc import gcd as engine_gcd
from sage.matrix.constructor import matrix as engine_matrix
from sage.matrix.matrix0 import Matrix
from sage.rings.integer import Integer as SageInteger
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.modules.free_module_element import vector as sage_vector
from itertools import combinations_with_replacement

from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
    _owned_engine_element,
)
from sage_extensions.categories.modules.framed.framed_free_modules import (
    FramedFreeModules,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.tensors.tensor import (
    Tensor,
    _engine_column_matrix_from_row_action,
    _engine_component_matrix,
    _engine_row_action_matrix,
    _engine_symmetrized_form_matrix,
    tensor,
)
from sage_extensions.validation import validator


@validator
def validate_isometric_embedding(embedding_datum):
    r"""Check that an engine's embedding ``A`` pulls the target Gram tensor ``G`` back to the source's: ``G(A-, A-) = G'``.

    ``embedding_datum`` is ``(target_gram, source_gram, embedding)`` as an
    engine returned it.  The engine's answer is untrusted; this law runs only
    when asked or under :data:`strict_checking`.
    """
    target_gram, source_gram, embedding = embedding_datum
    pulled_back = target_gram.pullback(embedding)
    if not pulled_back.is_equal_tensor(source_gram):
        raise ValueError(f"the embedding {embedding} into the form {target_gram} is not isometric: it pulls the target back to {pulled_back}, not {source_gram}")


@validator
def validate_even_unimodular_gram(gram):
    r"""Check that ``gram`` is symmetric, unimodular and even."""
    engine_gram = _engine_component_matrix(gram)
    if not engine_gram.is_symmetric():
        raise ValueError(f"the form {gram} is not symmetric")
    if abs(engine_gram.determinant()) != 1:
        raise ValueError(f"the form {gram} is not unimodular: its determinant is {engine_gram.determinant()}")
    if any(entry % 2 for entry in engine_gram.diagonal()):
        raise ValueError(f"the form {gram} is not even: some diagonal entry is odd")


@validator
def validate_lattice_signature(data):
    r"""Check that a computed lattice has the requested signature pair."""
    lattice, expected = data
    actual = lattice.signature_pair()
    if actual != expected:
        raise ValueError(
            f"the computed lattice {lattice} has signature {actual}, not {expected}"
        )


def _signed_diagonal_direction(gram, sign, engine_field):
    r"""Select a column of exact congruence diagonalization with the requested sign.

    This is the shared diagonalization step of the port's positive-direction
    and negative-direction-in-span computations. A subspace supplies its own
    restricted Gram tensor through its formed subobject construction.
    """
    from sage.quadratic_forms.quadratic_form import QuadraticForm

    if not isinstance(gram, Tensor) or gram.tensor_valence() != (NN**2)((0, 2)):
        raise TypeError(f"cannot find a vector of positive square for {gram}: it must be the Gram tensor of a bilinear form, a tensor of type (0, 2)")
    engine_hessian = _engine_symmetrized_form_matrix(gram).change_ring(engine_field)
    diagonal, change = QuadraticForm(engine_field, engine_hessian).rational_diagonal_form(return_matrix=True)
    diagonal_matrix = diagonal.matrix()
    index = next((
        index for index in range(diagonal_matrix.nrows())
        if sign * diagonal_matrix[index, index] > 0
    ), None)
    return None if index is None else change.column(index)


def _rational_positive_vector(gram):
    r"""Return one rational positive vector as a type-``(1,0)`` tensor."""
    column = _signed_diagonal_direction(gram, 1, SageQQ)
    if column is None:
        raise ValueError(f"the form with Gram tensor {gram} has no positive direction")
    rationals = gram.base_ring().fraction_field()
    return tensor.vector(
        rationals,
        tuple(_owned_engine_element(rationals, entry) for entry in column),
    )


def _congruence_diagonalization(lattice):
    r"""Raise Sage's diagonal form and transformation as an isometry.

    ``QuadraticForm.rational_diagonal_form(return_matrix=True)`` returns
    ``(D,T)`` with ``T.transpose()*G*T == D.matrix()``. The columns of T
    are the images of the new basis in the original space. No transpose
    or change of scalar field is made while raising this datum.
    """
    from sage_extensions.categories._lattice import _congruence_diagonal_form
    from sage_extensions.categories.lattices import Lattices
    from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
    from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers
    from sage_extensions.rings.real import RR

    ring = lattice.base_ring()
    if ring is _owned_real_algebraic_numbers() or (
        ring is RR and lattice in FormModules(RR).Nondegenerate()
    ):
        return _exact_real_diagonalization(lattice)
    diagonal, change = _congruence_diagonal_form(lattice.gram_tensor())
    gram = diagonal.matrix()
    normal = Lattices(ring)([
        [_owned_engine_element(ring, entry) for entry in row]
        for row in gram.rows()
    ]) if gram.nrows() else Lattices(ring)(0)
    images = tuple(
        lattice.linear_combination({
            label: _owned_engine_element(ring, entry)
            for label, entry in zip(lattice.module_generating_set(), column, strict=True)
        })
        for column in change.columns()
    )
    return normal.Isom(lattice)(images)


def _exact_real_diagonalization(lattice):
    r"""Diagonalize a finite exact real form with inverse maps.

    Basis directions and pairwise sums contain a nonisotropic direction
    outside the radical. Over AA, exact zero decisions also identify a
    remaining radical. For promised nonsingular RR input, refine all norm
    enclosures together until one excludes zero. Fraction-free projection
    and elementary inverse-row updates retain both maps. ``TRAPS.md``
    records why AA does not use Sage's rational diagonal form here.
    See docs/theory/hyperbolic-index.md for termination and the map equations.
    """
    from sage.rings.real_arb import RealBallField
    from sage_extensions.categories.lattices import Lattices
    from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers
    from sage_extensions.rings.real import RR

    ring = lattice.base_ring()
    assert ring in (_owned_real_algebraic_numbers(), RR)
    basis = list(lattice.module_generators())
    size = len(basis)
    inverse = [[ring(int(i == j)) for j in range(size)] for i in range(size)]
    diagonal = []
    for position in range(size):
        indices = (
            [(i, i) for i in range(position, size)]
            + [(i, j) for i in range(position, size) for j in range(i + 1, size)]
        )
        vectors = [basis[i] if i == j else basis[i] + basis[j] for i, j in indices]
        norms = [lattice.q(vector) for vector in vectors]
        if ring is RR:
            precision = 128
            selected = None
            while selected is None:
                field = RealBallField(precision)
                for index, norm in enumerate(norms):
                    enclosure = norm._arb_(field)
                    if enclosure.is_finite() and enclosure.is_nonzero():
                        selected = index
                        break
                precision *= 2
        else:
            selected = next((i for i, norm in enumerate(norms) if norm != ring.zero()), None)
            if selected is None:
                diagonal.extend([ring.zero()] * (size - position))
                break

        first, second = indices[selected]
        pivot, norm = vectors[selected], norms[selected]
        basis[position], basis[first] = basis[first], basis[position]
        inverse[position], inverse[first] = inverse[first], inverse[position]
        if first != second:
            # Adding column second to the pivot subtracts the pivot row
            # from inverse row second; second > first >= position.
            basis[position] = pivot
            inverse[second] = [
                inverse[second][j] - inverse[position][j] for j in range(size)
            ]

        pairings = [lattice.b(pivot, basis[j]) for j in range(position + 1, size)]
        for index, target in enumerate(range(position + 1, size)):
            basis[target] = norm * basis[target] - pairings[index] * pivot
            inverse[target] = [
                RR._divide_by_nonzero(entry, norm) if ring is RR else entry / norm
                for entry in inverse[target]
            ]
        inverse[position] = [
            inverse[position][j] + sum(
                (pairing * inverse[target][j]
                 for pairing, target in zip(pairings, range(position + 1, size), strict=True)),
                ring.zero(),
            )
            for j in range(size)
        ]
        diagonal.append(norm)

    category = Lattices(ring)
    normal = category([
        [diagonal[i] if i == j else ring.zero() for j in range(size)]
        for i in range(size)
    ]) if size else category(0)
    forward = normal.module_category().Mor(normal, lattice)(tuple(basis))
    labels = tuple(normal.module_generating_set())
    backward = lattice.module_category().Mor(lattice, normal)(tuple(
        normal.linear_combination({label: inverse[i][j] for i, label in enumerate(labels)})
        for j in range(size)
    ))
    module_isomorphism = normal.module_category().Core().Mor(normal, lattice)._from_known_inverse_pair(
        forward, backward,
    )
    isometries = normal.Isom(lattice)
    return isometries.element_class(isometries, module_isomorphism)


def _real_representation_witness(lattice, value):
    r"""Find a nonzero exact real vector of the requested norm, or return None.

    Use the retained congruence-diagonalization isometry. A nonzero value
    is represented exactly when a diagonal entry has the same sign; the
    positive square root of their ratio supplies its scale. Zero is
    represented nontrivially by a radical basis vector, or by the sum of
    opposite-sign basis vectors normalized to squares +1 and -1. If none
    of these cases applies, the diagonal form excludes a nonzero point.

    For promised nonsingular RR input, diagonal squares are nonzero.
    Their signs are found by enclosure refinement and root/quotient
    arithmetic consumes those hypotheses. The requested value must still
    have a decided zero status; arbitrary real equality is not decidable.
    """
    from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
    from sage_extensions.rings.real import RR

    ring = lattice.base_ring()
    diagonalization = lattice.diagonalization()
    vectors = tuple(
        diagonalization(generator)
        for generator in diagonalization.domain().module_generators()
    )
    positive = None
    negative = None
    if ring is RR and lattice in FormModules(RR).Nondegenerate():
        zero_value = bool(value == ring.zero())
        value_sign = 0 if zero_value else ring._sign_of_nonzero(value)
        for vector in vectors:
            square = lattice.q(vector)
            sign = ring._sign_of_nonzero(square)
            if not zero_value:
                if sign == value_sign:
                    ratio = ring._divide_by_nonzero(value, square)
                    return vector * ring._sqrt_of_positive(ratio)
            else:
                root = ring._sqrt_of_positive(square if sign > 0 else -square)
                normalized = vector * ring._divide_by_nonzero(ring.one(), root)
                if sign > 0:
                    positive = normalized
                else:
                    negative = normalized
                if positive is not None and negative is not None:
                    return positive + negative
        return None
    for vector in vectors:
        square = lattice.q(vector)
        if value != ring.zero():
            if value * square > ring.zero():
                return vector * (value / square).sqrt()
        elif square == ring.zero():
            return vector
        elif square > ring.zero():
            positive = vector * (ring.one() / square.sqrt())
        else:
            negative = vector * (ring.one() / (-square).sqrt())
    if value == ring.zero() and positive is not None and negative is not None:
        return positive + negative
    return None


def _real_witt_bases(lattice):
    r"""Raise an exact real Witt basis using congruence diagonalization.

    Private supplier to ``Lattices.witt_decomposition``. Sage's
    ``QuadraticForm.rational_diagonal_form(return_matrix=True)`` returns
    ``(D,T)`` with ``T.transpose()*G*T == D.matrix()``. Its columns are
    therefore an orthogonal basis in the input space. Normalize each
    positive or negative vector to square +1 or -1 using the positive
    square root in the selected real field. For an orthogonal pair p,n of
    these squares, e=p+n and f=(p-n)/2 have Gram U. The unpaired vectors all have the
    same sign, so their span is anisotropic.

    The input is a finite nondegenerate symmetric space over AA or the
    represented exact RR field. Each diagonal square is nonzero; over RR
    convergent enclosures therefore determine its sign by refinement.
    Positive roots and quotients use these established hypotheses rather
    than new bounded predicate queries. No approximate root or
    exhaustive real iterator is used.
    Sage documents the retained transformation in
    ``quadratic_form__local_field_invariants.rational_diagonal_form``.
    """
    from sage_extensions.categories.sets.finite_families import finite_family

    ring = lattice.base_ring()
    _diagonalization, positive_data, negative_data = _real_normalized_diagonal_basis(lattice)
    positive = [entry[2] for entry in positive_data]
    negative = [entry[2] for entry in negative_data]
    index = min(len(positive), len(negative))
    hyperbolic = tuple(
        vector
        for p, n in zip(positive[:index], negative[:index], strict=True)
        for vector in (p + n, (p - n) * (ring.one() / ring(2)))
    )
    anisotropic = (*positive[index:], *negative[index:])
    return finite_family(anisotropic), finite_family(hyperbolic)


def _real_normalized_diagonal_basis(lattice):
    r"""Retain diagonal labels, positive root scales and normalized vectors."""
    from sage_extensions.rings.real import RR

    ring = lattice.base_ring()
    diagonalization = lattice.diagonalization()
    positive, negative = [], []
    for label in diagonalization.domain().module_generating_set():
        vector = diagonalization(diagonalization.domain().module_generator(label))
        square = lattice.q(vector)
        sign = ring._sign_of_nonzero(square) if ring is RR else (1 if square > 0 else -1)
        if ring is RR:
            root = ring._sqrt_of_positive(square if sign > 0 else -square)
            normalized = vector * ring._divide_by_nonzero(ring.one(), root)
        else:
            root = (square if sign > 0 else -square).sqrt()
            normalized = vector * (ring.one() / root)
        if sign > 0:
            positive.append((label, root, normalized))
        else:
            negative.append((label, root, normalized))
    return diagonalization, positive, negative


def _real_witt_decomposition(lattice):
    r"""Assemble the real Witt isometry with explicit inverse coordinates.

    If x has diagonal coordinates c_i and v_i=r_i p_i, its normalized
    coordinates are r_i c_i. For e=p+n, f=(p-n)/2, the coordinates become
    ((a+b)/2, a-b). No span or inverse is rediscovered.
    """
    from sage_extensions.categories.lattices import Lattices

    ring = lattice.base_ring()
    diagonalization, positive, negative = _real_normalized_diagonal_basis(lattice)
    index = min(len(positive), len(negative))
    remaining = (*positive[index:], *negative[index:])
    signs = [1] * (len(positive) - index) + [-1] * (len(negative) - index)
    complement = Lattices(ring)([
        [ring(signs[i]) if i == j else ring.zero() for j in range(len(signs))]
        for i in range(len(signs))
    ]) if signs else Lattices(ring)(0)
    hyperbolic = Lattices(ring)("U") ** index
    normal = Lattices(ring).orthogonal_sum((hyperbolic, complement))
    half = ring.one() / ring(2)
    images = tuple(
        vector
        for p, n in zip(positive[:index], negative[:index], strict=True)
        for vector in (p[2] + n[2], (p[2] - n[2]) * half)
    )
    h_labels = tuple(hyperbolic.module_generating_set())
    a_labels = tuple(complement.module_generating_set())
    h_projection, a_projection = normal.projection(0), normal.projection(1)

    def forward_image(label):
        generator = normal.module_generator(label)
        h, a = h_projection(generator), a_projection(generator)
        return sum(
            (image * h(key) for key, image in zip(h_labels, images, strict=True)),
            lattice.zero(),
        ) + sum(
            (entry[2] * a(key) for key, entry in zip(a_labels, remaining, strict=True)),
            lattice.zero(),
        )

    h_inclusion, a_inclusion = normal.injection(0), normal.injection(1)

    def backward_image(label):
        coordinates = diagonalization.inverse()(lattice.module_generator(label))
        h_coefficients = []
        for p, n in zip(positive[:index], negative[:index], strict=True):
            a, b = p[1] * coordinates(p[0]), n[1] * coordinates(n[0])
            h_coefficients.extend(((a + b) * half, a - b))
        h = hyperbolic.linear_combination(dict(zip(h_labels, h_coefficients, strict=True)))
        a = complement.linear_combination({
            key: entry[1] * coordinates(entry[0])
            for key, entry in zip(a_labels, remaining, strict=True)
        })
        return h_inclusion(h) + a_inclusion(a)

    forward = normal.module_category().Mor(normal, lattice)(forward_image)
    backward = lattice.module_category().Mor(lattice, normal)(backward_image)
    module_isomorphism = normal.module_category().Core().Mor(normal, lattice)._from_known_inverse_pair(
        forward, backward,
    )
    isometries = normal.Isom(lattice)
    return isometries.element_class(isometries, module_isomorphism)


def _raise_lattice_direction(lattice, coordinates):
    r"""Raise a scalar-field direction, primitively over ZZ, in its given module."""
    ring = lattice.base_ring()
    engine_ring = _engine_ring(ring)
    if engine_ring is SageZZ:
        integral = sage_vector(SageZZ, coordinates * coordinates.denominator())
        content = engine_gcd(tuple(integral))
        if not content:
            raise ValueError("the zero vector has no primitive part")
        coordinates = tuple(coordinate // content for coordinate in integral)
    return lattice.linear_combination({
        label: _owned_engine_element(ring, engine_ring(coordinate))
        for label, coordinate in zip(lattice.module_generating_set(), coordinates, strict=True)
        if coordinate
    })


def _signed_vector_witness(lattice, sign):
    r"""Realize the norm-sign operation on a finite framed form module.

    Private computation for ``FormModules.vector_of_sign``.
    The input retains its own form and selected framing; the raised vector
    belongs to that same module, including a represented formed submodule.
    The symmetric Hessian ``G + G.transpose()`` represents the diagonal
    function of any bilinear Gram ``G``. For a quadratic datum, its polar
    diagonal is twice its selected norm, so its symmetrization has four
    times that norm. These positive factors preserve the sign over QQ and AA.
    Return None only if exact diagonalization excludes the sign.
    """
    from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers

    ring = lattice.base_ring()
    from sage_extensions.rings.real import RR
    from sage_extensions.categories.lattices import Lattices

    if ring is RR and lattice in Lattices(RR):
        return _real_representation_witness(lattice, ring(sign))
    assert (_engine_ring(ring) is SageZZ or _engine_ring(ring) is SageQQ
            or ring is _owned_real_algebraic_numbers()), (
        f"signed vector witnesses are computed over ZZ, QQ or AA, not {ring}"
    )
    assert lattice.value_module() is ring, (
        f"signed-vector computation needs values in the scalar ring {ring}, not {lattice.value_module()}"
    )
    assert lattice in FramedFreeModules(ring), (
        f"signed-vector computation needs a selected free framing on {lattice}"
    )
    assert lattice.module_rank().is_finite(), (
        f"diagonalization requires finite rank, not {lattice.module_rank()}"
    )
    if lattice.module_rank() == 0:
        return None
    coordinates = _signed_diagonal_direction(
        lattice.gram_tensor(), sign, _engine_ring(ring.fraction_field())
    )
    return None if coordinates is None else _raise_lattice_direction(lattice, coordinates)


def _isotropic_vector_witness(lattice):
    r"""Raise PARI's rational isotropic vector into the given lattice.

    Migrated from ``sage-indefinite-port``'s ``find_hyperbolic_pair``.
    Sage's ``quadratic_forms.qfsolve.qfsolve`` returns an integer obstruction,
    a vector, or a matrix whose columns span the radical. Integral inputs
    receive a primitive integral vector after clearing denominators.
    """
    ring = lattice.base_ring()
    engine_ring = _engine_ring(ring)
    assert engine_ring is SageZZ or engine_ring is SageQQ, (
        f"isotropic witnesses are computed over ZZ or QQ, not {ring}"
    )
    assert lattice.module_rank().is_finite(), (
        f"PARI isotropic witnesses require finite rank, not {lattice.module_rank()}"
    )
    if lattice.module_rank() == 0:
        return None
    from sage.quadratic_forms.qfsolve import qfsolve

    solution = qfsolve(_engine_component_matrix(lattice.gram_tensor()).change_ring(SageQQ))
    if isinstance(solution, SageInteger):
        return None
    if isinstance(solution, Matrix):
        solution = solution.column(0)
    return _raise_lattice_direction(lattice, solution)


def _rational_witt_index(space):
    r"""Count exact rational hyperbolic splittings of a nondegenerate space.

    This is Hecke ``e2ab5716``, ``Quad/Spaces.jl:1751--1815``:
    find an isotropic vector, split off its hyperbolic plane, and repeat
    on the perpendicular until the remainder is anisotropic.  The number
    of planes is the Witt index (O'Meara, §42F).

    If ``e`` is isotropic and ``d = b(e,h) != 0``, then
    ``f = h/d - q(h)e/(2d^2)`` satisfies ``q(f)=0`` and ``b(e,f)=1``.
    Nondegeneracy supplies such an ``h`` among the module generators.
    The retained subobject and its orthogonal complement perform the
    splitting; only the existing isotropic-witness owner lowers the Gram
    tensor for PARI's exact rational solvability decision.
    """
    field = space.base_ring()
    assert (
        _engine_ring(field) is SageQQ
        and space.module_rank().is_finite()
        and space.is_nondegenerate()
    ), f"rational Witt index requires a nondegenerate finite-dimensional QQ-space, not {space}"
    index = SageZZ.zero()
    remainder = space
    while int(remainder.module_rank()) >= 2:
        isotropic = _isotropic_vector_witness(remainder)
        if isotropic is None:
            break
        partner = next(
            generator for generator in remainder.module_generators()
            if remainder.b(isotropic, generator) != field.zero()
        )
        pairing = remainder.b(isotropic, partner)
        partner = remainder.scalar_multiple(field.one() / pairing, partner)
        partner -= remainder.scalar_multiple(
            remainder.q(partner) / field(2), isotropic
        )
        plane = remainder.subobject_on((isotropic, partner))
        remainder = plane.orthogonal_complement()
        index += 1
    return index


def _unit_divisibility_isotropic_witness(lattice):
    r"""Select a primitive integral null vector of divisibility one.

    Enumerate integral vectors by increasing l1-height.  If the lattice
    splits a hyperbolic plane, the basis image of either null generator
    occurs at finite height, so the search terminates under that existence
    hypothesis.  The scalar Gram calculation is a private exact engine
    realization; the result is raised in the original lattice.
    """
    gram = _engine_component_matrix(lattice.gram_tensor()).change_ring(SageZZ)
    rank = gram.nrows()
    directions = tuple((coordinate, sign) for coordinate in range(rank) for sign in (-1, 1))
    height = 1
    while True:
        for selected in combinations_with_replacement(directions, height):
            entries = [SageZZ.zero()] * rank
            for coordinate, sign in selected:
                entries[coordinate] += sign
            if sum(abs(entry) for entry in entries) != height:
                continue
            vector = sage_vector(SageZZ, entries)
            pairings = gram * vector
            if vector.dot_product(pairings) != 0:
                continue
            divisor = SageZZ.zero()
            for pairing in pairings:
                divisor = divisor.gcd(pairing)
            if divisor == 1:
                return _raise_lattice_direction(lattice, vector)
        height += 1


def _binary_form_discriminant(lattice):
    r"""Private binary-form datum for the lattice square-fibre operations."""
    if _engine_ring(lattice.base_ring()) is not SageZZ or lattice.module_rank() != 2:
        raise ValueError("binary square-fibre computation requires a rank-two ZZ-lattice")
    gram = _engine_component_matrix(lattice.gram_tensor())
    return gram[0, 1] ** 2 - gram[0, 0] * gram[1, 1]


def _split_binary_vectors_of_square(lattice, square):
    r"""All vectors of nonzero square for a split nondegenerate binary form.

    Sage's ``BinaryQF.solve_integer`` reduces a reducible form by an integral
    unimodular change of variables to ``A X^2 + B X Y`` and tests divisors of
    the target.  Apply the same maintained reduction to every signed divisor,
    rather than returning its single representative, to obtain the full
    finite fibre.
    """
    discriminant = _binary_form_discriminant(lattice)
    if not square or discriminant <= 0 or not discriminant.is_square():
        raise ValueError("a finite split binary square fibre requires nonzero square and positive square discriminant")
    gram = _engine_component_matrix(lattice.gram_tensor())
    a, b, c = gram[0, 0], 2 * gram[0, 1], gram[1, 1]
    polynomial_discriminant = b * b - 4 * a * c
    root = polynomial_discriminant.sqrt()
    if a:
        slope = (-b + (root if root != b else -root)) / (2 * a)
        p, q = slope.as_integer_ratio()
        _gcd, u, v = p.xgcd(q)
    elif c:
        v, p, u, q = SageZZ.zero(), SageZZ.one(), -SageZZ.one(), SageZZ.zero()
    else:
        v, p, u, q = SageZZ.one(), SageZZ.zero(), SageZZ.zero(), SageZZ.one()
    transformed_a = a * v * v - b * u * v + c * u * u
    transformed_b = 2 * a * v * p + b * (v * q - u * p) - 2 * c * u * q
    target = _engine_ring(lattice.base_ring())(square)
    signed_divisors = tuple(
        sign * divisor
        for divisor in abs(target).divisors()
        for sign in (SageZZ.one(), -SageZZ.one())
    )
    solutions = set()
    for x in signed_divisors:
        numerator = target // x - transformed_a * x
        if transformed_b.divides(numerator):
            y = numerator // transformed_b
            solutions.add((v * x + p * y, -u * x + q * y))
    labels = tuple(lattice.module_generating_set())
    ring = lattice.base_ring()
    return tuple(
        lattice.linear_combination({label: ring(int(coordinate)) for label, coordinate in zip(labels, solution, strict=True)})
        for solution in sorted(solutions)
    )


def _binary_primitive_isotropic_vectors(lattice):
    r"""Raise the primitive generators of the rational linear factors, with both signs."""
    discriminant = _binary_form_discriminant(lattice)
    if not discriminant:
        raise ValueError("this finite null-line computation requires a nondegenerate binary form")
    if discriminant < 0 or not discriminant.is_square():
        return ()
    gram = _engine_component_matrix(lattice.gram_tensor())
    a, b, c = gram[0, 0], 2 * gram[0, 1], gram[1, 1]
    root = discriminant.sqrt()
    if a:
        directions = tuple(
            (-b + sign * 2 * root, 2 * a)
            for sign in (SageZZ.one(), -SageZZ.one())
        )
    else:
        directions = (
            (SageZZ.one(), SageZZ.zero()),
            (c, -b),
        )
    labels = tuple(lattice.module_generating_set())
    ring = lattice.base_ring()
    primitive = tuple(
        lattice.linear_combination(
            {
                label: ring(int(coordinate // engine_gcd(direction)))
                for label, coordinate in zip(labels, direction, strict=True)
                if coordinate
            }
        )
        for direction in directions
    )
    return tuple(vector for point in primitive for vector in (point, -point))


def _split_binary_orthogonal_group_generators(lattice):
    r"""Generators of the integral orthogonal group of a nondegenerate split binary lattice.

    An isometry is determined by the images of the two framed generators.
    Each image lies in the finite fibre of the corresponding diagonal Gram
    entry (or on one of the four primitive null rays), their pairing is the
    off-diagonal entry, and their coordinate determinant is a unit.  Since
    ``SO(L) = {+-1}``, negation and one determinant-minus-one element, when
    that coset exists, generate all of ``O(L)``.
    """
    gram = _engine_component_matrix(lattice.gram_tensor())
    discriminant = _binary_form_discriminant(lattice)
    if not discriminant or discriminant <= 0 or not discriminant.is_square():
        raise ValueError("explicit split-binary isometries require a nondegenerate square discriminant")
    first = (
        _binary_primitive_isotropic_vectors(lattice)
        if gram[0, 0] == 0
        else _split_binary_vectors_of_square(lattice, gram[0, 0])
    )
    second = (
        _binary_primitive_isotropic_vectors(lattice)
        if gram[1, 1] == 0
        else _split_binary_vectors_of_square(lattice, gram[1, 1])
    )
    labels = tuple(lattice.module_generating_set())
    negative_first_basis = (-SageZZ.one(), SageZZ.zero())
    negative_second_basis = (SageZZ.zero(), -SageZZ.one())
    negation = None
    reversing = None
    for left in first:
        left_coordinates = tuple(
            _engine_element(lattice.base_ring(), left.to_vector()(label)) for label in labels
        )
        for right in second:
            right_coordinates = tuple(
                _engine_element(lattice.base_ring(), right.to_vector()(label)) for label in labels
            )
            cross_pairing = sum(
                left_coordinates[row] * gram[row, column] * right_coordinates[column]
                for row in range(2)
                for column in range(2)
            )
            if cross_pairing != gram[0, 1]:
                continue
            determinant = (
                left_coordinates[0] * right_coordinates[1]
                - left_coordinates[1] * right_coordinates[0]
            )
            if abs(determinant) == SageZZ.one():
                images = dict(zip(labels, (left, right), strict=True))
                if (
                    left_coordinates == negative_first_basis
                    and right_coordinates == negative_second_basis
                ):
                    negation = images
                elif determinant == -SageZZ.one() and reversing is None:
                    reversing = images
    assert negation is not None, "negation is an isometry of every binary lattice"
    return (negation,) if reversing is None else (negation, reversing)


def _rational_representation_witness(lattice, value):
    r"""Return a vector ``x`` of the nondegenerate ``QQ``-lattice with ``b(x, x) = value``, or ``None``.

    ``value`` is a nonzero element of the base ring, so ``b perp <-value>`` is
    nondegenerate and ``qfsolve`` returns either PARI's integer obstruction
    or one isotropic vector, never a matrix spanning a radical.  The space represents
    ``a != 0`` exactly when ``b perp <-a>`` represents 0 (Serre, *A Course
    in Arithmetic*, Ch. IV, 1.6, Cor. 1 of Prop. 3'), and PARI's
    ``qfsolve`` decides that isotropy (Hasse--Minkowski, Ch. IV, 3.2,
    Thm. 8).  A zero ``(x, z)`` with ``z != 0`` gives ``b(x/z, x/z) = a``.
    A zero with ``z = 0`` is a nonzero isotropic ``x`` of ``L``, and then
    every value is represented (Ch. IV, 1.3, Cor. of Prop. 3): with Gram
    matrix ``G``, ``y = G x`` has ``b(x, y) = (G x) . (G x) != 0``, and
    ``y + t x`` with ``t = (a - b(y, y)) / (2 b(x, y))`` has square ``a``.
    """
    assert _engine_ring(lattice.base_ring()) is SageQQ, (
        f"the rational representation witness is computed over QQ, not {lattice.base_ring()}"
    )
    gram = _engine_component_matrix(lattice.gram_tensor()).change_ring(SageQQ)
    rank = gram.nrows()
    augmented = gram.block_sum(engine_matrix(SageQQ, [[-SageQQ(_engine_element(lattice.base_ring(), value))]]))
    from sage.quadratic_forms.qfsolve import qfsolve

    solution = qfsolve(augmented)
    if solution in SageZZ:
        return None
    last = solution[rank]
    isotropic = solution[:rank]
    if last:
        return _raise_lattice_direction(lattice, isotropic / last)
    partner = gram * isotropic
    pairing = isotropic * gram * partner
    shift = (SageQQ(_engine_element(lattice.base_ring(), value)) - partner * gram * partner) / (2 * pairing)
    return _raise_lattice_direction(lattice, partner + shift * isotropic)


def _binary_special_orthogonal_representatives(lattice, square):
    r"""Raise PARI representatives for a nonsplit indefinite binary form.

    PARI ``qfbsolve`` flag 3 includes imprimitive solutions and returns
    every class modulo the integral special orthogonal group:
    https://pari.math.u-bordeaux.fr/dochtml/html-stable/Arithmetic_functions.html#qfbsolve
    """
    ring = lattice.base_ring()
    if _engine_ring(ring) is not SageZZ or lattice.module_rank() != 2:
        raise ValueError("binary representation classes require a rank-two ZZ-lattice")
    gram = _engine_component_matrix(lattice.gram_tensor())
    from sage.quadratic_forms.binary_qf import BinaryQF

    form = BinaryQF((gram[0, 0], 2 * gram[0, 1], gram[1, 1]))
    discriminant = form.discriminant()
    if discriminant <= 0 or discriminant.is_square():
        raise ValueError("this binary representation computation requires positive nonsquare discriminant")
    if not square:
        return (lattice.zero(),)
    labels = tuple(lattice.module_generating_set())
    return tuple(
        lattice.linear_combination({label: _owned_engine_element(ring, SageZZ(coordinate)) for label, coordinate in zip(labels, solution, strict=True)})
        for solution in form.solve_integer(SageZZ(int(square)), _flag=3)
    )


def _binary_reduction_cycle(lattice, bound, start):
    r"""Dispatch the oriented edgewalk cycle to its specialized implementation."""
    from sage_indefinite_port.indefinite.edgewalk_rank2 import anisotropic_cycle

    rational_bound = lattice.base_ring().fraction_field()(bound)
    engine_bound = SageQQ(int(rational_bound.numerator())) / int(rational_bound.denominator())
    return anisotropic_cycle(lattice, engine_bound, start)


def _integer_engine_matrix(value):
    if not isinstance(value, Tensor) or value.tensor_order() != 2:
        raise TypeError(f"{value} cannot be passed to OSCAR as an integer matrix: it must be a tensor with two indices")
    return _engine_component_matrix(value).change_ring(SageZZ)


def _rational_engine_matrix(value):
    if not isinstance(value, Tensor) or value.tensor_order() != 2:
        raise TypeError(f"{value} cannot be passed to OSCAR as a rational matrix: it must be a tensor with two indices")
    return _engine_component_matrix(value).change_ring(SageQQ)


def _gap_rational_spinor_norm_class(gram, isometry):
    r"""Return a representative in \(\mathbb Q^\times\) of the spinor norm of ``isometry`` on \((\mathbb Q^n, b)\), ``gram`` the Gram tensor of \(b\).

    Private adapter for ``_rational_spinor_norm_representative`` in
    ``lattice_morphisms.py``.  For \(g\in O(V)\) let \(W=\operatorname{im}(1-g)\)
    and \([w, w']=2b(u, w')\) for \(w=u(1-g)\): the discriminant of this Wall
    form on \(W\) is the class \(b(v_1,v_1)\cdots b(v_m,v_m)\) for
    \(g=s_{v_1}\cdots s_{v_m}\) (Taylor, *The Geometry of the Classical
    Groups*, p. 163).  GAP's ``WallForm`` (``grp/classic.gi``) computes the
    Wall form over any field; both GAP and the lowered isometry act on rows.
    For \(g=1\), \(W=0\) and the class is \(1\).  The route and its
    measurement are the ``TRAPS.md`` row on the rational spinor norm.
    """
    row_action = _engine_row_action_matrix(isometry).change_ring(SageQQ)
    if row_action.is_one():
        return SageQQ.one()
    from sage.libs.gap.libgap import libgap

    wall_form = libgap.WallForm(libgap(2 * _rational_engine_matrix(gram)), libgap(row_action))
    value = SageQQ(libgap.DeterminantMat(wall_form["form"]).sage())
    if value == 0:
        raise ArithmeticError(f"GAP computed a degenerate Wall form for the isometry {isometry} of the form {gram}, but the Wall form of an isometry of a nondegenerate space is nondegenerate")
    return value


def _owned_embedding_from_row_action(ring, row_action):
    r"""Raise an OSCAR embedding, which lists source generator images as rows, to an owned matrix Mor."""
    columns = _engine_column_matrix_from_row_action(row_action)
    return ring.matrix_space(columns.nrows(), columns.ncols()).from_rows(
        tuple(tuple(_owned_engine_element(ring, entry) for entry in row) for row in columns.rows())
    )


def _number_field_descriptor(field):
    r"""Return the selected absolute number field as rational power-basis data."""
    from sage.categories.number_fields import NumberFields as SageNumberFields

    engine = _engine_ring(field)
    assert engine in SageNumberFields() and engine is not SageQQ, f"the OSCAR number-field lattice adapter needs a nontrivial absolute number field, but got {field}"
    assert engine.is_absolute(), (
        f"the OSCAR number-field lattice adapter needs an absolute primitive-element presentation, but {field} is represented as a relative number field"
    )
    polynomial = engine.defining_polynomial()
    return tuple(SageQQ(coefficient) for coefficient in polynomial.list())


def _number_field_element_coefficients(field, value):
    r"""Return ``value`` in the selected power basis of the Sage realization of ``field``."""
    engine = _engine_ring(field)
    element = engine(value)
    coefficients = list(element.list())
    coefficients.extend([SageQQ.zero()] * (engine.degree() - len(coefficients)))
    return tuple(SageQQ(coefficient) for coefficient in coefficients)


def _number_field_coefficient_rows(engine, field):
    r"""Write a Sage matrix over ``field`` as nested rational power-basis coefficients."""
    return [[list(_number_field_element_coefficients(field, engine[row, column])) for column in range(engine.ncols())] for row in range(engine.nrows())]


def _number_field_engine_matrix(value, field):
    r"""Lower a two-index tensor to nested rational power-basis coefficients."""
    if not isinstance(value, Tensor) or value.tensor_order() != 2:
        raise TypeError(f"{value} cannot be passed to OSCAR as a number-field matrix: it must be a tensor with two indices")
    return _number_field_coefficient_rows(_engine_component_matrix(value), field)


_OSCAR_LATTICE_ADAPTER_SOURCE = r"""
module DzackResearchOscarLatticeAdapter
using Oscar

function _zz_matrix(entries)
    rows, columns = size(entries)
    return matrix(
        ZZ,
        rows,
        columns,
        [ZZ(entries[i, j]) for i in 1:rows for j in 1:columns],
    )
end

function _qq_matrix(entries)
    rows, columns = size(entries)
    return matrix(
        QQ,
        rows,
        columns,
        [QQ(entries[i, j]) for i in 1:rows for j in 1:columns],
    )
end

function _number_field(defining_coefficients)
    QQx, x = polynomial_ring(QQ, "a")
    polynomial = sum(
        QQ(defining_coefficients[i]) * x^(i - 1)
        for i in eachindex(defining_coefficients)
    )
    return number_field(polynomial, "a")
end

function _number_field_element(K, a, coefficients)
    return sum(
        K(QQ(coefficients[i])) * a^(i - 1)
        for i in eachindex(coefficients)
    )
end

function _number_field_matrix(K, a, entries)
    rows = length(entries)
    columns = rows == 0 ? 0 : length(entries[1])
    return matrix(
        K,
        rows,
        columns,
        [
            _number_field_element(K, a, entries[i][j])
            for i in 1:rows for j in 1:columns
        ],
    )
end

function definite_minimum(gram_entries)
    lattice = integer_lattice(; gram=change_base_ring(QQ, _zz_matrix(gram_entries)))
    return ZZ(Oscar.Hecke.minimum(lattice))
end

function definite_isometry_group(gram_entries)
    lattice = integer_lattice(; gram=change_base_ring(QQ, _zz_matrix(gram_entries)))
    group = isometry_group(lattice)
    return order(group), [matrix(generator) for generator in gens(group)]
end

function definite_isometry(source_entries, target_entries)
    source = integer_lattice(; gram=change_base_ring(QQ, _zz_matrix(source_entries)))
    target = integer_lattice(; gram=change_base_ring(QQ, _zz_matrix(target_entries)))
    return is_isometric_with_isometry(source, target)
end

function finite_form_isometry_group(gram_entries, invariants, modulus, modulus_qf)
    cover = integer_lattice(; gram=_qq_matrix(gram_entries))
    relations = lattice(ambient_space(cover), diagonal_matrix(QQ, collect(invariants)))
    form = torsion_quadratic_module(cover, relations;
        snf=false, modulus=QQ(modulus), modulus_qf=QQ(modulus_qf))
    group = orthogonal_group(form)
    return order(group), [matrix(generator) for generator in gens(group)]
end

function square_shell(gram_entries, square)
    gram = _zz_matrix(gram_entries)
    lattice = integer_lattice(; gram=change_base_ring(QQ, gram))
    vectors = Oscar.Hecke.short_vectors(lattice, ZZ(square), ZZ(square))
    return matrix(ZZ, length(vectors), nrows(gram),
                  [coordinate for (v, _) in vectors for coordinate in v])
end

function rational_witt_index(gram_entries)
    gram = _qq_matrix(gram_entries)
    _anisotropic, hyperbolic, radical = Oscar.Hecke._quadratic_form_decomposition(gram)
    nrows(radical) == 0 || error("Witt index requires a nondegenerate quadratic space")
    iseven(nrows(hyperbolic)) || error("Hecke returned an odd-dimensional hyperbolic summand")
    return div(nrows(hyperbolic), 2)
end

function rational_witt_bases(gram_entries)
    gram = _qq_matrix(gram_entries)
    anisotropic, hyperbolic, radical = Oscar.Hecke._quadratic_form_decomposition(gram)
    nrows(radical) == 0 || error("Witt decomposition requires a nondegenerate quadratic space")
    return [anisotropic, hyperbolic]
end

function number_field_spinor_norm_class(defining_coefficients, gram_entries, isometry_entries)
    K, a = _number_field(defining_coefficients)
    gram = _number_field_matrix(K, a, gram_entries)
    isometry = _number_field_matrix(K, a, isometry_entries)
    D, U = Oscar.Hecke._gram_schmidt(gram, K)
    transformed = U * isometry * inv(U)
    value = Oscar.spin(D, transformed)
    return [QQ(coeff(value, i)) for i in 0:(degree(K) - 1)]
end

function number_field_witt_index(defining_coefficients, gram_entries)
    K, a = _number_field(defining_coefficients)
    gram = _number_field_matrix(K, a, gram_entries)
    _anisotropic, hyperbolic, radical = Oscar.Hecke._quadratic_form_decomposition(gram)
    nrows(radical) == 0 || error("Witt index requires a nondegenerate quadratic space")
    iseven(nrows(hyperbolic)) || error("Hecke returned an odd-dimensional hyperbolic summand")
    return div(nrows(hyperbolic), 2)
end

function centralizer_discriminant_image(gram_entries, isometry_entries)
    gram = _zz_matrix(gram_entries)
    lattice = integer_lattice(; gram = change_base_ring(QQ, gram))
    isometry = _zz_matrix(isometry_entries)
    lattice_with_isometry = integer_lattice_with_isometry(
        lattice,
        change_base_ring(QQ, isometry);
        check = true,
    )
    invariant_rank = nrows(basis_matrix(invariant_lattice(lattice_with_isometry)))
    coinvariant_rank = nrows(basis_matrix(coinvariant_lattice(lattice_with_isometry)))
    image, _ = image_centralizer_in_Oq(lattice_with_isometry)
    generators = [matrix(generator) for generator in gens(image)]
    return [generators, order(image), invariant_rank, coinvariant_rank]
end

function even_unimodular_primitive_embedding(gram_entries, positive, negative)
    gram = _zz_matrix(gram_entries)
    source = integer_lattice(; gram = change_base_ring(QQ, gram))
    target, source_in_target, _ = embed_in_unimodular(
        source,
        Int(positive),
        Int(negative),
    )
    embedding = solve(
        basis_matrix(target),
        basis_matrix(source_in_target);
        side = :left,
    )
    return [
        change_base_ring(ZZ, gram_matrix(target)),
        change_base_ring(ZZ, embedding),
    ]
end

function target_primitive_embedding(source_gram_entries, target_gram_entries)
    source_gram = _zz_matrix(source_gram_entries)
    target_gram = _zz_matrix(target_gram_entries)
    source = integer_lattice(; gram = change_base_ring(QQ, source_gram))
    target = integer_lattice(; gram = change_base_ring(QQ, target_gram))
    exists, representatives = primitive_embeddings(
        target,
        source;
        classification = :sub,
        check = true,
    )
    if !exists
        return [1, 0]
    end
    target_prime, source_prime, _complement = first(representatives)
    inclusion = solve(
        basis_matrix(target_prime),
        basis_matrix(source_prime);
        side = :left,
    )
    return [
        1,
        1,
        change_base_ring(ZZ, gram_matrix(target_prime)),
        change_base_ring(ZZ, gram_matrix(source_prime)),
        change_base_ring(ZZ, inclusion),
    ]
end

function target_primitive_embedding_classes(
    source_gram_entries,
    target_gram_entries,
    classification_name,
)
    source_gram = _zz_matrix(source_gram_entries)
    target_gram = _zz_matrix(target_gram_entries)
    source = integer_lattice(; gram = change_base_ring(QQ, source_gram))
    target = integer_lattice(; gram = change_base_ring(QQ, target_gram))
    classification = Symbol(classification_name)
    @req classification in [:sub, :emb] "primitive embedding classes are :sub or :emb"
    exists, representatives = primitive_embeddings(
        target,
        source;
        classification = classification,
        check = true,
    )
    if !exists
        return [1, 0, []]
    end
    result = []
    for (target_prime, source_prime, _complement) in representatives
        inclusion = solve(
            basis_matrix(target_prime),
            basis_matrix(source_prime);
            side = :left,
        )
        push!(
            result,
            [
                change_base_ring(ZZ, gram_matrix(target_prime)),
                change_base_ring(ZZ, gram_matrix(source_prime)),
                change_base_ring(ZZ, inclusion),
            ],
        )
    end
    return [1, 1, result]
end

function integer_lattices_are_isometric(first_gram_entries, second_gram_entries)
    first = integer_lattice(; gram = change_base_ring(QQ, _zz_matrix(first_gram_entries)))
    second = integer_lattice(; gram = change_base_ring(QQ, _zz_matrix(second_gram_entries)))
    return is_isometric(first, second) ? 1 : 0
end

function leech_gram_rows()
    lattice = leech_lattice()
    gram = change_base_ring(ZZ, gram_matrix(lattice))
    rows, columns = size(gram)
    return [[Int(gram[i, j]) for j in 1:columns] for i in 1:rows]
end
end
"""


class _OscarLatticeAdapter:
    r"""One persistent OSCAR realization behind ``sage-julia-bridge``."""

    def _bridge(self):
        from sage_julia_bridge import julia

        module_loaded = julia.sage("isdefined(Main, :DzackResearchOscarLatticeAdapter)")
        if not module_loaded:
            julia.eval(_OSCAR_LATTICE_ADAPTER_SOURCE)
        return julia

    def definite_minimum(self, gram):
        r"""Return the positive minimum of a positive definite integral form."""
        return SageZZ(self._bridge().call(
            "DzackResearchOscarLatticeAdapter.definite_minimum",
            _integer_engine_matrix(gram),
        ))

    def definite_isometry_group(self, gram):
        r"""Return the order and row-action generators of a definite ZZ-lattice.

        Oscar 1.8.2, src/Groups/matrices/isometry_group.jl:20-63,
        computes the full group using Plesken--Souvignier or a decomposition
        into invariant sublattices.  Both return matrices in the ambient
        basis, which here is the supplied Gram basis.
        https://github.com/oscar-system/Oscar.jl/blob/v1.8.2/src/Groups/matrices/isometry_group.jl
        """
        order, generators = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.definite_isometry_group",
            _integer_engine_matrix(gram),
        )
        return SageZZ(order), tuple(generator.change_ring(SageZZ) for generator in generators)

    def definite_isometry(self, source_gram, target_gram):
        r"""Return an exact column-image witness, or False for non-isometric forms.

        Oscar 1.8.2, src/Groups/matrices/isometry_group.jl:645-844,
        uses invariant-sublattice decomposition. Its row matrix F satisfies
        F * target_gram * F.transpose() == source_gram.
        https://github.com/oscar-system/Oscar.jl/blob/v1.8.2/src/Groups/matrices/isometry_group.jl
        """
        isometric, witness = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.definite_isometry",
            _integer_engine_matrix(source_gram),
            _integer_engine_matrix(target_gram),
        )
        if not isometric:
            return False
        return witness.change_ring(SageZZ).transpose()

    def finite_form_isometry_group(self, gram, invariants, modulus, modulus_qf):
        r"""Return the order and row-action generators of a presented finite form.

        The quotient is ZZ^n / diag(invariants) ZZ^n, with both value
        moduli retained. Hecke Torsion.jl:10-110 with snf=false preserves
        this generator basis. Oscar 1.8.2 abelian_aut.jl:357-382 computes
        generators through the normal form, including degenerate forms.
        https://github.com/oscar-system/Oscar.jl/blob/v1.8.2/src/Groups/abelian_aut.jl
        """
        order, generators = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.finite_form_isometry_group",
            gram.change_ring(SageQQ),
            tuple(SageZZ(value) for value in invariants),
            SageQQ(modulus),
            SageQQ(modulus_qf),
        )
        return SageZZ(order), tuple(generator.change_ring(SageZZ) for generator in generators)

    def square_shell(self, gram, square):
        r"""Return one coordinate row per sign pair of nonzero square vectors."""
        return self._bridge().call(
            "DzackResearchOscarLatticeAdapter.square_shell",
            _integer_engine_matrix(gram),
            SageZZ(int(square)),
        )

    def rational_witt_index(self, gram):
        r"""Return the Witt index of the quadratic space ``(QQ^n, gram)``."""
        engine_gram = _rational_engine_matrix(gram)
        index = SageZZ(
            self._bridge().call(
                "DzackResearchOscarLatticeAdapter.rational_witt_index",
                engine_gram,
            )
        )
        if not 0 <= 2 * index <= engine_gram.nrows():
            raise ArithmeticError(f"OSCAR computed Witt index {index} for the form {gram}, but a Witt index r satisfies 0 <= 2r <= the dimension")
        return index

    def rational_witt_bases(self, lattice):
        r"""Raise Hecke's two Witt-summand bases into the given QQ-lattice.

        Private supplier to ``Lattices.witt_decomposition``. This extends
        the same selected Hecke computation as ``rational_witt_index``;
        it retains the computed basis instead of discarding it. In
        Hecke ``src/QuadForm/Quad/Spaces.jl``,
        ``_quadratic_form_decomposition`` returns the anisotropic,
        hyperbolic and radical basis matrices; its
        ``_find_hyperbolic_subspace`` normalizes each successive pair to
        square zero and mutual pairing one. Each row is therefore an
        actual summand-basis vector in the original quadratic space.
        https://github.com/thofma/Hecke.jl/blob/master/src/QuadForm/Quad/Spaces.jl

        No coordinate transpose or basis change is selected here. Rows
        are only decoded as vectors in the supplied lattice. Empty
        summands retain their empty finite basis family.
        """
        from sage_extensions.categories.sets.finite_families import (
            finite_family,
        )

        result = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.rational_witt_bases",
            _rational_engine_matrix(lattice.gram_tensor()),
        )
        return tuple(
            finite_family(
                tuple(_raise_lattice_direction(lattice, row) for row in basis.rows()),
                name="Witt summand basis",
            )
            for basis in result
        )

    def number_field_spinor_norm_class(self, field, gram, isometry):
        r"""Return an untwisted spinor-norm representative over the absolute number field ``field``."""
        coefficients = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.number_field_spinor_norm_class",
            list(_number_field_descriptor(field)),
            _number_field_engine_matrix(gram, field),
            _number_field_coefficient_rows(_engine_row_action_matrix(isometry), field),
        )
        engine = _engine_ring(field)
        generator = engine.gen()
        value = engine.zero()
        for exponent, coefficient in enumerate(coefficients):
            value += SageQQ(coefficient) * generator**exponent
        if value == 0:
            raise ArithmeticError(f"OSCAR computed spinor norm 0 for the isometry {isometry} of the form {gram} over {field}, but a spinor norm is a nonzero square class")
        return _owned_engine_element(field, value)

    def number_field_witt_index(self, field, gram):
        r"""Return the Witt index of a nondegenerate quadratic space over ``field``."""
        engine_gram = _engine_component_matrix(gram)
        index = SageZZ(
            self._bridge().call(
                "DzackResearchOscarLatticeAdapter.number_field_witt_index",
                list(_number_field_descriptor(field)),
                _number_field_engine_matrix(gram, field),
            )
        )
        if not 0 <= 2 * index <= engine_gram.nrows():
            raise ArithmeticError(f"Hecke computed Witt index {index} for the form {gram} over {field}, but a Witt index r satisfies 0 <= 2r <= the dimension")
        return index

    def centralizer_discriminant_image(self, gram, isometry):
        result = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.centralizer_discriminant_image",
            _integer_engine_matrix(gram),
            _engine_row_action_matrix(isometry).change_ring(SageZZ),
        )
        if not isinstance(result, list) or len(result) != 4:
            raise RuntimeError(f"the image of the centralizer of {isometry} in O(A_L) for the form {gram} came back from OSCAR as {result!r}, not a list of four entries")
        engine_generators, order, invariant_rank, coinvariant_rank = result
        generators = tuple(
            tensor.matrix(
                SageZZ,
                generator.nrows(),
                generator.ncols(),
                tuple(SageZZ(entry) for entry in generator.list()),
            )
            for generator in engine_generators
        )
        if any(generator.tensor_shape()[0] != generator.tensor_shape()[1] for generator in generators):
            raise ArithmeticError(f"OSCAR returned generators {generators} for the image of the centralizer of {isometry} in O(A_L), and some are not square matrices")
        return (
            generators,
            SageZZ(order),
            SageZZ(invariant_rank),
            SageZZ(coinvariant_rank),
        )

    def even_unimodular_primitive_embedding(self, gram, positive, negative):
        result = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.even_unimodular_primitive_embedding",
            _integer_engine_matrix(gram),
            int(positive),
            int(negative),
        )
        if not isinstance(result, list) or len(result) != 2:
            raise RuntimeError(
                f"the primitive embedding of the form {gram} into an even unimodular lattice of "
                f"signature ({positive}, {negative}) came back from OSCAR as {result!r}, not a "
                f"list of two entries"
            )
        target_engine, embedding_engine = result
        ring = gram.base_ring()
        target_shape = (target_engine.nrows(), target_engine.ncols())
        target_gram = tensor(
            ring,
            (),
            target_shape,
            tuple(tuple(_owned_engine_element(ring, entry) for entry in row) for row in target_engine.rows()),
        )

        embedding = _owned_embedding_from_row_action(ring, embedding_engine)
        validate_isometric_embedding((target_gram, gram, embedding), check=False)
        validate_even_unimodular_gram(target_gram, check=False)
        return target_gram, embedding

    def target_primitive_embedding(self, source_gram, target_gram):
        r"""Use OSCAR's target-specific primitive embedding decision.

        ``primitive_embeddings(target, source; check=true)`` filters the
        genus representatives with ``is_isometric``, not the indefinite
        isometry-witness routine. Only the Gram forms and inclusion are
        returned here; the actual research Isom objects transport them
        to the original endpoints when a witness is requested.
        """
        result = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.target_primitive_embedding",
            _integer_engine_matrix(source_gram),
            _integer_engine_matrix(target_gram),
        )
        if not isinstance(result, list) or not result:
            raise RuntimeError(f"the primitive embedding of the form {source_gram} into {target_gram} came back from OSCAR as {result!r}, not a nonempty list")
        if int(result[0]) == 0:
            return None
        if len(result) < 2:
            raise RuntimeError(
                f"the primitive embedding of the form {source_gram} into {target_gram} came back from OSCAR as {result!r}, without the entry saying whether one exists"
            )
        if int(result[1]) == 0:
            return False
        if len(result) != 5:
            raise RuntimeError(f"the primitive embedding of the form {source_gram} into {target_gram} came back from OSCAR as {result!r}, not a list of five entries")
        target_engine, source_engine, embedding_engine = result[2:]
        ring = source_gram.base_ring()

        def owned_gram(engine):
            return tensor(
                ring,
                (),
                (engine.nrows(), engine.ncols()),
                tuple(tuple(_owned_engine_element(ring, entry) for entry in row) for row in engine.rows()),
            )

        target_prime_gram = owned_gram(target_engine)
        source_prime_gram = owned_gram(source_engine)
        embedding = _owned_embedding_from_row_action(ring, embedding_engine)
        validate_isometric_embedding((target_prime_gram, source_prime_gram, embedding), check=False)
        return target_prime_gram, source_prime_gram, embedding

    def target_primitive_embedding_classes(
        self,
        source_gram,
        target_gram,
        classification,
    ):
        r"""Return the maintained classification filtered to the actual target.

        The lattice overload with ``check=true`` retains the original
        classification mode while excluding other classes in its genus.
        Filtering decides isometry; it need not construct a target
        isometry at this private engine boundary.
        """
        result = self._bridge().call(
            "DzackResearchOscarLatticeAdapter.target_primitive_embedding_classes",
            _integer_engine_matrix(source_gram),
            _integer_engine_matrix(target_gram),
            str(classification),
        )
        if not isinstance(result, list) or not result:
            raise RuntimeError(f"the classes of primitive embeddings of {source_gram} into {target_gram} came back from OSCAR as {result!r}, not a nonempty list")
        if int(result[0]) == 0:
            return None
        if len(result) != 3:
            raise RuntimeError(f"the classes of primitive embeddings of {source_gram} into {target_gram} came back from OSCAR as {result!r}, not a list of three entries")
        if int(result[1]) == 0:
            return ()
        representatives = []
        for record in result[2]:
            if not isinstance(record, list) or len(record) != 3:
                raise RuntimeError(f"a class of primitive embeddings of {source_gram} into {target_gram} came back from OSCAR as {record!r}, not a list of three entries")
            target_engine, source_engine, embedding_engine = record
            ring = source_gram.base_ring()

            def owned_gram(engine):
                return tensor(
                    ring,
                    (),
                    (engine.nrows(), engine.ncols()),
                    tuple(tuple(_owned_engine_element(ring, entry) for entry in row) for row in engine.rows()),
                )

            target_prime_gram = owned_gram(target_engine)
            source_prime_gram = owned_gram(source_engine)
            embedding = _owned_embedding_from_row_action(ring, embedding_engine)
            validate_isometric_embedding((target_prime_gram, source_prime_gram, embedding), check=False)
            representatives.append((target_prime_gram, source_prime_gram, embedding))
        return tuple(representatives)

    def integer_lattices_are_isometric(self, first, second):
        r"""Decide whether ``(ZZ^n, first)`` and ``(ZZ^n, second)`` are isometric, by Hecke's ``is_isometric``.

        ``first`` and ``second`` are Sage integer Gram matrices of
        nondegenerate lattices ``L`` and ``M``.  For an indefinite genus of rank
        at least 3 Hecke (``_is_isometric_indef``) answers ``False`` when the
        genera differ and ``True`` when the genus has no improper spinor
        generators.  Otherwise it approximates an isometry ``f`` of the rational
        quadratic spaces with ``f(L_p) = M_p`` at every prime ``p`` dividing
        ``2 det L``, and answers whether the index ``r = [M : f(L) cap M]`` is
        improperly automorphous (Conway and Sloane, *Sphere Packings, Lattices
        and Groups*, chapter 15, Theorem 15, as Hecke's
        ``improper_spinor_generators`` cites it).

        The one private adapter of the several-spinor-genera regime of
        ``LatticeIsometryMor._isometry_decision`` (``lattice_morphisms.py``).
        Owed at T (`ENG-07`): a measurement of this route against Sage's
        improper spinor kernel (``Genus._improper_spinor_kernel`` with the
        spinor operator of the index of a rational equivalence), as wall time
        against the determinant at more than one size, recorded in
        ``TRAPS.md`` before either route is fixed as the delegation.
        """
        answer = SageZZ(
            self._bridge().call(
                "DzackResearchOscarLatticeAdapter.integer_lattices_are_isometric",
                first,
                second,
            )
        )
        if answer not in (0, 1):
            raise RuntimeError(f"Hecke answered {answer} for the isometry of the forms {first} and {second}, not 0 or 1")
        return answer == 1

    def leech_gram_rows(self):
        rows = self._bridge().call("DzackResearchOscarLatticeAdapter.leech_gram_rows")
        if not isinstance(rows, list) or len(rows) != 24:
            raise RuntimeError(f"the Gram matrix of the Leech lattice came back from OSCAR as {rows!r}, not a list of 24 rows")
        matrix_rows = tuple(tuple(SageZZ(entry) for entry in row) for row in rows)
        if any(len(row) != 24 for row in matrix_rows):
            raise RuntimeError(f"the Gram matrix of the Leech lattice from OSCAR has row lengths {tuple(len(row) for row in matrix_rows)}, not 24 each")
        return matrix_rows


_oscar_lattices = _OscarLatticeAdapter()


def isometric_within_genus(domain, codomain):
    r"""Decide whether two lattices over ``ZZ`` of one genus, indefinite of rank at least 3, are isometric.

    Protected adapter contract (`OWN-05`).  Owner: this module.  Caller:
    ``LatticeIsometryMor._isometry_decision`` (``lattice_morphisms.py``), and
    only in the regime of several improper spinor genera, where membership in
    one spinor genus decides isometry [CS99, Ch. 15, Thms 14-15].  Input: two
    preamble lattices over ``ZZ``, nondegenerate, of finite rank at least 3,
    already established to lie in one genus.  Output: a Python ``bool``, the
    exact verdict of the native spinor-genus computation.

    Hecke ``e2ab5716``, ``ZLatticeMorphism.jl:797--893``, first identifies
    the rational spaces, then weakly approximates the local lattice maps
    at primes dividing ``2 det``.  The spinor operator of the remaining
    intersection index decides isometry.  Sage supplies rational-space
    isometry, local normal forms and the improper spinor kernel; the
    source's exact reflection-and-CRT approximation lives at the tensor
    arithmetic owner.  No Julia bridge or integral-group enumeration is
    used.  This decision requires no rational hyperbolic planes.  An
    integral isometry remains the separate ``Isom(...).an_element()``
    construction; the rational approximation is not such a witness.
    """
    from sage_extensions.tensors._spinor_isometry import _isometric_indefinite

    return _isometric_indefinite(
        _engine_component_matrix(domain.gram_tensor()),
        _engine_component_matrix(codomain.gram_tensor()),
    )

__all__: list[str] = []


def _roots_generating_lattice(gram, lengths):
    r"""Return coordinate rows of reflective roots generating the integral module.

    PARI's exact ``forvec(v=vector(n), ...)`` enumerates all integer vectors
    in increasing L1 degree (Programming in GP: control statements, ``forvec``).
    ``matinverseimage`` decides membership in the retained independent column
    span over QQ, and integral coefficients decide membership over ZZ;
    ``mathnf`` retains its basis. Only roots enlarging that span are retained.
    A returned family therefore consists of roots and generates the module;
    otherwise the semi-decision keeps enumerating without a precision bound.

    ``_root_generators.gp`` composes those maintained operations. TRAPS.md,
    "PARI forqfvec imposes a fixed floating-point bound", records why the
    former annular iterator cannot implement this unbounded procedure.
    """
    from pathlib import Path

    from sage.libs.pari import pari

    form = _engine_component_matrix(gram).change_ring(SageZZ)
    source = Path(__file__).with_name("_root_generators.gp").read_text()
    generators = pari(source)(pari(form), pari(sorted(int(length) for length in lengths)))
    return tuple(tuple(int(entry) for entry in column) for column in generators)
