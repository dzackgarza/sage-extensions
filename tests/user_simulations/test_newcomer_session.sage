r"""A newcomer's session: a Sage user who has never seen the preamble.

They type what they would type in any computer algebra system, in the
order they would think of it, and expect each line to work.  Names come
only from the star import, so a spelling the session lacks fails on its own
line with an undefined name, which is the dead end this session records.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


@pytest.mark.parametrize("radicand", [-1, 2, -5, 5, -23])
def test_a_newcomer_does_algebraic_number_theory(radicand) -> None:
    K = QuadraticField(radicand, "a")
    rendered(K)
    a = K.gen()
    assert a**2 == radicand
    OK = K.ring_of_integers()
    rendered(OK)
    assert OK.integral_basis().cardinality() == cardinal(2)
    assert K.discriminant() == OK.discriminant()
    h = K.class_number()
    Cl = K.class_group()
    rendered(Cl)
    assert Cl.order() == h
    U = K.unit_group()
    rendered(U)
    assert U.module_rank() == cardinal(1 if radicand > 0 else 0)
    G = K.galois_group()
    rendered(G)
    assert G.order() == 2
    sigma = G.gen()
    assert sigma(a) == -a
    for p in primes(2, 20):
        factorization = OK.ideal(p).factor()
        rendered(factorization)
        assert sum(P.ramification_index() * P.residue_degree() for P in OK.ideal(p).prime_factors()) == 2
        assert all(P.norm() == p ** P.residue_degree() for P in OK.ideal(p).prime_factors())
    P = OK.ideal(2).prime_factors()[0]
    Kp = K.completion(P)
    rendered(Kp)
    assert Kp.residue_field().characteristic() == 2
    assert K.zeta_function()(2) > 1


@pytest.mark.parametrize("n", [3, 4, 5])
def test_a_newcomer_does_finite_group_theory(n) -> None:
    G = SymmetricGroup(n)
    rendered(G)
    assert G.order() == factorial(n)
    assert G.center().order() == (1 if n > 2 else 2)
    A = G.commutator_subgroup()
    assert A.order() == factorial(n) / 2
    assert A.is_normal(G)
    assert (G / A).order() == 2
    assert G.is_solvable() == (n < 5)
    assert G.character_table().nrows() == G.conjugacy_classes().cardinality()
    H = G.stabilizer(1)
    assert H.order() == factorial(n - 1)
    assert G.cosets(H).cardinality() == cardinal(n)
    assert H.is_isomorphic_to(SymmetricGroup(n - 1))
    P = G.sylow_subgroup(2)
    assert G.order() % P.order() == 0
    assert G.abelianization().order() == 2
    QG = QQ[G]
    rendered(QG)
    assert QG.dimension() == factorial(n)
    assert QG.center().dimension() == G.conjugacy_classes().cardinality()
    V = G.permutation_representation(QQ)
    rendered(V)
    assert V.dimension() == n
    assert V.character()(G.one()) == n
    assert V.decompose().cardinality() == cardinal(2)
    assert V.invariants().dimension() == 1


@pytest.mark.parametrize("field_name", ["QQ", "GF(5)", "GF(7)"])
def test_a_newcomer_does_plane_curves(field_name) -> None:
    k = {"QQ": QQ, "GF(5)": GF(5), "GF(7)": GF(7)}[field_name]
    R = k.polynomial_ring(("x", "y"))
    x, y = R.algebra_generators()
    E = Curves(k).from_equation(y**2 - x**3 - x)
    rendered(E)
    assert E.genus() == 1
    assert E.is_smooth()
    assert E.dimension() == 1
    C = Curves(k).from_equation(y**2 - x**3)
    assert C.geometric_genus() == 0
    assert not C.is_smooth()
    assert C.singular_points().cardinality() == cardinal(1)
    Ebar = E.projective_closure()
    rendered(Ebar)
    assert Ebar.genus() == 1
    if k.is_finite():
        q = k.order()
        assert abs(Ebar.count_points() - (q + 1)) <= 2 * sqrt(q)
        assert Ebar.zeta_function().denominator().degree() == 2
    else:
        assert Ebar.rational_points(bound=5).cardinality() >= cardinal(2)
    J = Ebar.jacobian()
    assert J.dimension() == 1
    D = Ebar.divisor(Ebar.point((0, 0, 1)))
    assert D.degree() == 1
    assert Ebar.riemann_roch_space(2 * D).dimension() == 2
    assert Ebar.canonical_divisor().degree() == 0
    Omega = E.differentials()
    rendered(Omega)
    assert Omega.dimension() == 1


@pytest.mark.parametrize("rank", [2, 3, 4])
def test_a_newcomer_does_linear_algebra_over_a_pid(rank) -> None:
    M = ZZ**rank
    rendered(M)
    assert M.module_rank() == cardinal(rank)
    A = matrix(ZZ, rank, rank, lambda i, j: (i + 1) * (j + 1) + (1 if i == j else 0))
    rendered(A)
    f = M.hom(A)
    assert f.domain() == M
    assert f.matrix() == A
    assert f.kernel().module_rank() == rank - A.module_rank()
    assert f.image().module_rank() == A.module_rank()
    Q = M / f.image()
    rendered(Q)
    assert Q.order() == abs(A.determinant())
    assert Q.invariants() == A.elementary_divisors()
    assert A.smith_form()["diagonal"].diagonal() == A.elementary_divisors()
    N = M.submodule([M.gen(0) * 2, M.gen(1)])
    assert N.module_rank() == cardinal(2)
    assert (M / N).torsion_subgroup().order() == 2
    assert M.tensor_product(Q).order() == Q.order() ** rank
    assert Hom(M, ZZ).module_rank() == cardinal(rank)
    assert Hom(Q, ZZ).order() == 1
    assert Q.ext(ZZ, 1).order() == Q.order()
    assert Q.tor(Q, 1).order() == Q.order()
    L = IntegralLattice(A + A.transpose())
    rendered(L)
    assert L.module_rank() == cardinal(rank)
    assert L.determinant() == (A + A.transpose()).determinant()
    assert L.discriminant_group().order() == abs(L.determinant())
    assert L.automorphism_group().order() >= 2
    assert L.index_in(L.dual_lattice()) == abs(L.determinant())


def test_a_newcomer_does_commutative_algebra() -> None:
    R = QQ.polynomial_ring(("x", "y", "z"))
    x, y, z = R.algebra_generators()
    I = R.ideal(x * y, y * z, x * z)
    rendered(I)
    assert I.dimension() == 1
    assert I.primary_decomposition().cardinality() == cardinal(3)
    assert I.radical() == I
    assert I.is_radical()
    assert not I.is_prime()
    assert I.minimal_associated_primes().cardinality() == cardinal(3)
    assert I.hilbert_polynomial()(10) == 31
    assert I.hilbert_series().numerator().degree() <= 3
    assert I.groebner_basis().cardinality() == cardinal(3)
    assert R.quotient(I).krull_dimension() == 1
    assert R.quotient(I).is_reduced()
    assert not R.quotient(I).is_integral_domain()
    J = R.ideal(x**2, y**2)
    assert J.saturation(R.ideal(x, y)).is_one()
    assert (I + J).dimension() == 1
    assert (I * J).is_subideal(I.intersection(J))
    assert R.ideal(x, y, z).is_maximal()
    assert R.ideal(x, y, z).residue_field() == QQ
    S = R.localization(R.ideal(x, y, z))
    rendered(S)
    assert S.is_local()
    assert S.is_regular()
    assert S.dimension() == 3
    assert S.embedding_dimension() == 3
    assert R.completion(R.ideal(x, y, z)).is_complete()
    assert R.derivation_module().module_rank() == cardinal(3)
    assert R.differentials().module_rank() == cardinal(3)
    assert R.jacobian_matrix((x * y, y * z)).nrows() == 2
    assert (R.quotient(I)).affine_spectrum().irreducible_components().cardinality() == cardinal(3)
    assert (R.quotient(I)).affine_spectrum().dimension() == 1
    assert Proj(R).dimension() == 2
    assert Proj(R / I).dimension() == 0
    assert Proj(R / I).degree() == 3
