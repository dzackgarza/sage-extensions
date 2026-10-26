from sage_extensions.all import *


def group():
    return Groups.C(2)


def group_algebra():
    return ZZ[group()]


def permutation_module():
    r"""$\mathbb Z^2$ with the generator of $C_2$ swapping the coordinates."""
    plane = ZZ ^ 2
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    swap = plane.Mor(plane)({0: e1, 1: e0})
    return Modules(group_algebra())(plane, lambda g, v: v if g == group().one() else swap(v))


def test_the_permutation_module_is_the_regular_module() -> None:
    r"""$C_2$ acts simply transitively on the two coordinates, so $\mathbb Z^2 \cong \mathbb Z[C_2]$."""
    assert permutation_module().is_isomorphic_to(group_algebra().regular_module())


def test_the_coinduced_module_is_the_regular_module() -> None:
    r"""$\operatorname{Hom}_{\mathbb Z}(\mathbb Z[C_2], \mathbb Z) \cong \mathbb Z[C_2]$ for a finite group."""
    structure = group_algebra().algebra_structure_morphism()
    coinduced = Modules(ZZ).coextension_of_scalars(structure)(ZZ ^ 1)
    assert coinduced in Modules(group_algebra())
    assert coinduced.is_isomorphic_to(group_algebra().regular_module())


def test_the_induced_module_is_the_regular_module() -> None:
    r"""$\mathbb Z[C_2]\otimes_{\mathbb Z}\mathbb Z = \mathbb Z[C_2]$."""
    structure = group_algebra().algebra_structure_morphism()
    induced = Modules(ZZ).extension_of_scalars(structure)(ZZ ^ 1)
    assert induced.is_isomorphic_to(group_algebra().regular_module())


def test_the_categories_of_the_permutation_module() -> None:
    module = permutation_module()
    assert module in Modules(group_algebra())
    assert module.group() is group()


def test_the_action_on_the_permutation_module() -> None:
    module = permutation_module()
    e0 = module.module_generator(0)
    e1 = module.module_generator(1)
    assert module.action_of(group().one())(e0) == e0
    assert module.is_invariant(e0 + e1)
    assert not module.is_invariant(e0)


def test_the_invariants_and_coinvariants() -> None:
    r"""$(\mathbb Z^2)^{C_2} = \mathbb Z(e_0 + e_1)$ and $(\mathbb Z^2)_{C_2} = \mathbb Z^2/(e_0 - e_1) \cong \mathbb Z$."""
    module = permutation_module()
    invariants = module.module_invariants()
    coinvariants = module.module_coinvariants()
    assert invariants.module_rank() == 1
    assert invariants in Modules(ZZ)
    assert coinvariants.module_rank() == 1
    assert coinvariants.is_torsion_free()


def test_the_underlying_integral_module() -> None:
    structure = group_algebra().algebra_structure_morphism()
    assert permutation_module().restrict_scalars(structure).module_rank() == 2


def test_the_permutation_module_has_one_endomorphism_category() -> None:
    module = permutation_module()
    endomorphisms = module.Mor(module)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert module.Mor(module) is endomorphisms
    assert identity * identity == identity
