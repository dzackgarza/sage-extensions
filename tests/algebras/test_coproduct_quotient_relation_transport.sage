"""The coproduct of two presented commutative algebras retains both ideals.

Over QQ, QQ[x]/(x²) tensor QQ[y]/(y²-y) is
QQ[x,y]/(x²,y²-y). The independent relations do not impose xy=0.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_presented_commutative_coproduct_transports_both_relation_ideals():
    P = QQ["x"]
    Q = QQ["y"]
    A = P.quotient_by_relations((P.algebra_generator("x")**2,))
    B = Q.quotient_by_relations((Q.algebra_generator("y")**2 - Q.algebra_generator("y"),))
    category = Algebras(QQ).Associative().Unital().Commutative()
    C = category.coproduct((A, B))
    i, j = C.coproduct_injection(0), C.coproduct_injection(1)
    x = i(A.algebra_generator("x"))
    y = j(B.algebra_generator("y"))
    assert x**2 == C.zero()
    assert y**2 == y
    assert x * y != C.zero()

    T = QQ["t"]
    t = T.algebra_generator("t")
    target = T.quotient_by_relations((t**2,))
    f = A.Mor(target)({"x": target.algebra_generator("t")})
    g = B.Mor(target)({"y": target.one()})
    mediator = C.from_cocone(f, g)
    assert mediator * i == f
    assert mediator * j == g
    assert mediator(x * y) == target.algebra_generator("t")


def test_presented_commutative_coproduct_functor_respects_factor_maps():
    P = QQ["x"]
    Q = QQ["y"]
    A = P.quotient_by_relations((P.algebra_generator("x")**2,))
    B = Q.quotient_by_relations((Q.algebra_generator("y")**2 - Q.algebra_generator("y"),))
    category = Algebras(QQ).Associative().Unital().Commutative()
    coproduct = category.coproduct_functor()
    pair = coproduct.domain()(A, B)
    C = coproduct(pair)
    left_map = A.Mor(A)({"x": A.zero()})
    right_map = B.Mor(B)({"y": B.one() - B.algebra_generator("y")})
    pair_map = coproduct.domain().Mor(pair, pair)(left_map, right_map)
    induced = coproduct(pair_map)
    x = C.left_coproduct_map()(A.algebra_generator("x"))
    y = C.right_coproduct_map()(B.algebra_generator("y"))
    assert induced(x) == C.zero()
    assert induced(y) == C.one() - y
    assert induced(x * y) == C.zero()
    assert induced * C.left_coproduct_map() == C.left_coproduct_map() * left_map
    assert induced * C.right_coproduct_map() == C.right_coproduct_map() * right_map
