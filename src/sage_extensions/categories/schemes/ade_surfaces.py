r"""ADE log pairs: the toric base of an integral ADE polygon.

An ADE type of the families \(A\), \(D\), \(E\) and their affine partners is
recorded by an integral polygon \(Q\) in the plane together with a
distinguished rational point \(p^*\) on its boundary, and by decorations on
the sides of \(Q\) incident to \(p^*\).  The toric surface \(Y=V_Q\) of the
normal fan of \(Q\) is the base of the double cover that carries the ADE
surface, and the boundary of the toric log pair \((Y,\Delta)\) splits into the
*blue* divisor \(C\), summing the invariant divisors whose facet of \(Q\)
contains \(p^*\), and its complement \(C'\).

Both constructors use the toric shapes of Alexeev--Thompson, *ADE surfaces and
their moduli*, Tables 1 and 4.  The AT21 enhancement checks Lemma 3.4's linear
equivalence ``L ~ -2(K_Y+C) ~ 2C'`` on the live toric surface.  Table 5 sections
use its literal character coordinates.  A double-cover equation defines a
hypersurface; its ADE interpretation additionally requires the stated
log-canonicity hypothesis on the branch pair.  Projection is defined on the
toric complement of the pyramid's apex fixed point, which the hypersurface
avoids because its apex-square coefficient is a unit.
"""

from dataclasses import dataclass

from sage.categories.rings import Rings as SageRings
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedRings,
    _engine_numeral,
    _own_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.schemes.log_pairs import ToricLogPairs
from sage_extensions.categories.schemes.polytopes import (
    ConvexPolytopes,
    LatticePolygons,
)
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.owned_category import _object_of
from sage_extensions.logic import AtomicProposition
from sage_extensions.tensors.tensor import tensor
from sage_extensions.static_types import ProductOfNaturalNumbers


def _side(first, second):
    r"""The side of ``Q`` joining two vertices, as a point of ``NN x NN``.

    A vertex of ``Q`` is named by its position in the boundary order, which is
    a natural number, so a side is a point of the square of the natural
    numbers.
    """
    return (NN**2)((first, second))


@dataclass(frozen=True)
class SideDecoration:
    r"""The decoration of one side of ``Q`` incident to ``p*``.

    ``side`` is the point of ``NN x NN`` naming the two vertices the side
    joins, ``length_class`` is ``"long"`` or ``"short"``, and
    ``vertex_colour`` is ``"white"`` or ``"black"``.  The classification is
    Alexeev--Thompson's, and it distinguishes ADE types whose polygons
    otherwise agree.
    """

    side: ProductOfNaturalNumbers
    length_class: str
    vertex_colour: str


def _rationals():
    return _owned_rationals()


def _rational_point(polygon, coordinates):
    r"""A rational point of ``M_QQ``, the rational space ``Q`` lives in."""
    rationals = _rationals()
    return polygon.ambient_space()(
        tuple(_owned_engine_element(rationals, SageQQ(coordinate)) for coordinate in coordinates),
    )


def _has(variant, *names) -> bool:
    return any(name in variant for name in names)


def _ade_parameter(letter, rank, variant, affine):
    r"""The half-rank parameter ``n`` the polygon of a family is written in."""
    if letter == "A":
        # AT21 Table 4 indexes the primed polygon by A'_{2n-3} while the
        # corresponding log-pair has even rank 2n-2.  Thus the even-rank
        # primed case uses n = rank/2 + 1, unlike the odd-rank A'_{2n-1}
        # family and the ordinary unprimed parity rule.
        if _has(variant, "prime") and rank % 2 == 0:
            return rank // 2 + 1
        # _call_ passes the validated low-level tuple: (short,long) is a
        # left-short side pair, (long,short) is right-short, and
        # (short,short) is the odd-rank both-short family.
        if _has(variant[:1], "short"):
            return (rank + 3) // 2
        if _has(variant[1:2], "short"):
            return (rank + 2) // 2
        return (rank + 1) // 2
    if letter == "D":
        return (rank + 1) // 2
    return 2


def _affine_polygon_data(letter, rank, parameter):
    if letter == "D":
        return (((0, 2), (0, 0), (2 * parameter - 4, 0), (4, 2)), (2, 2))
    assert letter == "E", (
        f"the represented toric affine shapes have letter D or E, but the letter is {letter!r}"
    )
    if rank == 7:
        return (((0, 4), (0, 0), (4, 0)), (2, 2))
    assert rank == 8, f"the toric affine E shapes have rank 7 or 8, but n = {rank}"
    return (((0, 3), (0, 0), (6, 0)), (2, 2))


def _a_family_polygon_data(rank, variant, parameter):
    # The polygon constructor receives the validated low-level side tuple,
    # not the normalized public variant string.
    left_short = _has(variant[:1], "short")
    right_short = _has(variant[1:2], "short")
    if _has(variant, "prime", "primed", "p"):
        # The two primed AT21 families have different indices: A'_{2n-1}
        # for odd-rank A pairs, and A'_{2n-3} for even-rank A^- pairs.
        # The latter's endpoint is one less than the pair rank; the former's
        # endpoint equals the pair rank.
        endpoint = rank if rank % 2 else rank - 1
        return (
            ((2, 2), (0, 1), (0, 0), (endpoint, 0)),
            (2, 2),
        )
    if left_short and right_short:
        vertices = ((0, 2), (1, 0), (2 * parameter - 1, 0))
    elif left_short:
        vertices = ((0, 2), (1, 0), (2 * parameter, 0))
    elif right_short:
        vertices = ((0, 2), (0, 0), (2 * parameter - 1, 0))
    else:
        vertices = ((0, 2), (0, 0), (2 * parameter, 0))
    return (vertices, (0, 2))


def _d_family_polygon_data(rank, variant, parameter):
    if _has(variant, "primed", "prime", "p"):
        vertices = ((2, 2), (0, 2), (0, 0), (2 * parameter - 4, 0), (parameter, 1))
    elif "short" in variant or rank % 2 == 1:
        vertices = ((2, 2), (0, 2), (0, 0), (2 * parameter - 3, 0))
    else:
        vertices = ((2, 2), (0, 2), (0, 0), (2 * parameter - 2, 0))
    return (vertices, (2, 2))


def _e_family_polygon_data(rank):
    assert rank in (6, 7, 8), f"the type E_n has n = 6, 7 or 8, but n = {rank}"
    last = {6: 3, 7: 4, 8: 5}[rank]
    return (((2, 2), (0, 3), (0, 0), (last, 0)), (2, 2))


