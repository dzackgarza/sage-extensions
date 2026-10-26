r"""Satake diagrams: a Dynkin diagram with a black node set and a diagram involution.

Let \(A=(a_{ij})_{i,j\in I}\) be the Cartan matrix of a finite-type root basis,
\(a_{ij}=\alpha_j(h_i)=2\,b(\alpha_i,\alpha_j)/b(\alpha_i,\alpha_i)\).  A Satake
diagram is the Dynkin diagram of \(A\) together with a set \(X\subseteq I\) of
black nodes and a permutation \(\tau\) of \(I\).  The pair \((X,\tau)\) is
*admissible* (Kolb, *Quantum symmetric Kac-Moody pairs*, 2014, Definition 2.3;
Araki, *On root systems and an infinitesimal classification of irreducible
symmetric spaces*, 1962, pp. 32-33) when

- \(X\) is of finite type and \(\tau\in\operatorname{Aut}(A,X)\): \(\tau\)
  preserves \(A\), \(a_{\tau i\,\tau j}=a_{ij}\), and \(\tau(X)=X\);
- (1) \(\tau^2=\mathrm{id}_I\);
- (2) \(\tau\) agrees on \(X\) with \(-w_X\), where \(w_X\) is the longest element
  of the parabolic subgroup \(W_X\);
- (3) \(\alpha_j(\rho^\vee_X)\in\mathbb{Z}\) for every \(\tau\)-fixed
  \(j\in I\setminus X\), where \(2\rho^\vee_X\) is the sum of the positive
  coroots of \(\Phi_X\).

Admissibility is the validator of the object: construction does not run it.
"""

from sage.combinat.root_system.coxeter_group import CoxeterGroup
from sage.combinat.root_system.coxeter_matrix import CoxeterMatrix
from sage.matrix.constructor import matrix as engine_matrix
from sage.modules.free_module_element import vector as engine_vector
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.coxeter_diagrams import (
    RootedCoxeterDiagrams,
    _coxeter_diagram,
    _engine_coxeter_matrix_entry,
)
from sage_extensions.categories.lattices import Lattices
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _own_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.validation import validator


def _engine_cartan_entry(diagram, left, right):
    r"""Return \(a_{ij}=2\,b(\alpha_i,\alpha_j)/b(\alpha_i,\alpha_i)\) of a rooted diagram.

    The ratio does not depend on the sign convention of the form.
    """
    ranking = diagram.index_set().ranking_map()
    i, j = ranking(left), ranking(right)
    gram = diagram.root_gram_tensor()
    rationals = _owned_rationals()
    return 2 * _engine_element(rationals, gram[i, j]) / _engine_element(rationals, gram[i, i])


def _engine_opposition_images(diagram, black):
    r"""Return the images \(\sigma(v)\) on ``black`` of \(-w_X\), as a tuple aligned with ``black``.

    \(w_X\alpha_v=-\alpha_{\sigma(v)}\), so \(w_X s_v w_X=s_{\sigma(v)}\): the
    permutation is read from conjugating the simple reflections of the finite
    Coxeter group \(W_X\) by its longest element.  Sage's reflection
    representation computes \(W_X\) and \(w_X\).
    """
    group = CoxeterGroup(
        CoxeterMatrix(
            [
                [_engine_coxeter_matrix_entry(diagram.coxeter_entry(left, right)) for right in black]
                for left in black
            ]
        ),
        implementation="reflection",
    )
    longest = group.long_element()
    reflections = group.simple_reflections()
    labels = tuple(group.index_set())
    return tuple(
        next(
            image
            for image, image_label in zip(black, labels, strict=True)
            if longest * reflections[label] * longest == reflections[image_label]
        )
        for label in labels
    )


def _engine_rho_coweight_pairings(diagram, black):
    r"""Return \(v\mapsto\alpha_v(\rho^\vee_X)\) on the vertices of ``diagram``.

    \(\rho^\vee_X=\sum_{k\in X}c_k h_k\) is characterised by
    \(\alpha_i(\rho^\vee_X)=\sum_k c_k a_{ki}=1\) for \(i\in X\) (Kolb, 2014,
    Example 2.4), so \(c\) solves \(c\,A_X=(1,\dots,1)\) and
    \(\alpha_v(\rho^\vee_X)=\sum_k c_k a_{kv}\).
    """
    cartan = engine_matrix(
        QQ, [[_engine_cartan_entry(diagram, k, i) for i in black] for k in black]
    )
    coefficients = cartan.solve_left(engine_vector(QQ, [QQ.one() for _vertex in black]))
    return lambda vertex: sum(
        (
            coefficient * _engine_cartan_entry(diagram, k, vertex)
            for coefficient, k in zip(coefficients, black, strict=True)
        ),
        QQ.zero(),
    )


