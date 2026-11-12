r"""Sterk cusp and root configurations for degree-two Enriques moduli."""

from functools import cache

from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.rational_field import QQ

from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.catalogue import NamedLattices
from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.tensors.tensor import _engine_component_matrix


def _named_generators(lattice):
    return {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}


def _coordinates(lattice, vector):
    r"""Return the coordinates of ``vector`` in the selected basis of ``lattice``, as integers."""
    given = vector.to_vector()
    return [int(given(label)) for label in lattice.module_generating_set()]


def _family_gram(lattice, vectors):
    r"""Return the pairwise pairing matrix of ``vectors`` in one exact contraction.

    In the selected basis the family's Gram is ``C G C^T``, so the whole family is checked by one
    matrix product rather than one pairing at a time.
    """
    coordinates = sage_matrix(QQ, [_coordinates(lattice, vector) for vector in vectors])
    gram = _engine_component_matrix(lattice.gram_tensor()).change_ring(QQ)
    return coordinates * gram * coordinates.transpose()


def _cusp_class_lift(line, reduction, class_vector):
    r"""Return a vector of the ambient lattice, in ``v^\perp``, whose class in the reduction is ``class_vector``.

    The reduction's coordinate frame is its retained section of
    `v^\perp \to v^\perp/\mathbf Z v`, so a class is lifted by its coordinates there and the lift is
    checked against the projection.  This is the same section
    :meth:`sage_extensions.categories.isotropic_orbits.IsotropicVectorReductionImage.class_lift`
    takes, read here from the lattice-level owners so that a printed root can be read at a cusp
    without a group.
    """
    frame = reduction.coordinate_frame()
    given = class_vector.to_vector()
    lift = None
    for label in reduction.module_generating_set():
        coefficient = int(given(label))
        if coefficient:
            piece = coefficient * frame[label]
            lift = piece if lift is None else lift + piece
    assert lift is not None, (
        f"the class {class_vector!r} of {reduction!r} is the zero class, which is no printed root"
    )
    assert reduction.projection()(lift) == class_vector, (
        f"the coordinate frame of {reduction!r} does not lift the class {class_vector!r}"
    )
    return line.isotropic_perpendicular().inclusion()(lift)


def _transported_roots(printed, span, identification, reduction, line):
    r"""Carry the printed roots of ``span`` through ``identification`` into classes of ``reduction``.

    ``identification`` is an isometry or an isometric embedding of ``span`` into the boundary lattice;
    its matrix is read off the images of ``span``'s generators, each printed root is written in that
    basis by one exact solve, and the product is the class of the root in the boundary lattice.  The
    class is then lifted back into the ambient lattice by :func:`_cusp_class_lift`.
    """
    ambient = span.inclusion().codomain()
    labels_span = tuple(span.module_generating_set())
    labels_reduction = tuple(reduction.module_generating_set())
    columns = []
    for label in labels_span:
        given = identification(span.module_generator(label)).to_vector()
        columns.append([int(given(target)) for target in labels_reduction])
    transport = sage_matrix(
        QQ,
        [
            [column[row] for column in columns]
            for row in range(len(labels_reduction))
        ],
    )
    span_columns = [
        _coordinates(ambient, span.inclusion()(span.module_generator(label)))
        for label in labels_span
    ]
    system = sage_matrix(
        QQ,
        [
            [column[row] for column in span_columns]
            for row in range(int(ambient.module_rank()))
        ],
    )
    ring = reduction.base_ring()
    roots = []
    for root in printed:
        solution = system.solve_right(
            sage_matrix(QQ, int(ambient.module_rank()), 1, _coordinates(ambient, root))
        )
        assert all(entry.denominator() == 1 for entry in solution.list()), (
            f"the printed root {root!r} is not in the span of the printed family: its "
            f"coordinates there are {solution.list()}"
        )
        transported = [
            sum(
                int(transport[row, column]) * int(solution[column, 0])
                for column in range(len(labels_span))
            )
            for row in range(len(labels_reduction))
        ]
        class_vector = reduction.linear_combination(
            {
                label: ring(value)
                for label, value in zip(labels_reduction, transported)
                if value
            }
        )
        roots.append(_cusp_class_lift(line, reduction, class_vector))
    return tuple(roots), transport



