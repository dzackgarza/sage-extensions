r"""The native free algebra has the module basis of all words or monomials.

Stacks, Tag 00DM: the tensor algebra is the direct sum of tensor powers,
and the symmetric algebra of a free module is the polynomial algebra.
The specified monomials below test the correspondence, not just its two
implementations composed with each other.
"""

from sage_extensions.all import *


















def test_free_forgetful_counits_evaluate_the_full_polynomial_module():
    algebra = QQ.polynomial_ring("x")
    x = algebra.algebra_generator("x")
    for adjunction in (
        Modules(QQ).tensor_algebra_adjunction(),
        Modules(QQ).symmetric_algebra_adjunction(),
    ):
        unit = adjunction.unit(algebra)
        counit = adjunction.counit(algebra)
        formal = counit.domain()
        assert formal.generating_module() is algebra
        assert unit.codomain() is formal
        assert counit.codomain() is algebra
        assert counit(unit(x**3 + 2 * x + algebra.one())) == x**3 + 2 * x + algebra.one()

        # The generator labelled by 1 in U(A) is not the unit of F(U(A)).
        # Evaluation sends both to 1; identifying them at construction would
        # not give the free algebra on the underlying module.
        constant_label, = algebra.framing_morphism().lift(algebra.one()).support().domain()
        constant_generator = formal.algebra_generator(constant_label)
        assert constant_generator != formal.one()
        assert counit(constant_generator) == algebra.one()
        assert counit(formal.one()) == algebra.one()




def test_scalar_extension_of_free_algebra_morphism_uses_the_full_word_module():
    ring_map = ZZ.Mor(QQ)(lambda scalar: QQ(scalar))
    module = ZZ.free_module(("x", "y"))
    algebra = module.tensor_algebra()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    endomorphism = algebra.Mor(algebra)(
        {"x": x * y + 2 * x, "y": y}
    )
    extension = (
        Algebras(ZZ).Associative().Unital().base_change_adjunction(ring_map).left_adjoint()
    )
    changed = extension(algebra)
    changed_map = extension(endomorphism)
    changed_x = changed.algebra_generator("x")
    changed_y = changed.algebra_generator("y")

    assert changed_map.domain() is changed
    assert changed_map.codomain() is changed
    assert changed_map(changed_x) == changed_x * changed_y + 2 * changed_x
    assert changed_map(changed_x * changed_y) == (
        changed_x * changed_y + 2 * changed_x
    ) * changed_y




def test_coproduct_of_qq_x_and_qq_y_in_commutative_algebras_is_qq_x_y():
    r"""In commutative ``QQ``-algebras, ``QQ[x] ⊔ QQ[y] = QQ[x] ⊗_QQ QQ[y] = QQ[x, y]``:
    the map to ``QQ[x, y]`` induced by ``x ↦ x``, ``y ↦ y`` is an isomorphism
    (derivation: ``Sym(M ⊕ N) = Sym M ⊗ Sym N``, and ``⊗`` is the coproduct of
    commutative algebras)."""
    left, right = QQ["x"], QQ["y"]
    coproduct = Algebras(QQ).Associative().Unital().Commutative().coproduct((left, right))
    x = coproduct.left_coproduct_map()(left.gen())
    y = coproduct.right_coproduct_map()(right.gen())
    plane = QQ["x,y"]
    comparison = coproduct.universal_morphism(
        (left.Mor(plane)({left.gen(): plane.gen(0)}), right.Mor(plane)({right.gen(): plane.gen(1)}))
    )

    assert x * y == y * x
    assert x**2 * y != x * y**2
    assert comparison(x**2 * y + 3 * y) == plane.gen(0) ** 2 * plane.gen(1) + 3 * plane.gen(1)
    assert comparison.is_isomorphism()


def test_commutative_nonunital_theory_does_not_inherit_tensor_coproduct():
    """Root commutative arrows need not identify the images of two units."""
    left, right = QQ["x"], QQ["y"]
    for theory in (Algebras(QQ), Algebras(QQ).Commutative()):
        try:
            theory.coproduct((left, right))
        except NotImplementedError:
            pass
        else:
            raise AssertionError("a unital tensor cocone was admitted in a nonunital algebra theory")