def _polygon_side_decorations(vertices, point):
    r"""The long/short data of every side through the selected point.

    AT21 Definition 3.6 reads the intersection degree from the lattice length:
    2 and 4 are long, 1 and 3 are short.  White/black records the corresponding
    endpoint parity, with the single affine side using the same convention.
    The separate Dynkin variant retains priming.  Boundary-order positions
    refer to the actual sides, including when p* is interior to an affine side.
    """
    decorations = []
    for first_index, first in enumerate(vertices):
        second_index = (first_index + 1) % len(vertices)
        second = vertices[second_index]
        dx, dy = second[0] - first[0], second[1] - first[1]
        px, py = point[0] - first[0], point[1] - first[1]
        if dx * py != dy * px:
            continue
        if not (
            min(first[0], second[0]) <= point[0] <= max(first[0], second[0])
            and min(first[1], second[1]) <= point[1] <= max(first[1], second[1])
        ):
            continue
        length = int(SageZZ(dx).gcd(SageZZ(dy)))
        assert length in (1, 2, 3, 4), (
            f"the AT21 side from {first} to {second} has unsupported lattice length {length}"
        )
        indices = (second_index, first_index) if second == point else (first_index, second_index)
        long_side = length % 2 == 0
        decorations.append(SideDecoration(
            _side(*indices),
            "long" if long_side else "short",
            "white" if long_side else "black",
        ))
    return finite_family(tuple(decorations), name="Side decorations")


def _ade_polygon_data(letter, rank, variant, affine):
    r"""The polygon, distinguished point and complete side data of one admitted shape."""
    parameter = _ade_parameter(letter, rank, variant, affine)
    if affine:
        vertices, point = _affine_polygon_data(letter, rank, parameter)
    elif letter == "A":
        vertices, point = _a_family_polygon_data(rank, variant, parameter)
    elif letter == "D":
        vertices, point = _d_family_polygon_data(rank, variant, parameter)
    else:
        assert letter == "E", f"an ADE type has letter A, D or E, but the letter is {letter!r}"
        vertices, point = _e_family_polygon_data(rank)
    return (vertices, point, _polygon_side_decorations(vertices, point))


def _normalize_at21_variant(letter, rank, variant, affine):
    r"""Normalize public AT21 variant spellings to the finite internal vocabulary."""
    if isinstance(variant, str):
        source_variant = variant.lower().replace("_", "-").replace("−", "-").strip()
        if source_variant in ("prime", "primed", "p"):
            if letter == "A":
                return "prime-odd" if rank % 2 else "prime-even"
            return "prime"
        if letter == "A" and source_variant in ("'a", "'a'", "′a", "′a′"):
            return "prime-odd"
        if letter == "A" and source_variant in ("'a^-", "'a⁻", "′a^-", "′a⁻"):
            return "prime-even"
        if letter == "A" and rank == 0 and not affine and source_variant in ("^-a", "-a", "minus-a"):
            # AT21 Table 1 includes the degenerate-rank endpoint A^-_0.
            # At rank zero the one-short presentation has only its right
            # short side, represented by the low-level ``(long, short)``
            # tuple; the generic left-short alias would be rejected by the
            # rank-zero admission rule below.
            return "short"
        if letter == "A" and source_variant in ("^-a", "-a", "minus-a"):
            return "left-short"
        if letter == "A" and source_variant in ("a^-", "a⁻", "a-minus"):
            return "short"
        if letter == "A" and rank == 0 and not affine and source_variant == "pure":
            return "short"
        return source_variant
    variant = tuple(variant)
    match variant:
        case ():
            short = not affine and ((letter == "A" and rank % 2 == 0) or (letter == "D" and rank % 2 == 1))
            return "short" if short else "pure"
        case ("prime" | "primed" | "p",):
            if letter == "A":
                return "prime-odd" if rank % 2 else "prime-even"
            return "prime"
        case ("long", "short"):
            return "short"
        case ("short", "short"):
            return "both-short"
        case ("short", "long"):
            return "left-short"
        case ("short",):
            return "left-short" if letter == "A" else "short"
        case ("long", "long"):
            return "pure"
        case _:
            raise ValueError(f"{variant!r} is not a represented toric ADE side variant")


def _validated_at21_low_level_variant(letter, rank, variant, affine):
    if letter not in ("A", "D", "E"):
        raise ValueError(f"an ADE type has letter A, D or E, but the letter is {letter!r}")
    if rank < 0 or (rank == 0 and not (letter == "A" and variant == "short" and not affine)):
        raise ValueError(
            f"an ADE type {letter}_n needs rank n >= 1, except for the pure A_0^- shape "
            f"(variant='short'); got rank {rank} and variant {variant!r}"
        )
    if affine:
        if variant != "pure":
            raise ValueError(
                f"the affine type tilde {letter}_{rank} has only the pure toric polygon of "
                f"Alexeev-Thompson (AT21), not the variant {variant!r}"
            )
        if letter == "D" and rank >= 6 and rank % 2 == 0:
            return ()
        if letter == "E" and rank in (7, 8):
            return ()
        raise ValueError(
            f"the affine type tilde {letter}_{rank} has no toric polygon in Alexeev-Thompson "
            "(AT21): a torus-invariant boundary exists for tilde D_n with even n >= 6, "
            "tilde E_7 and tilde E_8; tilde D_4 has a diagonal/conic boundary, "
            "and tilde A_n is not toric"
        )
    if letter == "A":
        if variant == "pure" and rank % 2 == 1:
            return ()
        if variant == "short" and rank % 2 == 0:
            return ("long", "short")
        if variant == "left-short" and rank % 2 == 0:
            return ("short", "long")
        if variant == "both-short" and rank % 2 == 1:
            return ("short", "short")
        if variant == "prime-odd" and rank >= 3 and rank % 2 == 1:
            return ("prime",)
        if variant == "prime-even" and rank >= 2 and rank % 2 == 0:
            return ("prime",)
        raise ValueError(
            f"type A_{rank} has no toric polygon of variant {variant!r} in Alexeev-Thompson "
            "(AT21): the represented toric A shapes are pure A_n for odd n, one-short A_n for even n, "
            "both-short A_n for odd n, A'_{2n-1} for odd n >= 3, and A'_{2n-3} for even n >= 2"
        )
    if letter == "D":
        if variant == "pure" and rank >= 4 and rank % 2 == 0:
            return ()
        if variant == "short" and rank >= 5 and rank % 2 == 1:
            return ("short",)
        if variant == "prime" and rank >= 6 and rank % 2 == 0:
            return ("prime",)
        raise ValueError(
            f"type D_{rank} has no toric polygon of variant {variant!r} in Alexeev-Thompson "
            "(AT21): the represented toric D shapes are pure D_n for even n >= 4, one-short D_n for odd n, "
            "and primed D_n for even n >= 6 (AT21 Lemma 3.25)"
        )
    if rank not in (6, 7, 8) or variant != "pure":
        raise ValueError(
            f"type E_{rank} of variant {variant!r} has no toric polygon in Alexeev-Thompson "
            "(AT21): the toric E shapes are pure E_6, E_7 and E_8"
        )
    return ()