class SatakeDiagrams(OwnedCategory):
    r"""Satake diagrams: a Dynkin diagram, a set of black nodes and a diagram involution.

    ``SatakeDiagrams()(D, X, tau)`` takes the Dynkin diagram ``D`` of a root
    basis (a Coxeter diagram that retains its roots), the black nodes ``X`` among its vertices,
    and a morphism ``tau`` of ``D`` to itself that the caller constructs in
    ``D.Mor(D)``.  The result is a Coxeter diagram built on the data of ``D``,
    and :meth:`ParentMethods.dynkin_diagram` returns ``D`` itself.
    """

    @classmethod
    def _repr_object_names(cls):
        return "Satake diagrams"

    def super_categories(self):
        return [RootedCoxeterDiagrams()]

    def an_object(self):
        r"""The Satake diagram of \(SU(2,1)\): \(A_2\), no black node, \(\tau\) the swap."""
        diagram = Lattices(_owned_integers())("A2").dynkin_diagram()
        first, second = diagram.vertices()
        return self(diagram, (), diagram.Mor(diagram)((second, first)))

    def _call_(self, diagram, black_nodes, involution):
        assert diagram in RootedCoxeterDiagrams(), (
            f"{diagram} is not the Dynkin diagram of a root basis: a Satake diagram decorates a "
            f"Coxeter diagram constructed with its roots, and {diagram} has none"
        )
        satake = _coxeter_diagram(
            diagram.coxeter_matrix(),
            category=self,
            names=diagram.vertex_names(),
            roots=diagram.roots(),
            root_gram=diagram.root_gram_tensor(),
            dynkin_diagram=diagram,
            black_nodes=finite_ordered_set(tuple(black_nodes)),
            involution=involution,
        )
        satake.validate_admissibility(check=False)
        return satake

    class ParentMethods:
        def __init__(self, dynkin_diagram, black_nodes, involution, **rest) -> None:
            self._dynkin_diagram = dynkin_diagram
            self._black_nodes = black_nodes
            self._involution = involution
            super().__init__(**rest)

        def __eq__(self, other):
            r"""Equality by defining data: the Dynkin diagram, the black nodes and the involution."""
            if other is self:
                return True
            if other not in SatakeDiagrams():
                return False
            return (
                self.dynkin_diagram() == other.dynkin_diagram()
                and tuple(self.black_nodes()) == tuple(other.black_nodes())
                and self.involution() == other.involution()
            )

        def __ne__(self, other):
            return not self == other

        def __hash__(self) -> int:
            return hash((self.dynkin_diagram(), self.black_nodes(), self.involution()))

        def dynkin_diagram(self):
            r"""Return the Dynkin diagram this Satake diagram decorates."""
            return self._dynkin_diagram

        def black_nodes(self):
            r"""Return the black nodes \(X\), a set of vertices of the Dynkin diagram."""
            return self._black_nodes

        def involution(self):
            r"""Return the diagram involution \(\tau\), a morphism of the Dynkin diagram to itself."""
            return self._involution

        def is_admissible(self) -> bool:
            r"""Return whether \((X,\tau)\) is admissible (Kolb, 2014, Definition 2.3)."""
            diagram = self._dynkin_diagram
            tau = self._involution
            vertices = diagram.index_set()
            black = tuple(self._black_nodes)
            if not all(vertex in vertices for vertex in black):
                return False
            if not diagram.induced_subdiagram(black).is_elliptic():
                return False
            if not all(
                _engine_cartan_entry(diagram, tau(left), tau(right))
                == _engine_cartan_entry(diagram, left, right)
                for left in vertices
                for right in vertices
            ):
                return False
            if not all(tau(vertex) in self._black_nodes for vertex in black):
                return False
            if not all(tau(tau(vertex)) == vertex for vertex in vertices):
                return False
            if not black:
                # X is empty: (2) is vacuous and rho_X^vee = 0 pairs to 0 with every root.
                return True
            opposition = _engine_opposition_images(diagram, black)
            if not all(
                tau(vertex) == image for vertex, image in zip(black, opposition, strict=True)
            ):
                return False
            pairing = _engine_rho_coweight_pairings(diagram, black)
            return all(
                pairing(vertex).denominator() == 1
                for vertex in vertices
                if vertex not in self._black_nodes and tau(vertex) == vertex
            )

        @validator
        def validate_admissibility(self) -> None:
            r"""Check that \((X,\tau)\) is admissible (Kolb, 2014, Definition 2.3; Araki, 1962)."""
            if not self.is_admissible():
                raise ValueError(
                    f"{self} is not a Satake diagram: its black nodes {self._black_nodes} and "
                    f"involution {self._involution} are not an admissible pair, which needs X of "
                    f"finite type, tau a Cartan-matrix automorphism with tau(X) = X and tau^2 = id, "
                    f"tau = -w_X on X, and alpha_j(rho_X^vee) integral at every tau-fixed white node j"
                )


__all__ = ["SatakeDiagrams"]
