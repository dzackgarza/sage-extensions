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


_STERK_FIG10_VERTEX_ORDER = (10, 7, 6, 5, 4, 3, 2, 0, 9, 8, 1)
r"""The `II_{18,2}` vertex of Sterk's Fig. 10 (p. 23) carrying each printed label, in the order
``a₂, a₃, …, a₈, a₉, a₁₀, a₁₁, a₁₂`` of `Sterk._sterk4_in_TEn_cached`.

Read off the figure's own shape, a chain of nine `α₁₁—α₃—α₄—α₅—α₆—α₇—α₈—α₁₂—α₉` with `α₂` on `α₄`
and `α₁₀` on `α₈`: the chain's two endpoints are the only `(-2)`-vertices, the two degree-three
vertices are `α₄` and `α₈`, and the two remaining leaves are `α₂` and `α₁₀`.  The shape does not
separate the two orientations of the chain -- the diagram's Gram is invariant under reversing it --
but the *vectors* are fixed by the printed formulas, so the transcription does not depend on this
order; the order only lets the diagram be compared as a matrix.
"""

_STERK_FIG3_MINUS_EIGHT_COEFFICIENTS = (-4, -5, -7, -10, -8, -6, -4, -2)
r"""Sterk's `(-8)`-vector `\bar\alpha₁` of `E8(-2)`, in the library's `a₁, …, a₈` basis.

H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207 (1991),
4.3.4 with Fig. 3, p. 19: "Let `\bar\alpha \in E8(-2)` with `\bar\alpha^2 = -8`. As all `(-8)`-vectors
in `E8(-2)` are `O(E8(-2))`-equivalent" one may assume the coefficients Fig. 3 prints, node by node
`4, 7, 10, 8, 6, 4, 2` along `α₁—α₃—α₄—α₅—α₆—α₇—α₈` with `5` on `α₂`.  The library's `E8(-2)` is
the negative-definite one, so those coefficients appear with the opposite sign here, and that this is
the `\bar\alpha₁` of 4.3.8 is checked by the diagram it produces and by the card's row, not assumed.
"""

_STERK_FIG10_ALPHA8_COEFFICIENTS = (-2, -3, -4, -6, -5, -4, -3, -2)
r"""The `E8(-2)` vector Sterk writes `\bar\alpha₈` in Fig. 10, p. 23, in the library's `a`-basis.

4.3.8 prints `α₁₀ = \bar\alpha₈ + 2e'` and `α₁₂ = 2e - 2e' + \bar\alpha₈ - \bar\alpha₁`, so `\bar\alpha₈`
is the one vector of `E8(-2)` the printed formulas name without giving its coefficients.  It is the
only such vector for which the eleven printed vectors have the pairings Fig. 10 draws, which
`Sterk._sterk4_in_TEn_cached` checks against the diagram this library already realizes for that
figure; it is a `(-4)`-vector, and card `029J`'s 4.3.8 row stores the resulting walls.
"""


