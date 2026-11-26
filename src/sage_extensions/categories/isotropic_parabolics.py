r"""Parabolic subgroups of primitive isotropic subobjects, and their Levi data.

Let ``iota: I -> L`` be a primitive totally isotropic subobject of a lattice.
Its parabolic subgroup is the stabilizer

``P_I = Stab_{O(L)}(I) = {g in O(L) : g(iota(I)) = iota(I)}``.

Every ``g`` in ``P_I`` preserves ``I^perp`` as well, so it restricts along
``iota`` and descends to the isotropic reduction, giving two group morphisms
out of ``P_I``.  Writing ``K_I = I^perp/I``,

``1 -> U_I -> P_I -> M_I -> 1``,   ``M_I <= GL(I) x O(K_I)``,

where ``U_I`` is the common kernel: the isometries acting as the identity on
``I`` and on ``K_I``.  Membership in ``U_I`` is decided from that definition,
without constructing the quotient: ``g`` acts trivially on ``I^perp/I``
exactly when ``(g - 1)(I^perp)`` lies in ``iota(I)``.

For ``rank(I) = 1`` the ``O(L)``-orbit of ``I`` is a cusp, ``P_I`` is that
cusp's arithmetic stabilizer, and ``K_I = v^perp/v`` is the lattice whose
reflection group acts on the cusp's fundamental domain.  This is the object in
which the Sterk simple-root counts are compared: one count is taken under the
full reflection group ``W(K_I)`` of ``K_I``, the other under a reflection
subgroup of it, and the two group actions are what differ.

The Levi target ``GL(I) x O(K_I)`` is delivered here by its two components
separately.  ``levi_restriction`` lands in ``GL(I)``, the module
automorphisms of ``I``: the form ``I`` inherits is identically zero, so its
isometry group is all of ``GL(I)`` and nothing smaller is being asserted.
``levi_quotient_action`` lands in the module automorphisms of the represented
cokernel ``I^perp/I``.  Whether that automorphism is an isometry of the
induced form is the statement ``O(K_I)`` makes, and stating it needs the
projection ``I^perp ->> K_I`` that the owned ``isotropic_reduction`` does not
return; see ``isotropic_quotient_projection`` below.
"""

from sage.matrix.constructor import matrix
from sage.matrix.special import identity_matrix
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage.rings.rational_field import QQ
from sage.rings.real_mpfr import RR
from sage.modules.free_module_element import vector
from sage.structure.element import parent as element_parent

from sage_extensions.categories._lattice import subobject_record_name
from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.timing import stage, timed_stage


def _integral_solution(system, target):
    r"""Return one integral solution of ``system * x = target``, or ``None`` when there is none.

    ``system`` is a matrix over `ZZ` and ``target`` a column of its height.
    Smith normal form writes ``U * system * V = S`` with ``S`` diagonal, so
    ``system * x = target`` has an integral solution exactly when
    ``U * target`` is divisible entry by entry by the diagonal of ``S`` and
    vanishes past its rank; then ``x = V * (S^-1 * U * target)``.  Both answers
    are exact: a solution is never missed and a non-solution is never returned.
    """
    diagonal, left, right = system.smith_form()
    transformed = left * target
    rows, columns = system.nrows(), system.ncols()
    coordinates = [SageZZ.zero() for _ in range(columns)]
    for position in range(rows):
        entry = transformed[position, 0]
        pivot = (
            diagonal[position, position]
            if position < min(rows, columns)
            else SageZZ.zero()
        )
        if pivot:
            if entry % pivot:
                return None
            coordinates[position] = entry // pivot
        elif entry:
            return None
    solution = right * matrix(SageZZ, [[entry] for entry in coordinates])
    values = tuple(solution[position, 0] for position in range(columns))
    assert system * matrix(SageZZ, [[entry] for entry in values]) == target, (
        f"the Smith-normal-form solution of {system} * x = {target} does not satisfy it"
    )
    return values


def _content(values):
    r"""Return the content of an integer vector: the gcd of its entries, and zero for the zero vector."""
    content = SageZZ.zero()
    for value in values:
        content = content.gcd(SageZZ(value))
    return abs(content)


def general_linear_images(vectors):
    r"""Return images of ``vectors`` under generators of ``GL_k(Z)``, for ``k = len(vectors)``.

    Adjacent transpositions, one shear and one sign change generate ``GL_k(Z)``
    (Newman, *Integral Matrices*, VII.1).
    """
    images = []
    for i in range(len(vectors) - 1):
        swapped = list(vectors)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        images.append(tuple(swapped))
    if len(vectors) > 1:
        images.append((vectors[0] + vectors[1], *vectors[1:]))
    images.append((-vectors[0], *vectors[1:]))
    return tuple(images)


_PLANE_ACTION_WITNESS_BOUND = 4

# How many classes of the radical's parameter `unipotent_parameter_lattice` decides before
# it refuses: deciding every class of the residue system is what makes the lattice exact,
# and a truncation of it would return a lattice that is too small without saying so.
_UNIPOTENT_PARAMETER_CLASS_LIMIT = 1 << 18


def _extend_isotropic_basis_isometry(
    source_reduction,
    target_reduction,
    source_basis,
    images,
):
    r"""Extend a chosen isometry of ``I^perp`` to the rational ambient lattice.

    ``source_basis`` and ``images`` are a full basis of ``I^perp`` on the source
    and its proposed images.  The returned pair is the rational extension and
    the positive generator of its denominator ideal from the source lattice to
    the target lattice.  An isometry fixing ``I`` pointwise and acting on ``I``
    is unique on the isotropic normal, so the extension is forced; its
    existence is the rational Witt extension of the partial isometry.

    The block form this completes is Dutour Sikiric--Hulek,
    arXiv:2302.01679v2, Theorem 4.9, printed pp. 33--34, and the quotient
    action is Zemel, arXiv:1902.08264v2, Proposition 1.6, printed p. 10.
    """
    from sage_extensions.categories.modules.pure.modules import (
        Modules,
        ModulesOverIntegralDomains,
    )
    from sage_extensions.categories.lattices import Lattices

    source = source_reduction.isotropic_embedding().codomain()
    target = target_reduction.isotropic_embedding().codomain()
    fraction_map = source.base_ring().fraction_field_map()
    field = fraction_map.codomain()
    rank = int(source_reduction.orthogonal_complement().inclusion().domain().module_rank())
    if len(source_basis) != rank or len(images) != rank:
        raise ValueError(
            f"the perpendicular isometry needs a full chosen basis: it was given "
            f"{len(source_basis)} source vectors and {len(images)} images, but I^perp has rank {rank}"
        )
    rational_source = source.base_change(fraction_map)
    rational_target = target.base_change(fraction_map)
    source_rationalize = ModulesOverIntegralDomains(source.base_ring())(source).generic_fibre_map()
    target_rationalize = ModulesOverIntegralDomains(target.base_ring())(target).generic_fibre_map()
    frame = field.free_module(rank)
    labels = tuple(frame.module_generating_set())
    gram = rational_source.gram_tensor().pullback(
        Modules(field).Mor(frame, rational_source)(
            dict(
                zip(
                    labels,
                    (source_rationalize(point).underlying_element() for point in source_basis),
                    strict=True,
                )
            )
        )
    )
    span = Lattices(field)(
        [[gram[row, column] for column in range(rank)] for row in range(rank)]
    )
    span_labels = tuple(span.module_generating_set())
    source_inclusion = Modules(field).Mor(span, rational_source)(
        dict(
            zip(
                span_labels,
                (source_rationalize(point).underlying_element() for point in source_basis),
                strict=True,
            )
        )
    )
    target_inclusion = Modules(field).Mor(span, rational_target)(
        dict(
            zip(
                span_labels,
                (target_rationalize(point).underlying_element() for point in images),
                strict=True,
            )
        )
    )
    extension = span.Isom(span).identity().witt_extension(
        source_inclusion, target_inclusion
    )
    (denominator,) = tuple(
        extension.denominator_ideal(source, target).ideal_generators()
    )
    return extension, int(denominator)


def _pointed_stabilizer_action(subobject):
    r"""Return the finite-residue action whose lattice stabilizer is ``Stab_{O(L)}(v)``.

    The action's rational group is generated by one rational lift of every
    generator of ``O(K_I)``, together with the integral kernel ``U_I`` of the
    action itself -- the pointwise Levi kernel of
    ``...IsotropicReductions._pointwise_kernel_generators``.  Every generator
    fixes ``v``, so the integral stabilizer is a subgroup of ``P_I^1``, and it
    contains ``U_I``: the radical's generators are among the rational
    generators and are integral, and the four of them cross into the group and
    lie in its stabilizer at the rank-five proper-image specimen.  It is not
    asserted to be all of ``P_I^1``.  A word in rational lifts is a rational
    isometry and nothing in the construction makes it integral, so the
    stabilizer is ``G_QQ n O(L)``; for ``g`` in ``P_I^1`` whose class a word
    ``w`` carries, ``w^-1 g`` lies in the rational kernel unless ``w`` happens
    to be integral, so the Levi image of the stabilizer need not be ``M_I``.
    At the same specimen four of the five words of the coset graph cross in and
    lie in the stabilizer, and the fifth is refused as undecided rather than
    answered.  The kernel is not optional:
    at a line the perpendicular kernel ``ker(P_I -> O(I^perp))`` is trivial --
    an isometry fixing `I` and `I^\perp` pointwise is the identity -- so with
    the lifts alone the rational group omits the whole radical direction, and
    the stabilizer it cuts out is a proper subgroup of ``P_I^1`` whose
    generators a test can catch: a generator of ``U_I`` is not in it.

    The finite residue module is the stable containing module divided by its
    own multiple.  Its bound is
    ``2 d^2 |disc(K_I)|^2 [L : i^*(L)]``, with ``d`` the common denominator of
    the lift generators: the lift parameters are bounded by ``d``, the kernel's
    generators are integral and so impose no bound of their own, and the last
    factor makes the pairing ``L -> I^*`` finite.  The orbit span retains the
    least stable inclusion, and ``IntegralStructureAction`` cuts the stabilizer
    out as the preimage of its point stabilizer in that finite module.

    The complete quotient family is ``O(K_I)``'s certified family; the lifts
    are the marked-line torsors of Gritsenko--Hulek--Sankaran,
    arXiv:0810.1614v1, section 3.1, equations (4)--(5), printed pp. 8--9.
    """
    from sage_extensions.categories.lattices import Lattices
    from sage_extensions.categories.modules.orbit_spans import OrbitSpanConstructions
    from sage_extensions.categories.modules.pure.modules import (
        Modules,
        ModulesOverIntegralDomains,
    )
    from sage_extensions.categories.rational_integral_stabilizers import (
        IntegralStructureAction,
    )

    lattice = subobject.ambient_lattice()
    rank = int(subobject.module_rank())
    if rank != 1:
        raise ValueError(
            f"a pointed stabilizer action is for a primitive isotropic vector, but "
            f"{subobject} has rank {rank}"
        )
    reduction = subobject.isotropic_reduction()
    quotient = reduction.quotient_lattice()
    perpendicular = reduction.orthogonal_complement().inclusion()
    frame = reduction.coordinate_frame()
    labels = tuple(quotient.module_generating_set())
    lifts = {label: perpendicular(frame(label)) for label in labels}
    vector = subobject.inclusion()(subobject.module_generator(next(iter(subobject.module_generating_set()))))
    basis = (vector, *(lifts[label] for label in labels))

    def lift(element):
        coordinates = element.to_vector()
        return sum(
            (
                lattice.scalar_multiple(coordinates(label), lifts[label])
                for label in labels
                if coordinates(label)
            ),
            lattice.zero(),
        )

    image_families = []
    for isometry in quotient.O().group_generators():
        image_families.append(
            (
                vector,
                *(
                    lift(isometry(quotient.module_generator(label)))
                    for label in labels
                ),
            )
        )
    for sheared in range(len(labels)):
        image_families.append(
            (
                vector,
                *(
                    lifted + vector if position == sheared else lifted
                    for position, lifted in enumerate(lifts[label] for label in labels)
                ),
            )
        )

    extended = [
        _extend_isotropic_basis_isometry(reduction, reduction, basis, images)
        for images in image_families
    ]
    denominator = SageZZ.one()
    for _isometry, entry_denominator in extended:
        denominator = denominator.lcm(SageZZ(entry_denominator))

    field_map = lattice.base_ring().fraction_field_map()
    rational = lattice.base_change(field_map)
    inclusion = ModulesOverIntegralDomains(lattice.base_ring())(lattice).generic_fibre_map()

    def rationalized(isometry):
        return rational.Isom(rational)(
            lambda label: inclusion(
                isometry(lattice.module_generator(label))
            ).underlying_element()
        )

    kernel_generators = [
        rationalized(isometry)
        for isometry in reduction._pointwise_kernel_generators()
    ]

    generators = (
        *(isometry for isometry, _entry_denominator in extended),
        *kernel_generators,
    )
    space = inclusion.codomain()
    isotropic_inclusion = reduction.isotropic_embedding()
    dualization = Modules(lattice.base_ring()).dualization()
    opposite = dualization.domain()
    opposite_inclusion = opposite.Mor(
        opposite.object(lattice), opposite.object(isotropic_inclusion.domain())
    )(isotropic_inclusion)
    pairing = dualization(opposite_inclusion) * lattice.metric_map()
    pairing_domain_labels = tuple(pairing.domain().module_generating_set())
    pairing_codomain_labels = tuple(pairing.codomain().module_generating_set())
    pairing_matrix = matrix(
        SageZZ,
        tuple(
            tuple(
                pairing(pairing.domain().module_generator(label)).to_vector()(target_label)
                for target_label in pairing_codomain_labels
            )
            for label in pairing_domain_labels
        ),
    )
    pairing_rank = int(pairing_matrix.rank())
    if pairing_rank != len(pairing_codomain_labels):
        raise ArithmeticError(
            f"the pairing {lattice} -> I^* has infinite cokernel, so the isotropic "
            f"stabilizer action has no finite residue module"
        )
    smith = pairing_matrix.smith_form()[0]
    pairing_index = SageZZ.one()
    for position in range(pairing_rank):
        pairing_index *= abs(smith[position, position])
    bound = (
        2
        * int(denominator) ** 2
        * abs(int(quotient.discriminant())) ** 2
        * int(pairing_index)
    )
    scale = rational.base_ring().one() / rational.base_ring()(bound)
    containing = Modules(lattice.base_ring()).Mono(lattice, space)(
        lambda label: space.wrap(
            rational.scalar_multiple(
                scale,
                inclusion(lattice.module_generator(label)).underlying_element(),
            )
        )
    )
    action = IntegralStructureAction(
        rational.O().subgroup(tuple(generators)), inclusion
    )
    span = OrbitSpanConstructions(lattice.base_ring())(
        action.ambient_action_functor(), inclusion, containing=containing
    )
    return action.with_stable_containing_bound(span.inclusion())


def _plane_action_matrix(plane, automorphism):
    r"""Return the plane action of ``automorphism`` on ``plane``'s basis, as a matrix over `ZZ`.

    An isometry carrying the primitive isotropic plane onto itself acts on it
    by a matrix in `\GL_2(ZZ)`; the images of the two basis vectors are written
    in that basis and the coordinates are asserted integral, so the answer is
    the action itself and not the value of some extension of it.
    """
    from sage.rings.rational_field import QQ

    basis = plane.plane_basis()
    if len(basis) != 2:
        raise ValueError(
            f"no plane action is read at {plane}: it has {len(basis)} generators, "
            f"and the action on a plane is a GL_2(ZZ)-matrix"
        )
    coordinates = matrix(SageZZ, [plane.coordinates(vector) for vector in basis])
    images = matrix(QQ, [plane.coordinates(automorphism(vector)) for vector in basis])
    action = coordinates.change_ring(QQ).transpose().solve_right(images.transpose())
    if any(entry not in SageZZ for entry in action.list()):
        raise ValueError(
            f"no integral plane action is read for {automorphism} at {plane}: its images of the "
            f"plane's basis have coordinates {action.list()} on that basis"
        )
    return matrix(SageZZ, [[int(entry) for entry in row] for row in action.rows()])


def _matrix_key(entry):
    r"""Return the entries of a `2 \\times 2` matrix as a tuple, for use as a dictionary key."""
    return tuple(int(value) for value in entry.list())


def _unimodular_inverse(entry):
    r"""Return the inverse of a `2 \times 2` integer matrix of determinant `\pm 1`.

    `\operatorname{adj}(E) E = \det(E) 1`, so the adjugate is the inverse
    exactly when the determinant is `1`; a reversing element has determinant
    `-1`, and its inverse is `-\operatorname{adj}(E)`.  A comparison of cosets
    may not drop that sign: `-1` lies in the congruence subgroup only at level
    at most two, and every level occurs below.
    """
    determinant = int(entry.determinant())
    if abs(determinant) != 1:
        raise ValueError(
            f"no inverse is read for {entry}: it has determinant {determinant}, "
            f"and only a matrix of determinant +-1 is invertible over ZZ"
        )
    return determinant * entry.adjugate()


def right_coset_action(generators, in_subgroup, *, start=None, accept=None):
    r"""Return the action of ``generators`` on the right cosets of `H` by right multiplication.

    `H = \{x : \text{in\_subgroup}(x)\}` is a subgroup of `\mathrm{GL}_2(\ZZ)`
    given by its membership predicate, and the walk multiplies **on the
    right**: every coset it reaches is named by a word
    `\text{start} \cdot g_{i_1} \cdots g_{i_k}`.  The right cosets of `H` are
    the sets `Hx = \{h x\}`, so `Hx = Hy` exactly when `x y^{-1} \in H`, and
    that is the comparison this walk makes, with the inverse of `y` taken
    exactly (:func:`_unimodular_inverse`).  Two other comparisons are
    different partitions of the same group, and neither is what a right action
    enumerates: `y^{-1} x \in H` compares left cosets `xH = yH`, and
    `\operatorname{adj}(y) x \in H` compares or reverses neither, because
    `\operatorname{adj}(y) = \det(y) y^{-1}` differs from `y^{-1}` by a sign
    at every reversing element.

    This is the one walk the plane stabilizer's completeness rests on
    (:meth:`...PrimitiveIsotropicSubobjects.ParentMethods._levi_plane_action_presentation`):
    the special-linear half of the projection `\Gamma'` is its action on the
    right cosets of `H = \Gamma' \cap SL_2(\ZZ)`, and the
    determinant-reversing half is its action started at `\mathrm{diag}(-1,1)`,
    whose terminal word has determinant `-1`.  It is public so that a finite
    specimen of that comparison can be run and asserted without a lattice.

    ``start`` is the element the walk begins at, the identity by default.
    ``accept`` is an optional callback for a caller that stops at the first
    acceptable representative: it is called with every representative as the
    walk discovers it, beginning with ``start``, and once it answers something
    other than ``None`` the walk stops and returns that answer.  Liftability of
    a plane action is constant on the right cosets of `H`, since
    `x y^{-1} \in H` transports the lift of `x` to one of `y`, so the reversing
    search decides one representative per coset and takes
    :meth:`...plane_block_lift` as its ``accept``.

    Returns ``(representatives, tables, found)``.  ``tables[j][i]`` is the
    position of the coset of ``representatives[i] * generators[j]``, so the
    tables are the permutation representation of the generators on the cosets
    the walk reached; ``found`` is ``None`` unless ``accept`` answered, and
    ``tables`` is ``None`` when the walk stopped at an answer before it
    finished.
    """
    from collections import deque

    identity = matrix(SageZZ, [[1, 0], [0, 1]])
    representatives = [identity if start is None else start]
    tables = [{} for _ in generators]
    found = None if accept is None else accept(representatives[0])
    if found is not None:
        return tuple(representatives), None, found
    frontier = deque([0])
    while frontier:
        source = frontier.popleft()
        for position, generator in enumerate(generators):
            candidate = representatives[source] * generator
            target = next(
                (
                    index
                    for index, representative in enumerate(representatives)
                    if in_subgroup(candidate * _unimodular_inverse(representative))
                ),
                None,
            )
            if target is None:
                target = len(representatives)
                representatives.append(candidate)
                found = None if accept is None else accept(candidate)
                if found is not None:
                    return tuple(representatives), None, found
                frontier.append(target)
            tables[position][source] = target
    return tuple(representatives), tuple(tables), found


def _word_witness(generators, target, bound=_PLANE_ACTION_WITNESS_BOUND):
    r"""Return a tuple of ``generators`` whose product is ``target``, or ``None``.

    Breadth first over products of at most ``bound`` factors, so a returned
    tuple is an exhibited word: the caller multiplies it and gets ``target``
    exactly, in `\GL_2(ZZ)`.  Nothing is inferred when none is found within the
    bound.  Matrices are keyed by their entries, because a Sage matrix is a
    mutable object and is not a dictionary key.
    """
    target_key = _matrix_key(target)
    for generator in generators:
        if _matrix_key(generator) == target_key:
            return (generator,)
    products = {}
    words = {}
    for generator in generators:
        key = _matrix_key(generator)
        products.setdefault(key, generator)
        words.setdefault(key, (generator,))
    frontier = tuple(products)
    for _ in range(bound - 1):
        extended_products = {}
        extended_words = {}
        for key in frontier:
            element = products[key]
            word = words[key]
            for generator in generators:
                product = element * generator
                product_key = _matrix_key(product)
                if product_key == target_key:
                    return word + (generator,)
                if product_key in products or product_key in extended_products:
                    continue
                extended_products[product_key] = product
                extended_words[product_key] = word + (generator,)
        products.update(extended_products)
        words.update(extended_words)
        frontier = tuple(extended_products)
        if not frontier:
            break
    return None


def _generated_image_order(generators, modulus):
    r"""Return the order of the subgroup of `\GL_2(ZZ/modulus)` the images of ``generators`` generate."""
    identity = (1, 0, 0, 1)
    reduced = [
        (
            int(generator[0, 0]) % modulus,
            int(generator[0, 1]) % modulus,
            int(generator[1, 0]) % modulus,
            int(generator[1, 1]) % modulus,
        )
        for generator in generators
    ]
    seen = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for other in reduced:
            product = (
                (current[0] * other[0] + current[1] * other[2]) % modulus,
                (current[0] * other[1] + current[1] * other[3]) % modulus,
                (current[2] * other[0] + current[3] * other[2]) % modulus,
                (current[2] * other[1] + current[3] * other[3]) % modulus,
            )
            if product not in seen:
                seen.add(product)
                frontier.append(product)
    return len(seen)


def _general_linear_order(modulus):
    r"""Return `|\GL_2(\ZZ/m)|`, which is `m^4 \prod_{p | m} (1 - 1/p)(1 - 1/p^2)`.

    For `m = p^k` the order is `p^{4(k-1)} \cdot p(p-1)^2(p+1)`: the matrix is
    fixed by its four entries modulo `p^k`, and a matrix is invertible exactly
    when its reduction modulo `p` is, which leaves `|\GL_2(\FF_p)| =
    (p^2-1)(p^2-p)` of the `p^4` reductions and `p^{4(k-1)}` lifts of each.
    """
    order = SageZZ.one()
    for prime in SageZZ(modulus).prime_divisors():
        p = int(prime)
        power = 0
        remaining = int(modulus)
        while remaining % p == 0:
            remaining //= p
            power += 1
        order *= p ** (4 * (power - 1)) * p * (p - 1) ** 2 * (p + 1)
    return int(order)


def _first_block_stabilizer_index(pairing):
    r"""Return `[\GL_2(\ZZ) : \{A : J A^{-t} J^{-1} \text{ is integral}\}]`.

    `J` is the `(U, P)` block of :meth:`...plane_block_gram`.  The set is a
    subgroup of `\GL_2(\ZZ)`: it contains the congruence subgroup
    `\Gamma(|\det J|)`, because `J A^{-t} J^{-1} = J A^{-t} \operatorname{adj}(J)
    / \det J` and `A^{-t}` is integral, so the condition depends on `A` only
    modulo `|\det J|` and the index is the number of classes divided by the
    number of those that satisfy it.  Dutour Sikirić--Hulek, Theorem 4.9, printed
    p. 34, is the containment: the plane actions that admit an integral lift with
    a trivial class action preserve the lattice spanned by the rows of `J^t`, and
    those are exactly the `A` for which `J A^{-t} J^{-1}` -- their `P_1` -- is
    integral.  This index is therefore an upper bound on the index of the plane
    actions that lift.
    """
    from itertools import product

    determinant = abs(int(pairing.determinant()))
    if determinant == 0:
        raise ValueError(
            "the complement of P^perp does not pair nondegenerately with the plane"
        )
    total = _general_linear_order(determinant)
    adjugate = pairing.adjugate()
    preserving = 0
    for first, second, third, fourth in product(range(determinant), repeat=4):
        if SageZZ(first * fourth - second * third).gcd(SageZZ(determinant)) != 1:
            continue
        inverse_transpose = matrix(SageZZ, [[fourth, -second], [-third, first]])
        try:
            block = pairing * inverse_transpose * adjugate
        except (TypeError, ValueError):
            continue
        if all(
            SageZZ(int(entry)) % SageZZ(determinant) == 0 for entry in block.list()
        ):
            preserving += 1
    if preserving == 0 or total % preserving != 0:
        raise ArithmeticError(
            f"{preserving} of the {total} classes of GL_2(ZZ/{determinant}) make "
            f"J A^-t J^-1 integral, which does not divide the group order"
        )
    return total // preserving


def _plane_action_index(actions, plane):
    r"""Return `[\GL_2(ZZ) : \langle \text{actions} \rangle]` by the `\Gamma(2)` certificate.

    `\Gamma(2)`, the kernel of `\GL_2(ZZ) \to \GL_2(\FF_2)`, is generated by the
    two shears `A = \begin{pmatrix}1&2\\0&1\end{pmatrix}` and
    `B = \begin{pmatrix}1&0\\2&1\end{pmatrix}` together with `-1` (Sanov 1947:
    `\Gamma(2)/\{\pm 1\}` is free on the two shears).  When each of those three
    occurs as a product of at most :data:`_PLANE_ACTION_WITNESS_BOUND` of the
    given actions, `\Gamma(2)` lies in the generated group and
    `[\GL_2(ZZ) : H] = |\GL_2(\FF_2)| / |H \text{ in } \GL_2(\FF_2)|`, since
    then `H/\Gamma(2)` is that image and `|\GL_2(\FF_2)| = 6`.

    Otherwise the index is not decided here and the value raises, naming the
    witness that was not exhibited.
    """
    shears = {
        "A = ((1, 2), (0, 1))": matrix(SageZZ, [[1, 2], [0, 1]]),
        "B = ((1, 0), (2, 1))": matrix(SageZZ, [[1, 0], [2, 1]]),
        "-1": matrix(SageZZ, [[-1, 0], [0, -1]]),
    }
    missing = [
        name
        for name, target in shears.items()
        if _word_witness(actions, target) is None
    ]
    if missing:
        raise ValueError(
            f"no plane-action index is computed at {plane}: Gamma(2) is generated by the two "
            f"shears and -1, and {missing} do not occur as products of at most "
            f"{_PLANE_ACTION_WITNESS_BOUND} of the {len(actions)} plane actions, so "
            f"Gamma(2) <= <plane actions> is not exhibited"
        )
    order = _generated_image_order(actions, 2)
    if 6 % order:
        raise ValueError(
            f"the plane actions at {plane} have an image of order {order} in GL_2(F_2), which "
            f"does not divide the order of GL_2(F_2)"
        )
    return 6 // order


class LeviQuotientLiftAbsent(ValueError):
    r"""Raised when no plane action admits an integral lift of a prescribed class action.

    The message states which congruence of the block equations of Dutour
    Sikirić--Hulek, *Moduli of polarised Enriques surfaces -- computational
    aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, Theorem 4.9
    and its proof, printed pp. 33--34, fails for every plane action in
    `\GL_2(\ZZ)`, and the modulus at which it was read.  It is a proof of
    absence, not the exhaustion of a search: the plane actions are covered by a
    complete residue system of `\GL_2(\ZZ)` and the congruence is read on that
    system, so nothing outside it can lift.
    """