def _correlation_preimage_from_gram_inverse(lattice, dual_element, inverse_gram):
    r"""Compute the exact integral preimage under ``v |-> b(v,-)``.

    In the selected lattice and metric-dual bases, the correlation morphism
    has matrix ``G``. Thus the unique preimage of dual coordinates ``y`` is
    ``G^(-1)y``. The caller supplies the exact rational inverse once for the
    root family; integrality of every resulting coordinate is precisely the
    image-membership condition for this finite-rank free lattice map.
    """
    labels = tuple(lattice.module_generating_set())
    coordinates = tuple(dual_element.to_vector())
    preimage = inverse_gram * sage_matrix(
        QQ, len(coordinates), 1, [QQ(int(coefficient)) for coefficient in coordinates]
    )
    coefficients = tuple(preimage[i, 0] for i in range(len(labels)))
    if any(coefficient.denominator() != 1 for coefficient in coefficients):
        raise ValueError(
            f"the dual vector {dual_element!r} is not in the image of the lattice correlation map"
        )
    return lattice.linear_combination(
        {
            label: lattice.base_ring()(int(coefficient))
            for label, coefficient in zip(labels, coefficients, strict=True)
            if coefficient
        }
    )


_STERK_DIAGRAM_LAYOUTS = {
    "Sterk_1": {
        0: (0, 0),
        1: (4, 0),
        2: (8, 0),
        3: (8, -4),
        4: (8, -8),
        5: (4, -8),
        6: (0, -8),
        7: (0, -4),
        8: (2, -6),
        9: (QQ(13) / 4, -QQ(19) / 4),
        10: (QQ(9) / 2, -QQ(7) / 2),
        11: (6, -2),
    },
    "Sterk_2": {
        0: (0, 0),
        1: (-4, 0),
        2: (-8, 0),
        3: (-7, 4),
        4: (-6, 8),
        5: (-5, 12),
        6: (-4, 16),
        7: (-3, 20),
        8: (-2, 24),
        9: (-2, 6),
    },
    "Sterk_3": {
        0: (0, -4),
        1: (0, 4),
        2: (0, 8),
        3: (0, 12),
        4: (0, 16),
        5: (4, 16),
        6: (8, 16),
        7: (12, 16),
        8: (20, 16),
        9: (4, 12),
        10: (6, 2),
        11: (14, 10),
    },
    "Sterk_4": {
        0: (0, 0),
        1: (0, 4),
        2: (0, 8),
        3: (4, 8),
        4: (8, 8),
        5: (12, 8),
        6: (16, 8),
        7: (16, 4),
        8: (16, 0),
        9: (4, 4),
        10: (12, 4),
    },
    "Sterk_5": {
        0: (0, 0),
        1: (10, 0),
        2: (20, 0),
        3: (20, -10),
        4: (20, -20),
        5: (10, -20),
        6: (0, -20),
        7: (0, -10),
        8: (4, -4),
        9: (16, -4),
        10: (16, -16),
        11: (4, -16),
        12: (8, -8),
        13: (8, -12),
    },
}


