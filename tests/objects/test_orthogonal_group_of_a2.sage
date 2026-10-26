from sage_extensions.all import *


def a2():
    return Lattices(ZZ)("A2")


def test_the_constructions_of_o_a2_agree() -> None:
    lattice = a2()
    assert lattice.O() == lattice.Aut()
    assert lattice.O() == lattice.orthogonal_group()
    assert lattice.O() == Lattices(ZZ).Aut(lattice)


def test_o_a2_is_the_dihedral_group_of_order_twelve() -> None:
    r"""$O(A_2) = W(A_2)\times\{\pm1\} \cong D_{12}$, the symmetries of the hexagon of roots (Conway--Sloane, Ch. 4, §6.3)."""
    group = a2().O()
    assert group in Groups()
    assert group in FiniteGroups()
    assert group.order() == 12
    assert group.is_isomorphic_to(Groups.D(6))
    assert not group.is_abelian()
    assert group.center().order() == 2


def test_the_special_orthogonal_group_of_a2() -> None:
    r"""$SO(A_2)$ is the rotation group of the hexagon, cyclic of order $6$."""
    special = a2().SO()
    assert special.order() == 6
    assert special.is_isomorphic_to(Groups.C(6))


def test_the_spinor_kernel_of_a2() -> None:
    r"""With Kneser's spinor norm $\theta(s_v) = (v,v)/2$, a reflection in a root of square $-2$ has spinor norm $-1$
    in $\mathbb Q^\times/\mathbb Q^{\times 2}$, and $-1 = s_{v_1}s_{v_2}$ for the orthogonal pair $v_1 = e_0$,
    $v_2 = e_0 + 2e_1$ of squares $-2, -6$ has spinor norm $3$.  So the kernel is the rotations of order dividing $3$."""
    lattice = a2()
    kernel = lattice.spinor_kernel(form_multiplier=1/2)
    assert kernel.order() == 3
    assert kernel.is_isomorphic_to(Groups.C(3))
    assert lattice.spinorial_kernel().order() == 3


def test_the_spinor_kernel_of_a2_depends_on_the_multiplier_off_so() -> None:
    r"""With the spinor norm $-(v,v)/2$ of Gritsenko--Hulek--Sankaran (arXiv:0810.1614, §1), a root reflection has
    spinor norm $1$ and a reflection in a vector of square $-6$ has $3$, so the kernel is $W(A_2)\cong S_3$.  On
    $SO(A_2)$ both conventions agree, and the spinorial kernel is the same $C_3$."""
    lattice = a2()
    kernel = lattice.spinor_kernel()
    assert kernel.order() == 6
    assert kernel.is_isomorphic_to(Groups.S(3))
    assert lattice.reflection(lattice.module_generator(0)) in kernel


def test_the_stable_orthogonal_group_of_a2() -> None:
    r"""$W(A_2)$ acts trivially on $A_2^\vee/A_2$ and $-1$ does not, so $\ker(O(A_2)\to O(q)) = W(A_2) \cong S_3$."""
    stable = a2().stable_orthogonal_group()
    assert stable.order() == 6
    assert stable.is_isomorphic_to(Groups.S(3))


def test_the_discriminant_image_of_a2() -> None:
    r"""$O(A_2)\to O(q_{A_2}) = \{\pm1\}$ is onto."""
    assert a2().discriminant_image().order() == 2


def test_the_stabilizer_of_a_discriminant_class() -> None:
    r"""$O(q_{A_2}) = \{\pm1\}$ and $-x \ne x$ for $x \ne 0$ in $\mathbb Z/3$, so the stabilizer is trivial."""
    form = a2().discriminant_quadratic_form()
    stabilizer = form.O().stabilizer(form.module_generator(0))
    assert stabilizer.order() == 1


def test_the_stabilizer_of_a_root() -> None:
    r"""$O(A_2)$ is transitive on the six roots, so a root has a stabilizer of order $12/6 = 2$."""
    lattice = a2()
    assert lattice.O().stabilizer(lattice.module_generator(0)).order() == 2


def test_a_root_reflection() -> None:
    r"""$s_r$ is an involution of determinant $-1$ acting trivially on the discriminant group."""
    lattice = a2()
    group = lattice.O()
    reflection = lattice.reflection(lattice.module_generator(0))
    assert reflection in group
    assert reflection * reflection == group.one()
    assert reflection != group.one()
    assert reflection not in lattice.SO()
    assert reflection in lattice.stable_orthogonal_group()


def test_o_a2_has_one_endomorphism_category() -> None:
    group = a2().O()
    endomorphisms = group.Mor(group)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert group.Mor(group) is endomorphisms
    assert identity * identity == identity
    assert identity.domain() is group