class Sterk:
    @staticmethod
    @cache
    def _sterk4_in_TEn_cached():
        r"""Return Sterk's Fig. 10 walls as vectors of ``T_En``, transcribed from the printed ones.

        H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
        Math. Z. 207 (1991), 4.3.8, p. 23, draws the chamber of the fourth `0`-cusp at

            v = 2e' + f' + \bar\alpha₁

        in `L_- = H \oplus H(2) \oplus E8(-2)` -- which is `T_En` with `e, f` the `H`, `e', f'` the
        `H(2)` and `α₁, …, α₈` the `E8(-2)` (1.2--1.4, pp. 3--4) -- and prints there:

        * a basis of `v^\perp/\mathbf Z v \cong H \oplus E8(-2)`: `e, f, -e' + α₁, α₂, …, α₈`;
        * the eleven walls as explicit vectors of `L_-`: `α₂, …, α₈` (the `E8(-2)` basis),
          `α₉ = f - e`, `α₁₀ = \bar\alpha₈ + 2e'`, `α₁₁ = e + f + α₁ - e'`,
          `α₁₂ = 2e - 2e' + \bar\alpha₈ - \bar\alpha₁`;
        * and (4.3.10, p. 25) that the roots span `\mathbf Z{e + f, e - f} \oplus E8(-2)`.

        `\bar\alpha₁` is the `(-8)`-vector of Fig. 3 (`_STERK_FIG3_MINUS_EIGHT_COEFFICIENTS`) and
        `\bar\alpha₈` the vector of `_STERK_FIG10_ALPHA8_COEFFICIENTS`; both are printed formulas, not
        a search, so this transcription returns the same eleven vectors in every session.

        Everything asserted is a consequence of Sterk's own statements or of card `029J`'s row: `v` is
        isotropic and primitive and is a different line from (4.2.3)'s representative of the same cusp,
        which it pairs to `2` with; the eleven vectors lie in `v^\perp` with the figure's squares;
        their span is the `\mathbf Z{e + f, e - f} \oplus E8(-2)` of 4.3.10, of determinant `-1024`,
        index two in `K_J = H \oplus E8(-2)`; and their diagram is the one this library already
        realizes for Fig. 10 in `II_{18,2}` coordinates, in the order
        `_STERK_FIG10_VERTEX_ORDER`.
        """
        lattice = NamedLattices.TEn
        generators = _named_generators(lattice)
        indices = tuple(range(1, 9))
        ring = lattice.base_ring()

        def e8_vector(coefficients):
            total = None
            for index, coefficient in zip(indices, coefficients, strict=True):
                piece = ring(coefficient) * generators[f"a{index}"]
                total = piece if total is None else total + piece
            return total

        minus_eight = e8_vector(_STERK_FIG3_MINUS_EIGHT_COEFFICIENTS)
        alpha_eight = e8_vector(_STERK_FIG10_ALPHA8_COEFFICIENTS)
        assert lattice.q(minus_eight) == -ring(8), (
            f"Sterk's (-8)-vector has square {lattice.q(minus_eight)} in {lattice}, not -8: the "
            "coefficients Fig. 3 prints do not read into this E8(-2)"
        )
        assert lattice.q(alpha_eight) == -ring(4), (
            f"the vector written alpha-bar-eight in Sterk's Fig. 10 has square "
            f"{lattice.q(alpha_eight)}, not -4 in {lattice}"
        )
        e = generators["e"]
        f = generators["f"]
        eprime = generators["ep"]
        fprime = generators["fp"]
        isotropic = 2 * eprime + fprime + minus_eight
        assert isotropic == Sterk.sterk4_cusp_vector(), (
            f"Sterk's printed cusp vector {isotropic} is not the one this library returns for 4.3.8"
        )
        other_cusp = Sterk.selected_isotropic_vectors()["Sterk_4"]
        assert lattice.b(isotropic, other_cusp) == ring(2), (
            f"Sterk's (4.3.8) vector {isotropic} and (4.2.3)'s {other_cusp} do not pair to 2, so they "
            "are not the paper's two vectors for the fourth cusp"
        )
        walls = tuple(
            [generators[f"a{index}"] for index in range(2, 9)]
            + [
                f - e,
                alpha_eight + 2 * eprime,
                e + f + generators["a1"] - eprime,
                2 * e - 2 * eprime + alpha_eight - minus_eight,
            ]
        )
        assert all(lattice.b(wall, isotropic) == ring.zero() for wall in walls), (
            f"a printed wall of Sterk's Fig. 10 is not orthogonal to the cusp vector {isotropic}, so "
            "it is no class of the boundary lattice there"
        )
        squares = [lattice.q(wall) for wall in walls]
        assert all(square in (-ring(2), -ring(4)) for square in squares), (
            f"the printed walls of Sterk's Fig. 10 do not have the figure's squares: {squares}"
        )
        order = list(_STERK_FIG10_VERTEX_ORDER)
        printed_diagram = _family_gram(
            NamedLattices.TdP, tuple(Sterk.sterk_roots()["Sterk_4"])
        )[order, order]
        assert _family_gram(lattice, walls) == printed_diagram, (
            "the transcription of Sterk's Fig. 10 from the printed vectors does not have the diagram "
            "this library realizes for that figure in II_{18,2} coordinates"
        )
        span = lattice.sublattice_from(walls)
        boundary = lattice.primitive_isotropic_subobject(isotropic).isotropic_reduction()
        assert span.determinant() == 4 * boundary.determinant(), (
            f"the walls of Sterk's Fig. 10 span a lattice of determinant {span.determinant()}, which "
            f"is not of index two in the boundary lattice {boundary} of determinant "
            f"{boundary.determinant()}"
        )
        return walls

    @staticmethod
    def sterk4_cusp_vector():
        r"""Return the cusp vector of Sterk's (4.3.8), p. 23: `2e' + f' + \bar\alpha₁`.

        Two vectors of `T_En` represent the fourth `0`-cusp, and the paper prints both:

        * (4.2.3), p. 16, lists `e' + 2f' + \gamma`, `\gamma` of square `-8`, as one of the five cusp
          representatives; that is what :meth:`selected_isotropic_vectors` returns for ``Sterk_4``;
        * (4.3.8), p. 23, draws the chamber of that cusp at `2e' + f' + \bar\alpha₁`, and the eleven
          walls of Fig. 10 are its classes: they pair `4, -2, -4` with `α₁₀, α₁₁, α₁₂` against
          (4.2.3)'s vector and are orthogonal to this one.

        The two pair to `2`, so they span different lines; they are representatives of the same cusp,
        whose reductions are isometric.  `\bar\alpha₁` is the `(-8)`-vector of Fig. 3, p. 19.  Card
        `029J`'s `cusp_chambers` row for 4.3.8 stores this vector, term by term, and is what the tests
        read; a chamber is at this line and a cusp is either.
        """
        lattice = NamedLattices.TEn
        generators = _named_generators(lattice)
        ring = lattice.base_ring()
        minus_eight = None
        for index, coefficient in zip(
            range(1, 9), _STERK_FIG3_MINUS_EIGHT_COEFFICIENTS, strict=True
        ):
            piece = ring(coefficient) * generators[f"a{index}"]
            minus_eight = piece if minus_eight is None else minus_eight + piece
        vector = 2 * generators["ep"] + generators["fp"] + minus_eight
        assert lattice.q(vector) == ring.zero(), (
            f"Sterk's (4.3.8) vector {vector} is not isotropic in {lattice}"
        )
        assert vector.is_primitive() is True, (
            f"Sterk's (4.3.8) vector {vector} is not primitive"
        )
        return vector

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
        r"""Return Sterk's five cusp vectors, in the coordinates of ``T_En``.

        H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
        Math. Z. 207 (1991), (4.2.2)--(4.2.3), p. 16: the five `0`-cusps of `\Gamma_{En,2}` are the
        orbits of `e`, `e'`, `e' + f' + \omega` with `\omega` of square `-4`, `e' + 2f' + \gamma` with
        `\gamma` of square `-8`, and `2e + 2f + \alpha` with `\alpha` of square `-8`.  Those are the
        five vectors below, in this lattice's basis --- `e, f` the `H`, `e', f'` the `H(2)`,
        `α₁, …, α₈` the `E8(-2)` --- the last two read through the correlation, with
        `\gamma = \alpha = \bar\alpha₁` the `(-8)`-vector of Fig. 3, p. 19
        (`_STERK_FIG3_MINUS_EIGHT_COEFFICIENTS`).

        **The fourth cusp has two vectors in the paper.**  This call returns (4.2.3)'s,
        `e' + 2f' + \gamma`.  The chamber printed for that cusp, (4.3.8) with Fig. 10, p. 23, is drawn
        at `2e' + f' + \bar\alpha₁` instead, which :meth:`sterk4_cusp_vector` returns and which card
        `029J`'s `cusp_chambers` row for that statement stores; the eleven walls of Fig. 10 are its
        classes, pairing `4, -2, -4` with `α₁₀, α₁₁, α₁₂` against `e' + 2f' + \gamma`.  The two pair to
        `2` and span different lines, but they are two representatives of one cusp: their reductions
        are isometric (`tests/lattices/test_cusp_lattices.sage` asserts it for all five cusps).  A
        reduction read at either is the cusp's; a chamber is at the second.  This is the disagreement
        filed as `dzackgarza/lattice-database` #44, closed by storing the chamber's vector on the row.
        """
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
        # The chamber's own cusp vector: (4.2.3) lists representatives of the five cusps, and for
        # (4.3.8) the figure is drawn at the other of the paper's two vectors for that cusp.
        eta = Sterk.sterk4_cusp_vector() if name == "Sterk_4" else cusps[name]
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
                # Eleven walls printed as explicit vectors in the basis e, f, e', f', a₁, ..., a₈ of
                # L_- = H + H(2) + E8(-2), which is this lattice: no identification of lattices is
                # needed and none is chosen, only Sterk's printed vectors are read.
                roots = Sterk._sterk4_in_TEn_cached()
                order = list(_STERK_FIG10_VERTEX_ORDER)
                printed_gram = _family_gram(
                    NamedLattices.TdP, tuple(Sterk.sterk_roots()["Sterk_4"])
                )[order, order]
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
        r"""Return the printed walls of Sterk's cusp diagram ``name`` as vectors of ``T_{En}``.

        H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
        (1991), section 4.3.1, diagrams 4.3.5--4.3.9 (pp. 19, 21, 22, 23, 24), prints at each of the
        five `0`-cusps of the Enriques period domain the walls of the chamber of the boundary lattice
        `K_J = eta^\perp/\mathbf Z eta`; the five diagrams have 12, 10, 12, 11 and 14 walls (card
        `029J`'s `cusp_chambers` row `gamma-en-2`, read there by tag).

        **Every printed vector is read, none is searched for.**  Sterk's coordinates are those of
        `L_- = H \oplus H(2) \oplus E8(-2)` (1.2--1.4, pp. 3--4), which *is* `T_En`, so:

        * ``Sterk_1``--``Sterk_3``: :meth:`sterks_in_TEn`, the hand-read `T_En` coordinates;
        * ``Sterk_4`` (4.3.8, p. 23): :meth:`_sterk4_in_TEn_cached`, the eleven vectors of Fig. 10
          transcribed from the printed formulas and checked against the diagram this library
          realizes for that figure;
        * ``Sterk_5`` (4.3.9, p. 24): :meth:`sterk5_in_U_E8_2`'s fourteen vectors, printed in the
          model `U + E8(-2)` and carried in by
          :attr:`sage_extensions.catalogue.Embeddings.U_E8_2_into_TEn`, whose image lies in
          `eta^\perp` and keeps the pairings; that the model *is* `K_J` is the isometry decision of
          sage-extensions#298, asserted here.

        So a caller gets the same vectors in every session, and the classes of `K_J` they give are the
        same too.  The cusp vector for ``Sterk_4`` is :meth:`sterk4_cusp_vector`'s, the one that
        figure's chamber is drawn at; for the others it is :meth:`selected_isotropic_vectors`'.

        **What a returned vector is.**  A class of `K_J` has no canonical vector of `T_{En}`: its
        lifts are the class modulo `\mathbf Z eta`.  The vectors returned are the printed ones, which
        lie in `eta^\perp`, and their square and pairing with a vector of `T_Co` are invariants of
        their class --- `eta` lies in `T_Co`, so it is orthogonal to `delta` --- and those are what a
        caller asks of a printed wall.

        EXAMPLES::

            sage: from sage_extensions.sterk import Sterk
            sage: walls = Sterk.cusp_roots_in_TEn("Sterk_4")
            sage: all(wall.q() in (-2, -4) for wall in walls)
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
