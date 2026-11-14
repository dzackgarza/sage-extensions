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


def test_the_rational_valued_form_is_linear_over_its_own_scalars() -> None:
    r"""The defining law: $b(r x, y) = r\,b(x, y) = b(x, r y)$ for $r\in\mathbb Q$.

    This is the adjunction the semilinear arrow carries: the scalar map of the
    rational-valued form is the identity of $\mathbb Q$, so the arrow is
    $\mathbb Q$-linear on both sides, not $\mathbb Z$-linear.
    """
    gram = tensor(QQ, (), (3, 3), RATIONAL_TRIANGLE_GRAM)
    module = Modules(QQ)(QQ.free_module(Sets.Δ[2]))
    assert module.base_ring() is QQ
    form = module.bilinear_hom_space(QQ)(gram)

    left = module.module_generator(0)
    right = module.module_generator(1)
    scalar = QQ(-2) / 3
    value = form(left, right)
    assert form(module.scalar_multiple(scalar, left), right) == scalar * value
    assert form(left, module.scalar_multiple(scalar, right)) == scalar * value
    assert value != QQ.zero()


def test_the_rational_valued_form_carries_the_pairing_s_own_scalar_action() -> None:
    r"""The value object's selected action is over $\mathbb Q$, the ring the form is over.

    ``module.bilinear_hom_space(QQ)`` records a member of
    $\operatorname{Hom}_{\mathbb Q}(M\otimes_{\mathbb Q} M, W)$, so ``W``'s
    selected scalar action $\rho_W$ has $\mathbb Q$ as its domain -- that is what
    makes evaluating it at a rational coefficient an action of the selected
    structure rather than a multiplication supplied from outside it.  A pairing
    read over the ring object instead has $\rho_W$ over $\mathbb Z$, and then a
    rational coefficient has no image in $\rho_W$'s domain at all: the two agree
    numerically where the base ring can read the scalar, so no numeric example
    distinguishes them, but the action the morphism is over is not the action the
    value object carries.  No second action is needed to repair that: the ring
    owner already states the reading, $W = {}_R R$ with
    ``regular_module_isomorphism()`` the exact $r e_0 \mapsto r$.
    """
    gram = tensor(QQ, (), (3, 3), RATIONAL_TRIANGLE_GRAM)
    module = Modules(QQ)(QQ.free_module(Sets.Δ[2]))
    form = module.bilinear_hom_space(QQ)(gram)
    value_module = form.codomain()

    assert value_module.base_ring() is QQ
    assert value_module.scalar_action().domain() is QQ
    assert value_module is QQ.regular_module()

    # The readers' conversion is the ring owner's own identification, explicit.
    identification = QQ.regular_module_isomorphism()
    left = module.module_generator(0)
    right = module.module_generator(1)
    assert form.gram_tensor().base_ring() is QQ
    assert identification(form(left, right)) == QQ(-1) / 2

    # And evaluation at a rational scalar is that selected action.
    scalar = QQ(-2) / 3
    assert identification(form(module.scalar_multiple(scalar, left), right)) == scalar * (QQ(-1) / 2)
    assert identification(form(left, module.scalar_multiple(scalar, right))) == scalar * (QQ(-1) / 2)