def _general_linear_classes(modulus):
    r"""Return one integral matrix of determinant `\pm 1` for each class of `\GL_2(\ZZ/m)`.

    `\SL_2(\ZZ) \to \SL_2(\ZZ/m)` is onto, and `\SL_2(\ZZ/m)` is generated by
    the two shears `\begin{pmatrix}1&1\\0&1\end{pmatrix}` and
    `\begin{pmatrix}1&0\\1&1\end{pmatrix}`, so a breadth-first walk over their
    products from the identity reaches each class of `\SL_2(\ZZ/m)` exactly once.
    The walk keeps the *integral* product rather than its reduction, so the entry
    stored for a class is itself an integral matrix of determinant `1` in that
    class; multiplying on the left by `\mathrm{diag}(-1, 1)` gives the classes of
    determinant `-1`.  A class of `\GL_2(\ZZ/m)` has determinant congruent to
    `\pm 1` modulo `m`, so these are all its classes -- the reduction
    `\GL_2(\ZZ) \to \GL_2(\ZZ/m)` is *not* onto for `m \ge 3`, and the sign is
    therefore carried explicitly rather than read off the class.

    The set returned is a complete residue system: every class of `\GL_2(\ZZ)`
    modulo `\Gamma(m)` is the reduction of exactly one of these matrices, so
    testing a property that depends on a matrix only through its class modulo
    `m` on all of them decides it on `\GL_2(\ZZ)`.
    """
    identity = (1, 0, 0, 1)
    lifts = {identity: identity}
    shears = ((1, 1, 0, 1), (1, 0, 1, 1))
    frontier = [identity]
    while frontier and modulus > 1:
        current = frontier.pop()
        element = lifts[current]
        for shear in shears:
            product = (
                (current[0] * shear[0] + current[1] * shear[2]) % modulus,
                (current[0] * shear[1] + current[1] * shear[3]) % modulus,
                (current[2] * shear[0] + current[3] * shear[2]) % modulus,
                (current[2] * shear[1] + current[3] * shear[3]) % modulus,
            )
            if product in lifts:
                continue
            lifts[product] = (
                element[0] * shear[0] + element[1] * shear[2],
                element[0] * shear[1] + element[1] * shear[3],
                element[2] * shear[0] + element[3] * shear[2],
                element[2] * shear[1] + element[3] * shear[3],
            )
            frontier.append(product)
    representatives = {}
    for element in lifts.values():
        negated = (-element[0], -element[1], element[2], element[3])
        for entry in (element, negated):
            representatives.setdefault(
                tuple(value % modulus for value in entry), entry
            )
    return tuple(
        matrix(SageZZ, [[entry[0], entry[1]], [entry[2], entry[3]]])
        for entry in representatives.values()
    )


def _unimodular_lift(entries, modulus):
    r"""Return an integral matrix of determinant `\pm 1` in the class ``entries`` modulo ``modulus``.

    Let the given class be `(a,b;c,d)`.  Its first column generates `ZZ/m`, so
    adding multiples of `m` to `a` and `c` makes them coprime.  Write their
    Bezout relation as `u a + v c = 1`, and let `s = \pm 1` be the determinant
    of the class.  Since `t = (ad-bc-s)/m` is integral, the matrices

    .. math:: \begin{pmatrix} a & b+mtv\\ c & d-mtu \end{pmatrix}

    have the required residues, because `m` divides the two added terms.  Their
    determinant is `ad-bc-mt(a u+c v) = s`.  The construction
    therefore preserves both the whole residue class and the determinant sign.
    """
    first_entry, second_entry, third_entry, fourth_entry = (
        int(entry) for entry in entries
    )
    if modulus <= 0:
        raise ValueError(f"a residue lift needs a positive modulus, not {modulus}")
    determinant = first_entry * fourth_entry - second_entry * third_entry
    if modulus <= 2 or (determinant - 1) % modulus == 0:
        closed = 1
    elif (determinant + 1) % modulus == 0:
        closed = -1
    else:
        raise ArithmeticError(
            f"the class {entries} modulo {modulus} has determinant neither +1 nor -1"
        )
    coprime = None
    for shift in range(modulus + 1):
        for extra in (0, 1):
            left = first_entry + shift * modulus
            right = third_entry + extra * modulus
            if left == 0 and right == 0:
                continue
            if _content((left, right)) == 1:
                coprime = (left, right)
                break
        if coprime is not None:
            break
    if coprime is None:
        raise ArithmeticError(
            f"no lift of the class {entries} modulo {modulus} is built: no shift of its first "
            f"column by multiples of {modulus} makes the two entries coprime, and a class of "
            f"GL_2(ZZ/{modulus}) has a generating first column"
        )
    left, right = coprime
    divisor, bezout_left, bezout_right = SageZZ(left).xgcd(SageZZ(right))
    assert divisor == 1
    multiplier = (left * fourth_entry - right * second_entry - closed) // modulus
    lifted = matrix(
        SageZZ,
        [
            [left, second_entry + modulus * multiplier * bezout_right],
            [right, fourth_entry - modulus * multiplier * bezout_left],
        ],
    )
    assert int(lifted.determinant()) == closed
    assert all(
        (int(value) - int(entry)) % modulus == 0
        for value, entry in zip(lifted.list(), entries, strict=True)
    ), f"the lift {lifted} is not in the class {entries} modulo {modulus}"
    return lifted

