"""Primitive-vector and discriminant-action invariants of integral lattices.

This module owns the algorithms migrated from the former
``src/latticedb/sage_genus.py`` implementation of dzackgarza/lattice-database.  The
orthogonal group itself is never recomputed here: definite orbit calculations
consume ``L.orthogonal_group().group_generators()``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sized

from sage.groups.fqf_orthogonal import FqfIsometry
from sage.libs.gap.libgap import libgap
from sage.matrix.constructor import column_matrix, matrix
from sage.modules.free_module_element import vector
from sage.matrix.matrix_integer_dense import Matrix_integer_dense
from sage.matrix.matrix_rational_dense import Matrix_rational_dense
from sage.modules.free_quadratic_module_integer_symmetric import IntegralLattice
from sage.modules.torsion_quadratic_module import TorsionQuadraticModuleElement
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ

ORBIT_NORM_BOUND = 4


def _gram_matrix(lattice) -> Matrix_integer_dense:
    rank = int(lattice.module_rank())
    gram = lattice.gram_tensor()
    return matrix(
        ZZ,
        [[int(gram[i, j]) for j in range(rank)] for i in range(rank)],
    )


def _element_coordinates(element) -> tuple[int, ...]:
    lattice = element.parent()
    labels = tuple(lattice.module_generating_set())
    coordinates = lattice.framing_morphism().lift(element)
    return tuple(int(coordinates(label)) for label in labels)


def _isometry_matrix(isometry) -> Matrix_integer_dense:
    domain = isometry.domain()
    codomain = isometry.codomain()
    source_labels = tuple(domain.module_generating_set())
    target_labels = tuple(codomain.module_generating_set())
    rows = [
        [
            int(
                codomain.framing_morphism().lift(
                    isometry(domain.module_generator(source_label))
                )(target_label)
            )
            for source_label in source_labels
        ]
        for target_label in target_labels
    ]
    return matrix(ZZ, rows)


def _orthogonal_generator_matrices(lattice) -> list[Matrix_integer_dense]:
    return [
        _isometry_matrix(generator)
        for generator in lattice.orthogonal_group().group_generators()
    ]


def _discriminant_actions(
    gram: Matrix_integer_dense, generators: list[Matrix_integer_dense]
) -> tuple[list[int], list[Matrix_integer_dense]]:
    smith, left, _ = gram.smith_form()
    kept = [
        index
        for index in range(gram.nrows())
        if abs(smith[index, index]) > 1
    ]
    factors = [abs(int(smith[index, index])) for index in kept]
    left_inverse = left.inverse_of_unit()
    gram_inverse = gram.inverse()
    actions = []
    for generator in generators:
        # The Gram matrix is the correlation L -> L^dual in the dual basis, and
        # an isometry g commutes with it: g acts on L^dual by gram g gram^-1.
        # The Smith factor ``left`` changes the dual basis to the one in which
        # L^dual / L is a product of cyclic groups.
        dual_action = (gram * generator * gram_inverse).change_ring(ZZ)
        action = left * dual_action * left_inverse
        actions.append(action.matrix_from_rows_and_columns(kept, kept))
    return factors, actions


def _discriminant_points(
    factors: list[int], actions: list[Matrix_integer_dense]
) -> list[tuple[int, ...]]:
    r"""Return the orbit of the Smith generators of ``A_L`` under the actions.

    The Smith generators come first, in order.  An element of ``A_L`` is a
    column of residues modulo ``factors``, and each action moves it by left
    multiplication.
    """
    order = len(factors)
    found = {
        tuple(int(i == j) % factors[i] for i in range(order)): None for j in range(order)
    }
    frontier = list(found)
    while frontier:
        element = vector(ZZ, frontier.pop())
        for action in actions:
            image = tuple(int(entry) % factor for entry, factor in zip(action * element, factors, strict=True))
            if image not in found:
                found[image] = None
                frontier.append(image)
    return list(found)


def primitive_orbit_series(lattice, bound: int = ORBIT_NORM_BOUND):
    r"""Count the orbits of ``O``, ``SO``, ``Otilde`` and ``SOtilde`` on primitive vectors by norm.

    ``O(L)`` acts on the finite set ``X ⊔ D ⊔ {+1, -1}``: the vectors of
    norm at most ``bound``, the orbit ``D ⊆ A_L`` of the Smith generators, and
    the sign of the determinant.  Let ``P`` be the image permutation group.
    ``SO`` is the image of the stabilizer of ``+1``, ``Otilde`` the pointwise
    stabilizer of the Smith generators, and ``SOtilde`` both; GAP computes the
    stabilizers by Schreier-Sims and the orbits on ``X`` directly.  An isometry
    preserves primitivity, so one vector of each ``O``-orbit decides it for the
    whole orbit.
    """
    definiteness = lattice.definiteness()
    match definiteness:
        case "positive_definite":
            sign = 1
        case "negative_definite":
            sign = -1
        case _:
            raise ValueError(f"primitive bounded orbit series requires a definite lattice, not {lattice}")
    gram = _gram_matrix(lattice)
    generators = _orthogonal_generator_matrices(lattice)
    vectors = []
    norms = []
    for absolute_norm in range(1, int(bound) + 1):
        for element in lattice.vectors_of_square(sign * absolute_norm):
            vectors.append(element)
            norms.append(absolute_norm)
    coordinates = [_element_coordinates(element) for element in vectors]
    vector_points = {point: index for index, point in enumerate(coordinates)}
    factors, actions = _discriminant_actions(gram, generators)
    discriminant = _discriminant_points(factors, actions)
    discriminant_points = {point: len(coordinates) + index for index, point in enumerate(discriminant)}
    positive = len(coordinates) + len(discriminant)
    columns = (
        column_matrix(ZZ, coordinates)
        if coordinates
        else matrix(ZZ, int(lattice.module_rank()), 0)
    )
    permutations = []
    for generator, action in zip(generators, actions, strict=True):
        images = [vector_points[tuple(column)] for column in (generator * columns).columns()]
        images += [
            discriminant_points[
                tuple(int(entry) % factor for entry, factor in zip(action * vector(ZZ, point), factors, strict=True))
            ]
            for point in discriminant
        ]
        images += [positive, positive + 1] if generator.det() == 1 else [positive + 1, positive]
        permutations.append(libgap.PermList([image + 1 for image in images]))
    group = libgap.GroupByGenerators(permutations, libgap.eval("()"))
    primitive = [
        point
        for orbit in libgap.Orbits(group, list(range(1, len(coordinates) + 1))).sage()
        if vectors[orbit[0] - 1].is_primitive()
        for point in orbit
    ]
    smith_generators = [len(coordinates) + index + 1 for index in range(len(factors))]
    subgroups = {
        "O": group,
        "SO": libgap.Stabilizer(group, positive + 1),
        "Otilde": libgap.Stabilizer(group, smith_generators, libgap.OnTuples),
        "SOtilde": libgap.Stabilizer(group, [positive + 1, *smith_generators], libgap.OnTuples),
    }
    counts = {
        name: [
            sum(1 for orbit in orbits if norms[orbit[0] - 1] == norm)
            for norm in range(1, int(bound) + 1)
        ]
        for name, orbits in (
            (name, libgap.Orbits(subgroup, primitive).sage()) for name, subgroup in subgroups.items()
        )
    }
    zeros = [0] * int(bound)
    plus = (
        {"O+": "SO", "SO+": "SO", "Otilde+": "SOtilde", "SOtilde+": "SOtilde"}
        if sign > 0
        else {"O+": "O", "SO+": "SO", "Otilde+": "Otilde", "SOtilde+": "SOtilde"}
    )
    counts |= {group: counts[source] for group, source in plus.items()}
    return {
        group: {
            "constant": 0,
            "z": values if sign > 0 else zeros,
            "w": zeros if sign > 0 else values,
        }
        for group, values in counts.items()
    }


def _orbits(
    elements: list[TorsionQuadraticModuleElement],
    generators: tuple[FqfIsometry, ...],
) -> list[list[TorsionQuadraticModuleElement]]:
    found: list[list[TorsionQuadraticModuleElement]] = []
    seen: set[TorsionQuadraticModuleElement] = set()
    for start in elements:
        if start in seen:
            continue
        orbit = [start]
        seen.add(start)
        for element in orbit:
            for generator in generators:
                image = generator(element)
                if image not in seen:
                    seen.add(image)
                    orbit.append(image)
        found.append(orbit)
    return found


def discriminant_orbit_series(lattice, bound: int = ORBIT_NORM_BOUND):
    gram = _gram_matrix(lattice)
    backend = IntegralLattice(gram)
    if not backend.is_even():
        raise ValueError(f"discriminant orbit series requires an even lattice, not {lattice}")
    discriminant = backend.discriminant_group()
    elements = list(discriminant)
    classes = {
        norm: [element for element in elements if element.q() == QQ(norm) / element.order() ** 2]
        for norm in range(-int(bound), int(bound) + 1)
    }
    generators = discriminant.orthogonal_group().gens()
    orbits = {norm: _orbits(values, generators) for norm, values in classes.items()}
    series: dict[str, Mapping[int, Sized]] = {
        "Otilde": classes, "SOtilde": classes, "Otilde+": classes, "SOtilde+": classes,
        "O": orbits, "SO": orbits, "O+": orbits, "SO+": orbits,
    }
    return {
        group: {
            "constant": len(counted[0]),
            "z": [len(counted[n]) for n in range(1, int(bound) + 1)],
            "w": [len(counted[-n]) for n in range(1, int(bound) + 1)],
        }
        for group, counted in series.items()
    }


def discriminant_sequence_data(lattice):
    gram = _gram_matrix(lattice)
    lattice_generators = _orthogonal_generator_matrices(lattice)
    module = IntegralLattice(gram).discriminant_group()
    factors = [int(order) for order in module.invariants()]
    group = module.orthogonal_group()
    basis = module.gens()

    def rows(action: Matrix_integer_dense) -> list[list[int]]:
        # Sage's FQF automorphism matrix lists the image of generator i as
        # row i, so entry (i, j) is a coordinate in the cyclic factor j.
        return [
            [int(action[i, j]) % factors[j] for j in range(len(factors))]
            for i in range(len(factors))
        ]

    def rational_rows(value: Matrix_rational_dense) -> list[list[str]]:
        return [[str(entry) for entry in row] for row in value.rows()]

    images = [
        group(module.hom([module(generator * element.lift()) for element in basis]))
        for generator in lattice_generators
    ]
    image = group.subgroup(images)
    image_elements = list(image)
    group_elements = list(group)
    identity = group.one()
    remaining = set(group_elements)
    representatives = [identity]
    remaining.difference_update(identity * element for element in image_elements)
    while remaining:
        representative = min(remaining, key=lambda element: rows(element.matrix()))
        representatives.append(representative)
        remaining.difference_update(representative * element for element in image_elements)
    normal = all(
        conjugator * element * ~conjugator in image
        for conjugator in group.gens()
        for element in images
    )
    coset_index = {
        frozenset(representative * element for element in image_elements): index
        for index, representative in enumerate(representatives)
    }

    def coset_of(element: FqfIsometry) -> int:
        return coset_index[frozenset(element * member for member in image_elements)]

    orthogonal_order = int(lattice.orthogonal_group().cardinality())
    image_order = int(image.order())
    return {
        "discriminant_factors": factors,
        "discriminant_basis_lifts": [[str(coordinate) for coordinate in element.lift()] for element in basis],
        "discriminant_quadratic_gram": rational_rows(module.gram_matrix_quadratic()),
        "discriminant_group_order": int(group.order()),
        "discriminant_generators": [rows(generator.matrix()) for generator in group.gens()],
        "image_generators": [rows(element.matrix()) for element in images],
        "image_order": image_order,
        "kernel_order": orthogonal_order // image_order,
        "coset_representatives": [rows(element.matrix()) for element in representatives],
        "mm_trivial": len(representatives) == 1,
        "image_normal": normal,
        "quotient_generator_cosets": [coset_of(generator) for generator in group.gens()] if normal else None,
        "quotient_multiplication": [[coset_of(left * right) for right in representatives] for left in representatives] if normal else None,
    }
