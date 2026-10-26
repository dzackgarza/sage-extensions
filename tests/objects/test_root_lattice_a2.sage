from sage_extensions.all import *


def a2():
    return Lattices(ZZ)("A2")


def test_the_named_and_the_gram_constructions_agree() -> None:
    r"""$A_2$ in the algebraic-geometry sign convention has simple roots of square $-2$ meeting in $1$."""
    assert a2() == Lattices(ZZ)([[-2, 1], [1, -2]])


def test_the_root_system_construction_agrees() -> None:
    assert a2() == Lattices(ZZ)(CartanType(["A", 2]))


def test_the_positive_definite_gram_is_the_twist_by_minus_one() -> None:
    r"""$\begin{pmatrix}2&1\\1&2\end{pmatrix}$ is $A_2(-1)$: send $e_1 \mapsto -e_1$ in $A_2(-1)$."""
    positive = Lattices(ZZ)([[2, 1], [1, 2]])
    assert positive.is_isometric(a2().twist(-1))
    assert positive.signature_pair() == signature_pair(2, 0)
    assert positive.determinant() == 3


def test_the_categories_of_a2() -> None:
    lattice = a2()
    assert lattice in Lattices(ZZ)
    assert lattice in EvenLattices(ZZ)
    assert lattice in NondegenerateLattices(ZZ)
    assert lattice in FiniteRankLattices(ZZ)
    assert lattice in RootLattices()
    assert lattice in SymmetricBilinearFormModules(ZZ)
    assert lattice in BilinearFormModules(ZZ)
    assert lattice in FormModules(ZZ)
    assert lattice in Modules(ZZ)


def test_the_invariants_of_a2() -> None:
    r"""$\det\begin{pmatrix}-2&1\\1&-2\end{pmatrix} = 3$; negative definite of rank two; level $3$."""
    lattice = a2()
    e0, e1 = lattice.module_generator(0), lattice.module_generator(1)
    assert lattice.module_rank() == 2
    assert lattice.b(e0, e0) == -2
    assert lattice.b(e0, e1) == 1
    assert e1.b(e1) == -2
    assert lattice.b(e0 + e1, e0 + e1) == -2
    assert lattice.q(e0) == -1
    assert lattice.determinant() == 3
    assert lattice.signature_pair() == signature_pair(0, 2)
    assert lattice.is_even()
    assert lattice.is_negative_definite()
    assert not lattice.is_unimodular()
    assert lattice.level() == 3
    assert lattice.radical().module_rank() == 0
    assert tuple(int(prime) for prime in lattice.bad_reduction_primes()) == (2, 3)
    assert int(lattice.discriminant_character_discriminant()) == -3
    assert lattice.is_voronoi_perfect()


def test_the_roots_and_isometries_of_a2() -> None:
    r"""$A_2$ has six roots and $O(A_2) = W(A_2)\times\{\pm 1\}$ of order $12$ (Conway--Sloane, Ch. 4, §6.3)."""
    lattice = a2()
    assert lattice.roots().cardinality() == 6
    assert lattice.vectors_of_square(-2).cardinality() == 6
    assert lattice.Isom(lattice).cardinality() == 12
    assert Lattices(ZZ)("A1").Emb(lattice).cardinality() == 6
    assert lattice.root_sublattice().module_rank() == 2
    assert lattice.root_sublattice().determinant() == 3
    reflective = DefiniteLattices(ZZ)(lattice).reflective_roots()
    assert int(reflective.cardinality()) == 12
    assert {int(root.q()) for root in reflective} == {-2, -6}


def test_the_dual_lattice_of_a2() -> None:
    r"""$\det A_2^\vee = 1/\det A_2 = 1/3$."""
    lattice = a2()
    dual = lattice.dual_lattice()
    assert dual.module_rank() == 2
    assert dual.determinant() == 1/3
    assert lattice.dual_module().module_rank() == 2


def test_the_discriminant_group_of_a2() -> None:
    r"""$A_2^\vee/A_2 \cong \mathbb Z/3$, and it is the cokernel of the correlation $A_2 \to A_2^\vee$."""
    lattice = a2()
    assert lattice.discriminant_group().cardinality() == 3
    assert lattice.correlation_morphism().is_injective()
    assert lattice.correlation_morphism().cokernel().cardinality() == 3


