r"""Matrices of the projective invariants of the pairs of a family of mirrors.

For two non-isotropic vectors \(r,s\) of a formed module the invariant of the
pair (``vinberg_invariant``) is

.. MATH::

    t(r,s) \;=\; \bigl[\,4\,b(r,s)^2 \;:\; q(r)\,q(s)\,\bigr] \;\in\; \mathbb P^1(R),

the projective point of the pair.  When \(q(r),q(s)>0\) it dehomogenizes to
\(4g^2\), where \(g=b(r,s)/\sqrt{q(r)q(s)}\) is the entry of the Gram matrix
of the unit normals (Vinberg, section 1).  Rescaling either vector multiplies
numerator and denominator by the same square, so \(t\) depends on the two
mirrors and not on the normals chosen for them; that is why the value is a
point of the projective line rather than an element of \(R\).  Over \(\mathbb Z\) the ratio
\(4b(r,s)^2/q(r)q(s)\) is usually not an integer, so no matrix over the base
ring can hold these values while a matrix of projective points can.

Dehomogenized, \(t = 4\cos^2(\pi/m)\) for the angle \(\pi/m\) between the
mirrors, so the crystallographic bonds are the integers

======  ===  ===  ===  ===  ==========
\(m\)   2    3    4    6    \(\infty\)
\(t\)   0    1    2    3    \(\geq 4\)
======  ===  ===  ===  ===  ==========

and the invariant matrix carries strictly more than the Coxeter matrix: at
\(t \geq 4\) the Coxeter bond is \(\infty\) either way, while \(t = 4\)
says the mirrors are parallel and \(t > 4\) says they diverge.

Sources.  Vinberg, *Hyperbolic reflection groups*, Russian Math. Surveys 40
(1985), sections 1 and 4, for the Gram matrix of a family of mirrors, the classification of a pair of
mirrors, and the Lannér and quasi-Lannér conditions; Lannér, *On complexes
with transitive groups of automorphisms* (1950), for the cocompact simplex
groups; Bourbaki, *Groupes et algebres de Lie* VI.1.1 for crystallographic
Coxeter bonds.
"""

from itertools import combinations

from sage.misc.cachefunc import cached_method
from sage.rings.infinity import Infinity
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.qqbar import AA, QQbar

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams
from sage_extensions.categories.graph_categories import LabelledGraphs
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    OwnedRings,
    _cross_engine_ring_value,
    _engine_numeral,
    _own_ring,
    _owned_real_algebraic_numbers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    OrderedEnumeratedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.owned_category import _object_of
from sage_extensions.tensors.tensor import tensor
from sage_extensions.validation import validator


