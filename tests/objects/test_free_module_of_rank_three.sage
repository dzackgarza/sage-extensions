from sage_extensions.all import *


def cube():
    return ZZ ^ 3


def on_three_points():
    return ZZ.free_module(Sets.Δ[2])


def test_the_power_and_the_rank_constructions_agree() -> None:
    assert cube() == ZZ.free_module(3)


def test_the_free_functor_and_the_ring_construction_agree() -> None:
    assert Sets().free_module(ZZ)(Sets.Δ[2]) == on_three_points()


def test_the_module_category_applied_to_a_basis_set_agrees() -> None:
    assert Modules(ZZ)(Sets.Δ[2]) == on_three_points()


def test_the_rank_and_the_basis_set_constructions_are_isomorphic() -> None:
    r"""$e_i \mapsto e_{\,i}$ identifies $\mathbb Z^3$ with the free module on $\{0, 1, 2\}$."""
    source, target = cube(), on_three_points()
    points = Sets.Δ[2]
    identification = source.Mor(target)({index: target.module_generator(points(index)) for index in (0, 1, 2)})
    assert identification.is_injective()
    assert identification.is_surjective()


def test_the_categories_of_zz3() -> None:
    module = cube()
    assert module in Modules(ZZ)
    assert module in FreeModules(ZZ)
    assert module in FinitelyGeneratedModules(ZZ)
    assert module in FinitelyPresentedModules(ZZ)
    assert module in ProjectiveModules(ZZ)


def test_the_invariants_of_zz3() -> None:
    module = cube()
    e0 = module.module_generator(0)
    assert module.base_ring() is ZZ
    assert module.module_rank() == 3
    assert module.module_generators().cardinality() == 3
    assert module.cardinality() == aleph0
    assert e0 + e0 == 2 * e0
    assert e0 - e0 == module.zero()
    assert module.is_free()
    assert module.is_torsion_free()


def test_the_dual_and_the_squares_of_zz3() -> None:
    r"""$\operatorname{rank} M^\vee = 3$, $\operatorname{rank} M\otimes M = 9$, $\operatorname{rank}\Gamma^2 M = \binom{4}{2} = 6$."""
    module = cube()
    assert module.dual_module().module_rank() == 3
    assert Modules(ZZ).tensor_product((module, module)).module_rank() == 9
    assert module.divided_square().module_rank() == 6
    assert module.exterior_algebra().graded_piece(2).module_rank() == 3


def test_a_quotient_of_zz3() -> None:
    r"""$\mathbb Z^3/\langle 2e_0, e_1, e_2\rangle \cong \mathbb Z/2$."""
    module = cube()
    e0, e1, e2 = module.module_generator(0), module.module_generator(1), module.module_generator(2)
    submodule = module.subobject_on([2 * e0, e1, e2])
    assert submodule.index() == 2
    assert (module / submodule).cardinality() == 2
    assert submodule.inclusion().cokernel().cardinality() == 2


def test_the_automorphisms_of_zz3_are_infinite() -> None:
    r"""$\operatorname{GL}_3(\mathbb Z)$ contains the elementary matrices $1 + kE_{01}$ for every $k$."""
    automorphisms = cube().Aut()
    assert automorphisms in Groups()
    assert not automorphisms.is_finite()


def test_the_base_change_to_the_rationals() -> None:
    extended = cube().base_change(ZZ.Mor(QQ)(lambda n: QQ(n)))
    assert extended in VectorSpaces(QQ)
    assert extended.module_rank() == 3


def test_zz3_has_one_endomorphism_category() -> None:
    module = cube()
    endomorphisms = module.Mor(module)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert module.Mor(module) is endomorphisms
    assert module.End() is endomorphisms
    assert identity * identity == identity
    assert identity.domain() is module