class ADELogPairs(OwnedCategoryOverBaseRing):
    r"""Toric log pairs equipped with an ADE type, its polygon and ``p*``."""

    def an_object(self):
        r"""The base log pair of the ``A_1`` polygon."""
        return self("A", 1)

    def _call_(
        self,
        dynkin_letter,
        dynkin_rank,
        variant=(),
        affine=False,
        *,
        _source_variant=None,
    ):
        r"""Construct the base log pair of one ADE type over this category's base."""
        letter = str(dynkin_letter).upper()
        assert letter in ("A", "D", "E"), (
            f"an ADE type has letter A, D or E, but the letter is {letter!r}"
        )
        rank = int(_engine_numeral(SageZZ, dynkin_rank))
        source_variant = (
            _normalize_at21_variant(letter, rank, variant, bool(affine))
            if _source_variant is None
            else _source_variant
        )
        allow_a_zero = letter == "A" and rank == 0 and not affine and source_variant == "short"
        assert rank >= 1 or allow_a_zero, (
            f"an ADE type {letter}_n needs rank n >= 1, except for the pure A_0^- shape "
            f"(variant='short'); got rank {rank} and variant {source_variant!r}"
        )
        low_level_variant = _validated_at21_low_level_variant(
            letter, rank, source_variant, bool(affine)
        )
        if _source_variant is not None:
            assert tuple(variant) == low_level_variant, (
                f"the supplied low-level ADE side tuple {variant!r} does not represent "
                f"the retained source variant {source_variant!r}, whose tuple is {low_level_variant!r}"
            )

        vertices, point, decorations = _ade_polygon_data(
            letter,
            rank,
            low_level_variant,
            bool(affine),
        )
        polygon_lattice = _owned_integers().free_module(2)
        polygon = LatticePolygons(polygon_lattice)(vertices)
        toric_base = polygon.toric_variety(self.base_ring())
        from sage_extensions.categories.schemes.schemes import _scheme_with_structure

        return _scheme_with_structure(
            toric_base,
            self,
            construction_data={
                "dynkin_letter": letter,
                "dynkin_rank": rank,
                "source_variant": source_variant,
                # Public normalized variant strings and polygon side tuples
                # are different representations. Retain the latter here for
                # side decorations; the AT21 wrapper separately retains the
                # former as ``source_variant``.
                "dynkin_variant": low_level_variant,
                "is_affine_type": bool(affine),
                "polygon": polygon,
                "polygon_vertex_order": finite_family(
                    tuple(_rational_point(polygon, vertex) for vertex in vertices),
                    name="ADE polygon boundary order",
                ),
                "distinguished_point": _rational_point(polygon, point),
                "side_decorations": decorations,
                "log_scheme": toric_base,
                "boundary_divisor": toric_base.toric_boundary_divisor(),
            },
        )

    def at21(self, dynkin_letter, dynkin_rank, *, variant=(), affine=False):
        r"""Construct a toric AT21 base with its branch linear system.

        The source's ADE and log-canonicity assertions are geometric
        characteristic-zero statements. This enhancement is represented over
        a characteristic-zero field; the polygon constructor still constructs
        the toric scheme over any admitted base ring.
        """
        base = self.base_ring()
        assert base in OwnedFields() and base.characteristic().is_zero() is True, (
            f"the represented AT21 branch-pair construction requires a characteristic-zero field, "
            f"but its base is {base}"
        )
        letter = str(dynkin_letter).upper()
        rank = int(_engine_numeral(SageZZ, dynkin_rank))
        affine = bool(affine)
        source_variant = _normalize_at21_variant(letter, rank, variant, affine)
        low_variant = _validated_at21_low_level_variant(
            letter,
            rank,
            source_variant,
            affine,
        )
        pair = self(
            letter,
            rank,
            variant=low_variant,
            affine=affine,
            _source_variant=source_variant,
        )
        surface = pair.log_scheme()
        branch_class = surface.polarizing_divisor()
        expected = _owned_integers()(2) * pair.complementary_divisor()
        # Lemma 3.4 is an identity of divisor classes: L and 2C' differ by the
        # divisor of a character, so they are compared in Cl(Y).
        actual_class = surface.divisor_class(branch_class)
        expected_class = surface.divisor_class(expected)
        classes_match = actual_class is expected_class or (
            actual_class == expected_class
        ) is True
        if not classes_match:
            raise ArithmeticError(
                f"the log pair {pair} of type {letter}_{rank} does not satisfy AT21 Lemma 3.4: "
                f"the branch divisor L = -2(K_Y + C) = {branch_class} is not linearly equivalent "
                f"to 2C' = {expected}"
            )
        # `surface` is the exact selected log-scheme object used to compute
        # both divisor classes above. Reuse it rather than dispatching through
        # the pair's log_scheme accessor again during line-bundle construction.
        branch_line_bundle = surface.invertible_sheaf_of_divisor(branch_class)
        return ToricLogPairs(self.base_ring())(
            surface,
            pair.blue_divisor(),
            _engine=_AT21ToricADEPairEngine,
            construction_data={
                "base_pair": pair,
                "source_variant": source_variant,
                "branch_divisor_class": branch_class,
                "branch_line_bundle": branch_line_bundle,
            },
        )

    def _repr_object_names(self):
        return f"ADE log pairs over {self.base_ring()}"

    def super_categories(self):
        return [ToricLogPairs(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            dynkin_letter,
            dynkin_rank,
            source_variant,
            dynkin_variant,
            is_affine_type,
            polygon,
            polygon_vertex_order,
            distinguished_point,
            side_decorations,
            **rest,
        ) -> None:
            self._dynkin_letter = dynkin_letter
            self._dynkin_rank = dynkin_rank
            self._source_variant = source_variant
            self._dynkin_variant = dynkin_variant
            self._is_affine_type = is_affine_type
            self._polygon = polygon
            self._polygon_vertex_order = polygon_vertex_order
            self._distinguished_point = distinguished_point
            self._side_decorations = side_decorations
            super().__init__(**rest)

        def base(self):
            r"""Return this base ADE log pair itself."""
            return self

        def is_base(self) -> bool:
            return True

        def is_cover(self) -> bool:
            return False

        def dynkin_letter(self) -> str:
            return self._dynkin_letter

        def dynkin_rank(self):
            return _owned_integers()(self._dynkin_rank)

        def source_variant(self) -> str:
            r"""Return the normalized public variant spelling before side expansion."""
            return self._source_variant

        def letter(self) -> str:
            r"""Return the ADE letter; archived synonym for :meth:`dynkin_letter`."""
            return self.dynkin_letter()

        def rank(self):
            r"""Return the ADE rank; archived synonym for :meth:`dynkin_rank`."""
            return self.dynkin_rank()

        def dynkin_variant(self):
            r"""The decorations naming this member of its family."""
            return self._dynkin_variant

        def is_affine_type(self) -> bool:
            return self._is_affine_type

        def variant(self):
            r"""Return the selected ADE side-decoration variant."""
            return self.dynkin_variant()

        @cached_method
        def coxeter_diagram(self):
            r"""The owned Coxeter/Dynkin diagram of this finite or affine ADE type."""
            from sage_extensions.categories.coxeter_diagrams import (
                CoxeterDiagrams,
            )

            cartan_type = [self.dynkin_letter(), int(self.dynkin_rank())]
            if self.is_affine_type():
                cartan_type.append(1)
            return CoxeterDiagrams().from_cartan_type(cartan_type)

        def dynkin_diagram(self):
            r"""Return the selected ADE Dynkin diagram; archived mathematical name."""
            return self.coxeter_diagram()

        def polygon(self):
            r"""The integral ADE polygon ``Q``."""
            return self._polygon

        def polygon_vertex_order(self):
            r"""Return the boundary-ordered vertices used by the ADE side data.

            ``SideDecoration.side`` is indexed by positions in this family.
            A polytope as an unordered convex hull does not retain that
            presentation, so the ADE structure owns the order separately.
            """
            return self._polygon_vertex_order

        @cached_method
        def vertices(self):
            r"""Return the vertices of ``Q`` as the polygon's owned finite set."""
            return self.polygon().vertices()

        def distinguished_point(self):
            r"""The distinguished rational point ``p*`` on the boundary of ``Q``."""
            return self._distinguished_point

        def p_star(self):
            r"""Return the distinguished point ``p*``; archived mathematical name."""
            return self.distinguished_point()

        def polarizing_polytope(self):
            r"""Return the ADE polarizing polygon ``Q``."""
            return self.polygon()

        def side_decorations(self):
            r"""The decorations of the sides of ``Q`` incident to ``p*``."""
            return self._side_decorations

        def ade_svg(self):
            r"""Return a deterministic SVG view of the retained ADE polygon data.

            This is a view of the live log-pair object, not a second polygon
            presentation.  Vertices come from :meth:`polygon`, ``p*`` from
            :meth:`distinguished_point`, and the decorated sides from
            :meth:`side_decorations`.  Floating-point conversion is confined
            to this rendering boundary; stable ``data-*`` attributes retain
            the ADE semantics for notebook inspection and regression tests.
            """
            vertices = tuple(
                tuple(float(coordinate) for coordinate in vertex)
                for vertex in self.polygon_vertex_order()
            )
            if len(vertices) < 3:
                return None
            point = tuple(float(coordinate) for coordinate in self.p_star())
            all_x = tuple(vertex[0] for vertex in vertices) + (point[0],)
            all_y = tuple(vertex[1] for vertex in vertices) + (point[1],)
            minimum_x, maximum_x = min(all_x), max(all_x)
            minimum_y, maximum_y = min(all_y), max(all_y)
            span_x = max(maximum_x - minimum_x, 1.0)
            span_y = max(maximum_y - minimum_y, 1.0)
            scale = 260.0 / max(span_x, span_y)
            margin = 30.0

            def screen(coordinates):
                x, y = coordinates
                return (
                    margin + (x - minimum_x) * scale,
                    margin + (maximum_y - y) * scale,
                )

            width = 2 * margin + span_x * scale
            height = 2 * margin + span_y * scale
            polygon_points = " ".join(
                f"{screen(vertex)[0]:.2f},{screen(vertex)[1]:.2f}"
                for vertex in vertices
            )
            lines = [
                (
                    f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'viewBox="0 0 {width:.2f} {height:.2f}" '
                    f'data-role="ade-polygon" data-ade-type="{self.dynkin_letter()}{int(self.dynkin_rank())}">'
                ),
                f'<polygon data-role="polygon" points="{polygon_points}" fill="none" stroke="currentColor"/>',
            ]
            for position in self.side_decorations().index_set():
                decoration = self.side_decorations()[position]
                first = int(decoration.side[0])
                second = int(decoration.side[1])
                start = screen(vertices[first])
                end = screen(vertices[second])
                lines.append(
                    f'<line data-role="decorated-side" data-length-class="{decoration.length_class}" '
                    f'data-vertex-colour="{decoration.vertex_colour}" '
                    f'data-side="{first},{second}" x1="{start[0]:.2f}" y1="{start[1]:.2f}" '
                    f'x2="{end[0]:.2f}" y2="{end[1]:.2f}" stroke="currentColor" stroke-width="3"/>'
                )
            blue_coordinates = {
                tuple(float(coordinate) for coordinate in boundary_point)
                for boundary_point in self.distinguished_boundary_points()
            }
            for boundary_point in sorted(blue_coordinates):
                rendered = screen(boundary_point)
                lines.append(
                    f'<circle data-role="blue-boundary-point" data-lattice-point="{boundary_point[0]:g},{boundary_point[1]:g}" '
                    f'cx="{rendered[0]:.2f}" cy="{rendered[1]:.2f}" r="3"/>'
                )
            rendered_point = screen(point)
            lines.append(
                f'<circle data-role="p-star" data-point="{point[0]:g},{point[1]:g}" '
                f'cx="{rendered_point[0]:.2f}" cy="{rendered_point[1]:.2f}" r="6"/>'
            )
            lines.append("</svg>")
            return "".join(lines)

        def _repr_svg_(self):
            r"""Notebook SVG view retaining the ADE decorations and ``p*``."""
            return self.ade_svg()

        @cached_method
        def integral_invariants(self):
            r"""The invariant family of the retained polarizing polygon."""
            return self.polarizing_polytope().integral_invariants()

        def _blue_rays(self):
            polygon = self.polygon()
            return self.fan().cones(1).filtered(
                lambda ray: polygon.normal_supports_point(
                    next(iter(ray.rays())),
                    self.distinguished_point(),
                ),
                name="Blue rays",
            )

        @cached_method
        def distinguished_boundary_points(self):
            r"""Return the integral boundary points lying on a blue facet of ``Q``.

            A blue facet is one containing the distinguished point ``p*``.
            Equivalently its inner normal is one of :meth:`_blue_rays`, so a
            boundary lattice point lies on a blue facet exactly when it
            minimizes the corresponding linear functional on ``Q``.  The
            returned points remain elements of the polygon's owned ambient
            lattice.
            """
            polygon = self.polygon()
            blue_rays = self._blue_rays()

            def lies_on_blue_facet(point):
                return any(
                    polygon.normal_supports_point(
                        next(iter(ray.rays())),
                        point,
                    )
                    for ray in blue_rays
                )

            return polygon.boundary_integral_points().filtered(
                lies_on_blue_facet,
                name="Distinguished ADE boundary points",
            )

        @cached_method
        def blue_divisor(self):
            r"""``C``: the invariant divisors whose facet of ``Q`` contains ``p*``."""
            group = self.log_scheme().torus_invariant_divisor_group()
            blue = self._blue_rays()
            return group.linear_combination(
                {ray: _owned_integers().one() for ray in blue}
            )

        def blue_line_divisor(self):
            r"""Return the blue divisor ``C``; archived mathematical name."""
            return self.blue_divisor()

        @cached_method
        def complementary_divisor(self):
            r"""``C'``: the rest of the toric boundary, so that ``C + C' = Delta``."""
            return self.boundary_divisor() - self.blue_divisor()

        @cached_method
        def pyramid(self):
            r"""The 3-polytope ``P``: the cone over ``Q`` with apex ``(p*, 2)``.

            The admitted toric shapes have integral ``p*``, so this is a
            lattice polytope. The nontoric affine A shapes do not enter this
            construction.
            """
            polygon = self.polygon()
            rationals = _rationals()
            base = tuple(
                (*tuple(vertex), rationals.zero())
                for vertex in polygon.vertices()
            )
            apex = (
                *tuple(self.distinguished_point()),
                rationals(2),
            )
            pyramid_lattice = _owned_integers().free_module(3)
            return ConvexPolytopes(pyramid_lattice)((*base, apex))

        def cover_toric_threefold(self):
            r"""``V_P``, the toric threefold the double cover is cut out of."""
            pyramid = self.pyramid()
            assert pyramid.is_lattice_polytope(), (
                f"the toric threefold V_P of {self} is the toric variety of the pyramid over its "
                f"polygon, but the pyramid's apex over p* = {self.distinguished_point()} is not a "
                "lattice point, so the pyramid is not a lattice polytope"
            )
            return pyramid.toric_variety(self.log_scheme().scheme_base_ring())

        def _repr_(self) -> str:
            prefix = "affine " if self.is_affine_type() else ""
            return (
                f"ADE log pair of {prefix}type "
                f"{self.dynkin_letter()}_{self.dynkin_rank()} on {self.polygon()}"
            )


__all__ = ["ADELogPairs", "SideDecoration"]


class _AT21ToricADEPairEngine:
    r"""A source-admitted toric ADE base pair with its branch linear system.

    This is the toric part of Alexeev--Thompson's classification, not a second
    scheme model.  The underlying object of :class:`ADELogPairs` remains the actual toric
    surface with its boundary.  Admission uses AT21 Theorems 4.8 and 4.10 for
    the pure finite/affine shapes and Lemma 3.25 for the primed shapes that
    remain toric.  In particular ``tilde A`` is not admitted here (AT21
    Remark 3.11) and there is no affine ``E6`` case.

    ``variant`` is ``pure``, ``short``, ``left-short``, ``both-short`` or ``prime``.
    The name records the source shape rather than asking the archive polygon
    parser to infer parity from a loose token sequence.
    """

    def __init__(
        self,
        *,
        base_pair,
        source_variant,
        branch_divisor_class,
        branch_line_bundle,
        **rest,
    ) -> None:
        self._base_pair = base_pair
        self._source_variant = source_variant
        self._branch_divisor_class = branch_divisor_class
        self._branch_line_bundle = branch_line_bundle
        super().__init__(**rest)

    def base_pair(self):
        return self._base_pair

    def scheme(self):
        return self.log_scheme()

    toric_scheme = scheme

    def complementary_divisor(self):
        return self.base_pair().complementary_divisor()

    def blue_divisor(self):
        r"""The selected blue divisor of the retained ADE base pair."""
        return self.boundary_divisor()

    def source_variant(self):
        return self._source_variant

    def dynkin_letter(self):
        return self.base_pair().dynkin_letter()

    def dynkin_rank(self):
        return self.base_pair().dynkin_rank()

    def is_affine_type(self):
        return self.base_pair().is_affine_type()

    def polygon(self):
        return self.base_pair().polygon()

    def distinguished_point(self):
        return self.base_pair().distinguished_point()

    def side_decorations(self):
        return self.base_pair().side_decorations()

    def coxeter_diagram(self):
        return self.base_pair().coxeter_diagram()

    def pyramid(self):
        return self.base_pair().pyramid()

    def cover_toric_threefold(self):
        return self.base_pair().cover_toric_threefold()

    def branch_divisor_class(self):
        r"""The chosen toric representative of ``L ~ -2(K_Y+C) ~ 2C'``."""
        return self._branch_divisor_class

    def branch_line_bundle(self):
        return self._branch_line_bundle

    @cached_method
    def log_boundary_coefficient_ring(self):
        r"""The owned characteristic-zero polynomial ring for AT21 boundary coefficients."""
        return self.scheme().scheme_base_ring().polynomial_ring("epsilon")

    def branch_section_space(self):
        return self.scheme().divisor_section_space(self.branch_divisor_class())

    def branch_section(self, character_coefficients):
        r"""Construct a section from exact lattice coordinates and arbitrary coefficients.

        Integer ingress refuses nonintegral exponents. Zero coefficients are
        supplied to the linear-combination owner too: constructing a section
        requires no decision about which of its coefficients vanish. Owned
        coefficients use their actual ring ingress; raw Sage numerals cross
        the existing constructor boundary and immediately return to that ring.
        """
        sections = self.branch_section_space()
        characters = {
            tuple(int(coordinate) for coordinate in character): character
            for character in sections.module_generating_set()
        }
        coefficients = {}
        base = self.scheme().scheme_base_ring()
        for coordinates, coefficient in dict(character_coefficients).items():
            key = tuple(int(_engine_numeral(SageZZ, value)) for value in coordinates)
            if key not in characters:
                raise ValueError(
                    f"{key} is not a lattice point of the branch polytope of {self}, so it is "
                    "not the character of a branch section"
                )
            coefficient_parent = element_parent(coefficient)
            if coefficient_parent not in OwnedRings() and coefficient_parent in SageRings():
                value = _owned_engine_element(base, _engine_numeral(base, coefficient))
            else:
                value = base(coefficient)
            coefficients[characters[key]] = value
        return sections.linear_combination(coefficients)

    @cached_method
    def full_newton_branch_section(self):
        r"""A branch section whose Newton polygon is the whole selected ``Q``."""
        return self.branch_section(
            {
                tuple(int(coordinate) for coordinate in vertex): self.scheme().scheme_base_ring().one()
                for vertex in self.polygon().vertices()
            }
        )

    def branch_newton_polygon(self, section):
        r"""The Newton polygon when every coefficient's zero status is decided."""
        from sage_extensions.categories.schemes.polytopes import LatticePolygons

        sections = self.branch_section_space()
        coordinates = sections(section).to_vector()
        zero = self.scheme().scheme_base_ring().zero()
        support = []
        for character in sections.module_generating_set():
            vanished = coordinates(character) == zero
            if vanished is True:
                continue
            if vanished is not False:
                raise NotImplementedError(
                    f"the Newton polygon of this section needs the zero status of its coefficient "
                    f"at {character}, but that equality is undecided"
                )
            support.append(tuple(int(coordinate) for coordinate in character))
        if len(support) < 3:
            raise ValueError(
                f"the Newton polygon of the branch section needs a two-dimensional support, but "
                f"the section has only {len(support)} monomials"
            )
        polygon = LatticePolygons(self.scheme().character_lattice())(tuple(support))
        if polygon.dimension() != _owned_integers()(2):
            raise ValueError("the nonzero branch characters are collinear, so their hull is not a polygon")
        return polygon

    def source_normal_form_section(self, *, constant=1):
        r"""Return the AT21 Table 5 normal-form specimen in the D/E families.

        With all deformation parameters except ``c_0`` specialized to zero,
        Table 5 gives
        ``x^2y^2 + y^2 + x^(n-2) + c_0`` for ``D_n`` and
        ``x^2y^2 + y^3 + x^(n-3) + c_0`` for ``E_n``.
        The four exponent vectors are literal character-lattice points of the
        retained source polygon. This specimen factory represents the D and
        E rows; it does not construct the A normal-form families.
        """
        assert not self.is_affine_type(), (
            f"the normal forms of AT21 Table 5 are for finite types D and E, but {self} is of "
            "affine type"
        )
        rank = int(self.dynkin_rank())
        assert self.source_variant() not in ("prime", "prime-odd", "prime-even"), (
            f"AT21 Table 5 supplies pure-shape normal forms, but {self} is primed"
        )
        if self.dynkin_letter() == "D":
            terms = {
                (2, 2): 1,
                (0, 2): 1,
                (rank - 2, 0): 1,
                (0, 0): constant,
            }
        elif self.dynkin_letter() == "E":
            terms = {
                (2, 2): 1,
                (0, 3): 1,
                (rank - 3, 0): 1,
                (0, 0): constant,
            }
        else:
            assert self.dynkin_letter() in ("D", "E"), (
                f"the normal forms of AT21 Table 5 are implemented for types D and E, but {self} "
                f"has type {self.dynkin_letter()}"
            )
        return self.branch_section(terms)

    def branch_subscheme(self, section):
        return self.scheme().zero_subscheme_of_divisor_section(
            self.branch_divisor_class(),
            section,
            line_bundle=self.branch_line_bundle(),
        )

    def branch_log_canonicity(self, section):
        r"""The AT21 condition on ``(Y, C + (1+epsilon) B/2)``.

        The zero section defines no effective branch divisor and is refused.
        In characteristic zero the displayed pure-shape vertex specimens and
        Table 5 D/E normal forms meet the blue sides transversally at smooth
        points: on each side their endpoint coefficients are nonzero and the
        edge polynomial is a square-free binomial. AT21 Theorem 5.9's proof
        then gives log canonicity for sufficiently small positive epsilon.
        Here pure means unprimed: the admitted short, left-short and
        both-short variants are included. The constant D/E coefficient is
        off the blue sides, so this assertion needs no genericity or global
        smoothness of the branch divisor. Affine and primed shapes do not
        enter these positive decisions.
        A different section retains this mathematical condition as a
        proposition; no general log-resolution algorithm is claimed.
        """
        sections = self.branch_section_space()
        selected = sections(section)
        if (selected == sections.zero()) is True:
            return False
        if not self.is_affine_type() and self.source_variant() not in (
            "prime", "prime-odd", "prime-even",
        ):
            if (selected == self.full_newton_branch_section()) is True:
                return True
            if self.dynkin_letter() in ("D", "E"):
                constant = selected.to_vector()(self.scheme().character_lattice().zero())
                if (selected == self.source_normal_form_section(constant=constant)) is True:
                    return True
        return AtomicProposition("AT21_log_canonical_branch_pair", self, selected)

    def double_cover(self, section=None):
        r"""Construct the double-cover hypersurface, retaining its ADE condition.

        Its interpretation as an AT21 ADE double cover requires the
        log-canonicity condition of Definition 3.2. The returned
        ``ade_pair_condition()`` is True for the source specimens above and
        remains a proposition for an undecided section. A decided zero
        section is rejected. The characteristic-zero base makes the sign
        deck action nontrivial and permits the ramification interpretation.
        """
        selected = (
            self.full_newton_branch_section()
            if section is None
            else self.branch_section_space()(section)
        )
        condition = self.branch_log_canonicity(selected)
        if condition is False:
            raise ValueError("the zero section is not an effective AT21 branch divisor")
        return _at21_ade_double_cover(self, selected, condition)

    def _repr_(self):
        prefix = "affine " if self.is_affine_type() else ""
        return f"AT21 toric ADE pair of {prefix}type {self.dynkin_letter()}_{self.dynkin_rank()} ({self.source_variant()})"



class _AT21ADEDoubleCoverEngine:
    r"""The actual hypersurface and maps, with the branch pair's ADE condition.

    Being a double-cover hypersurface does not decide log canonicity. The
    selected branch condition is retained separately and may be undecided.
    """

    def __init__(
        self,
        *,
        base_pair,
        branch_section,
        ambient_toric_threefold,
        ambient_polarizing_divisor,
        ambient_hypersurface_section,
        ambient_projection,
        ambient_open_immersion,
        branch_log_canonicity,
        **rest,
    ) -> None:
        self._base_pair = base_pair
        self._branch_section = branch_section
        self._ambient = ambient_toric_threefold
        self._ambient_divisor = ambient_polarizing_divisor
        self._ambient_section = ambient_hypersurface_section
        self._ambient_projection = ambient_projection
        self._ambient_open_immersion = ambient_open_immersion
        self._branch_log_canonicity = branch_log_canonicity
        super().__init__(**rest)

    def base_pair(self):
        return self._base_pair

    def cover_base_scheme(self):
        r"""The surface Y receiving this cover; the inherited base_scheme is Spec(R)."""
        return self.base_pair().scheme()

    def branch_section(self):
        return self._branch_section

    def branch_subscheme(self):
        return self.base_pair().branch_subscheme(self.branch_section())

    def ambient_toric_threefold(self):
        return self._ambient

    def ambient_polarizing_divisor(self):
        return self._ambient_divisor

    def ambient_hypersurface_section(self):
        return self._ambient_section

    def scheme(self):
        return self

    def ambient_projection(self):
        r"""The projection from the ambient toric open to the base surface."""
        return self._ambient_projection

    def ambient_open_immersion(self):
        r"""The inclusion of the projection's domain in the complete pyramid variety."""
        return self._ambient_open_immersion

    def ade_pair_condition(self):
        r"""The retained log-canonicity condition for this hypersurface to be an ADE pair."""
        return self._branch_log_canonicity

    @cached_method
    def _cover_structure(self):
        from sage_extensions.categories.sets.indexed_families import (
            finite_indexed_family,
        )

        cover = self
        base_pair = self.base_pair()
        ambient_projection = self.ambient_projection()
        ambient = ambient_projection.domain()
        cover_atlas = cover.gluing_datum()
        local_cover_maps = {}
        local_global_cover_maps = {}
        local_deck = {}
        base = base_pair.scheme().scheme_base_ring()
        for cone in cover_atlas.chart_indices():
            local_cover = cover_atlas.chart(cone)
            target_cone = ambient_projection.chart_target(cone)
            to_target_chart = (
                ambient_projection.chart_morphism(cone) * local_cover.inclusion()
            )
            local_cover_maps[cone] = to_target_chart
            local_global_cover_maps[cone] = (
                base_pair.scheme().gluing_datum().chart_embedding(target_cone)
                * to_target_chart
            )

            ambient_chart = ambient.affine_chart(cone)
            algebra = ambient_chart.coordinate_algebra()
            labels = tuple(algebra.algebra_generating_set())
            images = {}
            for position, character in enumerate(cone.semigroup_generators()):
                height = int(tuple(character)[-1])
                scalar = -base.one() if height % 2 else base.one()
                images[labels[position]] = algebra.scalar_multiple(
                    scalar,
                    algebra.algebra_generator(labels[position]),
                )
            ambient_automorphism = ambient_chart.Mor(ambient_chart)(
                algebra.Mor(algebra)(images)
            )
            local_deck[cone] = local_cover.corestriction(
                ambient_automorphism * local_cover.inclusion()
            )

        cover_morphism = cover.Mor(base_pair.scheme())(local_global_cover_maps)
        deck = cover.Mor(cover)(
            {
                cone: cover.gluing_datum().chart_embedding(cone) * local_deck[cone]
                for cone in cover.gluing_datum().chart_indices()
            }
        )
        local_cover_family = finite_indexed_family(
            cover.gluing_datum().chart_index_set(),
            lambda cone: local_cover_maps[cone],
            name="Local maps of the AT21 double cover to the toric base charts",
        )
        local_deck_family = finite_indexed_family(
            cover.gluing_datum().chart_index_set(),
            lambda cone: local_deck[cone],
            name="Local deck involutions of the AT21 double cover",
        )
        # The character action chi^(m,h) |-> (-1)^h chi^(m,h) is
        # multiplicative and squares to the identity over the actual base.
        # Every retained chart trivializes the section at a height-zero base
        # vertex. Its branch terms have height zero and its apex term height
        # two, so the action preserves the defining section and restricts to
        # the cover. Pulled-back base characters have height zero, proving
        # pi*iota = pi. These are coefficient-independent identities of this
        # construction; a general arrow-equality algorithm may remain
        # undecided and is not an additional admission premise here.

        # AT21 Definition 2.1 permits isolated deck-fixed points away from R.
        # The apex monomial has divisor twice the base-facet prime, so its
        # restriction cuts out the ramification divisor itself, locally z=0.
        lattice = ambient.cocharacter_lattice()
        height_direction = lattice.module_generator(tuple(lattice.module_generating_set())[-1])
        base_facet_rays = tuple(
            ray for ray in ambient.fan().cones(1)
            if next(iter(ray.rays())) == height_direction
        )
        assert len(base_facet_rays) == 1, "the pyramid open has one positive-height base-facet ray"
        ambient_ramification = ambient.torus_invariant_divisor_support_subscheme(
            ambient.torus_invariant_prime_divisor(base_facet_rays[0])
        )
        ramification_atlas = ambient_ramification.gluing_datum()
        ramification_local = {}
        for cone in cover_atlas.chart_indices():
            local_cover = cover_atlas.chart(cone)
            pullback = local_cover.inclusion().coordinate_algebra_morphism()
            equations = tuple(
                pullback(equation)
                for equation in ramification_atlas.chart(cone).defining_equations()
            )
            ramification_local[cone] = local_cover.closed_subscheme(equations)
        ramification = cover.chartwise_closed_subscheme(
            ramification_local,
            name="AT21 ramification divisor",
        )
        base_boundary = base_pair.scheme().torus_invariant_divisor_support_subscheme(
            base_pair.boundary_divisor()
        )
        base_boundary_atlas = base_boundary.gluing_datum()
        pulled_boundary_local = {}
        for cone in cover.gluing_datum().chart_indices():
            target_cone = ambient_projection.chart_target(cone)
            local_boundary = base_boundary_atlas.chart(target_cone)
            pullback = local_cover_maps[cone].coordinate_algebra_morphism()
            equations = tuple(
                pullback(equation) for equation in local_boundary.defining_equations()
            )
            pulled_boundary_local[cone] = cover_atlas.chart(cone).closed_subscheme(equations)
        pulled_boundary = cover.chartwise_closed_subscheme(
            pulled_boundary_local,
            name="Pulled-back AT21 boundary",
        )
        return {
            "cover_morphism": cover_morphism,
            "local_cover_maps": local_cover_family,
            "local_deck": local_deck_family,
            "deck": deck,
            "ramification": ramification,
            "base_boundary": base_boundary,
            "pulled_boundary": pulled_boundary,
        }

    def cover_morphism(self):
        return self._cover_structure()["cover_morphism"]

    def local_cover_map(self, cone):
        return self._cover_structure()["local_cover_maps"][
            self.gluing_datum().normalize_chart_index(cone)
        ]

    def deck_involution(self):
        return self._cover_structure()["deck"]

    def local_deck_involution(self, cone):
        return self._cover_structure()["local_deck"][
            self.gluing_datum().normalize_chart_index(cone)
        ]

    def ramification_subscheme(self):
        r"""The divisorial ramification R, excluding isolated deck-fixed points."""
        return self._cover_structure()["ramification"]

    def boundary_subscheme(self):
        r"""Return ``D=pi^{-1}(C)`` scheme-theoretically."""
        return self._cover_structure()["pulled_boundary"]

    pulled_back_boundary = boundary_subscheme

    def base_boundary_subscheme(self):
        return self._cover_structure()["base_boundary"]

    def boundary_divisor(self):
        from sage_extensions.categories.divisors.divisor_groups import FormalDivisorGroups

        return FormalDivisorGroups(_rationals()).from_terms(
            {self.boundary_subscheme(): _rationals().one()}
        )

    @cached_method
    def log_boundary_coefficient_ring(self):
        return _rationals().polynomial_ring("epsilon")

    def log_boundary_divisor(self):
        r"""Return the equipped cover boundary ``D + epsilon R`` of AT21 Section 2."""
        from sage_extensions.categories.divisors.divisor_groups import FormalDivisorGroups

        coefficients = self.log_boundary_coefficient_ring()
        epsilon = coefficients.algebra_generator("epsilon")
        return FormalDivisorGroups(coefficients).from_terms(
            {
                self.boundary_subscheme(): coefficients.one(),
                self.ramification_subscheme(): epsilon,
            },
        )

    def equipped_pair(self):
        r"""Return ``(X, D + epsilon R)``; its ADE status is ``ade_pair_condition()``."""
        return self, self.log_boundary_divisor()

    def dynkin_diagram(self):
        return self.base_pair().coxeter_diagram()

    def polarizing_polytope(self):
        r"""The polygon polarizing the retained quotient base Y."""
        return self.base_pair().polygon()

    def local_surface_equation(self):
        r"""The actual E8 origin-chart equation ``z^2 + f(x,y)``.

        For the pure finite E8 polygon the origin chart of the open pyramid
        has coordinates x, y and z=xy*u. Its semigroup basis
        (1,0,0), (0,1,0), (1,1,1) is unimodular. Thus every retained branch
        character x^i*y^j pulls back literally and the apex term is z^2.
        No completed-square change of coordinates is asserted here.
        """
        assert (
            self.base_pair().dynkin_letter() == "E"
            and int(self.base_pair().dynkin_rank()) == 8
            and not self.base_pair().is_affine_type()
            and self.base_pair().source_variant() == "pure"
        ), (
            f"the represented origin chart is the pure finite E_8 chart, "
            f"but {self.base_pair()} has type {self.base_pair().dynkin_letter()}_"
            f"{self.base_pair().dynkin_rank()}"
        )
        ring = self.cover_base_scheme().scheme_base_ring().polynomial_ring(("x", "y", "z"))
        x, y, z = tuple(ring.algebra_generators())
        scalar_map = ring.algebra_structure_morphism()
        coordinates = self.branch_section().to_vector()
        equation = z**2
        for character in self.base_pair().branch_section_space().module_generating_set():
            i, j = tuple(int(value) for value in character)
            equation += scalar_map(coordinates(character)) * x**i * y**j
        return equation

    def local_surface_singularity(self):
        r"""The represented origin germ when its Jacobian needs no localization.

        The existing isolated-hypersurface engine computes a global Jacobian
        algebra. It applies here to the diagonal E8 equation, whose gradient
        vanishes only at the origin. For the literal Table 5 equation the
        extra x^2*y^2 term creates another critical point off the origin, so
        the local Milnor algebra needs localization first. The actual
        equation is always available from local_surface_equation().
        """
        from sage_extensions.categories.schemes.singularities import (
            IsolatedHypersurfaceSingularity,
        )

        equation = self.local_surface_equation()
        ring = equation.parent()
        x, y, z = tuple(ring.algebra_generators())
        constant = self.branch_section().to_vector()(self.cover_base_scheme().character_lattice().zero())
        vanishes = constant == ring.base_ring().zero()
        if vanishes is False:
            raise ValueError(f"the origin does not lie on the selected hypersurface {equation} = 0")
        if vanishes is not True:
            raise NotImplementedError("membership of the origin in this hypersurface is undecided")
        if (equation == z**2 + y**3 + x**5) is True:
            return IsolatedHypersurfaceSingularity(ring, equation)
        raise NotImplementedError(
            f"the origin germ of {equation} = 0 requires the Jacobian algebra localized at "
            "(x,y,z); the selected isolated-hypersurface engine computes the global Jacobian "
            "algebra, which is not a local Milnor-number computation"
        )

    def local_global_singularity_comparison(self):
        singularity = self.local_surface_singularity()
        rank = self.base_pair().dynkin_rank()
        return finite_family(
            (
                ("global_dynkin_rank", rank),
                ("local_milnor_number", singularity.milnor_number()),
                ("local_tjurina_number", singularity.tjurina_number()),
            ),
            name="AT21 E8 local/global singularity comparison",
        )

    def _repr_(self):
        return f"Double-cover hypersurface of {self.base_pair()}"


def _at21_ade_double_cover(base_pair, branch_section, branch_log_canonicity):
    r"""The hypersurface over the toric complement of the pyramid's apex orbit.

    The apex normal cone projects onto the entire base lattice, so projection
    is not a map of the complete ambient variety. Delete that maximal cone,
    retaining its proper faces. The hypersurface misses the removed fixed
    point because its section has unit apex coefficient. Restrict its actual
    Cartier-section coefficients to this open atlas and use the common
    chartwise closed-subscheme constructor.
    """
    from sage_extensions.categories.schemes.schemes import OpenImmersions
    from sage_extensions.categories.schemes.toric.fans import RationalPolyhedralFans

    selected_branch = base_pair.branch_section_space()(branch_section)
    ambient = base_pair.cover_toric_threefold()
    ambient_divisor = ambient.polarizing_divisor()
    ambient_sections = ambient.divisor_section_space(ambient_divisor)
    ambient_by_coordinates = {
        tuple(int(coordinate) for coordinate in character): character
        for character in ambient_sections.module_generating_set()
    }
    coefficients = {}
    branch_coordinates = selected_branch.to_vector()
    for character in base_pair.branch_section_space().module_generating_set():
        key = (*tuple(int(value) for value in character), 0)
        if key not in ambient_by_coordinates:
            raise ArithmeticError(
                f"the branch character {character} of {base_pair} is not a lattice point of the "
                f"height-0 face of the pyramid, so the branch section does not extend to {ambient}"
            )
        coefficients[ambient_by_coordinates[key]] = branch_coordinates(character)
    apex = (
        *tuple(int(value) for value in base_pair.distinguished_point()),
        2,
    )
    if apex not in ambient_by_coordinates:
        raise ArithmeticError(
            f"the apex {apex} of the pyramid over {base_pair} is not a lattice point of the "
            f"polytope of the polarizing divisor of {ambient}"
        )
    coefficients[ambient_by_coordinates[apex]] = base_pair.scheme().scheme_base_ring().one()
    ambient_section = ambient_sections.linear_combination(coefficients)

    source_lattice = ambient.cocharacter_lattice()
    target_lattice = base_pair.scheme().cocharacter_lattice()
    source_labels = tuple(source_lattice.module_generating_set())
    target_labels = tuple(target_lattice.module_generating_set())
    if len(source_labels) != 3 or len(target_labels) != 2:
        raise ArithmeticError(
            f"the projection from the pyramid's toric threefold to the ADE surface needs "
            f"cocharacter lattices of ranks 3 and 2, but they have ranks {len(source_labels)} and "
            f"{len(target_labels)}"
        )
    projection_lattice_map = source_lattice.module_category().Mor(source_lattice, target_lattice)(
        {
            source_labels[0]: target_lattice.module_generator(target_labels[0]),
            source_labels[1]: target_lattice.module_generator(target_labels[1]),
            source_labels[2]: target_lattice.zero(),
        }
    )
    identity_lattice_map = source_lattice.module_category().Mor(source_lattice, source_lattice).identity()
    downward = -source_lattice.module_generator(source_labels[2])
    apex_cones = tuple(
        cone for cone in ambient.fan().maximal_cones()
        if cone.relative_interior_contains(downward)
    )
    assert len(apex_cones) == 1, (
        f"the pyramid has one apex normal cone, but {len(apex_cones)} cones contain the "
        "negative height direction in their relative interior"
    )
    open_fan = RationalPolyhedralFans(source_lattice)(
        tuple(
            tuple(cone.rays()) for cone in ambient.fan().maximal_cones()
            if cone != apex_cones[0]
        )
    )
    opened = open_fan.toric_variety(
        base_pair.scheme().scheme_base_ring(),
        placements=(OpenImmersions(ambient),),
        inclusion_codomain=ambient,
        inclusion_datum=lambda mor: mor.domain().toric_morphism(identity_lattice_map, ambient),
    )
    ambient_open_immersion = opened.inclusion()
    ambient_projection = opened.toric_morphism(
        projection_lattice_map,
        base_pair.scheme(),
    )

    line_bundle = ambient.invertible_sheaf_of_divisor(ambient_divisor)
    compatible = ambient.compatible_divisor_section(
        ambient_divisor, ambient_section, line_bundle=line_bundle,
    )
    section_datum = line_bundle.module_sheaf().gluing_datum()
    local_closed = {}
    for cone in opened.gluing_datum().chart_indices():
        ambient_cone = ambient_open_immersion.chart_target(cone)
        local_module = line_bundle.module_sheaf().sections_on_chart(ambient_cone)
        label = next(iter(local_module.module_generating_set()))
        coefficient = local_module.framing_morphism().lift(
            section_datum.compatible_section_component(compatible, ambient_cone)
        )(label)
        restriction = ambient_open_immersion.chart_pullback(cone)
        local_closed[cone] = opened.affine_chart(cone).closed_subscheme(restriction(coefficient))
    return opened.chartwise_closed_subscheme(
        local_closed,
        name="Double-cover hypersurface over an AT21 toric base",
        _engine=_AT21ADEDoubleCoverEngine,
        construction_data={
            "base_pair": base_pair,
            "branch_section": selected_branch,
            "ambient_toric_threefold": ambient,
            "ambient_polarizing_divisor": ambient_divisor,
            "ambient_hypersurface_section": ambient_section,
            "ambient_projection": ambient_projection,
            "ambient_open_immersion": ambient_open_immersion,
            "branch_log_canonicity": branch_log_canonicity,
        },
    )


__all__ = [
    "ADELogPairs",
    "SideDecoration",
]
