r"""The Tits-building incidence of line and plane orbits on the Coble lattice (#391).

`T_Co = <2> + U(2) + E8(-2)` is the Coble period lattice, D. Dolgachev and
S. Kondo, *Enriques surfaces and Borel--Weil--Bott type duality*, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513.  `Gamma_{Co,2} =
rho^{-1}(P)` is the preimage of the stabilizer `P` of `A_{U(2)}` in `O(q)`
(research `prop:gamma-co-images`).

**The route.**  The edges at the orbit of a plane `P` are the
`Stab_{Gamma}(P)`-orbits of the isotropic lines of `P`: `P` is totally
isotropic, so every primitive line of `P` is an isotropic line of `T_Co`, and
two flags over the same plane are `Gamma`-equivalent exactly when their lines
lie in one `Stab_{Gamma}(P)`-orbit.  The lines of `P` decompose into orbits
of the plane's parabolic `Pi = Stab_{O(T_Co)}(P)` -- the divisibility of a
line of `P` is preserved by `Pi` -- and those orbits are the ambient flag
orbits read at `P`.  Within one such orbit the `Stab_{Gamma}(P)`-orbits are
the double cosets `K \ Pi / (Pi cap Stab(ell_0))` with
`K = Stab_{Gamma}(P)`, and because `Gamma` is the full preimage of its own
discriminant image the group `K` contains the kernel of `rho` on `Pi`, so
the double cosets descend to the finite image (D. Dutour Sikiri\'c and
K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  The parabolic's
family is certified complete (`is_parabolic_complete`, #331, #366), so the
stabilizer never reaches the indefinite port's generic enumeration, which is
killed at the memory guard on this lattice.  Each orbit's line is mapped to
its `Gamma`-line orbit by the line row's own cusps, and each edge joins the
line it retains to the plane it lies in.

**What is asserted.**  The construction guarantees, for every output of the
incidence call on any lattice whose plane rows return through this route:

* each edge joins a line that lies in its plane -- the edge's line term is
  contained in its plane term;
* every line orbit and every plane orbit has an edge -- each cusp of the line
  row and of the plane row appears as a vertex of some edge.

The `O(T_Co)` incidence through the same route has one edge: the ambient
group is the whole of `O(T_Co)`, so the left group of every double-coset
computation is the parabolic's own image and each plane contributes its one
transitive orbit of lines.  That is the value `main` held at `85284b8d18`.

**Where the run lives.**  The row is minutes of computation and its setup
(the subgroup, the line row, the plane row) does not fit this VM's memory
guard, so the run that decides it is the CI job
`coble-gamma-co-2-incidence-rows` (`tests/coble_gamma_co_2_incidence_rows.py`),
whose workflow file is delivered under `results/` for the orchestrator to
file; the counts it prints are the numbers the commit body records.  No
lattice-database card holds a `T_Co` value (lattice-database#7), so no count
is typed here.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _span(form, family):
    r"""The span of a finite family of classes of `A_L` over `ZZ/2ZZ`, as a set."""
    closure = {form.zero()}
    for generator in family:
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def _classes(lattice):
    r"""One class of `A_L` per named module generator: the primitive dual's class."""
    return {
        label: lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator(label)))
        for label in lattice.module_generating_set()
    }


def _decomposition(lattice):
    r"""`A_{U(2)}`, the span of the `U(2)`-generators' classes in `A_{T_Co}`."""
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    return _span(form, (classes["ep"], classes["fp"]))


def _assert_line_in_plane(line, plane) -> None:
    r"""The line term of an edge lies in the plane term of the same edge."""
    domain = line.inclusion().domain()
    label = next(iter(domain.module_generating_set()))
    assert plane.inclusion().is_in_image(line.inclusion()(domain.module_generator(label)))


def test_the_coble_gamma_co_2_incidence_joins_lines_to_their_planes() -> None:
    r"""Each edge of the Gamma_{Co,2} incidence joins a line that lies in its plane."""
    lattice = NamedLattices.Tco
    A_U2 = _decomposition(lattice)
    subgroup = lattice.Aut().discriminant_point_stabilizer(A_U2)

    incidences = subgroup.tits_building_incidence()

    lines = subgroup.cusps(1)
    planes = subgroup.cusps(2)
    for incidence in tuple(incidences):
        _assert_line_in_plane(incidence.line(), incidence.plane())
        assert incidence.line_cusp() in lines
        assert incidence.plane_cusp() in planes
    line_vertices = {incidence.line_cusp() for incidence in tuple(incidences)}
    plane_vertices = {incidence.plane_cusp() for incidence in tuple(incidences)}
    for cusp in tuple(lines):
        assert cusp in line_vertices
    for cusp in tuple(planes):
        assert cusp in plane_vertices


def test_the_coble_ambient_incidence_has_one_edge() -> None:
    r"""The O(T_Co) incidence through this route is one edge."""
    lattice = NamedLattices.Tco

    incidences = lattice.Aut().tits_building_incidence()

    assert incidences.cardinality() == cardinal(1)
    edge = tuple(incidences)[0]
    _assert_line_in_plane(edge.line(), edge.plane())
