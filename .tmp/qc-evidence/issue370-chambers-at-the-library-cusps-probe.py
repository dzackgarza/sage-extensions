"""#370 probe K: the fundamental chamber of K_I at T_Co's cusps 4 and 5, at the library's cusp vectors."""
from sage_extensions.all import HyperbolicLattices, Lattices, NamedLattices, Sterk, ZZ

Tco = NamedLattices.Tco
TEn = NamedLattices.TEn
ring = Tco.base_ring()
labels = tuple(TEn.module_generating_set())

for number in (3, 4, 5):
    cusp = Sterk.selected_isotropic_vectors()[f"Sterk_{number}"]
    coordinates = cusp.to_vector()
    given = {label: int(coordinates(label)) for label in labels}
    coefficients = {"h": ring(given["e"])} if given["e"] else {}
    for label in ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9)):
        if given[label]:
            coefficients[label] = ring(given[label])
    eta = Tco.linear_combination(coefficients)
    line = Tco.primitive_isotropic_subobject(eta)
    reduction = Lattices(ZZ)(line.isotropic_reduction())
    chamber = HyperbolicLattices(ZZ)(reduction).fundamental_chamber()
    walls = tuple(chamber.wall_roots())
    print(f"cusp {number}: K_I rank {int(reduction.module_rank())} det {reduction.determinant()} "
          f"signature {tuple(map(int, reduction.signature_pair()))}; chamber {len(walls)} walls, "
          f"norms {[int(reduction.q(wall)) for wall in walls]}")