def _unimodular_pair(ring, numerator, denominator):
    r"""Return homogeneous coordinates of ``[numerator : denominator]`` that generate ``ring``.

    An ``R``-point of ``P^1_R`` is an invertible module ``L`` on ``Spec R``
    with two global sections generating it, up to isomorphism of ``L``
    (Stacks, Lemma 27.13.1, tag 01NE, with ``P^1_R`` the base change of
    ``P^1_ZZ``, Definition 27.13.2, tag 01NF).  Over a field every nonzero
    pair generates ``R``.  Over a PID ``L`` is finite torsion free, hence
    free (Stacks, Lemma 15.22.11, tag 0AUW), so a point is a pair generating
    the unit ideal up to a unit; since ``(a, b) = (gcd(a, b))``, dividing by
    the gcd gives that pair.  Elsewhere the pair must generate ``R`` itself.
    """
    numerator = ring(numerator)
    denominator = ring(denominator)
    match ring:
        case _ if ring in OwnedFields():
            return (numerator, denominator)
        case _ if ring in OwnedRings().Commutative().NoZeroDivisors().PrincipalIdeals():
            divisor = numerator.gcd(denominator)
            return (numerator // divisor, denominator // divisor)
        case _:
            assert False, (
                f"[{numerator} : {denominator}] is an {ring}-point of the projective line "
                f"only if ({numerator}, {denominator}) generates {ring}; {ring} is neither a "
                f"field nor a principal ideal domain, and that is not decided here"
            )


def _reflection_cosine(index):
    r"""Return \(\cos(\pi/n)\) as an exact algebraic real."""
    index = SageZZ(index)
    assert index >= 1, f"a reflection cosine is indexed by an integer n >= 1; got {index}"
    if index == 1:
        return AA(-1)
    if index == 2:
        return AA.zero()
    root_of_unity = QQbar.zeta(2 * index)
    return AA((root_of_unity + root_of_unity**-1) / 2)


def _reflection_cosine_index(cosine):
    r"""Return the \(n\) with ``cosine`` \(=\cos(\pi/n)\), or ``None``.

    Exact, and without enumeration: for \(x\in[-1,1)\) put
    \(\zeta = x + i\sqrt{1-x^2}\), a point of the unit circle in
    \(\overline{\mathbb Q}\).  Then \(x=\cos(\pi/n)\) exactly when \(\zeta\) is
    a primitive \(2n\)-th root of unity, which is to say that \(\zeta\) has
    finite multiplicative order \(2n\) and \(\zeta^n=-1\).  Anything of
    infinite order, or of odd order, or with \(\zeta^n=+1\), is not a
    reflection cosine.
    """
    value = QQbar(cosine)
    if value == -1:
        return SageZZ.one()
    if value <= -1 or value >= 1:
        return None
    root_of_unity = value + QQbar.gen() * QQbar(1 - value**2).sqrt()
    order = root_of_unity.multiplicative_order()
    if order is Infinity or order % 2 != 0:
        return None
    index = SageZZ(order // 2)
    return index if root_of_unity**index == -1 else None


def _reflection_cosine_position(cosine):
    r"""Return the position of ``cosine`` in the enumeration, or ``None``.

    Position \(k\) carries \(n=k+1\), which is the one step between \(\omega\)
    and the positive integers that index the cosines.
    """
    index = _reflection_cosine_index(cosine)
    return None if index is None else NN(index - 1)


def reflection_cosines():
    r"""Return \(X_{\mathrm{ref}}=\{\cos(\pi/n) : n\in\mathbb Z_{\geq 1}\}\).

    The values a Coxeter bond can take as a cosine, as an owned set: countably
    infinite, enumerated by \(n\), and with exact membership through
    :func:`_reflection_cosine_index`.  Position \(k\) of the enumeration
    carries \(n=k+1\): the index set is \(\omega\) and the cosines start at
    \(n=1\).

    Membership is decided in \(\overline{\mathbb Q}\) and never by rounding,
    so \(1/2\) and \((1+\sqrt 5)/4\) belong, being \(\cos(\pi/3)\) and
    \(\cos(\pi/5)\), while \(1/3\) does not.
    """
    return OrderedEnumeratedSets()(
        NN,
        lambda position: _reflection_cosine(int(position) + 1),
        index_of=_reflection_cosine_position,
        contains=lambda value: _reflection_cosine_index(value) is not None,
        name="Reflection cosines { cos(pi/n) : n >= 1 }",
    )


def _coxeter_bond(invariant):
    r"""Return the Coxeter bond \(m\) of the Vinberg invariant ``invariant``.

    ``invariant`` is \(t=4\cos^2(\pi/m)\) as an exact rational or algebraic
    real.  Mirrors at \(t\geq 4\) do not meet inside hyperbolic space, so the
    bond is \(\infty\); otherwise \(\cos(\pi/m)=\sqrt t/2\) and the bond is the
    reflection-cosine index of that value.
    """
    assert invariant >= 0, (
        f"a Vinberg invariant of two mirrors is a square ratio and is never "
        f"negative; got {invariant}"
    )
    if invariant >= 4:
        return Infinity
    index = _reflection_cosine_index(AA(invariant).sqrt() / 2)
    assert index is not None, (
        f"the Vinberg invariant {invariant} is not 4 cos^2(pi/m) for any "
        f"integer m, so this pair of mirrors has no Coxeter bond"
    )
    return index


class VinbergInvariantMatrices(OwnedCategory):
    r"""Symmetric matrices of Vinberg invariants on a finite set of mirrors.

    The entries are points ``[4 b(r,s)^2 : q(r)q(s)]`` of a projective line,
    not scalars of the coefficient ring, so this is not an object of
    ``MatrixSpaces(R)``.  The same data is exactly the symmetric labelled graph
    whose non-orthogonal pairs are edges and whose projective invariants are
    vertex and edge labels; that is the immediate owned placement used here.
    """

    def an_object(self):
        r"""The invariant matrix of the \(A_2\) diagram."""
        return self.from_coxeter_diagram(CoxeterDiagrams().from_cartan_type(["A", 2]))

    @classmethod
    def _repr_object_names(cls):
        return "Vinberg invariant matrices"

    def super_categories(self):
        return [LabelledGraphs()]

    class ParentMethods:
        def __init__(
            self, base_ring, index_set, numerators, denominators, root_gram, **rest
        ) -> None:
            self._base_ring = base_ring
            self._index_set = finite_ordered_set(index_set)
            self._numerators = numerators
            self._denominators = denominators
            self._root_gram = root_gram
            super().__init__(**rest)

        def base_ring(self):
            return self._base_ring

        def index_set(self):
            r"""Return the ordered set of mirrors this matrix is indexed by."""
            return self._index_set

        def vertices(self):
            return self.index_set()

        def __contains__(self, mirror) -> bool:
            return mirror in self.index_set()

        def _element_constructor_(self, mirror):
            return self.index_set()(mirror)

        def __iter__(self):
            return iter(self.index_set())

        def has_edge(self, left, right) -> bool:
            return left != right and self.vinberg_ratio(left, right) != 0

        def edges(self):
            edge_space = self.index_set()**2
            return finite_ordered_set(
                tuple(
                    edge_space((left, right))
                    for left, right in combinations(tuple(self.index_set()), 2)
                    if self.has_edge(left, right)
                )
            )

        def is_directed(self) -> bool:
            return False

        def is_symmetric(self) -> bool:
            return True

        def vertex_label(self, vertex):
            return self.vinberg_invariant(vertex, vertex)

        def edge_label(self, left, right):
            if not self.has_edge(left, right):
                raise ValueError(
                    f"the mirrors {left} and {right} of {self} are orthogonal, so they are "
                    f"not joined by an edge of the graph of mirrors and the edge has no label"
                )
            return self.vinberg_invariant(left, right)

        def _cardinality_decision(self):
            return self._index_set.cardinality()

        @cached_method
        def _projective_line_scheme(self):
            r"""The scheme \(\mathbb P^1_R\) over the coefficient ring."""
            from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

            return ProjectiveSpaces(self._base_ring)(1)

        def projective_line(self):
            r"""Return \(\mathbb P^1(R)=\operatorname{Mor}_R(\operatorname{Spec}R,\mathbb P^1_R)\), where the invariants take their values.

            The scheme \(\mathbb P^1_R\) is the codomain of this Mor.
            """
            from sage_extensions.categories.schemes.schemes import Schemes

            line = self._projective_line_scheme()
            return Schemes(line.scheme_base_ring()).Mor(line.base_scheme(), line)

        def is_rooted(self) -> bool:
            r"""Return whether the matrix was built from a Gram of mirror normals."""
            return self._root_gram is not None

        def root_gram_tensor(self):
            r"""Return the Gram tensor of the mirror normals this matrix was built from."""
            assert self.is_rooted(), (
                f"{self} has no Gram tensor of mirror normals: it was given by its "
                f"invariants or by the bonds of a Coxeter diagram, not by normals"
            )
            return self._root_gram

        @validator
        def validate_mirror_normals(self) -> None:
            r"""Check that every stated normal is the normal of a mirror.

            The normal of a mirror is not isotropic, so every diagonal entry
            \(q(r_v)\) of the Gram tensor is nonzero.  This is the validator of
            the object :meth:`VinbergInvariantMatrices.from_root_gram` builds.
            """
            gram = self.root_gram_tensor()
            squares = tuple(gram[i, i] for i in range(gram.tensor_shape()[0]))
            if any(square == 0 for square in squares):
                raise ValueError(
                    f"the Gram tensor {gram} of {self} is not the Gram tensor of the normals "
                    f"of a family of mirrors: its diagonal {squares} has a zero, and the "
                    f"normal of a mirror is not isotropic"
                )

        def is_acute_angled_hyperbolic_polytope_gram(self) -> bool:
            r"""Return whether the normals are the walls of an acute-angled hyperbolic polytope.

            The Gram tensor \(G\) of the outward normals of the \(n\) walls of an
            acute-angled hyperbolic Coxeter polytope (Vinberg, *Hyperbolic
            reflection groups*) has, by definition,

            - at least three walls, \(n\geq 3\);
            - positive norms, \(G_{vv} > 0\);
            - nonpositive off-diagonal entries, \(G_{vw}\leq 0\) for \(v\neq w\),
              which is the condition that every dihedral angle is at most
              \(\pi/2\);
            - signature \((n-1, 1, 0)\).

            The signature is the pair \((p, q)\) of positive and negative indices of inertia of the symmetric
            form \(G\) on \(R^n\); \(p + q = n\) is the statement that the
            radical is zero, so the form is nondegenerate.
            """
            from sage_extensions.categories.modules.framed.formed.form_modules import FormModules

            gram = self.root_gram_tensor()
            ring = gram.base_ring()
            rank = gram.tensor_shape()[0]
            walls = self.cardinality()
            if walls < cardinal(3):
                return False
            positions = range(rank)
            if any(gram[i, i] <= 0 for i in positions):
                return False
            if any(gram[i, j] > 0 for i, j in combinations(positions, 2)):
                return False
            module = ring.free_module(self.index_set())
            normals = FormModules(ring)(
                module.bilinear_hom_space(ring)(gram)
            )
            signature = normals.signature_pair()
            return (
                signature.second() == cardinal(1)
                and signature.first() + signature.second() == walls
            )

        @validator
        def validate_acute_angled_hyperbolic_polytope_gram(self) -> None:
            r"""Check :meth:`is_acute_angled_hyperbolic_polytope_gram`."""
            if not self.is_acute_angled_hyperbolic_polytope_gram():
                raise ValueError(
                    f"the Gram tensor {self.root_gram_tensor()} of {self} is not the Gram "
                    f"tensor of the walls of an acute-angled hyperbolic Coxeter polytope: "
                    f"that needs at least three walls, positive norms, nonpositive "
                    f"off-diagonal entries and signature (n - 1, 1, 0)"
                )

        def _positions(self, left, right):
            ranking = self._index_set.ranking_map()
            return ranking(left), ranking(right)

        def vinberg_invariant(self, left, right):
            r"""Return \([4b(r,s)^2 : b(r,r)b(s,s)]\in\mathbb P^1(R)\) for the two mirrors.

            The point is the morphism \(\operatorname{Spec}R\to\mathbb P^1_R\)
            on a pair of coordinates generating \(R\) (:func:`_unimodular_pair`).
            The diagonal entry is \([4:1]\), the invariant of a mirror with
            itself: \(m_{vv}=1\) and \(4\cos^2\pi=4\).
            """
            i, j = self._positions(left, right)
            return self._projective_line_scheme().point_morphism(
                _unimodular_pair(
                    self._base_ring, self._numerators[i][j], self._denominators[i][j]
                )
            )

        def vinberg_ratio(self, left, right):
            r"""Return the dehomogenized invariant \(t=4\cos^2(\pi/m)\).

            The denominator is \(q(r)q(s)\), which is nonzero because the
            normals of mirrors are non-isotropic, so the projective point of
            :meth:`vinberg_invariant` always has an affine representative.
            """
            i, j = self._positions(left, right)
            denominator = self._denominators[i][j]
            assert denominator != 0, (
                f"the Vinberg invariant of the mirrors {left} and {right} in {self} has "
                f"denominator q(r)q(s) = 0, so one of their normals is isotropic and is "
                f"not the normal of a mirror"
            )
            return self._numerators[i][j] / denominator

        def coxeter_entry(self, left, right):
            r"""Return the Coxeter bond \(m\) between the two mirrors.

            This is the conversion to Coxeter data, and it is partial: an
            invariant that is not \(4\cos^2(\pi/m)\) for an integer \(m\) names
            a pair of mirrors at an angle no Coxeter matrix can record, and the
            conversion refuses rather than rounding to a nearby bond.  The bond is
            the order of the product of the two reflections, a cardinal, and
            \(\aleph_0\) when the mirrors do not meet.
            """
            if left == right:
                return cardinal(1)
            ratio = _engine_numeral(self._base_ring, self.vinberg_ratio(left, right))
            return cardinal(_coxeter_bond(ratio))

        def coxeter_matrix(self):
            r"""Return the Coxeter matrix \(m\colon V\times V\to\mathrm{Card}\) this invariant matrix determines.

            Its value at a pair of mirrors is :meth:`coxeter_entry`.
            """
            from sage_extensions.categories.sets.indexed_families import indexed_family

            return indexed_family(
                self._index_set**2,
                lambda pair: self.coxeter_entry(pair[0], pair[1]),
                name="Coxeter matrix",
            )

        def coxeter_diagram(self):
            r"""Return the Coxeter diagram of this invariant matrix.

            The passage forgets exactly the distinction between parallel and
            divergent mirrors, both of which the Coxeter matrix writes as
            \(m=\infty\).
            """
            return CoxeterDiagrams().from_coxeter_matrix(self.coxeter_matrix())

        def submatrix(self, mirrors):
            r"""Return the invariant matrix on the selected mirrors."""
            vertices = tuple(mirrors)
            ranking = self._index_set.ranking_map()
            positions = tuple(ranking(vertex) for vertex in vertices)
            selected = finite_ordered_set(positions)
            root_gram = (
                tensor(
                    self._root_gram.base_ring(),
                    (),
                    (selected.cardinality(), selected.cardinality()),
                    [[self._root_gram[i, j] for j in positions] for i in positions],
                )
                if self.is_rooted()
                else None
            )
            return _vinberg_invariant_matrix(
                self._base_ring,
                vertices,
                [[self._numerators[i][j] for j in positions] for i in positions],
                [[self._denominators[i][j] for j in positions] for i in positions],
                root_gram,
            )

        def weighted_graph(self):
            r"""Return the image of this invariant matrix in ``LabelledGraphs``.

            The vertices are the mirrors and an edge joins two mirrors that are
            not orthogonal, as in the scheme of a polytope (Vinberg, section
            5.2).  The label of an edge is the invariant
            \([4b(r,s)^2 : q(r)q(s)]\in\mathbb P^1(R)\) of its pair, which for
            the walls of a polytope dehomogenizes to four times the square of
            the weight of that edge in the scheme.  The label of a vertex is
            the diagonal invariant \([4:1]\).
            """
            vertices = tuple(self.vertices())
            edges = tuple(self.edges())
            return LabelledGraphs().object(
                vertices,
                edges,
                {vertex: self.vertex_label(vertex) for vertex in vertices},
                {edge: self.edge_label(edge[0], edge[1]) for edge in edges},
            )

        def is_crystallographic(self) -> bool:
            r"""Return whether every bond is \(2, 3, 4, 6\) or \(\infty\).

            The crystallographic restriction (Bourbaki VI.1.1): those are the
            bonds a reflection group preserving a lattice can realize, and in
            invariants they are \(t\in\{0,1,2,3\}\) together with \(t\geq 4\).
            """
            for left, right in combinations(self._index_set, 2):
                ratio = self.vinberg_ratio(left, right)
                if ratio < 4 and ratio not in (0, 1, 2, 3):
                    return False
            return True

        def is_simply_laced(self) -> bool:
            r"""Return whether every bond is \(2\) or \(3\).

            Equivalently every invariant is \(0\) or \(1\): all mirrors meet at
            right angles or at \(\pi/3\), which is the condition under which
            every root has the same square.
            """
            for left, right in combinations(self._index_set, 2):
                if self.vinberg_ratio(left, right) not in (0, 1):
                    return False
            return True

        def _vertex_deleted_diagrams(self):
            r"""Return the subdiagrams obtained by deleting one mirror."""
            diagram = self.coxeter_diagram()
            vertices = tuple(diagram.index_set())
            return finite_ordered_set(
                tuple(
                    diagram.induced_subdiagram(
                        tuple(other for other in vertices if other != vertex)
                    )
                    for vertex in vertices
                )
            )

        def is_elliptic(self) -> bool:
            r"""Return whether the Schlaefli form is positive definite."""
            return self.coxeter_diagram().is_elliptic()

        def is_parabolic(self) -> bool:
            r"""Return whether the Schlaefli form is positive semidefinite of corank one."""
            return self.coxeter_diagram().is_parabolic()

        def is_hyperbolic(self) -> bool:
            r"""Return whether the Schlaefli form has negative index of inertia one."""
            return self.coxeter_diagram().is_hyperbolic()

        def is_compact_hyperbolic(self) -> bool:
            r"""Return whether this is a Lannér diagram.

            Lannér's condition (Lannér 1950; Vinberg, *Hyperbolic reflection
            groups*, section 4): the diagram is hyperbolic and every proper
            subdiagram is elliptic.  Such a diagram is the diagram of a compact
            hyperbolic simplex, and its reflection group is cocompact.

            Deleting one mirror suffices to test it: a principal submatrix of a
            positive definite matrix is positive definite, so if every
            vertex-deleted subdiagram is elliptic then so is every smaller one.
            """
            if not self.is_hyperbolic():
                return False
            return all(
                subdiagram.is_elliptic()
                for subdiagram in self._vertex_deleted_diagrams()
            )

        def is_paracompact_hyperbolic(self) -> bool:
            r"""Return whether this is a quasi-Lannér diagram.

            Vinberg's condition (*Hyperbolic reflection groups*, section 4):
            the diagram is hyperbolic, every proper subdiagram has positive
            semidefinite Schlaefli form, and at least one of them is
            degenerate.  Such a diagram is the diagram of a hyperbolic simplex
            of finite volume with at least one ideal vertex, so its reflection
            group has finite covolume but is not cocompact.

            The degeneracy is stated on the index of inertia and not through
            parabolicity, because a proper subdiagram may be a direct sum of
            several affine components and so have a radical of dimension
            greater than one.
            """
            if not self.is_hyperbolic():
                return False
            deleted = self._vertex_deleted_diagrams()
            if any(subdiagram.negative_inertia_index() != 0 for subdiagram in deleted):
                return False
            return any(subdiagram.zero_inertia_index() != 0 for subdiagram in deleted)

        def _repr_(self):
            return f"Vinberg invariant matrix on {self.cardinality()} mirrors"

    def from_root_gram(self, gram, index_set=None):
        r"""Return the invariant matrix of a Gram of mirror normals.

        The numerators are \(4b(r_v,r_w)^2\) and the denominators are
        \(q(r_v)q(r_w)\), so the entries are the projective invariants of the
        pairs of mirrors and nothing is divided.  The Gram tensor is retained,
        and :meth:`ParentMethods.validate_mirror_normals` states the condition
        that it is a Gram tensor of mirror normals.
        """
        rank = gram.tensor_shape()[0]
        if index_set is None:
            index_set = range(rank)
        squares = [gram[i, i] for i in range(rank)]
        matrix = _vinberg_invariant_matrix(
            gram.base_ring(),
            tuple(index_set),
            [[4 * gram[i, j] ** 2 for j in range(rank)] for i in range(rank)],
            [[squares[i] * squares[j] for j in range(rank)] for i in range(rank)],
            gram,
        )
        matrix.validate_mirror_normals(check=False)
        return matrix

    def from_coxeter_diagram(self, diagram):
        r"""Return the invariant matrix of a Coxeter diagram.

        A rooted diagram supplies its root Gram, which is the exact integral
        datum and separates parallel mirrors from divergent ones.  An unrooted
        diagram supplies only its bonds, and the invariants are then the
        algebraic numbers \(4\cos^2(\pi/m)\), with the two open cases
        collapsed onto the single value \(4\).
        """
        if diagram.is_rooted():
            return self.from_root_gram(
                diagram.root_gram_tensor(), index_set=tuple(diagram.index_set())
            )
        vertices = tuple(diagram.index_set())
        real_algebraics = _owned_real_algebraic_numbers()
        values = [
            [
                _cross_engine_ring_value(
                    _vinberg_invariant_of_bond(diagram.coxeter_entry(left, right))
                )
                for right in vertices
            ]
            for left in vertices
        ]
        return _vinberg_invariant_matrix(
            real_algebraics,
            vertices,
            values,
            [[real_algebraics.one() for _ in vertices] for _ in vertices],
            None,
        )

    def from_invariants(self, base_ring, values, index_set=None):
        r"""Return the invariant matrix with the stated dehomogenized invariants.

        The combinatorial presentation: the caller states \(t_{vw}\) directly,
        with no mirrors behind it.  The denominators are all one, which is what
        makes these values themselves the projective points.
        """
        rows = tuple(tuple(row) for row in values)
        # The rows carry their own enumeration; the mirrors are indexed by it
        # unless the caller names them otherwise.
        row_positions = finite_ordered_set(
            tuple(position for position, _row in enumerate(rows))
        )
        mirrors = row_positions if index_set is None else finite_ordered_set(index_set)
        assert mirrors.cardinality() == row_positions.cardinality(), (
            f"the mirrors {mirrors} cannot index the invariant matrix: there are "
            f"{mirrors.cardinality()} of them, but the matrix has "
            f"{row_positions.cardinality()} rows"
        )
        return _vinberg_invariant_matrix(
            base_ring,
            tuple(mirrors),
            [[base_ring(entry) for entry in row] for row in rows],
            [[base_ring.one() for _ in mirrors] for _ in mirrors],
            None,
        )


def _vinberg_invariant_of_bond(bond):
    r"""Return \(t=4\cos^2(\pi/m)\) for a Coxeter bond ``m``, a cardinal.

    At \(m=\aleph_0\) the mirrors are parallel, \(\cos 0 = 1\), and \(t=4\).
    That is the smallest value at which the mirrors fail to meet, so the
    unrooted diagram records the parallel case and cannot record divergence.
    """
    if bond.is_countably_infinite():
        return AA(4)
    return 4 * _reflection_cosine(int(bond)) ** 2


def _vinberg_invariant_matrix(base_ring, index_set, numerators, denominators, root_gram):
    return _object_of(
        VinbergInvariantMatrices(),
        base_ring=base_ring,
        index_set=index_set,
        numerators=numerators,
        denominators=denominators,
        root_gram=root_gram,
    )


__all__ = [
    "VinbergInvariantMatrices",
    "reflection_cosines",
]
