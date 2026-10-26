from sage_extensions.all import *


def two_planes():
    return Lattices(ZZ)("U") + Lattices(ZZ)("U")


def test_the_sum_and_the_power_agree() -> None:
    assert two_planes() == Lattices(ZZ)("U") ^ 2


def test_the_sum_and_the_block_gram_agree() -> None:
    gram = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]
    assert two_planes() == Lattices(ZZ)(gram)


def test_the_categories_of_u_plus_u() -> None:
    lattice = two_planes()
    assert lattice in Lattices(ZZ)
    assert lattice in EvenLattices(ZZ)
    assert lattice in DirectSumObjects(Lattices(ZZ))


def test_the_invariants_of_u_plus_u() -> None:
    lattice = two_planes()
    assert lattice.module_rank() == 4
    assert lattice.determinant() == 1
    assert lattice.signature_pair() == signature_pair(2, 2)
    assert lattice.is_unimodular()
    assert lattice.summands().cardinality() == 2


def test_the_orthogonal_group_is_infinite() -> None:
    assert not two_planes().O().is_finite()


def test_primitive_isotropic_vectors_form_one_orbit() -> None:
    r"""On a lattice containing $U\oplus U$, primitive vectors of equal square and equal class $v/\operatorname{div}(v)$ in $A_L$ form one orbit (Eichler); $A_L = 0$ here."""
    assert two_planes().isotropic_line_orbit_representatives().cardinality() == 1


def test_an_isotropic_plane_and_its_stabilizer() -> None:
    r"""$P = \langle e_1, e_2\rangle$ is totally isotropic and primitive.  The maps $e_i \mapsto e_i$,
    $f_1 \mapsto f_1 + k e_2$, $f_2 \mapsto f_2 - k e_1$ are isometries fixing $P$ for every $k \in \mathbb Z$."""
    lattice = two_planes()
    e1, e2 = lattice.module_generator(0), lattice.module_generator(2)
    plane = lattice.primitive_isotropic_subobject(e1, e2)
    assert plane.module_rank() == 2
    assert plane.is_totally_isotropic()
    assert plane.is_primitive()
    assert not lattice.O().stabilizer(plane).is_finite()


def test_an_isotropic_flag_and_its_stabilizer() -> None:
    r"""The same unipotent isometries fix $\langle e_1\rangle \subset \langle e_1, e_2\rangle$ pointwise."""
    lattice = two_planes()
    e1, e2 = lattice.module_generator(0), lattice.module_generator(2)
    flag = lattice.isotropic_flag(e1, e2)
    assert not lattice.O().stabilizer(flag).is_finite()


def test_u_plus_u_has_one_endomorphism_category() -> None:
    lattice = two_planes()
    endomorphisms = lattice.Mor(lattice)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert lattice.Mor(lattice) is endomorphisms
    assert identity * identity == identity