def _row_congruence_coset(rectangle, target, modulus):
    r"""Return the solutions of `z\cdot\texttt{rectangle}\equiv \texttt{target}` modulo ``modulus``.

    ``rectangle`` is a `2 \times r` integral matrix, ``target`` a row of length
    `r`, and `z` ranges over `(\ZZ/m)^2` with `m = ``modulus``.  The Smith normal
    form of the transposed rectangle writes `M^t = L \Delta R` with `L` and `R`
    unimodular, so the congruence is `\Delta (R z^t) \equiv L^{-1}
    \texttt{target}^t`: one independent congruence per diagonal entry, whose
    right side must vanish past the rank and must be divisible by
    `\gcd(\Delta_{ii}, m)` where the entry is nonzero.  Each such entry leaves
    `\gcd(\Delta_{ii}, m)` values free and the rest are determined, so the
    solutions form one coset of the subgroup those free coordinates span.

    The answer is ``(particular, generators)`` -- a solution in `(\ZZ/m)^2` and a
    tuple of `(vector, order)` pairs whose multiples, taken over `0 \le a <
    \text{order}`, are exactly the solution set -- or ``None`` when there is no
    solution at all.  Both answers are exact: ``None`` is a theorem about the
    system and not the failure of a search.
    """
    transposed = rectangle.transpose()
    diagonal, left, right = transposed.smith_form()
    if abs(int(left.determinant())) != 1 or abs(int(right.determinant())) != 1:
        raise ArithmeticError(
            f"the Smith normal form of {transposed} came with transformations of determinant "
            f"{int(left.determinant())} and {int(right.determinant())}, which are not unimodular"
        )
    # transposed = left^-1 * diagonal * right^-1, so transposed * z = target is
    # diagonal * (right^-1 z) = left * target and z = right * y.
    transformed = left * matrix(
        SageZZ, len(target), 1, [int(value) for value in target]
    )
    coordinates = [SageZZ.zero(), SageZZ.zero()]
    generators = []
    for position in range(transposed.nrows()):
        value = int(transformed[position, 0])
        pivot = int(diagonal[position, position]) if position < 2 else 0
        divisor = (
            abs(SageZZ(pivot)).gcd(SageZZ(modulus)) if pivot else SageZZ(modulus)
        )
        if SageZZ(value) % divisor:
            return None
        if position >= 2:
            continue
        step = int(SageZZ(modulus) // divisor)
        if pivot:
            reduced = SageZZ(pivot // int(divisor))
            if step == 1:
                coordinates[position] = SageZZ.zero()
            else:
                coordinates[position] = (
                    SageZZ(value) // divisor
                ) * reduced.inverse_mod(SageZZ(step))
        generators.append((position, step, int(divisor)))
    particular = right * matrix(SageZZ, 2, 1, coordinates)
    coset = tuple(int(particular[position, 0]) % modulus for position in range(2))
    span = []
    for position, step, order in generators:
        direction = [0, 0]
        direction[position] = step
        image = right * matrix(SageZZ, 2, 1, direction)
        span.append(
            (
                tuple(int(image[index, 0]) % modulus for index in range(2)),
                order,
            )
        )
    return (coset, tuple(span))


def _coset_elements(coset, modulus):
    r"""Yield every element of the coset :func:`_row_congruence_coset` describes.

    The coset is `(particular, ((w_1, n_1), (w_2, n_2)))` and its elements are
    `particular + a_1 w_1 + a_2 w_2` for `0 \le a_i < n_i`, which is every
    solution exactly once because those multiples of the generators are precisely
    the kernel of the congruence.
    """
    particular, generators = coset
    (first, first_order), (second, second_order) = generators
    for left in range(first_order):
        for right in range(second_order):
            yield tuple(
                (particular[index] + left * first[index] + right * second[index])
                % modulus
                for index in range(2)
            )


def _chinese_remainder_matrix(lower, upper, first_modulus, second_modulus):
    r"""Return the matrix congruent to ``lower`` and ``upper`` modulo the two moduli, or ``None``.

    Both arguments are `2 \times 2` integral matrices.  Such a matrix exists
    exactly when the two agree modulo `\gcd(m_1, m_2)` entry by entry -- a
    necessary condition, and by the Chinese remainder theorem a sufficient one --
    and then it is unique modulo `\operatorname{lcm}(m_1, m_2)`, which is the
    matrix returned.  The caller lifts that class with :func:`_unimodular_lift`
    when it needs an integral matrix of determinant `\pm 1` in it.
    """
    common = int(SageZZ(first_modulus).gcd(SageZZ(second_modulus)))
    quotient = second_modulus // common
    entries = []
    for index in (0, 1):
        for column in (0, 1):
            first_entry = int(lower[index, column]) % first_modulus
            second_entry = int(upper[index, column]) % second_modulus
            difference = second_entry - first_entry
            if difference % common:
                return None
            if quotient == 1:
                shift = 0
            else:
                shift = int(
                    SageZZ(difference // common)
                    * SageZZ(first_modulus // common).inverse_mod(SageZZ(quotient))
                    % SageZZ(quotient)
                )
            entries.append(
                (first_entry + first_modulus * shift) % (first_modulus * quotient)
            )
    return matrix(SageZZ, [entries[0:2], entries[2:4]])


class PrimitiveIsotropicSubobjects(OwnedCategoryOverBaseRing):
    r"""Primitive totally isotropic subobjects of a lattice over ``R``.

    Membership states two facts about the chosen monomorphism ``iota``: the
    form of the codomain restricts to zero along it, and its cokernel is
    torsion free.  Both are checked by the ambient lattice's admission method.
    """

    def _repr_object_names(self):
        return f"primitive totally isotropic subobjects over {self.base_ring()}"

    def an_object(self):
        r"""The isotropic line spanned by the first generator of ``U``."""
        from sage_extensions.categories.lattices import Lattices

        plane = Lattices(self.base_ring())("U")
        return plane.primitive_isotropic_subobject(plane.module_generators()[0])

    def super_categories(self):
        return [ModuleSubobjects(self.base_ring())]

    class ParentMethods:
        def is_totally_isotropic(self) -> bool:
            r"""Return whether the codomain's form restricts to zero along the inclusion."""
            lattice = self.ambient_module()
            zero = lattice.base_ring().zero()
            embedded = self.embedded_module_generators()
            labels = self.module_generating_set()
            return all(
                lattice.b(embedded[left], embedded[right]) == zero
                for left in labels
                for right in labels
            )

        def ambient_lattice(self):
            r"""Return the lattice this isotropic subobject sits in."""
            return self.inclusion().codomain()

        @cached_method
        def isotropic_perpendicular(self):
            r"""Return ``I^perp`` as a subobject of the same lattice.

            The subobject is totally isotropic, so ``I <= I^perp``: this is
            the flag whose successive quotient is the isotropic reduction.
            """
            return self.inclusion().orthogonal_complement()

        @cached_method
        def into_perpendicular(self):
            r"""Return ``I -> I^perp``, the inclusion factored through its own perpendicular."""
            perpendicular = self.isotropic_perpendicular()
            lift = perpendicular.inclusion().lift
            inclusion = self.inclusion()
            return self.Mono(perpendicular)({
                    label: lift(inclusion(self.module_generator(label)))
                    for label in self.module_generating_set()
                })

        @cached_method
        def isotropic_quotient(self):
            r"""Return the represented module ``I^perp/I``.

            This is the underlying module of ``self.isotropic_reduction()``,
            which is the same quotient carrying the form ``I^perp`` induces
            on it.  The two ranks are asserted to agree.
            """
            quotient = self.into_perpendicular().cokernel()
            assert quotient.module_rank() == self.isotropic_reduction().module_rank(), (
                f"two constructions of I^perp/I for the isotropic sublattice I = {self} "
                f"disagree: the cokernel of I -> I^perp has rank {quotient.module_rank()}, "
                f"but the isotropic reduction has rank "
                f"{self.isotropic_reduction().module_rank()}"
            )
            return quotient

        def isotropic_quotient_projection(self):
            r"""Return the projection ``I^perp ->> I^perp/I``.

            The owned ``isotropic_reduction`` returns the quotient lattice
            ``K_I`` but not this map, so the descent of a parabolic element is
            expressed here on the represented cokernel.
            """
            return self.isotropic_quotient().presentation_projection()

        def stabilizes(self, automorphism) -> bool:
            r"""Return whether ``automorphism`` carries this subobject onto itself.

            Both ``g`` and ``g^{-1}`` are asked to send the selected
            generators into the image, so the answer is the set equality
            ``g(I) = I`` and not the inclusion ``g(I) <= I``.
            """
            inclusion = self.inclusion()
            inverse = ~automorphism
            embedded = self.embedded_module_generators()
            return all(
                inclusion.is_in_image(automorphism(embedded[label]))
                and inclusion.is_in_image(inverse(embedded[label]))
                for label in self.module_generating_set()
            )

        @cached_method
        def _stabilizer_action(self):
            r"""The integral-structure action whose stabilizer is ``Stab_{O(L)}(I)``.

            ``None`` for the zero isotropic sublattice, whose stabilizer is the
            whole ambient orthogonal group and so has no orbit to split.
            """
            from sage_indefinite_port.indefinite.marked_lattices import INDUCTION

            embedded = self.embedded_module_generators()
            vectors = tuple(embedded[label] for label in self.module_generating_set())
            if not vectors:
                return None
            # The radical action is what the port's stabilizer problem takes as
            # its "allowed action on J" (IndefiniteForms.g:1710-1723): generators
            # of GL(J). Adjacent transpositions, one shear and one sign change
            # generate GL_k(Z) for every k (Newman, Integral Matrices, VII.1).
            radical_images = general_linear_images(vectors)
            return INDUCTION.recursion.isotropic_stabilizer_action(
                vectors, radical_images
            )

        def _stabilizer_representation(self):
            r"""The finite lattice-orbit representation of the stabilizer action."""
            action = self._stabilizer_action()
            if action is None:
                raise ValueError(
                    f"the stabilizer of {self} has no lattice orbit to represent: it is the "
                    "zero isotropic sublattice, whose stabilizer is the ambient orthogonal group"
                )
            return action.finite_representation()

        def stabilizer_schreier_factors(self):
            r"""Return ``(letters, transversals)`` of the stabilizer's Schreier family.

            ``letters`` are the action groupoid's generators and ``transversals[i]``
            is the transporter of the ``i``-th lattice-orbit point, so the family is
            ``t_(s.p)^-1 s t_p`` over the two.
            """
            return self._stabilizer_representation().stabilizer_schreier_factors()

        def orbit_lattice_records(self):
            r"""Return one record per lattice-orbit point, with its maps.

            See ``_FiniteIntegralRepresentation.orbit_lattice_records``: each record
            states the orbit lattice, the module image and its own generating
            labels, the inclusion into the rational ambient, the images of the
            ambient lattice's generators, and the transport ``t_p: L -> L_p``.
            """
            return self._stabilizer_representation().orbit_lattice_records()

        def middle_transport(self, position, letter):
            r"""Return ``letter`` as an isometry between two orbit lattices.

            The domain is the orbit lattice at ``position``, whose generators are
            the image module's own canonical basis; the transported source basis is
            read once, by the transport, and not again here.
            """
            return self._stabilizer_representation().middle_transport(position, letter)

        def stabilizer_discriminant_image(self):
            r"""Return rho(P_I) as a subgroup of O(A_L) by the action-groupoid construction.

            The stabilizer is presented by the action's own orbit data, and each
            Schreier factor is converted through discriminant transports between
            integral orbit lattices, so no individual rational transporter is
            applied to A_L. The radical action is the full general linear
            group of the isotropic sublattice at every positive rank.
            At rank one, the ambient orthogonal group's certified reflection
            lifts may already attain the entire finite class stabilizer.
            In that case the two containments prove the actual image
            without constructing the lattice orbit. Otherwise the exact
            Schreier calculation remains required.
            The zero sublattice has the full ambient orthogonal stabilizer.
            """
            lattice = self.ambient_lattice()
            if int(self.module_rank()) == 1:
                label = next(iter(self.module_generating_set()))
                vector = self.inclusion()(self.module_generator(label))
                lifts = lattice.O().discriminant_image_reflection_lifts(vector)
                if lifts is not None:
                    return lattice.discriminant_group().O().subgroup(
                        tuple(g.discriminant_morphism() for g in lifts)
                    )
            action = self._stabilizer_action()
            if action is None:
                return lattice.O().discriminant_image()
            return action.finite_representation().stabilizer_discriminant_image()

        def rational_stabilizer_right_cosets(self):
            r"""Return a transversal of ``G/H`` for the rational stabilizer ``G`` of ``I^perp``.

            ``G`` extends the integral stabilizer of ``I^perp`` to the
            rational space, and ``H`` is its intersection with ``O(L)``.
            Elements of the transversal are isometries of ``L tensor QQ``.
            """
            from sage_extensions.categories.isotropic_orbits import _marked_isotropic_category, _marked_isotropic_object
            from sage_indefinite_port.indefinite.marked_lattices import isotropic_stabilizer_right_cosets

            return isotropic_stabilizer_right_cosets(
                _marked_isotropic_category(self.ambient_lattice(), 1), _marked_isotropic_object(self, flag=False)
            )

        def parabolic_subgroup(self):
            r"""Return ``P_I = Stab_{O(L)}(I)``, the one parabolic of the isotropic reduction of ``I``."""
            return self.isotropic_reduction().parabolic_subgroup()

        def levi_restriction(self, automorphism):
            r"""Return ``g|_I`` in ``GL(I)`` for ``g`` in the parabolic subgroup: the isotropic action of ``g``."""
            return self.isotropic_reduction().isotropic_action()(automorphism)

        def levi_quotient_action(self, automorphism):
            r"""Return the descent of ``g`` to ``I^perp/I`` for ``g`` in ``P_I``."""
            assert self.stabilizes(automorphism), (
                f"cannot descend {automorphism} to I^perp/I for the isotropic sublattice "
                f"I = {self}: descent is defined only for an isometry g with g(I) = I, "
                f"and this isometry does not map {self} onto itself"
            )
            perpendicular = self.isotropic_perpendicular()
            perpendicular_inclusion = perpendicular.inclusion()
            projection = self.isotropic_quotient_projection()
            quotient = self.isotropic_quotient()
            return quotient.module_category().Mor(quotient, quotient)(
                {
                    label: projection(
                        perpendicular_inclusion.lift(
                            automorphism(
                                perpendicular_inclusion(
                                    perpendicular.module_generator(label)
                                )
                            )
                        )
                    )
                    for label in perpendicular.module_generating_set()
                }
            )

        def acts_trivially_on_isotropic_reduction(self, automorphism) -> bool:
            r"""Return whether ``(g - 1)(I^perp)`` lies in ``iota(I)``.

            This is the definition of acting as the identity on ``I^perp/I``,
            decided on ``I^perp`` itself, so no quotient is constructed.
            """
            inclusion = self.inclusion()
            perpendicular = self.isotropic_perpendicular()
            perpendicular_inclusion = perpendicular.inclusion()
            return all(
                inclusion.is_in_image(automorphism(embedded) - embedded)
                for embedded in (
                    perpendicular_inclusion(perpendicular.module_generator(label))
                    for label in perpendicular.module_generating_set()
                )
            )

        @cached_method
        def unipotent_radical(self):
            r"""Return the generated kernel on I and on its perpendicular quotient."""
            return self.isotropic_reduction().unipotent_kernel()

        def eichler_transvection(self, orthogonal_vector):
            r"""Return the Eichler transvection ``E_{f,x}`` of this isotropic line.

            For the selected generator ``f`` of a rank-one isotropic subobject
            and ``x`` in ``f^perp``,

            ``E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x``.

            The framing supplies ``f``: the transvection depends on the chosen
            generator and not only on the line, since ``E_{-f,x} = E_{f,-x}``.
            The only coefficient outside `ZZ` is ``q(x)/2``, so the parameter
            ``x`` is admissible exactly when ``q(x)`` is even -- not when the
            whole lattice is even.  On an even lattice that is every ``x`` in
            ``f^perp``; on an odd one it is the even-norm sublattice of
            ``f^perp``, which is what a caller must ask for, and a parameter
            outside it is refused below with ``q(x)`` in the message.

            ``E_{f,x}`` fixes ``f`` and satisfies ``(E_{f,x} - 1)(f^perp) <=
            Z f``, so it lies in ``unipotent_radical()``.  The assignment
            ``x -> E_{f,x}`` is a group morphism from ``(f^perp, +)`` killing
            ``f``, hence a morphism from ``f^perp/f``, which is an
            isomorphism onto the radical on the even-norm parameters:
            ``...IsotropicReductions._pointwise_kernel_generators`` reads the
            kernel of the Levi action as their images.
            """
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            assert int(self.module_rank()) == 1, (
                f"no Eichler transvection is attached to {self}: an Eichler transvection "
                f"needs an isotropic sublattice of rank one, but {self} has rank "
                f"{self.module_rank()}"
            )
            isotropic_vector = self.embedded_module_generators()[
                self.module_generating_set()[0]
            ]
            assert (
                lattice.b(isotropic_vector, orthogonal_vector) == ring.zero()
            ), (
                f"no Eichler transvection E_(f,x) with f = {isotropic_vector} and "
                f"x = {orthogonal_vector}: x must be orthogonal to f, but b(f, x) = "
                f"{lattice.b(isotropic_vector, orthogonal_vector)}"
            )
            square = lattice.q(orthogonal_vector)
            half_square = square // ring(2)
            assert ring(2) * half_square == square, (
                f"no Eichler transvection E_(f,x) with x = {orthogonal_vector} preserves "
                f"{lattice}: q(x) = {square} is odd, so q(x)/2 is not in {ring}"
            )

            def image(label):
                source = lattice.module_generator(label)
                against_x = lattice.b(source, orthogonal_vector)
                against_f = lattice.b(source, isotropic_vector)
                return (
                    source
                    + lattice.scalar_multiple(
                        against_x - half_square * against_f, isotropic_vector
                    )
                    - lattice.scalar_multiple(against_f, orthogonal_vector)
                )

            return lattice.Aut()(
                {label: image(label) for label in lattice.module_generating_set()}
            )

        @cached_method
        def pointed_stabilizer_action(self):
            r"""Return the finite-residue action whose stabilizer fixes this rank-one vector.

            This is the pointwise stabilizer, not the setwise parabolic: the
            quotient action has trivial action on the line.  See
            :func:`_pointed_stabilizer_action` for the lift denominators and
            the finite stable module.  The construction is for a primitive
            isotropic vector, so a subobject of any other rank is refused.

            Its stabilizer is a subgroup of `P_I^1` and need not be all of it:
            a word in rational lifts is a rational isometry, so no family read
            off this action supplies the radical's parameters, and
            :meth:`pointed_stabilizer_generators` generates the two factors
            separately instead.
            """
            return _pointed_stabilizer_action(self)

        @cached_method
        def pointed_stabilizer_generators(self):
            r"""Return generators of the stabilizer of this rank-one vector.

            `P_I^1` is the pointwise stabilizer of `I = Z e`, and it sits in
            `1 -> U_I -> P_I^1 -> M_I -> 1`, where `M_I` is its image in
            `O(K_I)` and `U_I` is the kernel.  Which of the two constructions
            answers depends on whether `L` splits along the chosen lifts of
            `K_I`:

            * when `K'` is primitive and `M = K'^perp` is unimodular, every
              isometry of `K_I` extends as `id_M + sigma`, so `M_I = O(K_I)`
              and the family is one such lift of each generator of `O(K_I)`
              together with the radical's own generators.  It is the whole of
              `P_I^1`: the Levi class of an element is a word in those
              generators, and the same word in their lifts differs from the
              element by an element of the kernel, which the second factor
              generates.  The lifts are
              :meth:`...IsotropicReductions._split_pointwise_levi_lift`'s and
              the kernel's family is
              :meth:`...IsotropicReductions._pointwise_kernel_generators`'s --
              the Eichler transvections at the even-square parameters, exact on
              an odd lattice as well as an even one.  Splitting also forces the
              marked vector's divisibility to be one: `M` is primitive and
              unimodular, `v` lies in it and is primitive there, so
              `b(v, M) = Z`, and the even-square parameters are then the whole
              kernel;
            * otherwise the two factors are generated separately: one
              integral lift per generator of `M_I`, read off the coset graph of
              `O(K_I)/M_I` where a class is decided by whether its element has
              a pointwise lift
              (:meth:`...IsotropicReductions.pointwise_levi_image_generators`),
              together with the radical's own generators.  This is the whole of
              `P_I^1` however proper `M_I` is: the classes of the family are a
              generating set of `M_I` and the family contains `U_I`, so an
              element of `P_I^1` differs from the word in the lifted classes
              that carries its own class by an element of the kernel, which the
              second factor generates.

            Every member is checked to fix the marked vector before it is
            returned.
            """
            vector = self.inclusion()(
                self.module_generator(next(iter(self.module_generating_set())))
            )
            reduction = self.isotropic_reduction()
            if reduction._reduction_lift_splitting() is not None:
                quotient = reduction.quotient_lattice()
                family = tuple(
                    reduction.pointwise_levi_lift(generator)
                    for generator in quotient.O().group_generators()
                ) + tuple(reduction._pointwise_kernel_generators())
            else:
                family = tuple(
                    reduction.pointwise_levi_image_generators()
                ) + tuple(reduction._pointwise_kernel_generators())
            if any(isometry(vector) != vector for isometry in family):
                raise ArithmeticError(
                    f"the pointwise stabilizer action at {vector} returned an integral "
                    f"isometry that moves the marked vector"
                )
            return family


        def unipotent_group_generators(self):
            r"""Return a finite indexed family generating the full integral unipotent radical.

            These are the integral generators of the common kernel on I and
            I-perp/I. In higher null rank this includes the full Hom parameters
            and the central pointwise-perpendicular shears.
            """
            from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values

            return finite_indexed_family_from_values(None, tuple(self.unipotent_radical().group_generators()))

        def is_equivalent_to(self, other) -> bool:
            r"""Return whether ``O(L)`` carries this isotropic subobject to ``other``.

            The decision comes from the exact indefinite computation; where its
            hypotheses do not hold, that computation states the absence rather
            than searching the group.
            """
            return self.transporter_witness_to(other) is not None

        def transporter_witness_to(self, other):
            r"""Return one ``g`` in ``O(L)`` with ``g(I) = other``, or ``None``.

            The full transporter is the coset ``g P_I``, which is infinite
            whenever ``P_I`` is; one witness together with
            ``parabolic_subgroup`` presents it.
            """
            assert other.ambient_lattice() is self.ambient_lattice(), (
                f"no isometry can carry {self} to {other}: they are sublattices of "
                f"different lattices, {self.ambient_lattice()} and {other.ambient_lattice()}"
            )
            return self.ambient_lattice().Aut().isotropic_equivalence_witness(
                self, other
            )

        def _kernel_parameter_witness(self, source, target):
            r"""Solve ``k(source) = target`` for one element ``k`` of the pointwise kernel, or ``None``.

            The kernel is ``K = ker(P_I -> O(I^perp))`` and its elements act on
            the ambient lattice by ``x |-> x + N(pi(x))`` with
            ``N: L/I^perp -> rad(I^perp)`` linear, which is the parametrization
            :meth:`IsotropicReductions._pointwise_perpendicular_kernel_data`
            retains: there ``N`` runs over the complete integral solution module
            of the homogeneous isometry equations
            ``b(N f_a, f_b) + b(f_a, N f_b) = 0``, so the assignment
            ``parameter |-> 1 + N`` is a homomorphism from an additive lattice to
            ``K`` and every element of ``K`` is one of its values.  On a vector
            ``x`` the displacement is therefore linear in the parameter, and
            ``k(source) = target`` is one integer linear system, solved exactly
            by Smith normal form.  ``None`` is the exact statement that ``K``
            carries ``source`` onto ``target``; the returned isometry is checked
            against the two endpoints before it leaves this method.
            """
            lattice = self.ambient_lattice()
            reduction = self.isotropic_reduction()
            parameters = reduction.pointwise_perpendicular_parameter_module()
            labels = tuple(parameters.module_generating_set())
            ring = parameters.base_ring()
            source_coordinates = self.coordinates(source)
            target_coordinates = self.coordinates(target)
            if not labels:
                return lattice.Aut().one() if source_coordinates == target_coordinates else None
            columns = []
            for label in labels:
                isometry = reduction.pointwise_perpendicular_isometry(
                    parameters.module_generator(label)
                )
                image = self.coordinates(isometry(source))
                columns.append(
                    [
                        reached - start
                        for reached, start in zip(image, source_coordinates, strict=True)
                    ]
                )
            rows = [
                [column[position] for column in columns]
                for position in range(len(source_coordinates))
            ]
            displacement = [
                reached - start
                for reached, start in zip(target_coordinates, source_coordinates, strict=True)
            ]
            values = _integral_solution(
                matrix(SageZZ, rows),
                matrix(SageZZ, [[entry] for entry in displacement]),
            )
            if values is None:
                return None
            parameter = parameters.zero()
            for entry, label in zip(values, labels, strict=True):
                parameter = parameter + ring(int(entry)) * parameters.module_generator(label)
            isometry = reduction.pointwise_perpendicular_isometry(parameter)
            assert isometry(source) == target, (
                f"the pointwise-kernel parameter solving {source} |-> {target} does not carry "
                f"{source} onto {target}: it carries it onto {isometry(source)}"
            )
            return isometry

        def pointwise_vector_equivalence_witness(self, left, right):
            r"""Return one element of the pointwise stabilizer of ``I`` carrying ``left`` onto ``right``, or ``None``.

            ``left`` and ``right`` are vectors of the ambient lattice, and the
            pointwise stabilizer is \(C_I = \{g \in O(L) : g(\iota(I)) = \iota(I)\ \text{pointwise}\}\).

            **The maximal isotropic case** ``I = I^perp``.  Then \(C_I\) is
            exactly ``K = ker(P_I -> O(I^perp))``: an element fixing ``I``
            pointwise stabilizes ``I^perp`` and acts trivially on the whole of
            ``I = I^perp``, and conversely an element fixing ``I^perp``
            pointwise fixes ``I``.  The kernel is the one
            :meth:`IsotropicReductions._pointwise_perpendicular_kernel_data`
            retains as a complete integral parameter module, so
            :meth:`_kernel_parameter_witness` decides ``k(left) = right`` for
            ``k`` in the whole pointwise stabilizer and not merely for some
            selected generators of it.

            **The proper case** ``I < I^perp``.  \(C_I\) preserves
            \(I^\perp\) — for \(y \in I^\perp\) and \(i \in I\),
            \(b(i, g(y)) = b(g^{-1}(i), y) = b(i, y) = 0\) — and acts on it as
            the identity on \(I\), so it descends to \(I^\perp/I\), and the
            parabolic exact sequence stated at the top of this module reads

            \[
            1 \to U_I \to C_I \to M_I^0 \to 1, \qquad M_I^0 \le O(I^\perp/I),
            \]

            with \(U_I = \{g : g|_I = 1,\ (g-1)(I^\perp) \subseteq I\}\) the
            radical.  That is the \(Q_1 = 1\) case of the block form of an
            isometry preserving a totally isotropic \(k\)-plane: in a basis
            \((u_a \mid p_a \mid \tilde\kappa_b)\) of
            \(U \mid I \mid I^\perp/I\) the Gram matrix is
            \(\begin{pmatrix} H & J & 0 \\ J^t & 0 & 0 \\ 0 & 0 & A\end{pmatrix}\)
            with \(J\) and \(A\) non-degenerate, an extending isometry has the
            block form
            \(\begin{pmatrix} P_1 & P_2 & P_3 \\ 0 & Q_1 & 0 \\ 0 & Q_2 & Q_3\end{pmatrix}\)
            with \(J = P_1 J Q_1^t\), and \(Q_1\) is the action on \(I\);
            so \(Q_1 = 1\) together with the invertibility of \(J\) forces
            \(P_1 = 1\): the \(I\)-block and the \(U\)-block of a pointwise
            element are the identity, and what remains is \(Q_3\), the action on
            \(I^\perp/I\), and the radical entries \(P_2, P_3, Q_2\) (Dutour
            Sikirić--Hulek, *Moduli of polarised Enriques surfaces —
            computational aspects*, J. London Math. Soc. 110 (2024),
            arXiv:2302.01679v2, Theorem 4.9 and its proof, printed pp. 33--34).
            The radical is generated by the Eichler transvections
            \(t(p_a, X)\) for \(X \in I^\perp\), whose parameters add
            (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, Lemma 3.1 and
            equations (4)--(5), printed p. 8).

            Those two statements decide the following, each answered ``None``:

            * \(q(left) \ne q(right)\), since every element of \(C_I\) is an
              isometry of \(L\);
            * \(b(left, p_a) \ne b(right, p_a)\) for a generator \(p_a\) of
              \(I\), because \(b(g(left), p_a) = b(left, g^{-1}(p_a)) = b(left, p_a)\);
            * \(right - left\) outside \(I^\perp\), because
              \(b(p_a, g(left) - left) = 0\) for every \(a\);
            * both vectors in \(I\) and distinct, because \(C_I\) fixes them
              individually;
            * both in \(I^\perp\) with \(I^\perp/I\) definite and the two
              reductions in different \(O(I^\perp/I)\)-orbits, because \(C_I\)
              descends into \(O(I^\perp/I)\)
              (:meth:`_pointwise_reduction_witness`).

            A witness is built from those factors: the block
            \(\mathrm{diag}(1, 1, Q_3)\) of the carrying quotient action
            (:meth:`_pointwise_block_isometry`), a shear of the radical whose
            parameter is one integral linear system
            (:meth:`_pointwise_radical_element`), and an element of the
            pointwise kernel, whose parameter module is complete.  Each
            candidate is evaluated on ``left`` before it is returned.

            Where the search is not exhaustive the call raises and names the
            missing datum instead of answering ``None``: for a vector outside
            \(I^\perp\), whose image under the action on a complement of
            \(I^\perp\) is not parametrized here; for an indefinite
            \(I^\perp/I\), whose isometry group is infinite; and for a
            displacement that the transvection parameters do not reach
            integrally.  No element of the infinite group is listed and no
            generating family of it is selected.
            """
            lattice = self.ambient_lattice()
            source = left if element_parent(left) is lattice else lattice(left)
            target = right if element_parent(right) is lattice else lattice(right)
            perpendicular = self.isotropic_perpendicular()
            if perpendicular.module_rank() == self.module_rank():
                return self._kernel_parameter_witness(source, target)
            if lattice.q(source) != lattice.q(target):
                return None
            if self._reduction_values(source) != self._reduction_values(target):
                return None
            perpendicular_inclusion = perpendicular.inclusion()
            if not perpendicular_inclusion.is_in_image(target - source):
                return None
            inclusion = self.inclusion()
            if inclusion.is_in_image(source) and inclusion.is_in_image(target):
                return lattice.Aut().one() if source == target else None
            if not perpendicular_inclusion.is_in_image(source):
                raise ArithmeticError(
                    f"cannot decide whether {source} and {target} are equivalent under the "
                    f"pointwise stabilizer of {self}: they differ by an element of I^perp, so an "
                    f"element of the stabilizer would carry one onto the other through its action "
                    f"on a complement of I^perp, which is trivial on L/I^perp but is not "
                    f"parametrized here.  Both vectors must lie in I^perp = {perpendicular}"
                )
            witness = self._kernel_parameter_witness(source, target)
            if witness is not None:
                return witness
            return self._pointwise_reduction_witness(source, target)

        def vector_equivalence_witness(self, left, right):
            r"""Return one element of ``P_I = Stab_{O(L)}(I)`` carrying ``left`` onto ``right``, or ``None``, or refuse.

            ``left`` and ``right`` are vectors of the ambient lattice.  The
            parabolic is the semidirect-like product of its Levi factor and its
            unipotent radical, ``1 -> U_I -> P_I -> M_I -> 1`` with
            ``M_I <= GL(I) x O(I^perp/I)`` (this module's own statement at the
            top of the file), so a witness in ``P_I`` is a unipotent element
            composed with a Levi element and the decision below is exact on the
            unipotent part:

            * ``q(left) != q(right)``: ``None``, because every element of ``P_I``
              is an isometry of ``L`` and preserves the quadratic form.
            * the content of ``b(left, -)|_I`` differs from the content of
              ``b(right, -)|_I``, or the content of ``b(-, left)`` differs from
              the content of ``b(-, right)``: ``None``, because an element of
              ``P_I`` carries ``I`` onto ``I`` bijectively and hence acts on
              ``Hom(I, ZZ)`` and on ``Hom(L, ZZ)`` by unimodular changes of
              coordinates, which preserve the content, the gcd of the values on
              a basis.
            * the pointwise kernel ``K = ker(P_I -> O(I^perp))`` carries ``left``
              onto ``right``: that element is returned, solved for exactly as
              :meth:`_kernel_parameter_witness` does, and ``K`` is a subgroup of
              ``P_I``.  ``K`` lies in the unipotent radical ``U_I``, and equals it
              when ``I = I^perp``, so this decides the unipotent part of the
              parabolic on a maximal isotropic subobject.
            * otherwise :meth:`_reduction_orbit_witness` decides through the
              reduction modulo ``I``: its answer is an element of ``P_I``, or
              ``None`` when the reductions lie in different orbits of the image
              of ``P_I`` in ``O(I^perp/I)``.  That stage needs ``I^perp/I``
              definite, where the image is finite, and both vectors in
              ``I^perp``, where the reduction is defined; outside those
              hypotheses it refuses and names the missing datum.

            ``None`` is therefore a decision, and this call never answers
            ``None`` because it failed to find a witness.  No element of an
            infinite group is listed and no generating family of one is selected.
            """
            lattice = self.ambient_lattice()
            source = left if element_parent(left) is lattice else lattice(left)
            target = right if element_parent(right) is lattice else lattice(right)
            if lattice.q(source) != lattice.q(target):
                return None
            if _content(self._reduction_values(source)) != _content(
                self._reduction_values(target)
            ):
                return None
            if _content(self._dual_values(source)) != _content(self._dual_values(target)):
                return None
            witness = self._kernel_parameter_witness(source, target)
            if witness is not None:
                return witness
            return self._reduction_orbit_witness(source, target)

        def _reduction_classes(self, vector):
            r"""Return the class of ``vector`` in ``I^perp/I`` and its lift on the chosen frame.

            ``vector`` must lie in \(I^\perp\); the lift is the reduction's own
            coordinate frame, so ``vector`` equals the lift of its class plus an
            element of \(I\).
            """
            lattice = self.ambient_lattice()
            reduction = self.isotropic_reduction()
            perpendicular = reduction.orthogonal_complement().inclusion()
            if not perpendicular.is_in_image(vector):
                raise ArithmeticError(
                    f"the reduction of {vector} modulo {self} is not defined: the vector does "
                    f"not lie in the perpendicular I^perp of {self}, so it has no class in "
                    f"I^perp/I"
                )
            quotient = reduction.quotient_lattice()
            labels = tuple(quotient.module_generating_set())
            class_of = reduction.projection()(perpendicular.lift(vector))
            coordinates = class_of.to_vector()
            frame = self.quotient_frame_lifts()
            lifted = sum(
                (
                    lattice.scalar_multiple(
                        lattice.base_ring()(int(coordinates(label))), frame[label]
                    )
                    for label in labels
                    if int(coordinates(label))
                ),
                lattice.zero(),
            )
            return class_of, lifted, vector - lifted

        def _unimodular_carrying(self, source, target):
            r"""Return a matrix in ``GL_2(ZZ)`` carrying ``source`` onto ``target``, or ``None``.

            Two vectors of `ZZ^2` are carried onto one another by a unimodular
            matrix exactly when their contents agree: a unimodular matrix
            preserves the content, and two vectors of content `c` are `c` times
            primitive vectors, which the completion of each to a `ZZ`-basis
            (Bezout) carries onto one another.
            """
            if len(source) != 2 or len(target) != 2:
                return None
            source_content = _content(source)
            if source_content != _content(target):
                return None
            if source_content == 0:
                return matrix(SageZZ, [[1, 0], [0, 1]])
            primitive_source = tuple(SageZZ(entry) // source_content for entry in source)
            primitive_target = tuple(SageZZ(entry) // source_content for entry in target)

            def completion(primitive):
                first, second = int(primitive[0]), int(primitive[1])
                divisor, left, right = SageZZ(first).xgcd(SageZZ(second))
                assert abs(int(divisor)) == 1, (
                    f"{primitive} is not primitive: {first} and {second} have gcd {divisor}"
                )
                return matrix(SageZZ, [[first, -int(right)], [second, int(left)]])

            action = completion(primitive_target) * completion(primitive_source).inverse()
            assert action * matrix(SageZZ, [[entry] for entry in source]) == matrix(
                SageZZ, [[entry] for entry in target]
            ), (
                f"the unimodular matrix built for {source} |-> {target} does not carry it there"
            )
            return action

        def _preserves_the_form(self, automorphism) -> bool:
            r"""Whether ``automorphism`` preserves the pairing on a generating set of the lattice."""
            lattice = self.ambient_lattice()
            generators = tuple(lattice.module_generators())
            images = tuple(automorphism(generator) for generator in generators)
            return all(
                lattice.b(image, other) == lattice.b(generator, source)
                for generator, image in zip(generators, images, strict=True)
                for source, other in zip(generators, images, strict=True)
            )

        def _frame_matrix(self, automorphism):
            r"""Return the matrix of an isometry of ``I^perp/I`` on the reduction's frame.

            The frame is a section of \(I^\perp \twoheadrightarrow I^\perp/I\)
            on a generating set, so an isometry of the quotient is read as the
            coordinate matrix of its images of the frame's classes.
            """
            quotient = self.isotropic_reduction().quotient_lattice()
            labels = tuple(quotient.module_generating_set())
            columns = []
            for label in labels:
                image = automorphism(quotient.module_generator(label))
                coordinates = image.to_vector()
                columns.append([int(coordinates(other)) for other in labels])
            return matrix(SageZZ, columns).transpose()

        def _levi_block_isometry(self, plane_action, quotient_action=None):
            r"""Return the isometry of ``L`` with ``plane_action`` on ``I`` and the identity on ``I^perp/I``, or ``None``.

            With the plane basis \((p_1,p_2)\), a frame \((\tilde\kappa_a)\)
            of \(I^\perp\) over \(I\) and a complement \((u_1,u_2)\) of
            \(I^\perp\), the isometry asked for is the block matrix
            \(\mathrm{diag}(A, A^{-t}, 1)\) with
            \(A^{-t} = {}^{t}(J A^{-1} J^{-1})\) and \(J = (b(p_i,u_j))\),
            read in that basis and carried to the lattice's own generators.
            That is the block equation \(J = g|_I J g|_U^t\) of Dutour
            Sikirić–Hulek, *Moduli of polarised Enriques surfaces —
            computational aspects*, J. London Math. Soc. 110 (2024),
            arXiv:2302.01679v2, §"The Tits building", Theorem
            (`theorem_isotropic_k_planes`, printed pp. 33--34), which determines the
            \(I\)-block from the \(U\)-block; :meth:`levi_lift_generators`
            reads the same equation for the elementary matrices of \(GL(I)\).
            ``quotient_action`` is the isometry of \(I^\perp/I\) the element
            is to induce, read on the reduction's frame; the default is the
            identity.  The result is returned only after the pairing is checked
            on a generating set of ``L``, because the block equations constrain
            the \(I\)- and \(U\)-blocks against each other and say nothing
            about a complement that does not pair honestly with the plane.
            """
            complement = self.splitting_complement()
            if complement is None:
                return None
            plane = self.plane_basis()
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            pairing = matrix(
                SageZZ,
                [
                    [int(lattice.b(left, right)) for right in complement]
                    for left in plane
                ],
            )
            if int(pairing.determinant()) == 0:
                return None
            try:
                contragredient = (
                    pairing * plane_action.inverse() * pairing.inverse()
                ).transpose()
            except (ZeroDivisionError, ValueError):
                return None
            if any(entry not in SageZZ for entry in contragredient.list()):
                return None
            frame = self.quotient_frame_lifts()
            frame_vectors = tuple(frame[label] for label in sorted(frame, key=int))
            basis = tuple(plane) + tuple(complement) + frame_vectors
            change = matrix(SageZZ, [self.coordinates(vector) for vector in basis])
            if abs(int(change.determinant())) != 1:
                raise ArithmeticError(
                    f"the plane basis, the complement and the reduction's frame do not form a "
                    f"ZZ-basis of {lattice}: their coordinate matrix has determinant "
                    f"{change.determinant()}"
                )
            size = len(tuple(lattice.module_generating_set()))
            block = matrix(SageZZ, size, size, 0)
            for row in range(2):
                for column in range(2):
                    block[row, column] = plane_action[row, column]
                    block[2 + row, 2 + column] = contragredient[row, column]
            if quotient_action is None:
                for position in range(4, size):
                    block[position, position] = 1
            else:
                frame_block = self._frame_matrix(quotient_action)
                for row in range(size - 4):
                    for column in range(size - 4):
                        block[4 + row, 4 + column] = frame_block[row, column]
            lifted = change.inverse() * block * change
            if any(entry not in SageZZ for entry in lifted.list()):
                return None
            images = {
                label: lattice.linear_combination(
                    {
                        other: ring(int(lifted[row, column]))
                        for row, other in enumerate(lattice.module_generating_set())
                        if int(lifted[row, column])
                    }
                )
                for column, label in enumerate(lattice.module_generating_set())
            }
            candidate = lattice.Aut()(images)
            return candidate if self._preserves_the_form(candidate) is True else None

        def _reduction_orbit_witness(self, source, target):
            r"""Return an element of ``P_I`` carrying ``source`` onto ``target`` through ``I^perp/I``, or ``None``.

            Both vectors must lie in \(I^\perp\), where the reduction modulo
            \(I\) is defined, and \(I^\perp/I\) must be definite, so that its
            isometry group is finite.

            If the two reductions lie in different orbits of
            \(O(I^\perp/I)\), no element of \(P_I\) carries one vector onto
            the other, and ``None`` is the decision: an element of \(P_I\)
            stabilizes \(I^\perp\), hence descends to an isometry of
            \(I^\perp/I\), so it can only carry a class into the
            \(O(I^\perp/I)\)-orbit of that class.  That is a statement about
            the whole orthogonal group of the quotient, not about a selected
            generating family of it.

            Otherwise the two vectors reduce to classes in one orbit, their
            difference after the carrying isometry lies in \(I\), and an
            element with plane block \(A\) and quotient block \(\psi\) acts on
            the reduction's frame by
            \(i + \tilde\kappa \mapsto A i + \widetilde{\psi(\kappa)}\).
            So a witness is sought among the pairs \((A, \psi)\) with
            \(\psi\) carrying one class onto the other and \(A\)
            (:meth:`_unimodular_carrying`) carrying one \(I\)-part onto the
            other; :meth:`_levi_block_isometry` realizes each pair by the block
            equation of Dutour Sikirić–Hulek, *Moduli of polarised Enriques
            surfaces — computational aspects*, J. London Math. Soc. 110 (2024),
            arXiv:2302.01679v2, §"The Tits building", Theorem
            (`theorem_isotropic_k_planes`, printed pp. 33--34), and the composed
            element is returned only after it is evaluated on ``source``.

            The call raises rather than answering ``None`` where it cannot
            decide: when \(I^\perp/I\) is not definite, when a vector lies
            outside \(I^\perp\) (the action of \(P_I\) on \(L/I^\perp\) is
            not computed here), when the \(I\)-parts have different contents so
            that no unimodular matrix carries one onto the other, or when the
            block element for the pair is not integral.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            if quotient.is_definite() is not True:
                raise ArithmeticError(
                    f"cannot decide whether {source} and {target} are equivalent under "
                    f"{self.parabolic_subgroup()} through the reduction modulo I: that "
                    f"reduction is I^perp/I = {quotient} of signature "
                    f"{quotient.signature_pair()}, whose isometry group is infinite, so its "
                    f"orbits are not a finite computation here.  The pointwise kernel and the "
                    f"two reduction contents are already decided"
                )
            source_class, _source_lift, source_part = self._reduction_classes(source)
            target_class, _target_lift, target_part = self._reduction_classes(target)
            automorphisms = quotient.Aut()
            if not any(
                automorphism(source_class) == target_class
                for automorphism in automorphisms
            ):
                return None
            action = self._unimodular_carrying(
                self._plane_coordinates(source_part),
                self._plane_coordinates(target_part),
            )
            if action is None:
                raise ArithmeticError(
                    f"cannot decide whether {source} and {target} are equivalent under "
                    f"{self.parabolic_subgroup()}: their reductions modulo I lie in one orbit "
                    f"of O(I^perp/I), but the I-parts of their reductions have contents "
                    f"{_content(self._plane_coordinates(source_part))} and "
                    f"{_content(self._plane_coordinates(target_part))}, and the elements "
                    f"realized here act on I by unimodular matrices, which preserve content"
                )
            for automorphism in automorphisms:
                if automorphism(source_class) != target_class:
                    continue
                element = self._levi_block_isometry(action, automorphism)
                if element is not None and element(source) == target:
                    return element
            raise ArithmeticError(
                f"cannot decide whether {source} and {target} are equivalent under "
                f"{self.parabolic_subgroup()}: their reductions modulo I lie in one orbit of "
                f"O(I^perp/I) and their I-parts have one content, but no element with the "
                f"carrying plane block and the carrying quotient block was realized integrally "
                f"by the block equation.  Neither answer is claimed"
            )

        def _pointwise_reduction_witness(self, source, target):
            r"""Return an element of the pointwise stabilizer carrying ``source`` onto ``target`` through \(I^\perp/I\), or ``None``.

            Both vectors must lie in \(I^\perp\), where the reduction modulo
            \(I\) is defined, and \(I^\perp/I\) must be definite, so that its
            isometry group is finite.

            ``None`` is the decision exactly when the two reductions lie in
            different orbits of \(O(I^\perp/I)\): an element of the pointwise
            stabilizer fixes \(I\) pointwise, hence stabilizes \(I^\perp\) and
            descends to an isometry of \(I^\perp/I\), so it can only carry a
            class into the \(O(I^\perp/I)\)-orbit of that class.  That is a
            statement about the whole orthogonal group of the quotient, not
            about a selected generating family of it.

            Otherwise the two reductions lie in one orbit, and a witness is
            sought among the elements with the carrying quotient action
            (:meth:`_pointwise_block_isometry`), corrected by a shear of the
            radical (:meth:`_pointwise_radical_element`) and by an element of
            the pointwise kernel (:meth:`_pointwise_correction`).  Every
            candidate is evaluated on ``source``, and where the search is not
            exhaustive the call refuses rather than answering ``None``.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            if quotient.is_definite() is not True:
                raise ArithmeticError(
                    f"cannot decide whether {source} and {target} are equivalent under the "
                    f"pointwise stabilizer of {self} through the reduction modulo I: that "
                    f"reduction is I^perp/I = {quotient} of signature "
                    f"{quotient.signature_pair()}, whose isometry group is infinite, so its "
                    f"orbits are not a finite computation here.  The value of the quadratic "
                    f"form, the values b(-, I) and the class of the difference modulo I^perp "
                    f"are already decided"
                )
            source_class, _source_lift, _source_part = self._reduction_classes(source)
            target_class, _target_lift, _target_part = self._reduction_classes(target)
            automorphisms = quotient.Aut()
            if not any(
                automorphism(source_class) == target_class
                for automorphism in automorphisms
            ):
                return None
            for automorphism in automorphisms:
                if automorphism(source_class) != target_class:
                    continue
                element = self._pointwise_block_isometry(automorphism)
                if element is None:
                    continue
                reached = element(source)
                if reached == target and self._fixes_isotropic_pointwise(element):
                    return element
                correction = self._pointwise_correction(reached, target)
                if correction is None:
                    continue
                candidate = correction * element
                if candidate(source) == target and self._fixes_isotropic_pointwise(
                    candidate
                ):
                    return candidate
            raise ArithmeticError(
                f"cannot decide whether {source} and {target} are equivalent under the "
                f"pointwise stabilizer of {self}: their reductions modulo I lie in one orbit of "
                f"O(I^perp/I), but no element with the carrying quotient action was realized "
                f"integrally by the block equation and the radical's Eichler transvections, and "
                f"the pointwise kernel does not carry the residue either.  Neither answer is "
                f"claimed"
            )

        def _fixes_isotropic_pointwise(self, automorphism) -> bool:
            r"""Return whether ``automorphism`` fixes every generator of ``I``, i.e. lies in \(C_I\).

            The generators of \(I\) are a generating set, so fixing them fixes
            \(I\) pointwise; this is the condition a returned witness has to
            satisfy, checked on the candidate itself and not inherited from the
            factor it was built from.
            """
            return all(
                automorphism(vector) == vector for vector in self.isotropic_basis()
            )

        def _pointwise_correction(self, reached, target):
            r"""Return an element of the radical followed by one of the pointwise kernel carrying ``reached`` onto ``target``, or ``None``.

            ``reached`` and ``target`` lie in \(I^\perp\) and in one class
            modulo \(I\), so their difference lies in \(I\) and an Eichler
            transvection can realize it up to the integrality of one linear
            system (:meth:`_pointwise_radical_element`).  Whatever remains is
            asked of the pointwise kernel, whose parameter module is complete.
            """
            lattice = self.ambient_lattice()
            shear = self._pointwise_radical_element(reached, target - reached)
            candidate = lattice.Aut().one() if shear is None else shear
            if candidate(reached) == target:
                return candidate
            kernel = self._kernel_parameter_witness(candidate(reached), target)
            return None if kernel is None else kernel * candidate

        def _pointwise_radical_element(self, vector, displacement):
            r"""Return an Eichler shear carrying ``vector`` onto ``vector + displacement``, or ``None``.

            ``vector`` lies in \(I^\perp\) and ``displacement`` in \(I\).  Write
            \((p_a)\) for :meth:`isotropic_basis` and \((w_b)\) for a `ZZ`-basis
            of \(I^\perp\).  The transvection at \(p_a\) with parameter
            \(X \in I^\perp\),

            \[
            t(p_a, X)(y) = y - b(X, y)\,p_a + b(p_a, y)\,X
            - \tfrac12 q(X)\,b(p_a, y)\,p_a ,
            \]

            (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, Lemma 3.1 and
            equation (4), printed p. 8) is an integral isometry on an even
            lattice, fixes \(I\) pointwise — \(X \in I^\perp\) gives
            \(b(X, p_b) = b(p_a, p_b) = 0\), hence \(t(p_a, X)(p_b) = p_b\) —
            and acts on \(y \in I^\perp\) as \(y \mapsto y - b(X, y) p_a\).
            Parameters of one \(a\) add, by equation (5) of the same page, and
            parameters of different \(a\) commute because the displacement of
            each lies in the span of its own \(p_a\); so the composite carries
            \(y\) to \(y - \sum_a b(X_a, y) p_a\).  Prescribing
            ``displacement`` with coordinates \(d_a\) on \((p_a)\) is one
            integer linear system per \(a\),

            \[
            \sum_b \lambda_b\, b(w_b, y) = -d_a , \qquad X_a = \sum_b \lambda_b w_b ,
            \]

            decided exactly by Smith normal form.  ``None`` is therefore the
            statement that this family of shears does not realize the
            displacement integrally, and not a failure to look for one.
            """
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            if lattice.is_even() is not True:
                raise ArithmeticError(
                    f"cannot decide whether {vector} and {vector + displacement} are related "
                    f"by the radical at {self}: the Eichler transvections used here need the "
                    f"half-integral coefficient q(X)/2 of an even lattice, and {lattice} is odd"
                )
            isotropic = self.isotropic_basis()
            perpendicular = self.vector_perpendicular_basis(isotropic)
            coordinates = self._plane_coordinates(displacement)
            system = matrix(
                SageZZ,
                [[int(lattice.b(vector, basis_vector)) for basis_vector in perpendicular]],
            )
            transvections = []
            for position, coefficient in enumerate(coordinates):
                solution = _integral_solution(
                    system, matrix(SageZZ, [[-coefficient]])
                )
                if solution is None:
                    return None
                parameter = lattice.zero()
                for entry, basis_vector in zip(solution, perpendicular, strict=True):
                    if int(entry):
                        parameter = parameter + lattice.scalar_multiple(
                            ring(int(entry)), basis_vector
                        )
                transvections.append(
                    lattice.eichler_transvection(isotropic[position], parameter)
                )
            if not transvections:
                return lattice.Aut().one()
            result = transvections[0]
            for other in transvections[1:]:
                result = result * other
            return result

        def pointwise_quotient_lift(self, quotient_action):
            r"""Return the isometry fixing ``I`` pointwise whose class action is ``quotient_action``.

            ``quotient_action`` is an isometry of \(K_I=I^\perp/I\), read on
            the reduction's frame.  In the basis
            \((u_a\mid p_a\mid\tilde\kappa_b)\) of
            \(U\mid I\mid I^\perp/I\) the Gram matrix is
            \(\begin{pmatrix}H&J&0\\J^t&0&0\\0&0&A\end{pmatrix}\) with \(J\)
            and \(A\) non-degenerate, and
            :meth:`_pointwise_block_isometry` realizes the block
            \(\mathrm{diag}(1,1,Q_3)\) for the matrix \(Q_3\) of
            ``quotient_action`` on that frame.  The block is an isometry
            exactly when \(Q_3^tAQ_3=A\), which holds because
            ``quotient_action`` is an isometry of the form on \(K_I\); its
            \(U\)- and \(I\)-blocks are the identity, so the element it
            conjugates back to fixes \(I\) pointwise; and its mixed entries
            are zero, which is the split hypothesis of
            :meth:`splitting_complement` that the complement \(U\) pairs
            trivially with \(K_I\) (Dutour Sikirić--Hulek, *Moduli of
            polarised Enriques surfaces — computational aspects*, J. London
            Math. Soc. 110 (2024), arXiv:2302.01679v2, Theorem 4.9 and its
            proof, printed pp. 33--34, the block form of an isometry
            preserving a totally isotropic \(k\)-plane).

            Under that hypothesis a lift exists for every
            ``quotient_action``, so this method raises rather than answering
            ``None`` when the construction does not produce one: a ``None``
            here would say that the fibre over an isometry of \(K_I\) is
            empty, which the block equation contradicts.  Two cases are
            declined, each naming the missing datum: a line, whose pointwise
            fibre is decided by its signed lift torsor instead, and a plane
            with no complement of \(I^\perp\) pairing trivially with
            \(K_I\), where the lift needs the mixed block entries that the
            split hypothesis makes vanish.  At rank zero \(I=0\),
            \(I^\perp=L\), and the reduction's projection
            \(L\twoheadrightarrow K_I\) is an isomorphism, so the class
            isometry is carried across that identification and the result is
            kept only after it is checked against the pairing.
            """
            rank = int(self.module_rank())
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            if rank == 1:
                raise ValueError(
                    f"no pointwise quotient lift is constructed at {self}: the block equation here "
                    f"is stated for a totally isotropic plane and {self} has rank one, whose "
                    f"pointwise fibre is decided by the marked-line lift torsors"
                )
            if rank == 0:
                # I = 0, so I^perp = L and the reduction's projection L -> K_I
                # is an isomorphism; the lift of a class isometry is that
                # isomorphism conjugated by it, read on the reduction's frame.
                reduction = self.isotropic_reduction()
                quotient = reduction.quotient_lattice()
                quotient_labels = tuple(quotient.module_generating_set())
                perpendicular = reduction.orthogonal_complement()
                perpendicular_labels = tuple(perpendicular.module_generating_set())
                ambient_labels = tuple(lattice.module_generating_set())
                if len(perpendicular_labels) != len(ambient_labels):
                    raise ArithmeticError(
                        f"the perpendicular of the zero subobject {self} has "
                        f"{len(perpendicular_labels)} generators and {lattice} has "
                        f"{len(ambient_labels)}: they are the same lattice, so the identification "
                        f"of K_I with {lattice} does not apply"
                    )
                frame = self.quotient_frame_lifts()
                projection = reduction.projection()

                def frame_value(element):
                    coordinates = element.to_vector()
                    total = lattice.zero()
                    for position in quotient_labels:
                        coefficient = int(coordinates(position))
                        if coefficient:
                            total = total + lattice.scalar_multiple(
                                ring(coefficient), frame[position]
                            )
                    return total

                images = {
                    ambient_label: frame_value(
                        quotient_action(
                            projection(perpendicular.module_generator(perpendicular_label))
                        )
                    )
                    for perpendicular_label, ambient_label in zip(
                        perpendicular_labels, ambient_labels, strict=True
                    )
                }
                candidate = lattice.Aut()(images)
                if self._preserves_the_form(candidate) is not True:
                    raise ArithmeticError(
                        f"the lift of {quotient_action} through the identification of K_I with "
                        f"{lattice} at the zero subobject {self} does not preserve the pairing"
                    )
                return candidate
            if self.splitting_complement() is None:
                raise NotImplementedError(
                    f"cannot construct the pointwise lift of {quotient_action} in {lattice}: the "
                    f"lift here is the block diag(1, 1, Q_3), whose mixed entries vanish because "
                    f"the complement of I^perp pairs trivially with K_I = "
                    f"{self.isotropic_reduction().quotient_lattice()}, and {self} has no such "
                    f"complement, so the lift needs mixed block entries that are not solved here. "
                    f"Neither answer is claimed"
                )
            lift = self._pointwise_block_isometry(quotient_action)
            if lift is None:
                raise ArithmeticError(
                    f"the block diag(1, 1, Q_3) of {quotient_action} at {self} does not conjugate "
                    f"back to an automorphism of {lattice} that preserves the form, although "
                    f"{self} splits off with a complement orthogonal to K_I and Q_3 is the frame "
                    f"matrix of an isometry of K_I.  The block equation and this construction "
                    f"disagree"
                )
            if not self._fixes_isotropic_pointwise(lift):
                raise ArithmeticError(
                    f"the lift of {quotient_action} constructed at {self} does not fix I "
                    f"pointwise, although its I-block is the identity"
                )
            return lift

        def _pointwise_block_isometry(self, quotient_action):
            r"""Return the isometry fixing ``I`` pointwise with ``quotient_action`` on \(I^\perp/I\), or ``None``.

            The basis is \((p_a)\) for \(I\), a complement \((u_a)\) of
            \(I^\perp\) and the reduction's frame
            \((\tilde\kappa_b)\) of \(I^\perp/I\).  In it the Gram matrix is
            \(\begin{pmatrix} H & J & 0 \\ J^t & 0 & 0 \\ 0 & 0 & A\end{pmatrix}\)
            with \(J\) and \(A\) non-degenerate, and the isometry extending a
            map of \(I^\perp\) has the block form
            \(\begin{pmatrix} P_1 & P_2 & P_3 \\ 0 & Q_1 & 0 \\ 0 & Q_2 & Q_3\end{pmatrix}\)
            subject to \(J = P_1 J Q_1^t\)
            (Dutour Sikirić--Hulek, *Moduli of polarised Enriques surfaces —
            computational aspects*, J. London Math. Soc. 110 (2024),
            arXiv:2302.01679v2, Theorem 4.9 and its proof, printed pp. 33--34).
            An element fixing \(I\) pointwise has \(Q_1 = 1\), and then
            \(J = P_1 J\) with \(J\) invertible forces \(P_1 = 1\).  The block
            \(\mathrm{diag}(1, 1, Q_3)\) is an isometry exactly when
            \(Q_3 A Q_3^t = A\) and the complement is orthogonal to the frame,
            which is the split hypothesis of :meth:`splitting_complement`; the
            radical entries \(P_2, P_3, Q_2\) are not part of this block and
            are supplied by :meth:`_pointwise_radical_element` when they are
            needed.

            ``None`` is returned when the complement does not exist, when the
            lifted matrix is not integral, or when the candidate fails the
            lattice's own check that it preserves the form.
            """
            complement = self.splitting_complement()
            if complement is None:
                return None
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            isotropic = self.isotropic_basis()
            breadth = len(isotropic)
            quotient_labels = tuple(
                self.isotropic_reduction().quotient_lattice().module_generating_set()
            )
            frame = self.quotient_frame_lifts()
            basis = (
                tuple(isotropic)
                + tuple(complement)
                + tuple(frame[label] for label in quotient_labels)
            )
            change = matrix(SageZZ, [self.coordinates(vector) for vector in basis])
            if abs(int(change.determinant())) != 1:
                raise ArithmeticError(
                    f"the isotropic basis of {self}, the complement of I^perp and the "
                    f"reduction's frame do not form a ZZ-basis of {lattice}: their coordinate "
                    f"matrix has determinant {change.determinant()}"
                )
            size = len(tuple(lattice.module_generating_set()))
            block = matrix(SageZZ, size, size, 0)
            for position in range(2 * breadth):
                block[position, position] = 1
            frame_block = self._frame_matrix(quotient_action)
            for row in range(size - 2 * breadth):
                for column in range(size - 2 * breadth):
                    block[2 * breadth + row, 2 * breadth + column] = frame_block[row, column]
            lifted = change.inverse() * block * change
            if any(entry not in SageZZ for entry in lifted.list()):
                return None
            images = {
                label: lattice.linear_combination(
                    {
                        other: ring(int(lifted[row, column]))
                        for row, other in enumerate(lattice.module_generating_set())
                        if int(lifted[row, column])
                    }
                )
                for column, label in enumerate(lattice.module_generating_set())
            }
            candidate = lattice.Aut()(images)
            return candidate if self._preserves_the_form(candidate) is True else None

        def _plane_coordinates(self, element):
            r"""Return the coordinates of an element of ``I`` on ``plane_basis()``."""
            inclusion = self.inclusion()
            coordinates = inclusion.lift(element).to_vector()
            return tuple(
                int(coordinates(label)) for label in self.module_generating_set()
            )

        def _reduction_values(self, vector):
            r"""Return the values of ``b(vector, -)`` on the generators of ``I``."""
            lattice = self.ambient_lattice()
            embedded = self.embedded_module_generators()
            return tuple(
                int(lattice.b(vector, embedded[label]))
                for label in self.module_generating_set()
            )

        def _dual_values(self, vector):
            r"""Return the values of ``b(-, vector)`` on the generators of the ambient lattice."""
            lattice = self.ambient_lattice()
            return tuple(
                int(lattice.b(generator, vector))
                for generator in lattice.module_generators()
            )


        # -- the parabolic subgroup of a primitive isotropic plane -------------

        def isotropic_basis(self):
            r"""Return the images of this subobject's generating labels, as vectors of the ambient lattice.

            These are the ``iota(e_a)`` that every block construction in this
            class reads as the basis ``(p_a)`` of ``I``, in the order of
            ``module_generating_set()``.  No rank hypothesis is made: the
            parabolic constructions that need a plane say so themselves.
            """
            embedded = self.embedded_module_generators()
            return tuple(embedded[label] for label in self.module_generating_set())

        def plane_basis(self):
            r"""Return the two generators of this subobject, as vectors of the ambient lattice.

            The parabolic construction below is stated for a rank-two totally
            isotropic ``P``: its basis ``(p_1, p_2)`` fixes the coordinates in
            which the action on ``P`` is read.
            """
            if int(self.module_rank()) != 2:
                raise ValueError(
                    f"the parabolic construction here is stated for a primitive isotropic "
                    f"plane, but {self} has rank {int(self.module_rank())}"
                )
            return self.isotropic_basis()

        def coordinates(self, vector):
            r"""Return the coordinates of ``vector`` on the ambient lattice's generating set."""
            lattice = self.ambient_lattice()
            coordinates = vector.to_vector()
            return tuple(
                int(coordinates(label)) for label in lattice.module_generating_set()
            )

        def vector_from_coordinates(self, coordinates):
            r"""Return the ambient-lattice vector with the given coordinates."""
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            ring = lattice.base_ring()
            return lattice.linear_combination(
                {
                    label: ring(int(entry))
                    for label, entry in zip(labels, coordinates, strict=True)
                    if int(entry)
                }
            )

        def gram_matrix(self):
            r"""Return the Gram matrix of the ambient lattice on its generating set."""
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            generators = tuple(lattice.module_generator(label) for label in labels)
            return [
                [int(lattice.b(left, right)) for right in generators]
                for left in generators
            ]

        @cached_method
        def perpendicular_basis(self):
            r"""Return a `ZZ`-basis of \(P^\perp\) as vectors of the ambient lattice.

            ``P`` is this subobject at its own rank: the perpendicular is taken
            of :meth:`isotropic_basis`, so it is the perpendicular of the
            isotropic subobject and not only of an isotropic plane.
            """
            return self.vector_perpendicular_basis(self.isotropic_basis())

        def vector_perpendicular_basis(self, vectors):
            r"""Return a `ZZ`-basis of the perpendicular of a family of ambient vectors."""
            lattice = self.ambient_lattice()
            generators = tuple(
                lattice.module_generator(label)
                for label in lattice.module_generating_set()
            )
            rows = [
                [int(lattice.b(generator, vector)) for generator in generators]
                for vector in vectors
            ]
            basis = _kernel_basis_rows(matrix(SageZZ, rows))
            return tuple(self.vector_from_coordinates(row) for row in basis)

        @cached_method
        def parabolic_transvection_generators(self):
            r"""Return the plane's Eichler transvections: elements of the parabolic at the plane.

            For an isotropic p in the plane and x in p^\perp the Eichler
            transvection

            \[ t(p, x)(y) = y - b(x, y)\, p + b(p, y)\, x - \tfrac12 q(x)\, b(p, y)\, p \]

            (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, equations
            (4)--(5), transcribed in
            :meth:`sage_extensions.categories.lattices.Lattices.ParentMethods.eichler_transvection`,
            after Dawes, section 2 equation (7)) is an integral isometry on an even
            lattice, fixes `p`, and for `x\perp p` it acts on \(P^\perp/P\) as the
            identity: for \(k \in P^\perp\) it sends `k` to
            \(k - b(x,k)p \in k + P\).  It carries the plane onto itself, because
            for \(p' \in P\) it sends `p'` to \(p' + b(p',x)\,p \in P\), so it is an
            element of the parabolic at the plane -- and on the plane it is
            unipotent, fixing `p`.

            That is the whole of what it is: it is in the *unipotent radical* only
            when \(b(p',x) = 0\) for both generators of the plane, so that it fixes
            the plane pointwise.  :meth:`unipotent_radical_generators` returns that
            subfamily and this method returns all of them.  At Sterk's `P_2` of
            \(T_{\mathrm{En}}\) the difference is measured: 21 transvections are
            returned here and 14 of them lie in the radical.

            Eichler's criterion takes exactly this family, one parameter per basis
            vector of \(p^\perp\): Dutour Sikirić--Hulek, arXiv:2302.01679v2,
            subsection "Approximate models and the case of signature \(p,q\geq 2\)"
            (Lemma `sublattice_approx_model`, which cites Eichler's criterion and
            Scattone, Ph.D. thesis, section 3.7, Proposition 3.7.3: generators of
            \(SL_2(ZZ)^2\) together with the transvections \(E_{e_i, v_{i,j}}\)
            over a `ZZ`-basis \((v_{i,j})\) of \(e_i^\perp\)).  On
            \(L = U \oplus U(2) \oplus E_8(-2)\) at \(P_1\) it has 2 x 11 members.
            """
            lattice = self.ambient_lattice()
            assert lattice.is_even() is True, (
                f"the Eichler transvections at {self} need the half-integral "
                f"coefficient q(x)/2 of an even lattice, and {lattice} is odd"
            )
            generators = []
            for isotropic in self.plane_basis():
                seen = set()
                for vector in self.vector_perpendicular_basis((isotropic,)):
                    if vector.is_zero():
                        continue
                    key = self.coordinates(vector)
                    if key in seen:
                        continue
                    seen.add(key)
                    transvection = lattice.eichler_transvection(isotropic, vector)
                    if all(
                        transvection(generator) == generator
                        for generator in lattice.module_generators()
                    ):
                        continue
                    generators.append(transvection)
            return tuple(generators)

        @cached_method
        def unipotent_radical_generators(self):
            r"""Return the plane's Eichler transvections in the unipotent radical, and its block generators.

            The unipotent radical is the common kernel
            \(U_I = \ker(P_I \to \GL(I) \times O(I^\perp/I))\), and an element lies
            in it exactly when it fixes every vector of the plane and carries
            \(I^\perp\) into `I` modulo `I`.  Each element of
            :meth:`parabolic_transvection_generators` is checked against both
            conditions here, and only the ones that pass are returned, so that part
            of the family is a subfamily of the radical and not of the parabolic;
            :meth:`parabolic_transvection_generators` keeps the ones that move the
            plane, which the parabolic needs.  The second part is
            :meth:`unipotent_radical_block_generators`: one element over each vector
            of the parameter lattice :meth:`unipotent_parameter_lattice`, which is
            every parameter of an element of `U_I`, together with a generator of the
            centre `\ker \tau`.

            What is measured at Sterk's `P_2` of \(T_{\mathrm{En}}\): all fourteen
            transvections fix the plane pointwise and act trivially on
            \(I^\perp/I\), so all fourteen lie in \(U_I\) -- but their translations
            span only \(12\) of the \(16\)
            dimensions of \(\operatorname{Hom}(I^\perp/I, I)\)
            (:meth:`unipotent_translation_rank`), so they alone generate a subgroup
            of infinite index.  The block generators are what closes that: their
            translations are a `\ZZ`-basis of `\tau(U_I)` and their centre member
            generates `Z`, so the returned family has index \(1\) in a radical of
            rank \(17 = 16 + 1\) (:meth:`unipotent_radical_index`).  No transvection
            generation statement is used, so Scattone's Proposition 3.7.3 and its
            hypothesis -- two orthogonal hyperbolic planes, which \(T_{\mathrm{En}}\)
            does not have -- are not needed.
            """
            return tuple(
                transvection
                for transvection in self.parabolic_transvection_generators()
                if self._fixes_isotropic_pointwise(transvection)
                and self.acts_trivially_on_isotropic_reduction(transvection)
            ) + tuple(self.unipotent_radical_block_generators())

        def _unipotent_block_basis(self):
            r"""Return `(change, inverse, A_K, Gram)` of :meth:`plane_block_basis`.

            `change` has the block basis vectors as its rows, `A_K = b(K, K)`, and
            `Gram = change \cdot G \cdot change^t` is the Gram matrix of the block
            basis, so `b(x, y) = x^t \mathrm{Gram} y` in block coordinates.
            """
            from sage.rings.rational_field import QQ as SageQQ

            change, inverse, _h, _j, _k, A_K = self.plane_block_gram()
            gram = change * matrix(SageQQ, self.gram_matrix()) * change.transpose()
            return change, inverse, A_K, gram

        def _unipotent_block_matrix(self, c, a, tau):
            r"""Return the block matrix of an element of `U_I` with blocks `(c, a, \tau)`.

            In the basis `(U \mid P \mid K)` of :meth:`plane_block_basis` an element of
            the radical has the shape

            .. math::
                g = \begin{pmatrix} 1 & 0 & 0 \\ a & 1 & \tau \\ c & 0 & 1 \end{pmatrix},

            with `a` the plane vectors' coefficients of the images of the vectors of `U`,
            `\tau` the translations of the basis vectors of `K` into `P`, and `c` the
            coefficients of `U` in the images of the basis vectors of `K`.  That shape is
            what "fixes `I` pointwise and acts trivially on `I^\perp/I`" says in these
            coordinates: the `P`-columns and the `K`-columns are the identity outside the
            `P`-rows, and the `P`-rows of the `K`-columns are the translation.
            """
            change = self.plane_block_gram()[0]
            size = change.nrows()
            two = 2
            block = identity_matrix(SageZZ, size)
            block[two:4, 0:two] = a
            block[two:4, 4:size] = tau
            block[4:size, 0:two] = c
            return block

        def unipotent_block_solution(self, c, skew=None):
            r"""Return `(a, \tau)` for the parameter `c`, or ``None`` when there is no lift.

            Solving `g^t \mathrm{Gram} g = \mathrm{Gram}` for the block matrix

            .. math::
                g = \begin{pmatrix} 1 & 0 & 0 \\ a & 1 & \tau \\ c & 0 & 1 \end{pmatrix}

            in the basis `(U \mid P \mid K)` of :meth:`plane_block_basis`, with
            `\mathrm{Gram} = \begin{pmatrix} H & J & K \\ J^t & 0 & 0 \\ K^t & 0 & A
            \end{pmatrix}` and `H = 0`, gives exactly

            .. math::
                \tau = -J^{-1} c^t A, \qquad J a + a^t J^t = -(Kc + c^t K^t + c^t A c),

            the second equation fixing `a` up to the skew part, which ``skew`` fixes as
            `(a_{12} - a_{21})/2`.  Both were obtained by solving the equations exactly
            over `\QQ` in the twelve block coordinates of `P_2`, and every element this
            module builds is checked against the isometry condition itself -- the
            assertion below.  No lift exists for a `c` whose `\tau` or whose `a` is not
            integral, and `None` is returned for those rather than rounding; the
            parameters that do lift are decided class by class by
            :meth:`unipotent_parameter_lifts` and are the lattice
            :meth:`unipotent_parameter_lattice` returns.
            """
            from sage.rings.rational_field import QQ as SageQQ

            change = self.plane_block_gram()[0]
            _change, _inverse, A_K, gram = self._unipotent_block_basis()
            _h, J, K = self.plane_block_gram()[2:5]
            size = change.nrows()
            rows = A_K.nrows()
            two = 2
            J = matrix(SageQQ, J)
            if int(J.determinant()) == 0:
                raise ValueError(f"the plane's block basis at {self} pairs U with P degenerately")
            tau = -(J.inverse() * (c.transpose() * A_K))
            if any(entry.denominator() != 1 for entry in tau.list()):
                return None
            symmetric = -(K * c + c.transpose() * K.transpose() + c.transpose() * A_K * c)
            # the four equations: the three of J a + a^t J^t = symmetric, and the skew
            system = []
            target = []
            for first in range(two):
                for second in range(first, two):
                    row = []
                    for i in range(two):
                        for j in range(two):
                            unit = matrix(SageZZ, two, two, 0)
                            unit[i, j] = 1
                            value = J * unit + unit.transpose() * J.transpose()
                            row.append(SageQQ(value[first, second]))
                    system.append(row)
                    target.append(SageQQ(symmetric[first, second]))
            # the skew equation, scaled by two so that the system stays integral; it is
            # imposed only when asked for, because the skew part of a is half-integral for
            # a parameter whose translation pairs oddly with K, and integral only on the
            # centre
            if skew is not None:
                system.append([SageQQ(0), SageQQ(1), SageQQ(-1), SageQQ(0)])
                target.append(SageQQ(2 * skew))
            if any(SageQQ(entry).denominator() != 1 for row in system for entry in row) or any(
                SageQQ(entry).denominator() != 1 for entry in target
            ):
                return None
            integer_system = matrix(SageZZ, [[SageZZ(int(entry)) for entry in row] for row in system])
            integer_target = matrix(SageZZ, len(target), 1, [SageZZ(int(entry)) for entry in target])
            solution = _integral_solution(integer_system, integer_target)
            if solution is None:
                return None
            a = matrix(SageZZ, [[SageZZ(int(solution[two * i + j])) for j in range(two)] for i in range(two)])
            tau = matrix(SageZZ, [[SageZZ(int(tau[i, k])) for k in range(rows)] for i in range(two)])
            block = self._unipotent_block_matrix(c, a, tau)
            assert block.transpose() * gram * block == gram, (
                f"the block parameters c = {c}, skew = {skew} at {self} do not give an "
                f"isometry; the solved block equations are wrong"
            )
            return a, tau

        def unipotent_block_element(self, c, skew=None):
            r"""Return the element of `U_I` with parameter `c`, or ``None``.

            This is :meth:`unipotent_block_solution` transported to the ambient lattice:
            the block matrix is conjugated back by the block basis and the resulting
            integer matrix is the automorphism.
            """
            from sage.rings.rational_field import QQ as SageQQ

            solution = self.unipotent_block_solution(c, skew)
            if solution is None:
                return None
            a, tau = solution
            return self._unipotent_block_automorphism(c, a, tau)

        def _unipotent_block_automorphism(self, c, a, tau):
            r"""Return the ambient automorphism of the block matrix with blocks `(c, a, \tau)`, or ``None``.

            The block matrix of :meth:`_unipotent_block_matrix` is conjugated back by the
            block basis, and the result is kept only when it is integral: an element of
            `U_I` is an automorphism of the ambient lattice, so a block matrix whose
            conjugate has denominators is not one, and ``None`` says so instead of
            rounding.  The block equations are *not* rechecked here; the caller has
            solved them, and :meth:`unipotent_block_solution` asserts the isometry
            condition for the elements it builds.
            """
            from sage.rings.rational_field import QQ as SageQQ

            change, inverse, _A_K, _gram = self._unipotent_block_basis()
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            block = self._unipotent_block_matrix(c, a, tau)
            lifted = change.transpose() * block * inverse.transpose()
            if any(entry.denominator() != 1 for entry in matrix(SageQQ, lifted).list()):
                return None
            ring = lattice.base_ring()
            images = {}
            for column, label in enumerate(labels):
                images[label] = lattice.linear_combination(
                    {
                        other: ring(int(lifted[row, column]))
                        for row, other in enumerate(labels)
                        if lifted[row, column]
                    }
                )
            return lattice.Aut()(images)

        @cached_method
        def _unipotent_symmetric_lattice(self):
            r"""Return `(adjugate, determinant)` deciding membership in `\Lambda_J`.

            The second block equation of :meth:`unipotent_block_solution` is
            `J a + a^t J^t = S(c)`, so it has an integral solution `a` exactly when
            `S(c)` lies in the image of

            .. math::
                \phi: \operatorname{Mat}_2(\ZZ) \to \operatorname{Sym}_2(\ZZ),
                \qquad a \mapsto J a + a^t J^t ,

            and that image is the lattice `\Lambda_J` computed here: the Hermite
            normal form of the four images `\phi(E_{ij})` in the three coordinates
            `(s_{11}, s_{12}, s_{22})` of a symmetric matrix.  `J` is invertible in
            the block form of Dutour Sikirić--Hulek, Theorem 4.9
            (`theorem_isotropic_k_planes`), arXiv:2302.01679v2, printed pp. 33--34, so
            the image has rank three and that normal form is a `3 \times 3` basis
            `H`: then `s \in \Lambda_J` exactly when `\operatorname{adj}(H) s` is
            divisible by `\det H` entrywise, which is what the returned pair decides.
            At Sterk's `P_2` of \(T_{\mathrm{En}}\) the basis is
            `\operatorname{diag}(4, 2, 4)`, so `\Lambda_J` has index `32` in
            `\operatorname{Sym}_2(\ZZ)`.
            """
            J = matrix(SageZZ, self.plane_block_gram()[3])
            images = []
            for first in range(2):
                for second in range(2):
                    unit = matrix(SageZZ, 2, 2, 0)
                    unit[first, second] = 1
                    value = J * unit + unit.transpose() * J.transpose()
                    images.append((int(value[0, 0]), int(value[0, 1]), int(value[1, 1])))
            reduced = matrix(SageZZ, images).hermite_form()
            kept = [
                tuple(int(entry) for entry in row) for row in reduced.rows() if any(row)
            ]
            if len(kept) != 3:
                raise ArithmeticError(
                    f"the image of a -> J a + a^t J^t at {self} has rank {len(kept)}, "
                    f"not 3, so the second block equation is not the membership test "
                    f"this method returns the data for"
                )
            basis = matrix(SageZZ, 3, 3, [entry for row in kept for entry in row]).transpose()
            determinant = abs(int(basis.determinant()))
            assert determinant and basis * basis.adjugate() == determinant * identity_matrix(
                SageZZ, 3
            ), f"the basis {basis} of the lattice of the second block equation at {self} is not invertible"
            adjugate = basis.adjugate()
            return (
                tuple(
                    tuple(int(adjugate[first, second]) for second in range(3))
                    for first in range(3)
                ),
                determinant,
            )

        def _unipotent_symmetric_defect(self, parameter):
            r"""Return `S(c) = -(Kc + c^t K^t + c^t A_K c)` as the triple `(s_{11}, s_{12}, s_{22})`.

            This is the right side of the second block equation of
            :meth:`unipotent_block_solution`, in the three coordinates of a symmetric
            matrix that :meth:`_unipotent_symmetric_lattice` decides membership in.
            """
            _change, _inverse, _h, _J, K, A = self.plane_block_gram()
            product = K * parameter
            defect = -(
                product
                + parameter.transpose() * K.transpose()
                + parameter.transpose() * A * parameter
            )
            return (int(defect[0, 0]), int(defect[0, 1]), int(defect[1, 1]))

        def unipotent_parameter_lifts(self, parameter) -> bool:
            r"""Return whether `c` is the parameter of an element of `U_I`.

            `c` is the `(K, U)` block of the block matrix of
            :meth:`_unipotent_block_matrix`, an `\operatorname{rank}(K) \times 2`
            integer matrix.  By :meth:`unipotent_block_solution` an element of `U_I`
            over `c` exists exactly when

            .. math::
                \tau = -J^{-1} c^t A_K, \qquad
                J a + a^t J^t = -(Kc + c^t K^t + c^t A_K c)

            have an integral solution `(a, \tau)`, and both are decided here rather
            than searched for:

            * `\tau` is determined by `c`, and it is integral exactly when
              `\operatorname{adj}(J) c^t A_K` is divisible by `\det J` entrywise;
            * `a` exists exactly when the right side lies in the lattice
              `\Lambda_J = \{J a + a^t J^t : a \in \operatorname{Mat}_2(\ZZ)\}` of
              :meth:`_unipotent_symmetric_lattice`, since that map is onto the
              symmetric matrices over `\QQ` and its kernel -- the skew part of `a`
              -- is free.

            Both are integral membership tests, so `False` here means that no element
            of `U_I` has this parameter, not that none was found.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            if parameter.nrows() != rows or parameter.ncols() != 2:
                raise ValueError(
                    f"a parameter of the radical at {self} is a {rows} x 2 matrix, and "
                    f"{parameter} is {parameter.nrows()} x {parameter.ncols()}"
                )
            _change, _inverse, _h, J, _K, A = self.plane_block_gram()
            scalar = abs(int(J.determinant()))
            if scalar == 0:
                raise ValueError(
                    f"the block basis at {self} pairs U with P degenerately, so the "
                    f"translation is not determined by the parameter"
                )
            translation = J.adjugate() * (parameter.transpose() * A)
            if any(int(entry) % scalar for entry in translation.list()):
                return False
            return self._unipotent_symmetric_lifts(
                self._unipotent_symmetric_defect(parameter)
            )

        def _unipotent_symmetric_lifts(self, defect) -> bool:
            r"""Return whether the symmetric triple lies in `\Lambda_J`."""
            adjugate, determinant = self._unipotent_symmetric_lattice()
            image = matrix(SageZZ, 3, 3, [entry for row in adjugate for entry in row]) * matrix(
                SageZZ, 3, 1, [SageZZ(entry) for entry in defect]
            )
            return all(int(entry) % determinant == 0 for entry in image.list())

        def _unipotent_parameter_units(self):
            r"""Return the unit parameters of the radical, in the order of :meth:`unipotent_parameter_vector`.

            One `\operatorname{rank}(K) \times 2` matrix per coordinate: the `(2 i + j)`-th
            has a single `1` in row `i`, column `j`.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            units = []
            for position in range(rows):
                for column in range(2):
                    unit = matrix(SageZZ, rows, 2, 0)
                    unit[position, column] = 1
                    units.append(unit)
            return tuple(units)

        def _unipotent_symmetric_uniform(self, modulus) -> bool:
            r"""Return whether `S(c + m d) - S(c) \in \Lambda_J` for every integral `c, d`.

            Expanding the second block equation along a step `d` of length `m`,

            .. math::
                S(c + m d) - S(c) = -m(Kd + d^t K^t) - m^2 d^t A_K d
                    - m(c^t A_K d + d^t A_K c),

            the first two terms are a quadratic function of `d` and the third is
            bilinear in `(c, d)`.  A quadratic function is determined by its values on
            the coordinate vectors and on the pairwise sums -- the cross terms -- and a
            bilinear one by its values on pairs of coordinate vectors, so the three
            finite families of checks below decide this for all integral `c` and `d`;
            no range is searched.
            """
            _change, _inverse, _h, _J, _K, A = self.plane_block_gram()
            units = self._unipotent_parameter_units()
            order = len(units)
            for unit in units:
                if not self._unipotent_symmetric_lifts(
                    self._unipotent_symmetric_defect(modulus * unit)
                ):
                    return False
            for first in range(order):
                for second in range(first + 1, order):
                    if not self._unipotent_symmetric_lifts(
                        self._unipotent_symmetric_defect(modulus * (units[first] + units[second]))
                    ):
                        return False
            for first in range(order):
                for second in range(order):
                    step = modulus * units[second]
                    crossed = -(
                        units[first].transpose() * A * step
                        + step.transpose() * A * units[first]
                    )
                    if not self._unipotent_symmetric_lifts(
                        (int(crossed[0, 0]), int(crossed[0, 1]), int(crossed[1, 1]))
                    ):
                        return False
            return True

        @cached_method
        def unipotent_parameter_modulus(self) -> int:
            r"""Return the modulus at which the lift condition depends only on the class of `c`.

            Both block equations of :meth:`unipotent_block_solution` are conditions on
            the parameter `c` alone, and each is a condition on the class of `c` at its
            own modulus:

            * the translation `\tau = -J^{-1} c^t A_K` is **linear** in `c`, so its
              integrality depends on `c` modulo the least `m` with
              `m \operatorname{adj}(J) c^t A_K \equiv 0 \pmod{\det J}` for every `c`,
              which is `\operatorname{lcm}` over the sixteen coordinates of the
              quotients `\det J / \gcd(\det J, \text{entry})` -- computed, not assumed;
            * the second equation's right side is **quadratic** in `c`, so its
              membership in `\Lambda_J` is decided by
              :meth:`_unipotent_symmetric_uniform`: `m` such that the difference
              `S(c + m d) - S(c)` lies in `\Lambda_J` for every integral `c` and `d`,
              which makes membership depend on `c` modulo `m` and on nothing else.  The
              differences are quadratic in the step, so finitely many of them decide
              the whole family.

            The modulus returned is the `\operatorname{lcm}` of the two, and both
            conditions are recomputed on it before it is returned, so it is verified
            and not only derived.  At Sterk's `P_2` of \(T_{\mathrm{En}}\) both are `2`
            -- `\det J = 4` and `A_K` has an odd entry, so the translation needs the
            class modulo two, and `J = 2 \cdot 1_2` makes the second equation's
            integrality a parity condition -- and the radical's parameters are then
            decided on `2^{16} = 65536` classes, of which `4096` lift, an index of `16`.
            """
            _change, _inverse, _h, J, _K, A = self.plane_block_gram()
            scalar = abs(int(J.determinant()))
            if scalar == 0:
                raise ValueError(
                    f"the block basis at {self} pairs U with P degenerately, so the "
                    f"translation is not determined by the parameter"
                )
            adjugate = J.adjugate()
            translation_modulus = SageZZ.one()
            for unit in self._unipotent_parameter_units():
                for entry in (adjugate * (unit.transpose() * A)).list():
                    translation_modulus = translation_modulus.lcm(
                        SageZZ(scalar) // SageZZ(scalar).gcd(SageZZ(abs(int(entry))))
                    )
            adjugate, determinant = self._unipotent_symmetric_lattice()
            bound = 2 * int(translation_modulus) * determinant * scalar
            symmetric_modulus = None
            for candidate in range(1, bound + 1):
                if self._unipotent_symmetric_uniform(candidate):
                    symmetric_modulus = candidate
                    break
            if symmetric_modulus is None:
                raise ArithmeticError(
                    f"no modulus below {bound} makes the second block equation at {self} "
                    f"constant on the classes of the parameter, although the difference "
                    f"of its right side along a step of that length is decided by finitely "
                    f"many checks; the derivation of the modulus does not hold here"
                )
            modulus = int(SageZZ(symmetric_modulus).lcm(translation_modulus))
            if not self._unipotent_symmetric_uniform(modulus):
                raise ArithmeticError(
                    f"the modulus {modulus} of the radical's parameters at {self} was "
                    f"derived from the two block equations, and the second of them is not "
                    f"constant on its classes"
                )
            return modulus

        @cached_method
        def _unipotent_parameter_decision(self):
            r"""Return the exact parameter lattice and its finite class counts.

            First take the kernel of the linear translation congruence
            adj(J) c^t A = 0 modulo |det J|. On this lattice the symmetric
            defect S(c) is additive modulo Lambda_J: for two parameters
            c,d the cross term c^t A d + d^t A c is J a + a^t J^t with
            a = J^(-1)c^t A d integral by the translation congruence.
            Thus the second condition is another linear congruence in
            a basis of the first kernel. Compute both kernels over ZZ
            by adjoining modulus times the identity to the coefficient
            matrix and projecting its saturated integer kernel. The
            auxiliary variables are uniquely determined by each parameter,
            so projection is an isomorphism onto the congruence kernel.
            This gives the complete lattice without enumerating classes.
            """
            _change, _inverse, _h, J, _K, A = self.plane_block_gram()
            order = 2 * A.nrows()
            modulus = self.unipotent_parameter_modulus()
            classes = modulus**order
            if not order:
                return modulus, classes, 1, ()

            def congruence_kernel(coefficient, level):
                height, width = coefficient.nrows(), coefficient.ncols()
                system = coefficient.augment(-level * identity_matrix(SageZZ, height))
                return matrix(SageZZ, [list(v[:width]) for v in system.right_kernel().basis()])

            adjugate = J.adjugate()
            determinant = abs(int(J.determinant()))
            translation = matrix(SageZZ, [
                (adjugate * unit.transpose() * A).list()
                for unit in self._unipotent_parameter_units()
            ]).transpose()
            first = congruence_kernel(translation, determinant)
            symmetric_adjugate, symmetric_determinant = self._unipotent_symmetric_lattice()
            symmetric_adjugate = matrix(SageZZ, symmetric_adjugate)
            obstruction = matrix(SageZZ, [
                list(symmetric_adjugate * vector(SageZZ, self._unipotent_symmetric_defect(
                    self.unipotent_parameter_matrix(tuple(row))
                )))
                for row in first.rows()
            ]).transpose()
            second = congruence_kernel(obstruction, symmetric_determinant)
            basis = (second * first).hermite_form()
            index = abs(int(basis.determinant()))
            assert index and classes % index == 0
            assert all(
                self.unipotent_parameter_lifts(self.unipotent_parameter_matrix(tuple(row)))
                for row in basis.rows()
            )
            assert all(entry in SageZZ for entry in (modulus * basis.inverse()).list())
            return modulus, classes, classes // index, tuple(tuple(int(x) for x in row) for row in basis.rows())

        def unipotent_parameter_lattice(self):
            r"""Return a `ZZ`-basis of the parameters `c` of `U_I`, as sixteen-tuples.

            `c` is the `(K, U)` block of an element of the radical, an
            `\operatorname{rank}(K) \times 2` integer matrix, listed row by row by
            :meth:`unipotent_parameter_vector`.  The block equations of
            :meth:`unipotent_block_solution` -- derived from the block form of Dutour
            Sikirić--Hulek, Theorem 4.9 (`theorem_isotropic_k_planes`),
            arXiv:2302.01679v2, printed pp. 33--34 -- determine the rest of the element
            from `c`:

            .. math::
                \tau = -J^{-1} c^t A_K, \qquad
                J a + a^t J^t = -(Kc + c^t K^t + c^t A_K c),

            The translation congruence is linear, and on its kernel the
            symmetric obstruction is additive modulo the symmetric image
            lattice. The two exact integer congruence kernels of
            :meth:`_unipotent_parameter_decision` therefore construct all
            parameters. The class counts follow from the index of their
            lattice and the uniform modulus, not a sample of parameters.

            At Sterk's `P_2` of \(T_{\mathrm{En}}\): modulus `2`, `4096` of
            `65536` classes admissible, rank `16`, index `16` in `\ZZ^{16}`; the
            parameters of the plane's Eichler transvections that lie in the radical and
            of the elements over the parameters supported on the third and fourth
            basis vectors of `K` all lie in it.
            """
            return self._unipotent_parameter_decision()[3]

        @cached_method
        def unipotent_parameter_class_counts(self):
            r"""Return how many classes of the parameter are decided, and how many of them lift.

            `(modulus, classes, admissible)`, the numbers behind
            :meth:`unipotent_parameter_lattice`; they are what makes the returned
            lattice exact rather than a sample.  At Sterk's `P_2` of
            \(T_{\mathrm{En}}\): `(2, 65536, 4096)`.
            """
            decision = self._unipotent_parameter_decision()
            return decision[0], decision[1], decision[2]

        def unipotent_parameter_matrix(self, parameters):
            r"""Return the `\operatorname{rank}(K) \times 2` parameter matrix of a parameter tuple.

            The inverse of :meth:`unipotent_parameter_vector`: entry `(i, j)` of the
            result is coordinate `2 i + j` of ``parameters``, the coefficient of the
            `i`-th basis vector of `K = I^\perp/I` in the image of the `j`-th basis
            vector of the plane.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            if len(tuple(parameters)) != 2 * rows:
                raise ValueError(
                    f"a parameter of the radical at {self} has {2 * rows} coordinates, "
                    f"and {parameters} has {len(tuple(parameters))}"
                )
            c = matrix(SageZZ, rows, 2, 0)
            for column in range(2):
                for position in range(rows):
                    c[position, column] = SageZZ(int(parameters[2 * position + column]))
            return c

        def unipotent_parameter_vector(self, parameter):
            r"""Return the coordinates of a parameter matrix, as :meth:`unipotent_parameter_lattice` lists them.

            The entry at position `2 i + j` is the coefficient of the `i`-th basis
            vector of `K = I^\perp/I` in the image of the `j`-th basis vector of the
            plane: the `(K, U)` block of :meth:`_unipotent_block_matrix`, read row by
            row.  This is the one flattening the parameter lattice, its coordinates and
            the radical's block generators are all expressed in.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            if parameter.nrows() != rows or parameter.ncols() != 2:
                raise ValueError(
                    f"a parameter of the radical at {self} is a {rows} x 2 matrix, and "
                    f"{parameter} is {parameter.nrows()} x {parameter.ncols()}"
                )
            return tuple(
                int(parameter[position, column])
                for position in range(rows)
                for column in range(2)
            )

        def unipotent_parameter_coordinates(self, parameters):
            r"""Return the coordinates of a parameter on :meth:`unipotent_parameter_lattice`.

            Raises ``ValueError`` naming the parameter when it is not in the lattice,
            which by :meth:`unipotent_parameter_lattice` is the statement that no
            element of `U_I` has it.  The coordinates are integers exactly then: the
            lattice is returned as a basis of its own span, so it is saturated in
            `\ZZ^{\text{order}}` and a parameter in it is an integral combination of the
            basis.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            order = 2 * rows
            if len(tuple(parameters)) != order:
                raise ValueError(
                    f"a parameter of the radical at {self} has {order} coordinates, and "
                    f"{parameters} has {len(tuple(parameters))}"
                )
            basis = matrix(SageZZ, [list(row) for row in self.unipotent_parameter_lattice()])
            if int(basis.rank()) != order:
                raise ArithmeticError(
                    f"the parameter lattice of the radical at {self} has rank "
                    f"{int(basis.rank())}, not {order}"
                )
            expressed = matrix(
                SageZZ, 1, order, [int(entry) for entry in parameters]
            ) * basis.inverse()
            if any(entry.denominator() != 1 for entry in expressed.list()):
                raise ValueError(
                    f"{parameters} is not a parameter of the radical at {self}: it is not "
                    f"in the lattice unipotent_parameter_lattice() returns, so no element "
                    f"of the radical has it"
                )
            return tuple(int(entry) for entry in expressed.list())

        def unipotent_parameter_from_coordinates(self, coordinates):
            r"""Return the parameter that a coordinate vector names on :meth:`unipotent_parameter_lattice`.

            The inverse of :meth:`unipotent_parameter_coordinates`: the `\ZZ`-linear
            combination of the lattice's basis with these coefficients, in the listing
            order of :meth:`unipotent_parameter_vector`.
            """
            basis = self.unipotent_parameter_lattice()
            rows = int(self.plane_block_gram()[5].nrows())
            order = 2 * rows
            if len(tuple(coordinates)) != order:
                raise ValueError(
                    f"the parameter lattice of the radical at {self} has {order} basis "
                    f"vectors, and {len(tuple(coordinates))} coordinates are given"
                )
            total = [0] * order
            for coefficient, row in zip(coordinates, basis, strict=True):
                for position in range(order):
                    total[position] += int(coefficient) * row[position]
            return tuple(total)

        def unipotent_central_coordinate(self, automorphism):
            r"""Return the power `k` with `g = z^k` for a central element of the radical, or refuse.

            The centre `Z = \ker \tau` of `U_I` is infinite cyclic, generated by
            :meth:`unipotent_central_generator`, so an element of `Z` is a power of that
            generator and this returns its integer power: `|k| = 1` says the element is a
            generator of `Z` as well.  An element of the radical outside `Z` -- one with
            `c \neq 0` or with a nonzero translation `\tau` -- and an element outside the
            radical are both named in the error, and so is an element of `Z` whose matrix
            `a` is not a multiple of the generator's
            (:meth:`_unipotent_central_coordinate`).

            This is what makes "the returned family meets the centre in a generator" a
            computation on the family's members rather than a search for one of them.
            """
            parameter, translation, matrix_a = self.unipotent_block_coordinates(automorphism)
            if any(int(entry) for entry in parameter.list()):
                raise ValueError(
                    f"{automorphism} is not central in the radical at {self}: its parameter "
                    f"is {[int(entry) for entry in parameter.list()]} and not zero"
                )
            if any(int(entry) for entry in translation.list()):
                raise ValueError(
                    f"{automorphism} is not central in the radical at {self}: it translates "
                    f"by {[int(entry) for entry in translation.list()]} and not by zero"
                )
            return self._unipotent_central_coordinate(matrix_a)

        def unipotent_radical_element(self, parameters):
            r"""Return the element of `U_I` over a parameter, or refuse when there is none.

            ``parameters`` is a coordinate tuple of :meth:`unipotent_parameter_lattice`'s
            listing (:meth:`unipotent_parameter_vector`).  The element is
            :meth:`unipotent_block_element` of that parameter's matrix: its block matrix
            satisfies the two block equations by construction, and every element this
            builds is checked against `g^t \mathrm{Gram} g = \mathrm{Gram}` there before
            it is carried back to the ambient lattice.  A parameter outside the lattice
            names no element of `U_I` -- :meth:`unipotent_parameter_lattice` is every
            parameter that lifts -- so it is refused here, with that reason, rather than
            answered with ``None``.
            """
            self.unipotent_parameter_coordinates(parameters)
            element = self.unipotent_block_element(self.unipotent_parameter_matrix(parameters))
            if element is None:
                raise ArithmeticError(
                    f"the parameter {parameters} is in the parameter lattice of the radical "
                    f"at {self} and has no integral element over it, so the lattice is not "
                    f"the set of parameters that lift"
                )
            return element

        @cached_method
        def _unipotent_central_matrix(self):
            r"""Return the least positive generator of the lattice of integral `a` with `J a` skew.

            The centre `Z = \ker \tau` consists of the elements of `U_I` with `c = 0` and
            `\tau = 0`, whose second block equation of :meth:`unipotent_block_solution` is
            `Ja + a^t J^t = 0`, i.e. `Ja` skew.  Those `a` form the one-dimensional
            lattice `J^{-1}\operatorname{so}_2(\ZZ) \cap \operatorname{Mat}_2(\ZZ)`:
            with `a = s J^{-1} K` for the rotation `K = ((0,-1),(1,0))` and
            `J^{-1} = \operatorname{adj}(J)/\det J`, `a` is integral exactly when
            `s \operatorname{adj}(J) K` is divisible by `\det J` entrywise, so the least
            such `s` is the lcm of `\det J / \gcd(\det J, \text{entry})` over the four
            entries.  That is `2` at Sterk's `P_2` of \(T_{\mathrm{En}}\), where the
            generator is `((0,-1),(1,0))`.

            The generator need not be a skew matrix: at a plane with
            `J = \operatorname{diag}(1,2)` it is `((0,-2),(1,0))`, whose
            `(a_{12} - a_{21})/2` is not an integer.  That is why the centre's element is
            built from this matrix and not from the scalar `skew` parameter of
            :meth:`unipotent_block_solution`, which only reaches the skew matrices.
            """
            J = matrix(SageZZ, self.plane_block_gram()[3])
            scalar = abs(int(J.determinant()))
            if scalar == 0:
                raise ValueError(
                    f"the block basis at {self} pairs U with P degenerately, so the "
                    f"centre of the radical is not read off the plane block"
                )
            rotation = matrix(SageZZ, 2, 2, [0, -1, 1, 0])
            defect = J.adjugate() * rotation
            scale = SageZZ.one()
            for entry in defect.list():
                scale = scale.lcm(
                    SageZZ(scalar) // SageZZ(scalar).gcd(SageZZ(abs(int(entry))))
                )
            generator = matrix(
                SageZZ,
                2,
                2,
                [
                    int(SageZZ(scale) * SageZZ(int(defect[first, second])) // SageZZ(scalar))
                    for first in range(2)
                    for second in range(2)
                ],
            )
            assert matrix(SageZZ, J * generator + generator.transpose() * J.transpose()).is_zero(), (
                f"the lattice generator {generator} of the centre at {self} does not make J a skew"
            )
            return generator

        def _unipotent_central_coordinate(self, a):
            r"""Return `|k|` for `a = k a_0`, with `a_0` the generator of :meth:`_unipotent_central_matrix`.

            An element of the radical with `c = 0` is central exactly when its matrix `a`
            lies in the lattice that generator spans, because `Z` is that lattice in the
            block coordinates.  An `a` outside it is named in the error: the index
            argument of :meth:`unipotent_radical_index` divides by the lattice of the
            family's central members, and an element counted as central while it is not
            would make that index wrong.
            """
            generator = self._unipotent_central_matrix()
            pivot = None
            for first in range(2):
                for second in range(2):
                    if pivot is None and int(generator[first, second]):
                        pivot = (first, second)
            if pivot is None:
                raise ArithmeticError(
                    f"the lattice of the centre at {self} is trivial, so a central element "
                    f"has no coordinate on it"
                )
            first, second = pivot
            step = SageZZ(int(generator[first, second]))
            value = SageZZ(int(a[first, second]))
            if value % step:
                raise ValueError(
                    f"the matrix {a} is not in the lattice of the centre at {self}, so the "
                    f"element over it is not central"
                )
            coordinate = value // step
            if coordinate * generator != a:
                raise ValueError(
                    f"the matrix {a} is not a multiple of the centre's generator at {self}"
                )
            return int(abs(coordinate))

        def unipotent_central_generator(self):
            r"""Return a generator of the centre `Z = \ker \tau` of `U_I`.

            `Z` is the part of `U_I` with `c = 0` and `\tau = 0`, whose second block
            equation is `Ja + a^t J^t = 0`, i.e. `Ja` skew: the one-dimensional lattice
            of :meth:`_unipotent_central_matrix`, so `Z \cong \ZZ`.  It is the dimension
            of `U_I` that the translation map fixes
            (:meth:`unipotent_translation_kernel_rank`), the rest of the radical being
            `\tau(U_I)` (:meth:`unipotent_translation_basis`).

            The element over that generator is returned after three checks -- it is an
            integral automorphism of the ambient lattice, it fixes the plane pointwise
            and acts trivially on `I^\perp/I` so it lies in the radical, and it is not
            the identity -- so the generator is measured and not assumed.

            Measured at Sterk's `P_2` of \(T_{\mathrm{En}}\): one generator, its parameter
            `c = 0`, its translations zero, all three checks true.
            """
            rows = int(self.plane_block_gram()[5].nrows())
            zero = matrix(SageZZ, rows, 2, 0)
            matrix_a = self._unipotent_central_matrix()
            element = self._unipotent_block_automorphism(
                zero, matrix_a, matrix(SageZZ, 2, rows, 0)
            )
            if element is None:
                raise ArithmeticError(
                    f"the generator {matrix_a} of the lattice of the centre at {self} does "
                    f"not give an integral automorphism of the ambient lattice"
                )
            if not self._fixes_isotropic_pointwise(
                element
            ) or not self.acts_trivially_on_isotropic_reduction(element):
                raise ArithmeticError(
                    f"the element over the generator {matrix_a} at {self} does not fix the "
                    f"plane pointwise and act trivially on I^perp/I, so it is not the centre's "
                    f"generator"
                )
            if element == self.ambient_lattice().Aut().one():
                raise ArithmeticError(
                    f"the generator {matrix_a} of the lattice of the centre at {self} gives "
                    f"the identity, so the centre's generator was not found"
                )
            return element

        def unipotent_block_coordinates(self, automorphism):
            r"""Return `(c, \tau, a)` of an element of `U_I`, and refuse anything else.

            The block matrix of ``automorphism`` in the basis of
            :meth:`plane_block_basis` must have the shape of
            :meth:`_unipotent_block_matrix` and satisfy the isometry condition there; an
            element that does not fix `I` pointwise, does not act trivially on
            `I^\perp/I`, or is not an isometry of that shape is named in the error rather
            than silently given coordinates.
            """
            change, inverse, A_K, gram = self._unipotent_block_basis()
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            size = change.nrows()
            columns = [self.coordinates(automorphism(lattice.module_generator(label))) for label in labels]
            standard = matrix(SageZZ, size, size, 0)
            for index in range(size):
                for column in range(size):
                    standard[index, column] = SageZZ(int(columns[column][index]))
            block = inverse.transpose() * standard * change.transpose()
            if any(entry.denominator() != 1 for entry in block.list()):
                raise ValueError(f"{automorphism} does not preserve the block basis of {self} integrally")
            block = matrix(SageZZ, [[SageZZ(int(block[i, j])) for j in range(size)] for i in range(size)])
            c = block[4:size, 0:2]
            a = block[2:4, 0:2]
            tau = block[2:4, 4:size]
            if block != self._unipotent_block_matrix(c, a, tau):
                raise ValueError(
                    f"{automorphism} is not in the radical of {self}: its block matrix has "
                    f"entries outside the blocks a, tau and c of an element fixing I "
                    f"pointwise and acting trivially on I^perp/I"
                )
            if block.transpose() * gram * block != gram:
                raise ValueError(f"{automorphism} is not an isometry of the block form of {self}")
            return c, tau, a

        @cached_method
        def unipotent_translation_basis(self):
            r"""Return the translations of the elements over :meth:`unipotent_parameter_lattice`.

            Each entry is the `2 \times \operatorname{rank}(K)` matrix of the images of
            the basis vectors of `K` in the plane's basis: the translation `\tau(g)` of
            :meth:`unipotent_translation_rank`, read off the element's block matrix
            rather than assumed from a formula.

            At Sterk's `P_2` of \(T_{\mathrm{En}}\): sixteen translations whose
            span has rank sixteen and covolume `1` in the coordinate lattice of
            `\operatorname{Hom}(K, I)` -- they are a `\ZZ`-basis of the whole of it, as
            `\tau(U_I)` is of rank `2 \operatorname{rank}(K) = 16` there.
            """
            translations = []
            for parameters in self.unipotent_parameter_lattice():
                element = self.unipotent_block_element(self.unipotent_parameter_matrix(parameters))
                if element is None:
                    raise ArithmeticError(
                        f"the parameter {parameters} of the radical at {self} has no integral "
                        f"lift, although the parameter lattice was computed from it"
                    )
                translations.append(self.unipotent_block_coordinates(element)[1])
            return tuple(translations)

        @cached_method
        def unipotent_radical_block_generators(self):
            r"""Return a generating family of `U_I` read off the plane's block equations.

            One element over each vector of :meth:`unipotent_parameter_lattice` -- their
            translations form a `ZZ`-basis of `\tau(U_I)` by
            :meth:`unipotent_translation_basis` -- together with a generator of the
            centre (:meth:`unipotent_central_generator`).  The family generates `U_I`,
            which is a central extension

            .. math:: 1 \to Z \to U_I \to \tau(U_I) \to 1,

            of the lattice `\tau(U_I)` by `Z`.  `Z` is central, hence normal, and
            `\tau` induces `U_I/Z \cong \tau(U_I)`, so the generated subgroup is
            identified by the correspondence between subgroups of a group containing a
            normal subgroup and subgroups of the quotient: J. S. Milne, *Group Theory*,
            version 4.01 of 6 November 2025, **Theorem 1.47 (Correspondence Theorem)**,
            printed **p. 22** -- "there is a one-to-one correspondence {subgroups of `G`
            containing `N`} `\leftrightarrow` {subgroups of `\bar G`}" under
            `H \mapsto \alpha(H)` and `\bar H \mapsto \alpha^{-1}(\bar H)` -- with
            **Corollary 1.48**, printed **p. 23**, for the quotient map `g \mapsto gN`.
            The step used is the one the proof of 1.47 carries on p. 23,
            `\alpha^{-1}\alpha(H) = HN`, "which equals `H` if and only if `H \supset N`":
            the subgroup generated by the returned family contains `Z` -- all of it, by
            :meth:`unipotent_central_generator` -- and its image is all of
            `\tau(U_I)` -- a `\ZZ`-basis of it, by :meth:`unipotent_translation_basis`
            -- so `HN = H` and its preimage is itself, which is the whole of `U_I`.

            Nothing here uses a transvection generation statement, so Scattone's
            Proposition 3.7.3 and its hypothesis of two orthogonal hyperbolic planes are
            not needed: at a plane that does not split they do not apply, and the block
            equations do.
            """
            generators = []
            for parameters in self.unipotent_parameter_lattice():
                element = self.unipotent_block_element(self.unipotent_parameter_matrix(parameters))
                if element is None:
                    raise ArithmeticError(
                        f"the parameter {parameters} of the radical at {self} has no integral "
                        f"lift, although the translation lattice was computed from it"
                    )
                generators.append(element)
            generators.append(self.unipotent_central_generator())
            return tuple(generators)

        @cached_method
        def unipotent_radical_rank(self) -> int:
            r"""Return the rank of `U_I` as a free abelian group, from the plane's block form.

            `U_I` is unipotent, so it is a free abelian group whose rank is its
            dimension, and the dimension is read off the block form.  In the basis
            `(U \mid P \mid K)` of :meth:`plane_block_basis`, with `K = P^\perp/P`
            and the Gram matrix `B` of :meth:`plane_block_gram`, an element of the
            radical acts as

            .. math::
                g = \begin{pmatrix} 1 & a & \tau \\ 0 & A & 0 \\ 0 & c & 1
                \end{pmatrix},

            because it fixes `P` pointwise (no `P`-column outside the first block),
            carries `P^\perp` into `P^\perp` and `P^\perp` into `P` modulo `P` (no
            `K`-row above the last block).  The isometry condition `g^t B g = B`
            then reads, block by block,

            .. math::
                A = 1, \qquad \tau = -J^{-1} c^t A_K, \qquad
                J a + a^t J^t = -(Kc + c^t K^t + c^t A_K c),

            with `J = b(U, P)`, `K = b(U, K)` and `A_K = b(K, K)`.  These are the
            equations :meth:`unipotent_block_solution` solves, in the ordering of
            :meth:`_unipotent_block_matrix`, where `a` is the `(P, U)`-block, `c` the
            `(K, U)`-block and `\tau` the `(P, K)`-block.  The translation is
            `-J^{-1} c^t A_K` and not `-c^t A_K`, and the second equation carries `J` on
            both sides together with the linear term `Kc + c^t K^t`: the shorter forms
            `\tau + c^t A_K = 0` and `a + a^t + c^t A_K c = 0` hold only in a basis with
            `J = 1_2` and `K = b(U, K) = 0`, which is a splitting plane in a unimodular
            plane basis.  At Sterk's `P_2` of \(T_{\mathrm{En}}\) neither holds -- there
            `J = 2 \cdot 1_2` and `K` has a nonzero entry, and the two are what the plane
            not splitting off the lattice means -- so the equations above are the ones
            this module uses.

            With `A_K = b(K, K)`: the Levi torus of the plane is not in the radical,
            the translation `\tau` is determined by `c \in \operatorname{Hom}(U, K)`,
            and only the skew part of `a` is left free.  So `U_I` is nilpotent of
            class two, `2 \operatorname{rank}(K_I)` of its dimensions are translations
            (:meth:`unipotent_translation_rank`) and one is fixed by the translation
            map (:meth:`unipotent_translation_kernel_rank`).

            **The block form is cited; the consequence is derived and computed.**
            The basis and the Gram matrix are those of Dutour Sikirić--Hulek,
            arXiv:2302.01679v2, Theorem 4.9 (`theorem_isotropic_k_planes`), proof,
            printed pp. 33--34, and :meth:`plane_block_basis` and :meth:`plane_block_gram`
            build and check them.  No published numbered statement gives this
            structure at a plane of a lattice without two hyperbolic planes --
            Scattone, *Mem. Amer. Math. Soc.* 374, §3.7, Proposition 3.7.3, which
            the repository quotes, generates the radical *by transvections*, and its
            hypothesis of two orthogonal hyperbolic planes is not met here -- so the
            derivation above is written here and its dimension is computed by
            `_unipotent_rank` rather than quoted.  The radical's generation does not
            rest on that statement: :meth:`unipotent_parameter_lattice` decides every
            parameter that lifts, and :meth:`unipotent_radical_index` is `1` at this
            plane.

            Measured at Sterk's `P_2` of \(T_{\mathrm{En}}\): `17 = 2 \cdot 8 + 1`,
            against `16` translations and `1` central dimension.
            """
            return self._unipotent_rank(zero_on_perpendicular=False)

        @cached_method
        def unipotent_translation_kernel_rank(self) -> int:
            r"""Return the rank of the kernel of the radical's translation map.

            This is the part of `U_I` that fixes `I^\perp` pointwise: the centre, in
            the block form of :meth:`unipotent_radical_rank`, where it is the skew
            part of `a` with `c = 0` and `\tau = 0`.  It is computed as the dimension
            of the same linear system with the extra conditions `N(K) = 0`.

            At Sterk's `P_2` of \(T_{\mathrm{En}}\): `1`, so `U_I/Z` has rank
            `17 - 1 = 16 = 2 \operatorname{rank}(K)`, the whole of
            `\operatorname{Hom}(I^\perp/I, I)`.
            """
            return self._unipotent_rank(zero_on_perpendicular=True)

        def _unipotent_rank(self, zero_on_perpendicular: bool) -> int:
            r"""Return the dimension of the radical's block-form system.

            The unknowns are the `n^2` entries of `N = g - 1` in the block
            coordinates of :meth:`plane_block_basis`, the conditions are the three
            of :meth:`unipotent_radical_rank` -- `N` kills the two plane vectors,
            `N` carries the `n - 4` basis vectors of `K` into the plane, and
            `N^t B + B N = 0` -- and the dimension of the solution space is the rank
            of `U_I`, because exp and log are polynomial bijections between a
            unipotent group in characteristic zero and its Lie algebra.  With
            ``zero_on_perpendicular`` the conditions `N(K) = 0` are added, which cuts
            out the kernel of the translation map.
            """
            from sage.rings.rational_field import QQ as SageQQ

            change = self.plane_block_gram()[0]
            gram = change * matrix(SageQQ, self.gram_matrix()) * change.transpose()
            size = change.nrows()
            unknowns = size * size
            plane_positions = (2, 3)
            kernel_positions = tuple(range(4, size))

            def empty():
                return [SageQQ(0)] * unknowns

            rows = []
            for column in plane_positions:
                for index in range(size):
                    entry = empty()
                    entry[size * index + column] = SageQQ(1)
                    rows.append(entry)
            for column in kernel_positions:
                for index in range(size):
                    if index in plane_positions:
                        continue
                    entry = empty()
                    entry[size * index + column] = SageQQ(1)
                    rows.append(entry)
            if zero_on_perpendicular:
                for column in kernel_positions:
                    for index in range(size):
                        entry = empty()
                        entry[size * index + column] = SageQQ(1)
                        rows.append(entry)
            for first in range(size):
                for second in range(first, size):
                    entry = empty()
                    for middle in range(size):
                        if gram[middle, second]:
                            entry[size * middle + first] += gram[middle, second]
                        if gram[first, middle]:
                            entry[size * middle + second] += gram[first, middle]
                    rows.append(entry)
            return unknowns - int(matrix(SageQQ, rows).rank())

        @cached_method
        def unipotent_translation_rank(self, family=None) -> tuple[int, int]:
            r"""Return the rank of ``family``'s translations, and the rank of their target.

            An element of the radical fixes `I` pointwise, so its *translation*

            .. math:: \tau(g): I^\perp/I \to I, \qquad \bar x \mapsto g(x) - x

            is a homomorphism of groups -- `\tau(g h) = \tau(g) + \tau(h)`, because
            `h` fixes `I` pointwise and `g` fixes `I` pointwise -- with values in the
            free abelian group `\operatorname{Hom}(K_I, I)` of rank
            `2 \operatorname{rank}(K_I)`.  The subgroup a family generates sits in
            the preimage of the span of its translations, so its rank is at most
            `\operatorname{rank} \tau(\text{family})` plus the rank of the translation
            kernel: a family whose translations fall short of the target therefore
            generates a subgroup of infinite index in the radical, and a target the
            translations reach does *not* by itself prove the index finite (the
            kernel direction can still be missed).

            ``family`` defaults to :meth:`unipotent_radical_generators`, since that
            is the family whose index :meth:`unipotent_radical_index` reports.  A
            member that does not act trivially on `I^\perp/I` has no translation and
            raises, rather than being silently dropped from the rank.

            Measured at Sterk's `P_2` of \(T_{\mathrm{En}}\): `(12, 16)` for the
            fourteen returned unipotent transvections, `(14, 16)` for the
            twenty-eight generators of :meth:`parabolic_stabilizer_generators` that lie
            in the radical, and `(16, 16)` for the family the default returns, which
            includes the block generators of
            :meth:`unipotent_radical_block_generators`.  The first two families fall
            short and generate subgroups of infinite index; the third reaches the target
            and, meeting the centre in a generator, generates the radical, of rank `17`
            (:meth:`unipotent_radical_rank`, :meth:`unipotent_radical_index`).
            """
            from sage.rings.rational_field import QQ as SageQQ

            if family is None:
                family = self.unipotent_radical_generators()
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            rank = int(lattice.module_rank())
            plane_vectors = [self.coordinates(vector) for vector in self.plane_basis()]
            plane = matrix(
                SageQQ,
                [[plane_vectors[column][position] for column in range(len(plane_vectors))] for position in range(rank)],
            )
            perpendicular = self.isotropic_perpendicular()
            perpendicular_vectors = [
                perpendicular.inclusion()(perpendicular.module_generator(label))
                for label in perpendicular.module_generating_set()
            ]

            def plane_coordinates(vector):
                r"""Return the coordinates of ``vector`` on the plane's basis, or ``None``."""
                image = matrix(SageQQ, rank, 1, [int(vector.to_vector()(label)) for label in labels])
                try:
                    solution = plane.solve_right(image)
                except (ValueError, ArithmeticError):
                    return None
                if (plane * solution - image).norm() != 0:
                    return None
                if any(entry.denominator() != 1 for entry in solution.list()):
                    return None
                return [int(entry) for entry in solution.list()]

            translations = []
            for generator in family:
                entry = []
                for vector in perpendicular_vectors:
                    written = plane_coordinates(generator(vector) - vector)
                    if written is None:
                        raise ValueError(
                            f"the element {generator} at {self} does not act trivially on "
                            f"I^perp/I, so it has no translation and is not in the radical"
                        )
                    entry.extend(written)
                translations.append(entry)
            return (
                int(matrix(SageQQ, translations).rank()) if translations else 0,
                2 * (len(perpendicular_vectors) - int(self.module_rank())),
            )

        @cached_method
        def unipotent_radical_index(self):
            r"""Return `[U_I : \langle\text{the returned unipotent generators}\rangle]`.

            The returned family is :meth:`unipotent_radical_generators` -- the plane's
            Eichler transvections that lie in the radical together with the block
            generators of :meth:`unipotent_radical_block_generators` -- and the index is
            the product of the two factors of

            .. math:: [U_I : H] = [\tau(U_I) : \tau(H)] \cdot [Z : H \cap Z],

            `Z` being the centre and `\tau` the translation
            (:meth:`unipotent_translation_rank`, :meth:`unipotent_translation_kernel_rank`).
            Both factors are lattice indices:

            * the first is the index of the `ZZ`-span of the family's parameters `c` in
              :meth:`unipotent_parameter_lattice`, computed by Smith normal form -- the
              map `c \mapsto \tau` is injective, so it is the index of `\tau(H)` in
              `\tau(U_I)` as well.  When the rank falls short the index is infinite and
              this returns `\aleph_0`;
            * the second is the gcd of the coordinates of the family's central members on
              the generator of `Z` (:meth:`_unipotent_central_coordinate`), those being
              the members with `c = 0`.  It is exact as soon as that gcd is `1` -- then
              the subgroup meets `Z` in all of `Z` -- and when it is not, the products of
              non-central members that land in `Z` would have to be enumerated, which
              this method refuses rather than guesses.

            At Sterk's `P_2` of \(T_{\mathrm{En}}\) both factors are `1`: the returned
            family's parameters span the whole parameter lattice (`16` of `16`, the
            lattice of the exact decision) and the central generator is one of its
            members, so the returned family generates the radical, of rank
            `17 = 16 + 1`, and this returns `1`.  The fourteen transvections alone
            are not enough: their translations reach rank `12` of the `16`.
            """
            from sage.arith.misc import gcd
            from sage_extensions.categories.sets.cardinals import aleph0

            rows = int(self.plane_block_gram()[5].nrows())
            order = 2 * rows
            coordinates = []
            central = []
            for generator in self.unipotent_radical_generators():
                c, _tau, a = self.unipotent_block_coordinates(generator)
                parameter = self.unipotent_parameter_vector(c)
                if not any(parameter):
                    central.append(self._unipotent_central_coordinate(a))
                    coordinates.append([0] * order)
                    continue
                coordinates.append(list(self.unipotent_parameter_coordinates(parameter)))
            images = matrix(SageZZ, coordinates)
            if int(images.rank()) < order:
                return aleph0
            diagonal = images.smith_form()[0]
            index = 1
            for position in range(2 * rows):
                index *= abs(int(diagonal[position, position]))
            if not central:
                raise NotImplementedError(
                    f"no member of the returned family at {self} lies in the centre of the "
                    f"radical, so [Z : H cap Z] is not read off the family and the index "
                    f"there is not computed"
                )
            central_index = int(gcd(central))
            if central_index != 1:
                raise NotImplementedError(
                    f"the returned family at {self} meets the centre in {central_index} Z; the "
                    f"products of its non-central members that land in the centre would have to "
                    f"be enumerated to get [Z : H cap Z], and that case is not implemented"
                )
            return index

        def half_vector_transvection_generators(self):
            r"""Return the Eichler transvections of the plane along its half lattice vectors.

            For a primitive isotropic `\\(e \\in P\\)` of divisibility two and
            `\\(w \\in L^{\\#}\\)` with `\\(b(e,w) = 0\\)`, `\\(2w \\in L\\)` and
            `\\(q(w) \\in \\mathbb{Z}\\)`, the transvection

            \\[ E_{e,w}(x) = x - b(w,x)\\, e + b(e,x)\\, w - \\tfrac12 q(w)\\, b(e,x)\\, e \\]

            is an integral isometry of `L` fixing `e` (Dawes, section 2 equation
            (7); Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
            equations (4)--(5); Scattone, Mem. Amer. Math. Soc. 374, section 3.7,
            Proposition 3.7.3, whose criterion generates the radical of the
            parabolic at an isotropic sublattice by these transvections).  It
            fixes `e` and moves `e^\\perp` by multiples of `e`, so it lies in the
            parabolic at `P` and acts trivially on `P^\\perp/P`; on `P` it is
            unipotent.  Because `\\(w \\notin L\\)` it acts nontrivially on the
            discriminant classes of `L`, where every transvection of
            :meth:`parabolic_transvection_generators` acts trivially: on
            `T_{\\mathrm{En}}` at `P_1`, those 20 generate a subgroup of
            `\\rho(O(L))` of order 1, while these generate one of order
            `\\(2^8\\)`.

            The construction and its integrality conditions are
            :meth:`sage_extensions.categories.lattices.Lattices.ParentMethods.eichler_transvection_half_vector`
            and ``half_vector_transvection_parameters``; every returned
            generator is checked there to be an integral isometry before it is
            built.
            """
            lattice = self.ambient_lattice()
            generators = []
            seen = set()
            for isotropic in self.plane_basis():
                for parameter in lattice.half_vector_transvection_parameters(isotropic):
                    transvection = lattice.eichler_transvection_half_vector(isotropic, parameter)
                    key = tuple(int(transvection(vector).to_vector()(label)) for vector in lattice.module_generators() for label in lattice.module_generating_set())
                    if key in seen:
                        continue
                    seen.add(key)
                    generators.append(transvection)
            return tuple(generators)


        @cached_method
        def quotient_reflection_generators(self):
            r"""Return the pointwise-plane reflections in the root shells of \(P^\perp/P\).

            The quotient \(K = P^\perp/P\) is the lattice the Levi acts on.  When
            it is definite its shells are finite; a vector `w` of `K` lifts to a
            vector `\tilde w` of \(P^\perp\) through the reduction's frame, and
            the reflection \(s_{\tilde w}\) is an integral isometry of `L`
            (asserted by the lattice's own reflection) that fixes `P` pointwise,
            since \(P \subseteq \tilde w^\perp\).  So every such reflection lies
            in the parabolic, and its image in \(O(K)\) is the reflection in
            `w`: the Levi factor.

            A shell is taken whole, and further shells are taken while the
            running count stays below 128: for \(T_{\mathrm{En}}\) at \(P_1\),
            \(K = E_8(-4)\) (the catalogue's doubling of \(E_8(-2)\)) has one
            shell of 240 vectors, whose reflections generate
            \(W(E_8) = O(E_8)\) and so the whole Levi factor -- the reflection
            group *is* the orthogonal group of \(E_8\), because \(-1\) is its
            longest element, so no sign class is divided out; for the
            odd \(I_{0,7}(2)\) of the Coble ambient the first shell alone gives
            only the sign changes and the second is needed for the permutations.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            if quotient.is_definite() is not True:
                raise ValueError(
                    f"the Levi factor of the parabolic at {self} is not spanned by "
                    f"reflections: the quotient P^perp/P = {quotient} is not definite, "
                    f"so its shells are infinite and no shell enumeration of the "
                    f"reflection family is available here"
                )
            lattice = self.ambient_lattice()
            if int(quotient.module_rank()) == 0:
                # P^perp = P: the whole group is the parabolic, and the Levi factor
                # on K = P^perp/P = 0 is trivial.  A rank-zero cartesian lattice has
                # no shortest vector, so the shell enumeration below must not run.
                return ()
            labels = tuple(quotient.module_generating_set())
            lifts = self.quotient_frame_lifts()

            def coordinates(element):
                vector = element.to_vector()
                return tuple(int(vector(label)) for label in labels)

            def lift(element):
                entries = coordinates(element)
                return sum(
                    (
                        lattice.scalar_multiple(
                            lattice.base_ring()(entries[position]), lifts[label]
                        )
                        for position, label in enumerate(labels)
                        if entries[position]
                    ),
                    lattice.zero(),
                )

            shortest = tuple(quotient.shortest_vectors())
            if not shortest:
                raise ValueError(
                    f"the Levi factor of the parabolic at {self} has no reflection to "
                    f"lift: the definite quotient P^perp/P = {quotient} has no shortest "
                    f"vector other than zero"
                )
            square = int(quotient.b(shortest[0], shortest[0]))
            shells = [shortest]
            count = len(shortest)
            step = 1
            while count <= 128 and step <= 3:
                shells.append(tuple(quotient.vectors_of_square(square * (step + 1))))
                count = sum(len(shell) for shell in shells)
                step += 1
            lifted = []
            seen = set()
            for shell in shells:
                for element in shell:
                    key = coordinates(element)
                    if all(-entry == 0 for entry in key):
                        continue
                    negative = tuple(-entry for entry in key)
                    if negative in seen:
                        continue
                    seen.add(key)
                    lifted.append(lift(element))
            generators = []
            for vector in lifted:
                if vector.is_integral_reflection_vector():
                    generators.append(lattice.reflection(vector))
            return tuple(generators)

        @cached_method
        def quotient_frame_lifts(self):
            r"""Return the reduction's frame, lifted into the ambient lattice, by quotient label.

            ``isotropic_reduction().coordinate_frame()`` is a section of
            \(P^\perp \twoheadrightarrow P^\perp/P\) on a generating set of the
            quotient lattice; this returns the same section with values in the
            ambient lattice, so a vector of the quotient can be lifted linearly.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            perpendicular_inclusion = reduction.orthogonal_complement().inclusion()
            frame = reduction.coordinate_frame()
            return {
                label: perpendicular_inclusion(frame(label))
                for label in quotient.module_generating_set()
            }

        @cached_method
        def splitting_complement(self):
            r"""Return a `ZZ`-basis complement of `P^\perp` that is orthogonal to `K`, or ``None``.

            The Levi action on `P` is read in the coordinates `(P, U)` where `U`
            completes a `ZZ`-basis of \(P^\perp\) to one of `L`.  A Levi element
            acts on `P` by `M` and on `U` by the contragredient matrix; it is an
            isometry of `L` exactly when that matrix is integral, which is what
            makes the lift constructive in the *split* case of
            :meth:`levi_lift_generators`: `P \perp U` is then an orthogonal
            summand of `L` carrying the plane.  The returned pair is ``None``
            when no such complement exists, i.e. when the complement pairs
            nontrivially with \(K = P^\perp/P\).
            """
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            rank = len(labels)
            current = matrix(
                SageZZ, [self.coordinates(vector) for vector in self.perpendicular_basis()]
            )
            breadth = int(self.module_rank())
            complement = []
            for position in range(rank):
                row = tuple(1 if other == position else 0 for other in range(rank))
                augmented = matrix(SageZZ, tuple(current.rows()) + (row,))
                if augmented.rank() > current.rank():
                    current = augmented
                    complement.append(row)
                if len(complement) == breadth:
                    break
            if len(complement) != breadth:
                return None
            vectors = tuple(self.vector_from_coordinates(row) for row in complement)
            zero = lattice.base_ring().zero()
            for lifted in self.quotient_frame_lifts().values():
                for vector in vectors:
                    if lattice.b(vector, lifted) != zero:
                        return None
            return vectors

        @cached_method
        def plane_block_basis(self):
            r"""Return the basis `(U \mid P \mid K)` in which the parabolic's block form is stated.

            `(p_1, p_2)` is :meth:`plane_basis`; `(k_1, \dots, k_{n-4})`
            completes it to a `ZZ`-basis of \(P^\perp\) -- the plane is
            primitive, so it is saturated there and the completion exists --
            and `(u_1, u_2)` completes that to a `ZZ`-basis of `L`.  Nothing
            here requires `U` to be orthogonal to `K`: that orthogonality *is*
            the split hypothesis, and it fails exactly when the plane does not
            split off the lattice.

            Dutour Sikirić--Hulek, *Moduli of polarised Enriques surfaces --
            computational aspects*, J. London Math. Soc. 110 (2024),
            arXiv:2302.01679v2, Theorem 4.9 (`theorem_isotropic_k_planes`),
            proof, printed pp. 33--34: "Let us take a basis
            \((e_{k+1}, \dots, e_{2k})\) of `Is` ... we can complete this to a
            basis \((e_{k+1}, \dots, e_n)\) of \(Is^\perp\) ... We then complete
            this to a basis of `L` by finding suitable vectors
            \((e_1, \dots, e_k)\)", the matrix of scalar products then being

            \[
            B = \begin{pmatrix} H & J & K\\ J^t & 0 & 0\\ K^t & 0 & A\end{pmatrix}
            \]

            with `J` and `A` non-degenerate.  In their indexing `(e_1..e_k)` is
            this `U`, `(e_{k+1}..e_{2k})` is `P`, and `(e_{2k+1}..e_n)` is `K`;
            the block `K = b(U, K)` is their `K` and vanishes for a splitting
            plane only, while `b(P, K) = 0` always, because `K` lies in
            \(P^\perp\).

            **The two completions are the cokernels'.**  Each completion above
            is of a *saturated* sublattice, so each is available from the
            quotient rather than by a search.  `P` is saturated in
            \(P^\perp\): it is saturated in `L`, and if `n v` lies in `P` for a
            `v` of \(P^\perp\) then `v` lies in `L` and `n v` in `P`, so `v`
            itself lies in `P`; likewise \(P^\perp\) is saturated in `L` by its
            own definition as the perpendicular of a family of vectors.  So
            \(P^\perp/P\) and \(L/P^\perp\) are torsion-free, and a finitely
            generated torsion-free module over the principal ideal domain `ZZ`
            is free -- :meth:`...finite_free_trivialization`, which returns the
            isomorphism with the free module on the quotient's own generators.
            Lifting those basis points back along the cokernel projection gives
            the completing vectors.  Keeping standard basis vectors in order
            while they raise the rank does **not** compute this, and on
            \(T_{\mathrm{Co}}\) at a plane whose generators are congruent modulo
            `2` the first such vector to raise the rank of \(P^\perp\)'s chosen
            basis to `9` leaves a sublattice of index `2`, so the assembled rows
            were not a `ZZ`-basis of `L` at all.  The standard rows are kept
            where they do give a basis -- the block coordinates of the planes
            this repository measures do not move -- and the cokernel completion
            is what this method falls back on otherwise.
            """
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            rank = len(labels)
            plane_rows = [self.coordinates(vector) for vector in self.plane_basis()]
            perpendicular_rows = _rank_completed_rows(
                plane_rows,
                [self.coordinates(vector) for vector in self.vector_perpendicular_basis(self.plane_basis())],
                rank - 4,
            )
            complement_rows = _rank_completed_rows(
                plane_rows + perpendicular_rows,
                [tuple(1 if other == position else 0 for other in range(rank)) for position in range(rank)],
                2,
            )
            rows = plane_rows + perpendicular_rows + complement_rows
            if len(rows) != rank or abs(int(matrix(SageZZ, rows).determinant())) != 1:
                rows, plane_rows, perpendicular_rows, complement_rows = self._cokernel_block_rows()
            current = matrix(SageZZ, rows)
            assert (
                len(complement_rows) == 2
                and len(perpendicular_rows) == rank - 4
                and abs(int(current.determinant())) == 1
            ), (
                f"the plane's basis, its completion to P^perp and that to L must give a "
                f"ZZ-basis of L, but the ranks came out as {len(perpendicular_rows)} and "
                f"{len(complement_rows)} with determinant {int(current.determinant())}"
            )
            return tuple(
                self.vector_from_coordinates(row)
                for row in complement_rows + plane_rows + perpendicular_rows
            )

        def _cokernel_block_rows(self):
            r"""Return the block rows `(U \mid P \mid K)`, completed through the cokernels.

            The fallback of :meth:`plane_block_basis`, for a plane at which keeping
            standard basis vectors in order while they raise the rank does not give
            a `ZZ`-basis of `L` — at a `T_Co` plane it leaves a sublattice of
            index `2`.  Both completions are then the cokernels': `P`
            is saturated in \(P^\perp\) (`P` is saturated in `L`, and if `n v` lies
            in `P` for a `v` of \(P^\perp\) then `v` lies in `L` and `n v` in `P`),
            and \(P^\perp\) is saturated in `L` by its own definition, so both
            quotients are torsion-free and free over `ZZ`
            (:meth:`...finite_free_trivialization`); lifting that trivialization's
            basis points back along the cokernel projection completes the basis.
            """
            lattice = self.ambient_lattice()
            rank = len(tuple(lattice.module_generating_set()))
            perpendicular = lattice.subobject_on(tuple(self.perpendicular_basis()))
            into_perpendicular = self.inclusion().factor_through(perpendicular.inclusion())
            perpendicular_basis = _completed_basis(
                into_perpendicular,
                tuple(
                    into_perpendicular(into_perpendicular.domain().module_generator(label))
                    for label in into_perpendicular.domain().module_generating_set()
                ),
            )
            into_lattice = perpendicular.inclusion()
            from_perpendicular = tuple(into_lattice(vector) for vector in perpendicular_basis)
            completing = _completed_basis(
                into_lattice,
                tuple(
                    into_lattice(into_lattice.domain().module_generator(label))
                    for label in into_lattice.domain().module_generating_set()
                ),
            )[len(perpendicular_basis):]
            plane_rows = [self.coordinates(vector) for vector in self.plane_basis()]
            perpendicular_rows = [self.coordinates(vector) for vector in from_perpendicular[2:]]
            complement_rows = [self.coordinates(vector) for vector in completing]
            return (
                complement_rows + plane_rows + perpendicular_rows,
                plane_rows,
                perpendicular_rows,
                complement_rows,
            )

        @cached_method
        def plane_block_gram(self):
            r"""Return `(change, inverse, H, J, K, A)` from the block form of :meth:`plane_block_basis`.

            ``change`` is the change-of-basis matrix whose rows are the basis
            vectors' coordinates on the ambient lattice's generating set and
            ``inverse`` its inverse, and the blocks are as stated by Dutour
            Sikirić--Hulek, Theorem 4.9, printed pp. 33--34: `H = b(U,U)`,
            `J = b(U,P)`, `K = b(U,K)`, `A = b(K,K)`; the block `b(P,K)` is zero
            and is not returned.
            """
            lattice = self.ambient_lattice()
            basis = self.plane_block_basis()
            rank = len(basis)
            change = matrix(SageZZ, [self.coordinates(vector) for vector in basis])
            gram = matrix(SageZZ, self.gram_matrix())
            block_gram = change * gram * change.transpose()
            inverse_entries = change.inverse()
            assert all(
                entry in SageZZ for entry in inverse_entries.list()
            ), f"the block basis of {self} is not a ZZ-basis of L"
            inverse = matrix(
                SageZZ,
                [
                    [int(inverse_entries[row, column]) for column in range(rank)]
                    for row in range(rank)
                ],
            )
            return (
                change,
                inverse,
                block_gram[0:2, 0:2],
                block_gram[0:2, 2:4],
                block_gram[0:2, 4:rank],
                block_gram[4:rank, 4:rank],
            )

        def plane_block_parameter_period(self, action):
            r"""Return the period of the free parameter of the plane block equations.

            With the block basis of :meth:`plane_block_basis` and the notation of
            :meth:`plane_block_lift`, the solutions of the `P_2` equation

            \[
            (P_1 J P_2^t)^t + P_1 J P_2^t = \mathrm{remainder}
            \]

            are `P_2 = (\mathrm{remainder}/2 + sK)^t (P_1J)^{-t}` over the skew
            matrices `sK`, `K = ((0,-1),(1,0))`, so their integrality is a condition
            on one rational parameter `s`.  It is periodic: adding the least common
            multiple of the denominators of `K (P_1J)^{-t}` to `s` adds an integral
            matrix to `P_2`, and nothing smaller does.  That multiple is the period
            returned here. A period of the rational parameter is not a proof
            that an integral solution has an integral parameter value.
            The lift itself uses the integral symmetric linear system.

            The period divides $|\det J|$, since
            $(P_1J)^{-t}=J^{-t}Q_1$ has denominators dividing $\det J$.
            """
            from sage.rings.rational_field import QQ as SageQQ

            J = self.plane_block_gram()[3].change_ring(SageQQ)
            if int(J.determinant()) == 0:
                raise ValueError(
                    f"the complement of P^perp found for {self} does not pair "
                    f"nondegenerately with the plane"
                )
            # P_1 = J Q_1^{-t} J^{-1} makes P_1 J = J Q_1^{-t}, hence
            # (P_1 J)^{-t} = J^{-t} Q_1: the linear part of P_2 in the parameter is
            # K J^{-t} Q_1, whose denominators divide det J.
            linear = (
                matrix(SageQQ, [[0, -1], [1, 0]])
                * J.inverse().transpose()
                * action.change_ring(SageQQ)
            )
            period = SageZZ.one()
            for entry in linear.list():
                denominator = SageZZ(entry.denominator())
                period = period * denominator // period.gcd(denominator)
            return period

        def quotient_block_matrix(self, quotient_action):
            r"""Return the matrix of ``quotient_action`` on the basis `K` of \\(K_I\\) that :meth:`plane_block_basis` carries.

            The `K` block of the block basis is a `ZZ`-basis of
            \\(K_I=I^\\perp/I\\) -- the reduction's own frame is only a section on
            a generating set -- so a class action is read on it, one column per
            basis class.  Writing the classes of the basis vectors in the
            reduction's coordinates turns "the image of the `i`-th basis class"
            into one integral linear system, solved exactly by Smith normal form;
            a system with no integral solution means the vectors are not a basis
            of the quotient and is refused rather than solved approximately.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            labels = tuple(quotient.module_generating_set())
            perpendicular_inclusion = reduction.orthogonal_complement().inclusion()
            projection = reduction.projection()
            basis = self.plane_block_basis()
            rank = len(basis)
            width = rank - 4
            classes = tuple(
                projection(perpendicular_inclusion.lift(vector)) for vector in basis[4:rank]
            )
            coordinates = matrix(
                SageZZ,
                [
                    [int(vector.to_vector()(label)) for vector in classes]
                    for label in labels
                ],
            )
            block = matrix(SageZZ, width, width, 0)
            for column, vector in enumerate(classes):
                image = quotient_action(vector)
                target = matrix(
                    SageZZ,
                    len(labels),
                    1,
                    [int(image.to_vector()(label)) for label in labels],
                )
                solution = _integral_solution(coordinates, target)
                if solution is None:
                    raise ArithmeticError(
                        f"the classes of the K block of {self} do not span the quotient "
                        f"K_I = {quotient} integrally, so the class action cannot be read on them"
                    )
                for row in range(width):
                    block[row, column] = int(solution[row])
            return block

        def plane_block_lift(self, action, quotient_action=None):
            r"""Return the integral isometry of `L` carrying `P` by ``action``, or ``None``.

            This solves the block equations of Dutour Sikirić--Hulek, Theorem
            4.9 (`theorem_isotropic_k_planes`), printed pp. 33--34, in the basis
            `(U \mid P \mid K)` of :meth:`plane_block_basis`, for an isometry
            whose block form is

            \[
            g = \begin{pmatrix} P_1 & P_2 & P_3\\ 0 & Q_1 & 0\\ 0 & Q_2 & Q_3\end{pmatrix},
            \qquad Q_1 = \text{action},\quad Q_3 = \\text{quotient action},
            \]

            ``quotient_action`` is an isometry of \\(K_I=P^\\perp/P\\), read on the
            reduction's frame, and its matrix \\(Q_3\\) is the third diagonal block;
            The default quotient action is the identity. The row block Q2 is free; setting it to zero is only a rational normal form, not an integral hypothesis.
            Solve the three equations of Dutour Sikirić--Hulek, Theorem 4.9,
            printed pp. 33--34, including the mixed term P1 J Q2^t in E3.
            The last symmetric equation is an integer linear system for P2.
            The finite residue orbit in _plane_block_lift_for decides it
            for all integral solutions of E3, not just Q2=0.
            """
            from sage.rings.rational_field import QQ as SageQQ

            lattice = self.ambient_lattice()
            change, inverse, H, J, K, A = self.plane_block_gram()
            rank = len(self.plane_block_basis())
            if int(J.determinant()) == 0:
                raise ValueError(
                    f"the complement of P^perp found for {self} does not pair "
                    f"nondegenerately with the plane"
                )
            rational = SageQQ
            H = H.change_ring(rational)
            J = J.change_ring(rational)
            K = K.change_ring(rational)
            A = A.change_ring(rational)
            action = action.change_ring(rational)
            breadth = rank - 4
            requested_frame = None
            if quotient_action is None:
                identity_breadth = matrix(rational, breadth, breadth, 0)
                for position in range(breadth):
                    identity_breadth[position, position] = 1
                quotients = [identity_breadth]
            else:
                requested_frame = self._frame_matrix(quotient_action)
                quotients = [
                    self.quotient_block_matrix(quotient_action).transpose().change_ring(rational)
                ]
            for quotient in quotients:
                found = self._plane_block_lift_for(
                    action, quotient, requested_frame, change, inverse, H, J, K, A, rank, rational
                )
                if found is not None:
                    return found
            return None

        def _plane_block_lift_for(
            self, action, quotient, requested_frame, change, inverse, H, J, K, A, rank, rational
        ):
            r"""Return the integral lift of the pair `(action, quotient)` for one `Q_3`, or ``None``."""
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            first = J * action.transpose().inverse() * J.inverse()
            if any(entry not in SageZZ for entry in first.list()):
                return None
            if abs(action.determinant()) != 1 or abs(quotient.determinant()) != 1:
                return None
            if quotient * A * quotient.transpose() != A:
                return None
            first = first.change_ring(SageZZ)
            H, J, K, A = (block.change_ring(SageZZ) for block in (H, J, K, A))
            action, quotient = action.change_ring(SageZZ), quotient.change_ring(SageZZ)
            mixed = first * J
            definite = A * quotient.transpose()
            target = K - first * K * quotient.transpose()
            breadth = A.nrows()
            entries = ((0, 0), (0, 1), (1, 1))
            symmetric_system = matrix(
                SageZZ, 3, 4,
                lambda row, col: (
                    int(entries[row][1] == col // 2) * mixed[entries[row][0], col % 2]
                    + int(entries[row][0] == col // 2) * mixed[entries[row][1], col % 2]
                ),
            )

            def build(third, quotient_mixed):
                remainder = (
                    H - first * H * first.transpose() - third * A * third.transpose()
                    - third * K.transpose() * first.transpose()
                    - first * K * third.transpose()
                )
                if remainder.is_zero():
                    second = matrix(SageZZ, 2, 2)
                else:
                    solution = _integral_solution(
                        symmetric_system,
                        matrix(SageZZ, 3, 1, [remainder[i, j] for i, j in entries]),
                    )
                    if solution is None:
                        return None
                    second = matrix(SageZZ, 2, 2, solution)
                block = matrix(SageZZ, rank, rank)
                block[0:2, 0:2] = first
                block[0:2, 2:4] = second
                block[0:2, 4:rank] = third
                block[2:4, 2:4] = action
                block[4:rank, 2:4] = quotient_mixed
                block[4:rank, 4:rank] = quotient
                lifted = change.transpose() * block.transpose() * inverse.transpose()
                images = {
                    label: lattice.linear_combination({
                        other: ring(int(lifted[row, column]))
                        for row, other in enumerate(lattice.module_generating_set())
                        if lifted[row, column]
                    })
                    for column, label in enumerate(lattice.module_generating_set())
                }
                candidate = lattice.Aut()(images)
                assert self._preserves_the_form(candidate) is True
                assert self.stabilizes(candidate)
                if requested_frame is not None:
                    induced = self.isotropic_reduction().levi_action()(candidate)
                    assert self._frame_matrix(induced) == requested_frame
                return candidate

            third = target * definite.inverse() if breadth else matrix(SageZZ, 2, 0)
            if all(entry in SageZZ for entry in third.list()):
                found = build(third.change_ring(SageZZ), matrix(SageZZ, breadth, 2))
                if found is not None:
                    return found
            if breadth == 0:
                return None

            # Smith coordinates separate the two mixed rows and the two
            # diagonal quadratic conditions. Only the cross-pairing couples
            # the rows. The changes of coordinates are integral unimodular.
            diagonal, left, right = mixed.smith_form()
            scales = tuple(abs(int(diagonal[i, i])) for i in range(2))
            assert all(scales)
            h = left * (H - first * H * first.transpose()) * left.transpose()
            k = left * first * K
            t = left * target
            even = all(A[i, i] % 2 == 0 for i in range(breadth))

            def rows(i):
                d = scales[i]
                # A shift by d preserves the norm condition modulo 2d when
                # the quotient is even or d is even; otherwise use 2d.
                modulus = d if even or d % 2 == 0 else 2 * d
                system = definite.transpose().augment(d * identity_matrix(SageZZ, breadth))
                solution = _integral_solution(system, matrix(SageZZ, breadth, 1, list(t.row(i))))
                if solution is None:
                    return
                start = tuple(int(x) % modulus for x in solution[:breadth])
                generators = tuple(
                    tuple(int(x) % modulus for x in v[:breadth])
                    for v in system.right_kernel().basis()
                )
                frontier = [start]
                seen = {start}
                while frontier:
                    current = frontier.pop()
                    y = vector(SageZZ, current)
                    ay = A * y
                    if (h[i, i] - y.dot_product(ay) - 2 * y.dot_product(k.row(i))) % (2 * d) == 0:
                        yield y
                    for generator in generators:
                        moved = tuple((x + z) % modulus for x, z in zip(current, generator, strict=True))
                        if moved not in seen:
                            seen.add(moved)
                            frontier.append(moved)

            second_rows = tuple(rows(1))
            if not second_rows:
                return None
            cross_modulus = SageZZ(scales[0]).gcd(scales[1])
            for y0 in rows(0):
                for y1 in second_rows:
                    if (
                        h[0, 1] - y0.dot_product(A * y1)
                        - y0.dot_product(k.row(1)) - k.row(0).dot_product(y1)
                    ) % cross_modulus:
                        continue
                    transformed = matrix(SageZZ, [y0, y1])
                    third = left.inverse() * transformed
                    quotient_mixed = (right * diagonal.inverse() * (t - transformed * definite)).transpose()
                    found = build(third.change_ring(SageZZ), quotient_mixed.change_ring(SageZZ))
                    assert found is not None, "Smith-row divisibility implies an integral symmetric solution"
                    return found
            return None

        def _plane_mixed_block_system(self, mixed, definite):
            r"""Integer system for mixed Q2 and P3 in the third block equation.

            For M=P1 J, N=A Q3^t, the unknowns are the entries of Q2^t
            and P3 in row order. The equation is M Q2^t + P3 N = target.
            Its full solution lattice projects to the P3 residue classes
            modulo 2|det J|. Replacing P3 by another representative of
            such a class changes the symmetric remainder by a multiple
            of 2|det J|. The correction
            (delta_remainder/2)(M^t)^-1 is integral, so existence of an
            integral P2 is constant on this class. A finite orbit of the
            projected integer kernel therefore decides all mixed lifts.
            """
            breadth = definite.nrows()
            return matrix(
                SageZZ, 2 * breadth, 4 * breadth,
                lambda row, col: (
                    mixed[row // breadth, col // breadth] * int(row % breadth == col % breadth)
                    if col < 2 * breadth else
                    int(row // breadth == (col - 2 * breadth) // breadth)
                    * definite[(col - 2 * breadth) % breadth, row % breadth]
                ),
            )

        def _elementary_plane_actions(self):
            r"""Return the elementary plane actions whose lifts present the kernel's plane factor.

            `\Gamma(2)`, the kernel of `\GL_2(\ZZ) \to \GL_2(\FF_2)`, is generated
            by the two shears `\begin{pmatrix}1&2\\0&1\end{pmatrix}` and
            `\begin{pmatrix}1&0\\2&1\end{pmatrix}` together with `-1` (Sanov 1947;
            the standard statement that `\Gamma(2)/\{\pm 1\}` is free on the two
            shears).  `_plane_action_index` certifies a plane-action subgroup by
            exhibiting those three as products of at most four of its members, so a
            family a caller feeds it has to contain them: the list below is the
            identity, the negation, the two unit shears, the swap, and the two
            shears of level `|\det J|`.

            It is a generating list and not a decision device.  Which plane actions
            admit an integral lift at all is decided over the whole of
            `\GL_2(\ZZ)` by :meth:`plane_action_congruence_classes`, and the
            completeness of the kernel :meth:`levi_quotient_kernel_generators`
            builds from this list is the agreement of two computed indices, not the
            length of this list.
            """
            modulus = abs(int(self.plane_block_gram()[3].determinant()))
            if modulus == 0:
                raise ValueError(
                    f"the complement of P^perp found for {self} does not pair "
                    f"nondegenerately with the plane"
                )
            level = modulus if modulus % 2 == 0 else 2 * modulus
            return (
                matrix(SageZZ, [[1, 0], [0, 1]]),
                matrix(SageZZ, [[-1, 0], [0, -1]]),
                matrix(SageZZ, [[1, 1], [0, 1]]),
                matrix(SageZZ, [[1, 0], [1, 1]]),
                matrix(SageZZ, [[0, 1], [1, 0]]),
                matrix(SageZZ, [[1, level], [0, 1]]),
                matrix(SageZZ, [[1, 0], [level, 1]]),
            )

        def plane_action_congruence_classes(self, quotient_action):
            r"""Plane residue classes admitting integral blocks P1,Q2,P3.

            The second and third equations of Dutour Sikirić--Hulek,
            Theorem 4.9 (printed pp. 33--34), are necessary but not
            sufficient for the full lift. For a prescribed quotient action
            C, P1=J Q1^(-t) J^-1 must be integral, and the third equation
            is the integer linear system in _plane_mixed_block_system.
            These conditions are constant on fixed-determinant classes
            modulo |det J|^2: P1 changes by a multiple of |det J|,
            and the change in the third equation can be absorbed in Q2
            since the columns of P1 J span the same lattice as J.
            A multiple of this modulus distinguishes the determinant signs
            and retains parity. The full lift uses the exact coset method
            rather than enumerating this potentially large residue set.
            """
            _change, _inverse, _H, J, K, A = self.plane_block_gram()
            quotient = self.quotient_block_matrix(quotient_action).transpose()
            determinant = abs(int(J.determinant()))
            discriminant = abs(int(A.determinant()))
            assert determinant and discriminant
            level = determinant**2
            if level <= 2:
                level *= 4
            if level % 2:
                level *= 2
            definite = A * quotient.transpose()
            breadth = A.nrows()
            classes = []
            for action in _general_linear_classes(level):
                first = J * action.transpose().inverse() * J.inverse()
                if any(entry not in SageZZ for entry in first.list()):
                    continue
                first = first.change_ring(SageZZ)
                target = K - first * K * quotient.transpose()
                if target.is_zero() or breadth == 0:
                    classes.append(action)
                    continue
                system = self._plane_mixed_block_system(first * J, definite)
                if _integral_solution(system, matrix(SageZZ, 2 * breadth, 1, target.list())) is not None:
                    classes.append(action)
            if not classes:
                raise LeviQuotientLiftAbsent(
                    f"no integral second and third block equation solution at {self}"
                )
            return tuple(classes)

        @cached_method
        def levi_quotient_lift_or_none(self, quotient_action):
            r"""Decide and lift a quotient action by the integral plane projection cosets.

            Let H be the plane projection of the kernel of the quotient
            action, intersected with SL_2(ZZ). The exact block lift
            decides membership in H. It contains the principal congruence
            subgroup at _levi_plane_congruence_level, hence has finite
            index. For fixed quotient action the liftable plane actions
            are a union of right cosets Hx (indeed one coset of the full
            kernel projection when nonempty). Thus the transitive coset
            walk in each determinant component decides existence.
            """
            for action in self._elementary_plane_actions():
                found = self.plane_block_lift(action, quotient_action)
                if found is not None:
                    return found
            level = self._levi_plane_congruence_level()
            decisions = {}

            def in_special(action):
                key = tuple(int(entry) % level for entry in action.list())
                if key not in decisions:
                    decisions[key] = self.plane_block_lift(action) is not None
                return decisions[key]

            generators = (
                matrix(SageZZ, [[1, 1], [0, 1]]),
                matrix(SageZZ, [[1, 0], [1, 1]]),
            )
            for start in (matrix.identity(SageZZ, 2), matrix(SageZZ, [[-1, 0], [0, 1]])):
                _, _, found = right_coset_action(
                    generators, in_special, start=start,
                    accept=lambda action: self.plane_block_lift(action, quotient_action),
                )
                if found is not None:
                    return found
            return None

        def levi_quotient_lift(self, quotient_action):
            r"""An integral lift of the given quotient isometry, if it exists."""
            lift = self.levi_quotient_lift_or_none(quotient_action)
            if lift is None:
                raise LeviQuotientLiftAbsent(
                    f"the quotient action at {self} has no integral lift in either determinant component"
                )
            return lift

        @cached_method
        def levi_quotient_image_lifts(self):
            r"""Lift generators of the actual quotient image of a maximal plane.

            The image M of the integral plane stabilizer in O(K) is a
            subgroup, with membership decided by the exact block lift.
            The quotient K is definite (or zero), so O(K) is finite.
            If its generators lift, their lifts suffice. Otherwise form
            the actual coset space O(K)/M using that membership predicate
            and read its complete Schreier family. Lifting those elements
            gives a family whose quotient image is exactly M, even if M
            is proper or its lifts require nontrivial plane actions.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            if int(quotient.module_rank()) == 0:
                return ()
            assert quotient.is_definite() is True
            orthogonal = reduction.levi_action().codomain()
            generators = tuple(orthogonal.group_generators())
            lifts = tuple(self.levi_quotient_lift_or_none(g) for g in generators)
            if all(lift is not None for lift in lifts):
                return lifts
            liftable = orthogonal.predicate_subgroup(
                lambda action: self.levi_quotient_lift_or_none(action) is not None,
                lambda: "quotient actions with an integral plane stabilizer lift",
            )
            cosets = orthogonal.left_cosets(liftable)
            result = []
            for action in cosets.schreier_family_members():
                if action == orthogonal.one():
                    continue
                lift = self.levi_quotient_lift_or_none(action)
                assert lift is not None
                result.append(lift)
            return tuple(result)

        @cached_method
        def levi_quotient_image_is_all(self) -> bool:
            r"""Surjectivity onto the actual definite quotient orthogonal group.

            The image is a subgroup, so it is all of O(K) exactly when
            every member of a complete generating family of O(K) lifts.
            The integral lift decision checks both determinant components
            of the plane action, not merely the pointwise plane stabilizer.
            """
            reduction = self.isotropic_reduction()
            if int(reduction.quotient_lattice().module_rank()) == 0:
                return True
            assert reduction.quotient_lattice().is_definite() is True
            return all(
                self.levi_quotient_lift_or_none(action) is not None
                for action in reduction.levi_action().codomain().group_generators()
            )

        @cached_method
        def _levi_plane_congruence_level(self):
            r"""Return a level on which existence of an integral plane lift is constant.

            Put `D=|\det J|` and `E=|\det A|`. For plane matrices
            of the same determinant sign, congruence modulo `2D^2` makes
            their inverse transposes congruent modulo `2D^2` by the
            two-by-two adjugate formula. Thus their `U=JB^{-t}J^{-1}`
            differ by a multiple of `2D`, preserving integrality.
            Both mixed coefficient matrices `M=UJ=JB^{-t}` have
            column lattice `J\ZZ^2`. Keep the same free block Y:
            the change of the mixed right-hand side is divisible by
            `2D` and hence lies in that column lattice. The symmetric
            coefficient image is unchanged under unimodular column
            operations on M. Its right-hand side changes by a symmetric
            matrix Delta divisible by `2D`; the integral correction
            `(\Delta/2)M^{-t}` maps to Delta. Reversing the argument
            proves equivalence of liftability. The returned level
            `2D^3E^2` is a multiple of this sufficient level.
            """
            _change, _inverse, _H, J, _K, A = self.plane_block_gram()
            determinant = abs(int(J.determinant()))
            discriminant = abs(int(A.determinant()))
            if determinant == 0 or discriminant == 0:
                raise ValueError(
                    f"the plane block at {self} is degenerate, so its Levi plane "
                    f"projection has no congruence presentation"
                )
            return 2 * determinant**3 * discriminant**2

        def _levi_plane_residue_lift(self, residues):
            r"""Return the integral plane lift of a residue class, or ``None``.

            ``residues`` has determinant one.  The class lift preserves its
            residues and determinant, and :meth:`_levi_plane_congruence_level`
            makes the answer independent of the representative.
            """
            level = self._levi_plane_congruence_level()
            action = _unimodular_lift(residues, level)
            assert int(action.determinant()) == 1
            return self.plane_block_lift(action)

        @cached_method
        def _levi_plane_action_presentation(self):
            r"""Return the SL presentation of the plane projection and a reversing lift.

            The projection of the setwise quotient kernel is

            .. math:: \Gamma' = \{Q_1 : Q_1 \text{ has an integral lift with } Q_3=1\}.

            This is a congruence subgroup of `GL_2(ZZ)` by
            :meth:`_levi_plane_congruence_level`.  Both determinant halves are
            the same walk, :func:`right_coset_action`, and the walk's
            comparison is `xy^{-1}\in H`: it multiplies on the right, so the
            classes it enumerates are the right cosets `Hx`, and no left coset
            and no adjugate stands in for the inverse.  The special-linear part
            is the action of the two elementary shears on the right cosets of
            `H=\Gamma'\cap SL_2(ZZ)`.  Starting with the identity coset the
            shears reach every right coset, because they generate `SL_2(ZZ)` and
            `SL_2(ZZ)\to SL_2(ZZ/\text{level})` is onto.  Candidates are
            identified by an exact integral lift test
            (:meth:`plane_block_lift`), not by a bounded word search and
            not by an enumeration of unimodular sequences.  Sage's
            `ArithmeticSubgroup_Permutation` then reconstructs `H` from that
            permutation action and returns its generators.

            For determinant `-1`, write every action as `diag(-1,1)S` with
            `S\in SL_2(ZZ)`.  The same walk started at `diag(-1,1)` enumerates
            the right cosets of `H` in the reversing half.  Both elements of a
            comparison there have determinant `-1`, so the inverse it uses is
            `-\operatorname{adj}` (:func:`_unimodular_inverse`); the order of
            the product and that sign are the whole difference between this
            partition and the left-coset one, which
            `tests/lattices/test_the_plane_projection_walks_its_right_cosets.sage`
            separates on a finite specimen.  Liftability is constant on such a
            right coset, so one representative per coset decides whether a
            reversing lift exists.  One reversing lift, if present, together
            with `H` gives all of `\Gamma'`; otherwise `\Gamma'=H`.
            """
            from sage.modular.arithgroup.arithgroup_perm import (
                ArithmeticSubgroup_Permutation,
            )

            level = self._levi_plane_congruence_level()
            identity = matrix(SageZZ, [[1, 0], [0, 1]])
            shears = (
                matrix(SageZZ, [[1, 1], [0, 1]]),
                matrix(SageZZ, [[1, 0], [1, 1]]),
            )
            decisions = {}

            def residues(action):
                return tuple(int(entry) % level for entry in action.list())

            def is_in_special_projection(action):
                key = residues(action)
                if key not in decisions:
                    decisions[key] = self.plane_block_lift(action) is not None
                return decisions[key]

            if not is_in_special_projection(identity):
                raise ArithmeticError(
                    f"the identity plane action has no integral lift at {self}, although "
                    f"the identity of the lattice is such a lift"
                )
            representatives, tables, _ = right_coset_action(
                shears, is_in_special_projection, start=identity
            )
            permutations = tuple(
                [table[index] + 1 for index in range(len(representatives))]
                for table in tables
            )
            special = ArithmeticSubgroup_Permutation(
                L=permutations[0], R=permutations[1]
            )
            _, _, reversing_lift = right_coset_action(
                shears,
                is_in_special_projection,
                start=matrix(SageZZ, [[-1, 0], [0, 1]]),
                accept=self.plane_block_lift,
            )
            return special, reversing_lift

        @cached_method
        def levi_plane_action_projection_index(self) -> int:
            r"""Return the index in `GL_2(ZZ)` of the plane actions with trivial class action.

            The coset action of :meth:`_levi_plane_action_presentation` gives
            the special-linear index directly.  If no determinant-reversing
            lift exists, the projection lies in `SL_2(ZZ)` and the index in
            `GL_2(ZZ)` has one further factor of two.
            """
            special, reversing = self._levi_plane_action_presentation()
            return int(special.index()) * (1 if reversing is not None else 2)

        @cached_method
        def levi_quotient_kernel_generators(self):
            r"""Return generators of `\ker(P_I\to O(K_I))`.

            Modulo the unipotent radical, an element of this kernel is
            determined by its plane action `Q_1`, since two lifts differ by the radical
            (:meth:`plane_block_lift`).  The plane actions form exactly the
            congruence group generated by :meth:`levi_lift_generators`, so the
            kernel is generated by those lifts together with
            :meth:`unipotent_radical_generators`.
            """
            return tuple(self.unipotent_radical_generators()) + tuple(
                self.levi_lift_generators()
            )

        @cached_method
        def levi_lift_generators(self):
            r"""Return integral lifts generating the full plane projection with trivial class action.

            For every matrix returned by Sage's transitive-coset arithmetic
            subgroup presentation, :meth:`plane_block_lift` constructs the
            integral isometry with trivial quotient action.  Their plane
            actions generate the special-linear part of the projection; the
            optional determinant-reversing lift completes the other determinant
            class.  A missing lift is an error, never a generator silently
            omitted from the answer.  The two level-`|\det J|` shears are also
            included whenever they lift: they are useful elementary witnesses
            of the congruence condition, but completeness rests on the coset
            presentation, not on those or any other finite list of shears.

            The proof is the correspondence theorem applied to the quotient by
            the unipotent radical (Milne, *Group Theory*, v4.01, Theorem 1.47,
            printed p. 22, with Corollary 1.48, p. 23): arbitrary elements of
            the kernel's plane projection reduce into the certified special
            generators and, when present, the reversing lift.  It is not an
            inference from the five Enriques orbit rows.
            """
            special, reversing = self._levi_plane_action_presentation()
            lifts = []
            for generator in special.generators():
                lift = self.plane_block_lift(generator.matrix())
                if lift is None:
                    raise ArithmeticError(
                        f"the arithmetic-group generator {generator.matrix()} at {self} "
                        f"has no integral lift with trivial quotient action, contradicting "
                        f"the residue-class certificate used to construct that generator"
                    )
                lifts.append(lift)
            if reversing is not None:
                lifts.append(reversing)
            level = abs(int(self.plane_block_gram()[3].determinant()))
            for action in (
                matrix(SageZZ, [[1, level], [0, 1]]),
                matrix(SageZZ, [[1, 0], [level, 1]]),
            ):
                lift = self.plane_block_lift(action)
                if lift is not None:
                    lifts.append(lift)
            return tuple(lifts)


        @cached_method
        def _discriminant_orthogonal_action(self):
            r"""Return `(|O(q)|, action, ranking, elements)` for the permutation action on the discriminant group.

            `O(q) = O(A_L, q)` is a finite group; its elements are module
            automorphisms of the discriminant module, and a permutation of the
            group's own element enumeration is built from its generators'
            images.  The GAP group they generate is returned as ``action``, so a
            setwise stabilizer or an orbit asks the engine and not this module.
            The group order is checked against the group's own `order()`.
            """
            from sage.libs.gap.libgap import libgap

            lattice = self.ambient_lattice()
            discriminant = lattice.discriminant_group()
            orthogonal = discriminant.orthogonal_group()
            elements = tuple(discriminant.elements())
            ranking = discriminant.elements().ranking_map()
            permutations = [
                libgap.PermList([int(ranking(generator(element))) + 1 for element in elements])
                for generator in orthogonal.group_generators()
            ]
            action = libgap.Group(*permutations)
            order = orthogonal.order()
            assert int(action.Size()) == int(order), (
                f"the generators of O(q) for {lattice} generate a group of order {int(action.Size())}, "
                f"not the group's own {int(order)}"
            )
            return order, action, ranking, elements

        def stabilizer_discriminant_index(self) -> int:
            r"""Return `[O(q) : \mathrm{Stab}_{O(q)}(D(P))]` for this plane's divided class set `D(P)`.

            This is the number of points in the `O(q)`-orbit of `D(P)`: every
            `g \in \mathrm{Stab}_{O(L)}(P)` permutes the divided discriminant
            classes `[u/\mathrm{div}(u)]` of the plane's primitive directions, so
            the orbit is the index of the largest subgroup of `O(q)` that
            `\rho(G_P)` can fill.  Computed from the orbit, not read from a page;
            see :meth:`stabilizer_discriminant_image_orders` for the bound and
            the lower side.
            """
            from sage.libs.gap.libgap import libgap

            from sage_extensions.categories.isotropic_orbits import (
                _divided_discriminant_classes,
            )

            lattice = self.ambient_lattice()
            _order, action, ranking, _elements = self._discriminant_orthogonal_action()
            classes = _divided_discriminant_classes(lattice, self)
            points = sorted(
                {
                    int(ranking(classes[0])) + 1,
                    int(ranking(classes[1])) + 1,
                    int(ranking(classes[2])) + 1,
                    int(ranking(classes[3])) + 1,
                }
            )
            point_set = libgap.eval("Set([" + ",".join(str(point) for point in points) + "])")
            return int(libgap.Length(libgap.Orbit(action, point_set, libgap.eval("OnSets"))))

        @timed_stage(
            "stabilizer discriminant image orders",
            input=lambda self, *arguments, **keywords: subobject_record_name(self),
        )
        def stabilizer_discriminant_image_orders(self):
            r"""Return `(upper, lower)`: the bound on `\rho(G_P)` and the order of the returned images.

            **Upper bound.**  For a primitive isotropic plane `P` and
            `g \in \mathrm{Stab}_{O(L)}(P)`, the divided discriminant classes
            `[u/div(u)]` of `P`'s primitive directions are permuted by `\rho(g)`:
            `g u` is again isotropic and primitive with the same divisibility, so
            `\rho(g)` preserves the class set `D(P)`.  Hence

            \[ \rho(G_P) \subseteq \mathrm{Stab}_{O(q)}(D(P)), \qquad
               |\mathrm{Stab}_{O(q)}(D(P))| = |O(q)| / |O(q)\cdot D(P)| . \]

            `D(P)` is the `\mathbb{F}_2`-span of the classes of the plane's two
            generators together with their sum, and on an even lattice whose
            discriminant group has exponent two that is the whole class set
            (``_divided_discriminant_classes``); it is a two-dimensional totally
            singular subspace of `A_L`.

            **Lower bound.**  `\rho` of :meth:`parabolic_stabilizer_generators`,
            every one of which is an isometry of `L` carrying `P` onto itself,
            so the order of the subgroup they generate is a lower bound without
            any generation claim for `G_P` itself -- the point of this pair.

            Both orders are computed, not read from a page: the upper from the
            orbit of `D(P)` in the permutation action of `O(q)` on its
            discriminant group, the lower from the order of the subgroup the
            images generate in `O(q)` itself.  Neither is a count of this
            module's own search, and both are cached.
            """
            lattice = self.ambient_lattice()
            group = lattice.discriminant_group().orthogonal_group()
            order = group.order()
            orbit_size = self.stabilizer_discriminant_index()
            if int(order) % orbit_size:
                raise ValueError(
                    f"the orbit of the divided classes of {self} has {orbit_size} points, "
                    f"which does not divide |O(q)| = {int(order)}"
                )
            upper = int(order) // orbit_size
            rho = lattice.discriminant_representation()
            images = tuple(
                rho(generator) for generator in self.parabolic_stabilizer_generators()
            )
            lower = int(group.subgroup(images).order()) if images else 1
            return upper, lower

        def stabilizer_discriminant_image_is_exact(self) -> bool:
            r"""Return whether the returned generators' discriminant image is the whole of `\rho(G_P)`.

            The bound is the one :meth:`stabilizer_discriminant_image_orders`
            states: `\rho(G_P)` preserves the plane's divided discriminant
            classes, so it lies in `\mathrm{Stab}_{O(q)}(D(P))`, and the images
            of the returned generators lie in `\rho(G_P)`.  Equal orders decide
            the image *whatever* the generation of `G_P` itself, which is why
            this predicate and :meth:`is_parabolic_complete` answer different
            questions: the second is about `G_P`, the first about `\rho(G_P)`.

            `\rho(G_P)` is the object the plane-orbit call consumes, so
            a caller that needs only the image can accept an incomplete family
            of `G_P` exactly when this returns ``True``.
            """
            upper, lower = self.stabilizer_discriminant_image_orders()
            return upper == lower

        def stabilizer_discriminant_image_index(self) -> int:
            r"""Return `[\mathrm{Stab}_{O(q)}(D(P)) : \rho(\text{returned generators})]`.

            One exactly when :meth:`stabilizer_discriminant_image_is_exact`
            holds; otherwise it is the missing factor in the returned family's
            image, which a caller can name instead of guessing.
            """
            upper, lower = self.stabilizer_discriminant_image_orders()
            return upper // lower

        def levi_plane_action_index(self, trivial_on_quotient=False) -> int:
            r"""Return `[\GL(I) : \langle \text{the plane actions} \rangle]`.

            The index is decided by two facts, both checked when the method runs:

            * the principal congruence subgroup `\Gamma(2) \subseteq \GL_2(ZZ)`
              lies in the group generated by the plane actions.  `\Gamma(2)` is
              generated by the two shears `A = \begin{pmatrix}1&2\\0&1\end{pmatrix}`,
              `B = \begin{pmatrix}1&0\\2&1\end{pmatrix}` and `-1` (Sanov 1947; the
              standard statement that `\Gamma(2)/\{\pm 1\}` is free on the two
              shears), so the method exhibits each of the three as a product of at
              most four of the returned actions;
            * the reduction `\GL_2(ZZ) \to \GL_2(\FF_2)` has kernel `\Gamma(2)`
              and image of order six, which is computed here.

            Then `[\GL(I) : H] = 6 / |H \text{ in } \GL_2(\FF_2)|`, because
            `H/\Gamma(2)` is that image once `\Gamma(2) \subseteq H`.

            With ``trivial_on_quotient`` the answer is instead read from the
            ordinary transitive right-coset presentation of
            :meth:`_levi_plane_action_presentation`.  Those are the elements
            `(M, 1)` of `\GL(I) \times O(I^\perp/I)`, and their full
            congruence projection is constructed at the level on which all
            three block equations are constant.  No `\Gamma(2)` hypothesis is
            needed in this case.  When that projection is all of `\GL(I)`, the
            Levi image is the whole product `\GL(I) \times H_0` with `H_0`
            the quotient actions that lift at all (:meth:`parabolic_obstruction`).

            A plane whose family does not exhibit one of the three witnesses
            raises, naming it and the bound on the searched products: the index
            of that subgroup is not decided by this certificate, and returning a
            measured congruence level instead would be a number without a proof.
            """
            if trivial_on_quotient:
                return self.levi_plane_action_projection_index()
            return _plane_action_index(
                self.levi_plane_action_generators(), self
            )

        def levi_plane_action_generators(self, trivial_on_quotient=False):
            r"""Return the plane actions of :meth:`parabolic_stabilizer_generators`, one per distinct action.

            An isometry of `L` carrying the plane `I` onto itself acts on `I` by
            a matrix in `\GL_2(ZZ)`, read here on :meth:`plane_basis`: the
            images `g(p_j)` are written in that basis and the coordinates are
            asserted integral, so the action is computed geometrically and not
            read from a block of a matrix in an auxiliary basis.  One matrix per
            distinct action is returned, in the order the actions first occur
            among the parabolic's generators.  With ``trivial_on_quotient`` only
            the generators that act as the identity on `I^\perp/I` are read,
            which is the subset whose plane actions are the first coordinates of
            elements of the Levi image of the form `(M, 1)`.
            """
            actions = []
            seen = set()
            for generator in self.parabolic_stabilizer_generators():
                if trivial_on_quotient and not self.acts_trivially_on_isotropic_reduction(
                    generator
                ):
                    continue
                action = _plane_action_matrix(self, generator)
                key = tuple(int(entry) for entry in action.list())
                if key in seen:
                    continue
                seen.add(key)
                actions.append(action)
            return tuple(actions)

        def liftable_plane_action_classes(self):
            r"""Exact parity classes of the plane projection with trivial quotient action.

            Reduce the complete integral Levi lifts and close their finite
            image. No condition on only two of the block equations is used
            as an exact liftability criterion.
            """
            generators = tuple(
                _class_modulo_two(_plane_action_matrix(self, lift))
                for lift in self.levi_lift_generators()
            )
            generated = {(1, 0, 0, 1)}
            frontier = list(generated)
            while frontier:
                current = frontier.pop()
                for generator in generators:
                    moved = _class_product(current, generator)
                    if moved not in generated:
                        generated.add(moved)
                        frontier.append(moved)
            return frozenset(generated)

        def antipodal_root_class_pairs(self):
            r"""Return the antipodal pairs of vectors of square `-2` in `I^\perp/I`.

            `-1` lies in every congruence subgroup of `O(L)`, so no element of the
            stabilizer separates a vector of `K_I = I^\perp/I` from its negative, and the
            units a stabilizer can move are the eight antipodal pairs.

            The enumeration is exact.  With `A` the Gram matrix of `K_I` on the `K` block of
            :meth:`plane_block_basis`, `-A = L D L^t` and `x^t(-A)x = \sum_k D_k (\sum_{j
            \geq k} L_{jk} x_j)^2`, whose `k`-th summand depends on `x_k, \ldots` only, so
            the coordinates are chosen from the last to the first against the target.  The
            square root prunes only; every vector it admits is checked by the exact product
            `x^t A x == -2`.
            """
            A = self.plane_block_gram()[5]
            width = A.nrows()
            positive = matrix(QQ, -A)
            lower = matrix(QQ, width, width, lambda i, j: QQ(1) if i == j else QQ(0))
            diagonal = [QQ(0)] * width
            for column in range(width):
                diagonal[column] = positive[column, column] - sum(
                    lower[column, j] ** 2 * diagonal[j] for j in range(column)
                )
                for row in range(column + 1, width):
                    lower[row, column] = (
                        positive[row, column]
                        - sum(lower[row, j] * lower[column, j] * diagonal[j] for j in range(column))
                    ) / diagonal[column]
            found = []
            coordinates = [SageZZ(0)] * width

            def walk(position, partial):
                if partial > 2:
                    return
                if position < 0:
                    if partial == 2:
                        found.append(tuple(int(entry) for entry in coordinates))
                    return
                known = sum(lower[j, position] * coordinates[j] for j in range(position + 1, width))
                ratio = (QQ(2) - partial) / diagonal[position]
                radius = RR(ratio).sqrt() if ratio >= 0 else RR(0)
                low = int((RR(-known) - radius).floor()) - 1
                high = int((RR(-known) + radius).ceil()) + 1
                while low <= high and (known + high) ** 2 > ratio:
                    high -= 1
                while low <= high and (known + low) ** 2 > ratio:
                    low += 1
                for value in range(low, high + 1):
                    coordinates[position] = SageZZ(value)
                    walk(position - 1, partial + diagonal[position] * (known + value) ** 2)
                coordinates[position] = SageZZ(0)

            walk(width - 1, QQ(0))
            pairs = []
            seen = set()
            for entry in found:
                vector_of_entry = vector(SageZZ, entry)
                if vector_of_entry * A * vector_of_entry != -2:
                    continue
                key = min(tuple(entry), tuple(-value for value in entry))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append(key)
            return finite_ordered_set(tuple(pairs))

        def antipodal_root_class_orbits(self, generators, *, character_subgroup=None):
            r"""Return the orbits of the group generated by ``generators`` on the antipodal pairs.

            ``generators`` is any family of isometries of `L` carrying `I` onto itself, and
            the returned tuple is one tuple of pair indices per orbit, in the order of
            :meth:`antipodal_root_class_pairs`.

            An element acts on `K_I` through its class in `O(I^\perp/I)`, which is read
            here on the `K` block of :meth:`plane_block_basis`; a vector of `K_I` of square
            `-2` is a coordinate vector in that block, its image is the corresponding block
            of the ambient image, and the plane's own component is discarded -- that is
            exactly the quotient.
            """
            pairs = self.antipodal_root_class_pairs()
            if not pairs:
                raise ArithmeticError(
                    f"the quotient lattice of {self} has no vectors of square -2, so there is "
                    f"no antipodal class set for the stabilizer to act on"
                )
            index = {key: position for position, key in enumerate(pairs)}
            A = self.plane_block_gram()[5]
            width = A.nrows()
            lattice = self.ambient_lattice()
            basis = self.plane_block_basis()
            labels = tuple(lattice.module_generating_set())

            def coordinates_of(element):
                given = element.to_vector()
                return [int(given(entry)) for entry in labels]

            def ambient_matrix(generator):
                return matrix(
                    SageZZ,
                    len(labels),
                    len(labels),
                    [coordinates_of(generator(lattice.module_generator(label))) for label in labels],
                ).transpose()

            def class_coordinates(entry):
                total = lattice.zero()
                for position, coefficient in enumerate(entry):
                    if coefficient:
                        total = total + coefficient * basis[4 + position]
                return total

            permutations = []
            for generator in generators:
                standard = ambient_matrix(generator)
                moved = []
                for key in pairs:
                    image = generator(class_coordinates(key))
                    found = None
                    for sign in (1, -1):
                        target = coordinates_of(sign * image)
                        block = matrix(SageZZ, 1, 12, target) * matrix(SageZZ, [[int(entry) for entry in row] for row in self.plane_block_gram()[1]])
                        tuple_of = tuple(int(block[0, 4 + position]) for position in range(width))
                        key_of = min(tuple_of, tuple(-entry for entry in tuple_of))
                        if key_of in index:
                            found = index[key_of]
                            break
                    if found is None:
                        raise ArithmeticError(
                            f"a generator of the family at {self} does not carry the vectors of "
                            f"square -2 of I^perp/I to such vectors: it is not an isometry of "
                            f"the quotient"
                        )
                    moved.append(found)
                permutations.append(tuple(moved))
            def parity(entry):
                value = 0
                for position, coefficient in enumerate(entry):
                    if int(coefficient) % 2:
                        value |= 1 << position
                return value

            def span_of(first, second):
                return tuple(sorted({first, second, first ^ second}))

            def move_span(rows, span):
                images = []
                for entry in span:
                    image = 0
                    for position, row in enumerate(rows):
                        if (entry >> position) & 1:
                            image ^= row
                    images.append(image)
                values = sorted(set(images))
                return tuple(values) if len(values) == 3 else None

            if character_subgroup is None:
                seen = {}
                stack = []
                for start in range(len(pairs)):
                    if start in seen:
                        continue
                    seen[start] = start
                    stack.append(start)
                    while stack:
                        current = stack.pop()
                        for image in permutations:
                            moved = image[current]
                            if moved not in seen:
                                seen[moved] = start
                                stack.append(moved)
                orbits = {}
                for pair, root in seen.items():
                    orbits.setdefault(root, set()).add(pair)
                return finite_ordered_set(tuple(tuple(sorted(orbit)) for _, orbit in sorted(orbits.items())))
            # The subgroup contains the discriminant kernel and is cut out by it, so an
            # element lies in it exactly when its parity image fixes the span of the
            # divided classes of the lattice's own e' and f'.  That invariant is carried
            # along the walk instead of the element, whose orbit is infinite.
            first_class = parity([int(entry) for entry in coordinates_of(lattice.module_generator(labels[2]))])
            second_class = parity([int(entry) for entry in coordinates_of(lattice.module_generator(labels[3]))])
            base_span = span_of(first_class, second_class)

            def image_of_the_class(rows, entry):
                r"""The image of a class at ``entry``, read through the images of the basis.

                ``rows`` holds the image of each basis vector of the framing, one mask
                per position, so a class is carried by the exclusive-or of the rows its
                mask selects: the action of the element on `L/2L`, which is the action
                on `A_L` read at coordinates.
                """
                value = 0
                for position, row in enumerate(rows):
                    if (entry >> position) & 1:
                        value ^= row
                return value

            parity_rows = []
            for generator in generators:
                standard = ambient_matrix(generator)
                rows = []
                for position in range(len(labels)):
                    column = [int(standard[row, position]) for row in range(len(labels))]
                    rows.append(parity(column))
                parity_rows.append(tuple(rows))
                moved = span_of(
                    image_of_the_class(rows, first_class),
                    image_of_the_class(rows, second_class),
                )
                if (moved == base_span) != bool(generator in character_subgroup):
                    raise ArithmeticError(
                        f"the subgroup {character_subgroup} is not cut out by the divided classes "
                        f"of e' and f' at {self}: its own membership test and that invariant "
                        f"disagree on a generator of the family, so cutting by either would "
                        f"compute a different subgroup's orbits"
                    )
            spans = {base_span: 0}
            queue = [base_span]
            while queue:
                current = queue.pop()
                for rows in parity_rows:
                    moved = move_span(rows, current)
                    if moved is not None and moved not in spans:
                        spans[moved] = len(spans)
                        queue.append(moved)
            representatives = list(spans)
            seen = {}
            stack = []
            for start in range(len(pairs)):
                if (start, 0) in seen:
                    continue
                seen[(start, 0)] = start
                stack.append((start, 0))
                while stack:
                    pair, coset = stack.pop()
                    for position, image in enumerate(permutations):
                        moved = move_span(parity_rows[position], representatives[coset])
                        state = (image[pair], spans[moved])
                        if state not in seen:
                            seen[state] = start
                            stack.append(state)
            orbits = {}
            for (pair, coset), root in seen.items():
                if coset == 0:
                    orbits.setdefault(root, set()).add(pair)
            return finite_ordered_set(tuple(tuple(sorted(orbit)) for _, orbit in sorted(orbits.items())))

        def plane_action_class_image(self):
            r"""Return the subgroup modulo `2` generated by the plane actions of the family.

            These are the plane actions of :meth:`parabolic_stabilizer_generators` read on
            :meth:`plane_basis`, one per distinct action, reduced modulo `2`.  The family's
            image is the stabilizer's image exactly when this set contains
            :meth:`liftable_plane_action_classes` and the actions themselves generate
            `\Gamma(2)` -- the certificate :meth:`levi_plane_action_index` computes.  The
            second half is not implied by the first: `\Gamma(2)` has index two in
            `\Gamma^1(2)`, so a family meeting every liftable class can still miss
            `\Gamma(2)`, and omission was the defect of reading the index in `\GL(I)`
            instead.
            """
            generators = tuple(
                _class_modulo_two(action)
                for action in self.levi_plane_action_generators(
                    trivial_on_quotient=True
                )
            )
            identity = (1, 0, 0, 1)
            generated = {identity}
            frontier = [identity]
            while frontier:
                class_ = frontier.pop()
                for generator in generators:
                    product = _class_product(class_, generator)
                    if product not in generated:
                        generated.add(product)
                        frontier.append(product)
            return frozenset(generated)

        @cached_method
        def levi_quotient_image_index(self, trivial_on_plane=False) -> int:
            r"""Return `[O(I^\perp/I) : H_0]`, the index of the returned generators' quotient image.

            `H_0` is the subgroup of `O(I^\perp/I)` generated by the images of
            :meth:`parabolic_stabilizer_generators` under the Levi quotient action
            :meth:`~sage_extensions.categories.lattices.IsotropicReductions.ParentMethods.levi_action`.
            Those generators are isometries with `g(I) = I`, so their images lie in the image
            `M` of the whole setwise stabilizer, and `M` lies in `O(I^\perp/I)` by definition:

            .. math:: H_0 \subseteq M \subseteq O(I^\perp/I).

            Without a plane-action restriction, the complete family
            contains lifts of generators of M by
            :meth:`levi_quotient_image_lifts`, so the index is exact,
            including when M is proper.

            With ``trivial_on_plane`` use only the returned generators
            fixing I pointwise. Their quotient image is a subgroup of
            the actual pointwise stabilizer image; index one proves
            surjectivity, but a larger index need not give the exact
            pointwise image. This diagnostic is not a completeness
            condition for the full parabolic.

            For a maximal isotropic plane the quotient is definite or
            zero; its orthogonal group is finite.
            """
            reduction = self.isotropic_reduction()
            orthogonal = reduction.quotient_lattice().Aut()
            levi = reduction.levi_action()
            images = tuple(
                levi(generator)
                for generator in self.parabolic_stabilizer_generators()
                if not trivial_on_plane or self._fixes_isotropic_pointwise(generator)
            )
            generated = orthogonal.subgroup(images)
            total = int(orthogonal.cardinality())
            part = int(generated.cardinality())
            if total % part != 0:
                raise ArithmeticError(
                    f"the image of the generators of the parabolic at {self} has order "
                    f"{part}, which does not divide the order {total} of "
                    f"O(I^perp/I) for I = {self}: a subgroup's order divides its group's "
                    f"(Lagrange), so one of the two orders is wrong"
                )
            return total // part

        @cached_method
        def parabolic_completeness_decision(self):
            r"""Construct and certify the complete integral maximal-plane family.

            The block radical generators lift a basis of the full translation
            lattice and a generator of its central kernel. The complete
            trivial-quotient plane lifts generate the remaining kernel of
            the quotient action. Finally levi_quotient_image_lifts computes
            lifts of generators of the actual image, not necessarily O(K).
            Success in these three constructions proves generation by the
            subgroup correspondence theorem. No equality of an exhibited
            pointwise image with O(K) is required.
            """
            if int(self.module_rank()) != 2:
                return False, "the complete block construction is for a primitive plane"
            quotient = self.isotropic_reduction().quotient_lattice()
            if int(quotient.module_rank()) and quotient.is_definite() is not True:
                return False, "the quotient of this plane is not definite"
            self.parabolic_stabilizer_generators()
            return True, None

        def is_parabolic_complete(self) -> bool:
            r"""Whether the complete integral maximal-plane construction applies."""
            return self.parabolic_completeness_decision()[0]

        def parabolic_obstruction(self) -> str | None:
            r"""Return why the parabolic's generators are not established to be all of it.

            ``None`` exactly when :meth:`is_parabolic_complete` is ``True``; otherwise the
            reason :meth:`parabolic_completeness_decision` gives.
            """
            return self.parabolic_completeness_decision()[1]

        @cached_method
        def parabolic_stabilizer_generators(self):
            r"""Complete generators of the integral maximal-plane stabilizer.

            In the parabolic map to O(P^perp/P), the kernel is generated by
            the exact radical block generators and the full integral plane
            projection with trivial quotient action. The image is generated
            by the quotient actions lifted by levi_quotient_image_lifts.
            Thus the three complete families generate the actual integral
            parabolic by the correspondence theorem, without assuming a
            splitting or surjectivity onto a direct product. Include the
            existing transvection witnesses used by the discriminant-image
            calculations; no generation claim about these witnesses is needed.
            """
            return (
                self.parabolic_transvection_generators()
                + self.half_vector_transvection_generators()
                + self.unipotent_radical_block_generators()
                + self.levi_lift_generators()
                + self.levi_quotient_image_lifts()
            )


__all__ = ["PrimitiveIsotropicSubobjects", "right_coset_action"]

# ---------------------------------------------------------------------------
# The parabolic subgroup of an isotropic plane, by its published block form.
# ---------------------------------------------------------------------------


def _class_product(first, second):
    r"""Return the class modulo `2` of the product of two `2 x 2` matrices given by their classes.

    The four entries of a class are stored in row order, so the product
    `(a b; c d) (e f; g h) = (ae + bg, af + bh; ce + dg, cf + dh)` is read off the two
    tuples directly, modulo `2`.
    """
    a, b, c, d = first
    e, f, g, h = second
    return (
        (a * e + b * g) % 2,
        (a * f + b * h) % 2,
        (c * e + d * g) % 2,
        (c * f + d * h) % 2,
    )


def _class_modulo_two(action):
    r"""Return the class modulo `2` of a `2 x 2` integral matrix, as four residues in row order.

    `\\Gamma(2) = \\ker(\\GL_2(\\ZZ) \\to \\GL_2(\\FF_2))`, so two plane actions generate the
    same subgroup of `\\GL_2(\\ZZ)` modulo `\\Gamma(2)` exactly when their classes here
    agree.
    """
    return tuple(int(action[row, column]) % 2 for row in range(2) for column in range(2))


def _rank_completed_rows(rows, candidates, count):
    r"""Return up to ``count`` of ``candidates`` that raise the rank of ``rows``, in order.

    This is the cheap completion: the standard basis rows are taken in order while
    they raise the rank.  It is a completion only when the rows it returns span a
    *saturated* extension, which is not automatic -- at a `T_Co` plane the rows so
    chosen span a sublattice of index `2` -- so its caller checks that the rows
    assembled from it are a `ZZ`-basis and falls back on
    :func:`_completed_basis` when they are not.
    """
    current = matrix(SageZZ, tuple(rows))
    kept = []
    for row in candidates:
        augmented = matrix(SageZZ, tuple(current.rows()) + (row,))
        if augmented.rank() > current.rank():
            current = augmented
            kept.append(row)
        if len(kept) == count:
            break
    return kept


def _completed_basis(arrow, basis):
    r"""Return ``basis``, a `ZZ`-basis of ``arrow``'s image, extended to one of its codomain.

    ``arrow`` is an inclusion of lattices whose quotient is torsion-free, and
    ``basis`` a `ZZ`-basis of the image.  A finitely generated torsion-free
    module over the principal ideal domain `ZZ` is free
    (:meth:`sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules.ParentMethods.finite_free_trivialization`,
    which returns the isomorphism with the free module on the quotient's own
    generators), so lifting those basis points back along the cokernel
    projection gives vectors of the codomain; they complete ``basis`` to a
    `ZZ`-basis of it.  A quotient with torsion means the included lattice is not
    saturated, and then no basis completes it -- that is refused, not guessed.
    """
    quotient = arrow.cokernel()
    if quotient.is_torsion_free() is not True:
        raise ArithmeticError(
            f"the quotient {quotient} of the inclusion {arrow} has torsion: the included "
            f"lattice is not saturated in the ambient one, and no basis of the ambient one "
            f"contains its basis"
        )
    trivialization = quotient.finite_free_trivialization()
    free = trivialization.codomain()
    projection = arrow.cokernel_projection()
    return tuple(basis) + tuple(
        projection.preimage(trivialization.inverse()(point))
        for point in free.module_generators()
    )


def _kernel_basis_rows(integer_matrix):
    r"""Return the integer kernel of ``integer_matrix`` as a tuple of coordinate rows.

    The kernel of an integer matrix is a saturated sublattice of ``ZZ^n``, so the
    rows returned span its integer points and not only its rational span.  Sage's
    ``kernel()`` is the left kernel, so the transpose is what carries the rows
    ``x`` with ``A x = 0``.
    """
    kernel = integer_matrix.transpose().kernel()
    return tuple(tuple(int(entry) for entry in row) for row in kernel.basis_matrix().rows())
