r"""Relative projectivization `\mathbb{P}(\mathcal{F}) = \operatorname{Proj} \operatorname{Sym} \mathcal{F}`.

Source: Hartshorne, *Algebraic Geometry*, II.7 (definition, `\mathbb{P}(\mathcal{O}^{n+1})
= \mathbb{P}^n \times X`) and V.2.8--V.2.9 (for a rank-2 bundle `\mathcal{F}` on a
curve, `\operatorname{Pic} \mathbb{P}(\mathcal{F}) = \mathbb{Z}\xi \oplus \pi^*
\operatorname{Pic}` and `\xi^2 = \deg \mathcal{F}` with `\xi = c_1(\mathcal{O}(1))`).
"""

from sage_extensions.all import *


def test_projectivization_of_a_non_locally_free_sheaf_jumps_at_its_torsion() -> None:
    r"""For `\mathcal{F} = \mathcal{O} u \oplus \mathcal{O} v / (x u)` on `\mathbb{A}^1`,
    `\operatorname{Sym} \mathcal{F} = \mathbb{Q}[x][u, v]/(xu)`: over `x = 0` the fibre
    is `\mathbb{P}^1`, over `x = 1` it is the single point `u = 0`."""
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_ring()
    x = ring.algebra_generator("x")
    free = ring.free_module(("u", "v"))
    module = free.quotient(free.submodule((x * free.module_generator("u"),)))
    projection = line.associated_module_sheaf(module).projectivization()

    over_origin = projection.fiber(line.point((0,)))
    over_one = projection.fiber(line.point((1,)))
    assert over_origin.is_isomorphic(ProjectiveSpaces(QQ)(1))
    assert over_one.relative_dimension() == 0
    assert over_one.coordinate_ring().dimension() == 1


def test_projectivization_of_a_rank_two_free_module_over_a_field_is_the_projective_line() -> None:
    point = QQ.affine_spectrum()
    total = point.associated_module_sheaf(QQ.free_module(("s", "t"))).projectivization().domain()

    assert total.is_isomorphic(ProjectiveSpaces(QQ)(1))


def test_projectivization_of_the_trivial_rank_two_bundle_on_the_line_is_the_quadric() -> None:
    r"""`\mathbb{P}(\mathcal{O}^2)` over `\mathbb{P}^1` is `\mathbb{P}^1 \times \mathbb{P}^1`
    over the first factor, and `\xi^2 = \deg \mathcal{O}^2 = 0`."""
    line = ProjectiveSpaces(QQ)(1)
    projection = line.O(0).direct_sum(line.O(0)).projectivization()
    total = projection.domain()
    xi = total.tautological_line_bundle().first_chern_class()

    assert projection.codomain() is line
    assert total.is_isomorphic(Schemes(QQ).product((line, line)))
    assert total.picard_group().module_rank() == 2
    assert total.intersection_number(xi, xi) == 0


def test_projectivization_of_o_plus_o_one_on_the_line_is_the_first_hirzebruch_surface() -> None:
    r"""`\mathbb{P}(\mathcal{O} \oplus \mathcal{O}(1))` has Picard rank 2, `\xi^2 = 1`,
    and `K^2 = 8` (it is `\mathbb{F}_1 = \mathrm{Bl}_p \mathbb{P}^2`)."""
    line = ProjectiveSpaces(QQ)(1)
    total = line.O(0).direct_sum(line.O(1)).projectivization().domain()
    xi = total.tautological_line_bundle().first_chern_class()
    canonical = total.canonical_class()
    plane = ProjectiveSpaces(QQ)(2)

    assert total.picard_group().module_rank() == 2
    assert total.intersection_number(xi, xi) == 1
    assert total.intersection_number(canonical, canonical) == 8
    assert total.is_isomorphic(plane.blowup(plane.point((0, 0, 1))))


def test_map_induced_by_multiplication_by_x_is_defined_exactly_on_d_x() -> None:
    r"""`x: \mathcal{O} \to \mathcal{O}` on `\mathbb{A}^1` induces a rational map
    `\mathbb{P}(\mathcal{O}) \dashrightarrow \mathbb{P}(\mathcal{O})` defined exactly
    where the map is surjective, the preimage of `D(x)`."""
    line = AffineSpaces(QQ)(1, names=("x",))
    x = line.coordinate_ring().algebra_generator("x")
    structure = line.structure_sheaf()
    multiplication = x * structure.Mor(structure).identity()
    projection = structure.projectivization()

    locus = multiplication.projectivization_map().domain_of_definition()
    assert locus == projection.inverse_image(line.distinguished_open(x))
