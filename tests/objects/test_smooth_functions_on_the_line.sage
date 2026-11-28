from sage_extensions.all import *


def smooth():
    return C(oo, RR, RR)


def test_the_constructions_of_smooth_functions_agree() -> None:
    r"""$C^\infty(\mathbb R) = C^\infty(\mathbb R, \mathbb R)$."""
    assert C(oo, RR, RR) is smooth()


def test_the_categories_of_smooth_functions() -> None:
    assert smooth() in VectorSpaces(RR)
    assert smooth() in Algebras(RR)


def test_there_are_continuum_many_smooth_functions() -> None:
    r"""A continuous function is fixed by its values on $\mathbb Q$: at most $|\mathbb R|^{\aleph_0} = 2^{\aleph_0}$; the constants give at least that many."""
    assert smooth().cardinality() == continuum


def test_evaluating_a_gaussian() -> None:
    r"""$g(t) = e^{-t^2}$ has $g(0) = 1$, so $(g^2)(0) = 1$ and $(g + g)(0) = 2$."""
    maps = smooth()
    g(t) = exp(-t^2)
    gaussian = maps(g)
    assert gaussian(0) == 1
    assert (gaussian * gaussian)(0) == 1
    assert (gaussian + gaussian)(0) == 2


def test_smooth_functions_have_one_endomorphism_category() -> None:
    maps = smooth()
    endomorphisms = maps.Mor(maps)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert maps.Mor(maps) is endomorphisms
    assert identity * identity == identity


def test_formula_literals_and_captured_scalars_preserve_owned_evaluation() -> None:
    r"""For a=3/2, g(t)=a*exp(-t^2)+t/2 has g(0)=a, g'(0)=1/2,
    and g''(0)=-2a. The declaration must retain those exact formulas
    without adding a coercion from the owned scalar ring to Sage's SR.
    """
    a = QQ(3) / QQ(2)
    g(t) = a * exp(-t^2) + t / 2
    f = smooth()(g)
    assert f(RR(0)).parent() is RR
    assert f(RR(0)) == RR(3)/RR(2)
    assert f.derivative()(RR(0)) == RR(1)/RR(2)
    assert f.derivative().derivative()(RR(0)) == RR(-3)
    assert (1 / 2).parent() is QQ


def test_declared_formulas_act_on_a_cauchy_presented_real() -> None:
    r"""The sequence 5+2^-n represents 5, so t^3+t and its first two
    derivatives have values 130, 76, 30 at the limit; exp(-25) lies
    strictly between 0 and 10^-10.
    """
    sequence = Sets().Mor(NN, QQ)(lambda n: QQ(5)+QQ(1)/QQ(2)**int(n))
    point = RR.of_cauchy(sequence)
    polynomial(t) = t^3+t
    gaussian(s) = exp(-s^2)
    f, g = smooth()(polynomial), smooth()(gaussian)
    frame = RR.tangent_bundle().sections().coordinate_vector_field(RR.identity_chart(), 0)
    for value, lower, upper in ((f(point),129,131), (f.derivative()(point),75,77),
                                (frame(f)(point),75,77), (frame(frame(f))(point),29,31)):
        assert value.parent() is RR
        assert ask(value > RR(lower)) is True
        assert ask(value < RR(upper)) is True
    assert ask(g(point)>RR(0)) is True
    assert ask(g(point)<RR(QQ(1)/QQ(10000000000))) is True