class Sterk:
    @staticmethod
    @cache
    def _roots_18_2_0_cached():
        TdP = NamedLattices.TdP
        b = _named_generators(TdP)
        dual = tuple(TdP.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8, w1t, w2t, w3t, w4t, w5t, w6t, w7t, w8t = dual
        c = TdP.correlation()
        inverse_gram = _engine_component_matrix(TdP.gram_tensor()).change_ring(QQ).inverse()
        vectors = {
            "v1": b["b8"],
            "v2": _correlation_preimage_from_gram_inverse(TdP, c(b["ep"] + b["fp"]) + w1 + w8t, inverse_gram),
            "v3": b["a1"],
            "v4": b["a3"],
            "v5": b["a4"],
            "v6": b["a5"],
            "v7": b["a6"],
            "v8": b["a7"],
            "v9": b["a8"],
            "v10": _correlation_preimage_from_gram_inverse(TdP, c(b["ep"] + b["fp"]) + w8 + w1t, inverse_gram),
            "v11": b["b1"],
            "v12": b["b3"],
            "v13": b["b4"],
            "v14": b["b5"],
            "v15": b["b6"],
            "v16": b["b7"],
            "v17": _correlation_preimage_from_gram_inverse(TdP, c(b["ep"]) + w8t, inverse_gram),
            "v18": b["a2"],
            "v19": _correlation_preimage_from_gram_inverse(TdP, c(b["ep"]) + w8, inverse_gram),
            "v20": b["b2"],
            "v21": b["fp"] - b["ep"],
            "v22": _correlation_preimage_from_gram_inverse(TdP, c(5 * b["ep"] + 3 * b["fp"]) + 2 * w2 + 2 * w2t, inverse_gram),
        }
        assert len(vectors) == 22
        return vectors

    @staticmethod
    def roots_18_2_0():
        r"""Return the verified 22-root configuration in signature ``(18,2,0)``."""
        return dict(Sterk._roots_18_2_0_cached())

    @staticmethod
    @cache
    def _roots_18_0_0_cached():
        TdP = NamedLattices.TdP
        b = _named_generators(TdP)
        dual = tuple(TdP.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8, w1t, w2t, w3t, w4t, w5t, w6t, w7t, w8t = dual
        c = TdP.correlation()
        inverse_gram = _engine_component_matrix(TdP.gram_tensor()).change_ring(QQ).inverse()
        vectors = {
            "w1": b["a1"],
            "w2": b["a3"],
            "w3": b["a4"],
            "w4": b["a5"],
            "w5": b["a6"],
            "w6": b["a7"],
            "w7": b["a8"],
            "w8": _correlation_preimage_from_gram_inverse(TdP, c(b["e"]) + w8, inverse_gram),
            "w9": b["f"] - b["e"],
            "w10": _correlation_preimage_from_gram_inverse(TdP, c(b["e"]) + w8t, inverse_gram),
            "w11": b["b8"],
            "w12": b["b7"],
            "w13": b["b6"],
            "w14": b["b5"],
            "w15": b["b4"],
            "w16": b["b3"],
            "w17": b["b1"],
            "w18": b["a2"],
            "w19": b["b2"],
        }
        assert len(vectors) == 19
        return vectors

    @staticmethod
    def roots_18_0_0():
        r"""Return the verified 19-root configuration in signature ``(18,0,0)``."""
        return dict(Sterk._roots_18_0_0_cached())

    @staticmethod
    @cache
    def _sterk_roots_cached():
        v = Sterk.roots_18_2_0()
        w = Sterk.roots_18_0_0()

        def reflect(x):
            half = x.parent().base_ring()(v["v22"].b(x) / 2)
            return x + half * v["v22"]

        def orbit_sum(x):
            return x + reflect(x)

        configurations = {
            "Sterk_1": (
                v["v3"] + v["v11"],
                v["v4"] + v["v12"],
                v["v5"] + v["v13"],
                v["v6"] + v["v14"],
                v["v7"] + v["v15"],
                v["v8"] + v["v16"],
                v["v9"] + v["v1"],
                v["v10"] + v["v2"],
                v["v17"] + v["v19"],
                v["v21"],
                v["v22"],
                v["v18"] + v["v20"],
            ),
            "Sterk_2": (
                w["w1"] + w["w17"],
                w["w2"] + w["w16"],
                w["w3"] + w["w15"],
                w["w4"] + w["w14"],
                w["w5"] + w["w13"],
                w["w6"] + w["w12"],
                w["w7"] + w["w11"],
                w["w8"] + w["w10"],
                w["w9"],
                w["w18"] + w["w19"],
            ),
            "Sterk_3": (
                v["v13"],
                v["v14"] + v["v12"],
                v["v15"] + v["v11"],
                v["v16"] + v["v10"],
                v["v1"] + v["v9"],
                v["v2"] + v["v8"],
                v["v3"] + v["v7"],
                v["v4"] + v["v6"],
                v["v5"],
                v["v17"] + v["v19"],
                orbit_sum(v["v20"]),
                orbit_sum(v["v18"]),
            ),
            "Sterk_4": (
                v["v15"],
                v["v16"] + v["v14"],
                v["v1"] + v["v13"],
                v["v2"] + v["v12"],
                v["v3"] + v["v11"],
                v["v4"] + v["v10"],
                v["v5"] + v["v9"],
                v["v6"] + v["v8"],
                v["v7"],
                v["v17"] + v["v20"],
                v["v18"] + v["v19"],
            ),
            "Sterk_5": (
                v["v16"] + 2 * v["v1"] + v["v2"],
                v["v2"] + 2 * v["v3"] + v["v4"],
                v["v4"] + 2 * v["v5"] + v["v6"],
                v["v6"] + 2 * v["v7"] + v["v8"],
                v["v8"] + 2 * v["v9"] + v["v10"],
                v["v10"] + 2 * v["v11"] + v["v12"],
                v["v12"] + 2 * v["v13"] + v["v14"],
                v["v14"] + 2 * v["v15"] + v["v16"],
                v["v17"],
                v["v18"],
                v["v19"],
                v["v20"],
                v["v21"],
                v["v22"],
            ),
        }
        configurations = {
            name: finite_ordered_set(roots) for name, roots in configurations.items()
        }
        # Verify all root squares in one exact Gram contraction. Calling
        # ``root.q()`` separately for each of the sixty configured roots
        # repeatedly rebuilds the selected tensor-index machinery. In the
        # chosen lattice basis, the entire root Gram is C G C^T, so its
        # diagonal gives precisely the same individual norms in one batch.
        lattice = NamedLattices.TdP
        labels = tuple(lattice.module_generating_set())
        roots_by_configuration = tuple(
            (name, root)
            for name, roots in configurations.items()
            for root in roots
        )
        rooted_vectors = tuple(
            (name, root, root.to_vector()) for name, root in roots_by_configuration
        )
        coordinate_vectors = tuple(
            vector.parent()._selected_module_coefficients(vector)
            for _name, _root, vector in rooted_vectors
        )
        coordinate_matrix = sage_matrix(
            QQ,
            [
                [QQ(int(vector.get(label, 0))) for label in labels]
                for vector in coordinate_vectors
            ],
        )
        gram = _engine_component_matrix(lattice.gram_tensor()).change_ring(QQ)
        root_gram = coordinate_matrix * gram * coordinate_matrix.transpose()
        for position, (name, root, _vector) in enumerate(rooted_vectors):
            square = root_gram[position, position]
            assert square in (-2, -4), (
                f"the configuration {name} contains {root}, which is not a root: "
                f"its square is {square}, not -2 or -4"
            )
        assert reflect(reflect(v["v20"])) == v["v20"]
        assert reflect(reflect(v["v18"])) == v["v18"]
        assert orbit_sum(v["v20"]) == v["v22"] + 2 * v["v20"]
        assert orbit_sum(v["v18"]) == v["v22"] + 2 * v["v18"]
        return configurations

    @staticmethod
    def sterk_roots():
        r"""Return the five verified root configurations in documented order.

        Root construction includes metric-dual lifts and exact square checks.
        Cache that data so diagram construction does not repeat the work after
        a caller has already requested the configurations. Return a fresh
        dictionary so callers cannot mutate the cached mapping.
        """
        return dict(Sterk._sterk_roots_cached())

    @staticmethod
    def selected_isotropic_vectors():
        TEn = NamedLattices.TEn
        b = _named_generators(TEn)
        dual = tuple(TEn.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8 = dual
        c = TEn.correlation()
        omega = 2 * w8
        alpha = 2 * w1
        vectors = {
            "Sterk_1": b["e"],
            "Sterk_2": b["ep"],
            "Sterk_3": c.lift(c(b["ep"] + b["fp"]) + omega),
            "Sterk_4": c.lift(c(b["ep"] + 2 * b["fp"]) + alpha),
            "Sterk_5": c.lift(c(2 * b["e"] + 2 * b["f"]) + alpha),
        }
        assert all(vector.q() == 0 for vector in vectors.values())
        return vectors

    @staticmethod
    def sterk5_in_U_E8_2():
        r"""Return Sterk 5's fourteen roots in ``U + E8(2)`` coordinates."""
        lattice = NamedLattices.U_E8_2
        generators = tuple(lattice.module_generators())
        e, f = generators[:2]
        a = {index: generators[index + 1] for index in range(1, 9)}
        dual = tuple(lattice.dual_lattice().module_generators())
        ad = {index: dual[index + 1] for index in range(1, 9)}
        c = lattice.correlation()
        roots = (
            a[2],
            a[4],
            a[5],
            a[6],
            a[7],
            a[8],
            c.lift(2 * ad[8]),
            c.lift(c(2 * e) + 2 * (ad[2] - ad[3])),
            f - e,
            c.lift(c(e + f) + 2 * (ad[6] - ad[3])),
            c.lift(c(e + f) + 2 * (ad[1] + ad[8] - ad[3])),
            e + f + a[3],
            a[1],
            2 * e - a[1],
        )
        assert len(roots) == 14
        assert all(root.q() in (-2, -4) for root in roots)
        return lattice, roots

    @staticmethod
    def sterks_in_TEn():
        r"""Return the alternative Sterk 1--3 roots in ``TEn`` coordinates."""
        lattice = NamedLattices.TEn
        b = _named_generators(lattice)
        e, f, ep, fp = b["e"], b["f"], b["ep"], b["fp"]
        a = {index: b[f"a{index}"] for index in range(1, 9)}
        dual = tuple(lattice.dual_lattice().module_generators())
        ad2 = {index: 2 * dual[index + 3] for index in range(1, 9)}
        ad1 = {index: dual[index + 3] for index in range(1, 9)}
        c = lattice.correlation()
        configurations = {
            "Sterk_1": tuple(a[index] for index in range(1, 9))
            + (
                fp - ep,
                c.lift(c(2 * ep) + ad2[8]),
                c.lift(c(2 * ep + 2 * fp) + ad2[1] + ad2[8]),
                c.lift(c(5 * ep + 3 * fp) + 2 * ad2[2]),
            ),
            "Sterk_2": tuple(a[index] for index in range(1, 9))
            + (
                c.lift(c(2 * f) + ad2[8]),
                e - f,
            ),
            "Sterk_3": tuple(a[index] for index in range(1, 8))
            + (
                f - e,
                c.lift(c(2 * fp) + 2 * ad1[8]),
                c.lift(c(2 * e - 2 * fp) - 2 * ad1[8]),
                c.lift(c(2 * e) + 2 * (ad1[1] - ad1[8])),
                e + f + a[8] - fp,
            ),
        }
        assert tuple(map(len, configurations.values())) == (12, 10, 12)
        assert all(root.q() in (-2, -4) for roots in configurations.values() for root in roots)
        return configurations

    @staticmethod
    def isotropic_vectors():
        v = Sterk.roots_18_2_0()
        s = v["v22"] + v["v21"]
        assert s.q() == 0
        return {"s4_12": s}

    @staticmethod
    @cache
    def _diagram(name):
        r"""Construct one immutable rooted Sterk diagram and cache its realization."""
        roots = Sterk._sterk_roots_cached()[name]
        return CoxeterDiagrams().from_roots(
            # Vertex names are the actual root-family labels. Passing a
            # separate ``names`` datum does not relabel the vertices in
            # the rooted Coxeter diagram, and integer labels obscure the
            # dissertation's explicit r_0,...,r_{n-1} indexing.
            finite_indexed_family_from_values(
                finite_ordered_set(tuple(f"r{i}" for i in range(len(roots)))),
                tuple(roots),
            ),
            positions={
                f"r{index}": point
                for index, point in _STERK_DIAGRAM_LAYOUTS[name].items()
            },
        )

    @staticmethod
    @cache
    def _cusp_roots_in_TEn_cached(name):
        r"""Carry the printed roots of Sterk's diagram ``name`` into ``T_En``, once."""
        from sage_extensions.catalogue import Embeddings

        lattice = NamedLattices.TEn
        cusps = Sterk.selected_isotropic_vectors()
        if name not in cusps:
            raise ValueError(
                f"Sterk's printed cusp roots are the five diagrams of Math. Z. 207 (1991), section "
                f"4.3.1, diagrams 4.3.5--4.3.9, and {name!r} is none of them"
            )
        eta = cusps[name]
        line = lattice.primitive_isotropic_subobject(eta)
        reduction = line.isotropic_reduction()
        match name:
            case "Sterk_1" | "Sterk_2" | "Sterk_3":
                # The hand-read transcription: the printed roots are already vectors of T_En.
                roots = tuple(Sterk.sterks_in_TEn()[name])
                printed_gram = _family_gram(lattice, roots)
            case "Sterk_5":
                # Fourteen roots in U + E8(-2), a rank-ten model of K_J.  The library's embedding
                # U + E8(-2) -> T_En lands in eta^perp, and both lattices have determinant -256, so
                # the composite with the projection to K_J is an isometry onto K_J.
                model, printed = Sterk.sterk5_in_U_E8_2()
                assert reduction.is_isometric_to(model) is True, (
                    f"Sterk's diagram 4.3.9 is printed in the model {model}, which is not the boundary "
                    f"lattice {reduction} of the cusp of that diagram: the two are not isometric, so the "
                    "printed roots are no classes of K_J"
                )
                roots = tuple(Embeddings.U_E8_2_into_TEn(root) for root in printed)
                printed_gram = _family_gram(model, printed)
            case "Sterk_4":
                # Eleven roots in II_{18,2} coordinates.  No map into T_En carries them: their span is a
                # rank-ten lattice of determinant -1024, an index-two sublattice of K_J (determinant
                # -256), so the identification is an isometric embedding and not an isometry.
                ambient = NamedLattices.TdP
                printed = tuple(Sterk.sterk_roots()["Sterk_4"])
                span = ambient.sublattice_from(printed)
                embeddings = span.Emb(reduction)
                assert embeddings.is_empty() is False, (
                    f"the printed roots of Sterk's diagram 4.3.8 span {span}, which this library does "
                    f"not embed into the boundary lattice {reduction} of the cusp of that diagram, so "
                    "they cannot be read there"
                )
                roots, transport = _transported_roots(
                    printed, span, embeddings.an_element(), reduction, line
                )
                assert transport.det() * transport.det() == QQ(4), (
                    f"the identification of Sterk's diagram 4.3.8 with the boundary lattice {reduction} "
                    f"is not of index two: its matrix has determinant {transport.det()}, while the span "
                    f"has determinant {span.determinant()} and the boundary lattice {reduction.determinant()}"
                )
                printed_gram = _family_gram(ambient, printed)
            case _:
                raise ValueError(f"no cusp roots are held for {name!r}")
        assert all(lattice.b(root, eta) == lattice.base_ring().zero() for root in roots), (
            f"a printed root of Sterk's diagram {name} is not orthogonal to the cusp vector {eta!r}, "
            "so it is no class of the boundary lattice K_J there"
        )
        assert _family_gram(lattice, roots) == printed_gram, (
            f"the printed roots of Sterk's diagram {name} do not keep their pairwise pairings when "
            "read in T_En, so the identification used here is not a form-preserving one"
        )
        return tuple(roots)

    @staticmethod
    def cusp_roots_in_TEn(name):
        r"""Return the printed roots of Sterk's cusp diagram ``name`` as vectors of ``T_{En}``.

        H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
        (1991), section 4.3.1, diagrams 4.3.5--4.3.9 (pp. 19, 21, 22, 23, 24), prints at each of the
        five `0`-cusps of the Enriques period domain the roots of the chamber of the boundary lattice
        `K_J = eta^\perp/\mathbf Z eta`; the five diagrams have 12, 10, 12, 11 and 14 walls (card
        `029J`'s `cusp_chambers` row `gamma-en-2`, read there by tag).  The cusp vector of each diagram
        is :meth:`selected_isotropic_vectors`'.

        Three of the five are held as hand-read ``T_{En}'`` coordinates (:meth:`sterks_in_TEn`) and are
        returned unchanged.  The other two are printed in coordinates of a *model* of `K_J` and are
        carried here by an identification of lattices, each one *checked* rather than assumed:

        * ``Sterk_5`` (4.3.9, p. 24): :meth:`sterk5_in_U_E8_2` prints the fourteen roots in
          `U + E8(-2)`, a rank-ten model of `K_J` of the same determinant `-256`.
          :attr:`sage_extensions.catalogue.Embeddings.U_E8_2_into_TEn` carries that model into
          `T_{En}`, its image lies in `eta^\perp`, and the composite with the projection to `K_J` is an
          isometry onto `K_J`: that the model *is* the boundary lattice is the isometry decision of
          sage-extensions#298, asserted here.
        * ``Sterk_4`` (4.3.8, p. 23): :meth:`sterk_roots` prints the eleven roots in `II_{18,2}`
          coordinates (:attr:`NamedLattices.TdP`), and no map into `T_{En}` carries them.  Their span
          is a rank-ten lattice of determinant `-1024`, an index-two sublattice of `K_J`
          (determinant `-256`), so the identification is the isometric *embedding* the lattice
          embedding Mor decides, and its matrix has determinant `2` -- the equation
          `M^T G_{K_J} M = G_span` of an isometry with a non-unimodular `M`, which sage-extensions#298's
          isometry call, stated for a unimodular change of basis, correctly reports as no isometry
          between the two lattices.

        **What a returned vector is.**  A class of `K_J` has no canonical vector of `T_{En}`: its lifts
        are the class modulo `\mathbf Z eta`.  For ``Sterk_5`` the model's own vectors are the lifts;
        for ``Sterk_4`` the class is lifted through the section the reduction's coordinate frame
        retains.  In both cases the square and the pairing with a vector of `T_Co` are invariants of
        the class -- `eta` lies in `T_Co`, so it is orthogonal to `delta` -- and those are what a
        caller asks of a printed root.

        **What the identification does not fix.**  Any element of `O(K_J)` composes with it, so a
        statement that depends on *which* sublattice or which copy of the model was chosen is a
        statement about the identification and not about Sterk's diagram.  The pairwise pairings are
        preserved by construction and asserted, so the number of printed *classes* is
        identification-free; how many of them lie in `T_Co` is not, and is reported as this
        identification's.

        EXAMPLES::

            sage: from sage_extensions.sterk import Sterk
            sage: roots = Sterk.cusp_roots_in_TEn("Sterk_5")
            sage: all(root.q() in (-2, -4) for root in roots)
            True
        """
        return tuple(Sterk._cusp_roots_in_TEn_cached(name))

    @staticmethod
    def diagrams():
        r"""Return the five exact rooted diagrams in their documented order.

        Rooted diagram construction includes the owned graph and root Gram
        realizations. Cache each immutable diagram separately because the
        public acceptance routines request the same diagrams repeatedly.
        """
        return {name: Sterk._diagram(name) for name in Sterk.sterk_roots()}

    @staticmethod
    def diagram_layouts():
        r"""Return copies of the optional exact presentation coordinates."""
        return {name: dict(positions) for name, positions in _STERK_DIAGRAM_LAYOUTS.items()}


__all__ = ["Sterk"]
