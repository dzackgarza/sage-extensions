r"""#307: the rational hyperbolic triangle's acute-angle predicate, through the owned object.

The rational triangle with angles $(\pi/2, \pi/3, 0)$ has mirror normals of Gram

    [[1, -1/2, 0], [-1/2, 1, -1], [0, -1, 1]]

over $\mathbb Q$, so it is an acute-angled hyperbolic Coxeter polytope: positive norms,
nonpositive off-diagonal entries, and signature $(2, 1, 0)$.  The public predicate must
answer that from the retained Gram, and the order it reads the entries with is the owned
rational field's.

Reported failure (lattice-database#18, provider 7494af73): the predicate reaches
``vinberg_invariants.py:343`` and raises ``TypeError: '<=' not supported between instances
of 'OwnedJoinCategory.element_class' and 'OwnedJoinCategory.element_class'``.
"""

from sage_extensions.all import *  # noqa: F401,F403

RATIONAL_TRIANGLE_GRAM = (
    (1, QQ(-1) / 2, 0),
    (QQ(-1) / 2, 1, -1),
    (0, -1, 1),
)


def _invariant_matrix():
    gram = tensor(QQ, (), (3, 3), RATIONAL_TRIANGLE_GRAM)
    return VinbergInvariantMatrices().from_root_gram(gram)


def test_the_owned_rationals_are_ordered() -> None:
    r"""$\mathbb Q$ is an ordered field: its elements compare, as $\mathbb Z$'s do."""
    assert QQ(1) > QQ(0)
    assert QQ(0) <= QQ(0)
    assert QQ(-1) / 2 < QQ(0)


def test_the_rational_triangle_is_an_acute_angled_hyperbolic_polytope() -> None:
    r"""Three walls, positive norms, nonpositive off-diagonal entries, signature $(2, 1)$."""
    matrix = _invariant_matrix()

    assert matrix.is_rooted() is True
    assert matrix.is_acute_angled_hyperbolic_polytope_gram() is True