def test_the_discriminant_bilinear_form_of_a2() -> None:
    r"""$G^{-1} = -\tfrac13\begin{pmatrix}2&1\\1&2\end{pmatrix}$, so a dual vector $w$ has $b(w,w) = -2/3 \equiv 1/3 \bmod \mathbb Z$, and so does $2w$."""
    form = a2().discriminant_bilinear_form()
    values = FractionFieldQuotients(ZZ)(1)
    generator = form.module_generator(0)
    one_third = values(1/3)
    assert form.cardinality() == 3
    assert form.b(generator, generator) == one_third
    assert form.b(2 * generator, 2 * generator) == one_third
    assert one_third + one_third == values(2/3)
    assert -one_third == values(2/3)
    assert 2 * one_third == values(2/3)
    assert 3 * generator == form.zero()


def test_the_discriminant_quadratic_form_of_a2() -> None:
    r"""$q(w) = -2/3 \equiv 4/3 \bmod 2\mathbb Z$, $q(2w) = -8/3 \equiv 4/3$; $O(q) = \{\pm 1\}$."""
    form = a2().discriminant_quadratic_form()
    values = FractionFieldQuotients(ZZ)(2)
    generator = form.module_generator(0)
    assert form.cardinality() == 3
    assert form.q(generator) == values(4/3)
    assert form.q(2 * generator) == values(4/3)
    assert form.O().order() == 2
    assert a2().discriminant_representation_is_surjective()


def test_the_tensor_and_divided_squares_of_a2() -> None:
    r"""For a free module of rank $2$: $M\otimes M$ has rank $4$ and $\Gamma^2 M$ rank $3$."""
    module = a2().unformed_module()
    assert Modules(ZZ).tensor_product((module, module)).module_rank() == 4
    assert module.divided_square().module_rank() == 3


def test_the_form_is_a_morphism_into_the_value_module() -> None:
    r"""A bilinear form on $M$ with values in $W$ is a morphism $M\otimes_R M \to W$."""
    lattice = a2()
    module = lattice.unformed_module()
    f0, f1 = module.module_generator(0), module.module_generator(1)
    square = Modules(ZZ).tensor_product((module, module))
    form = lattice.form()
    one = lattice.value_module().module_generator(0)
    assert lattice.value_module() == ZZ.regular_module()
    assert form.domain() is square
    assert form.codomain() is lattice.value_module()
    assert form(square.pure_tensor(f0, f1)) == one
    assert form(square.pure_tensor(f0, f0)) == -2 * one
    assert form in module.bilinear_forms(ZZ)
    assert module.bilinear_forms(ZZ)([[-2, 1], [1, -2]]) == form


def test_the_quadratic_form_is_a_morphism_out_of_the_divided_square() -> None:
    r"""$q(x e_0 + y e_1) = -x^2 + xy - y^2$, with polar form $b(e_0, e_1) = 1$."""
    module = a2().unformed_module()
    quadratic = module.quadratic_forms(ZZ)([[-1, 1], [0, -1]])
    assert quadratic.domain() is module.divided_square()
    assert quadratic.codomain() == ZZ.regular_module()


def test_a2_satisfies_the_defining_properties_of_a_lattice() -> None:
    r"""A lattice is finite free, integral-valued and nondegenerate."""
    lattice = a2()
    basis = lattice.module_generators()
    assert lattice.module_rank() == basis.cardinality() == 2
    assert all(left.b(right) in ZZ for left in basis for right in basis)
    assert lattice.is_nondegenerate()
    assert lattice.correlation_morphism().is_injective()


def test_a2_has_one_endomorphism_category() -> None:
    lattice = a2()
    endomorphisms = lattice.Mor(lattice)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert lattice.Mor(lattice) is endomorphisms
    assert lattice.End() is endomorphisms
    assert identity in endomorphisms
    assert identity * identity == identity
    assert identity.domain() is lattice
    assert identity.codomain() is lattice
