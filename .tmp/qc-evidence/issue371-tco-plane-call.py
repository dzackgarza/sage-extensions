"""#360: the plane row, the two cusp sets and the Tits-building incidence of T_Co for O(T_Co). One run."""
import time

from sage_extensions.all import *  # noqa: F401,F403


def stamp(label, start):
    print(f"[{time.strftime('%H:%M:%S')}] {label}: {round(time.time() - start, 1)} s", flush=True)


def stage(label, function):
    start = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] {label} ...", flush=True)
    value = function()
    text = repr(value)
    stamp(f"{label} = {(text[:600] + ' ...') if len(text) > 600 else text}", start)
    return value


start = time.time()
lattice = NamedLattices.Tco
print("T_Co rank", int(lattice.module_rank()), "signature", tuple(lattice.signature_pair()),
      "det", lattice.determinant(), "classes", int(lattice.discriminant_group().cardinality()),
      "|O(q)|", int(lattice.discriminant_group().orthogonal_group().order()), flush=True)
print("T_Co is_isotropic():", lattice.is_isotropic(), flush=True)
group = lattice.Aut()
stamp("setup", start)

planes = stage("isotropic_orbit_representatives(2)", lambda: group.isotropic_orbit_representatives(2))
print("PLANE ROW:", planes.cardinality(), flush=True)
for plane in planes:
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    vectors = tuple(inclusion(domain.module_generator(label)) for label in domain.module_generating_set())
    print("  plane representative:", tuple(tuple(int(entry) for entry in vector.to_vector()) for vector in vectors),
          "| primitive", plane.is_primitive(), flush=True)
    print("  divided classes of the representative:",
          [str(lattice.divided_discriminant_class(vector)) for vector in vectors], flush=True)

plane_cusps = stage("cusps(2)", lambda: group.cusps(2))
print("PLANE CUSPS:", plane_cusps.cardinality(), flush=True)

lines = stage("isotropic_orbit_representatives(1)", lambda: group.isotropic_orbit_representatives(1))
print("LINE ROW:", lines.cardinality(), flush=True)
for line in lines:
    vector = line.inclusion()(line.inclusion().domain().module_generator(line.inclusion().domain().module_generating_set()[0]))
    print("  line representative:", tuple(int(entry) for entry in vector.to_vector()),
          "| q", lattice.q(vector), "| div", lattice.divisibility(vector) if hasattr(lattice, "divisibility") else "-", flush=True)

line_cusps = stage("cusps(1)", lambda: group.cusps(1))
print("LINE CUSPS:", line_cusps.cardinality(), flush=True)

incidence = stage("tits_building_incidence()", lambda: group.tits_building_incidence())
print("INCIDENCE EDGES:", incidence.cardinality(), flush=True)
for edge in incidence:
    print("  edge: line", tuple(int(entry) for entry in edge.line().inclusion()(edge.line().inclusion().domain().module_generator(edge.line().inclusion().domain().module_generating_set()[0])).to_vector()),
          "-> plane", edge.plane(), flush=True)
stamp("whole run", start)
