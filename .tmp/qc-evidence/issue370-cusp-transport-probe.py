"""#298/#370 probe G: the library-shaped routes.

G1  The canonical cusp-5 identification: U + E8(-2) -> T_En lands in eta_5^perp and its classes span
    K_J (the pairings of the images equal the model's Gram).
G2  The cusp-4 identification through `sublattice_from` + the embedding Mor, with the class lifted to
    T_En through the reduction's coordinate frame.
G3  The class counts and the (-2) classes at T_Co for both cusps.
"""
import json
import time
from pathlib import Path

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage.matrix.constructor import matrix  # noqa: E402
from sage.rings.integer_ring import ZZ as SageZZ  # noqa: E402
from sage.rings.rational_field import QQ  # noqa: E402
from sage_extensions.all import (  # noqa: E402
    Embeddings,
    Lattices,
    NamedLattices,
    Sterk,
    ZZ,
)
from sage_extensions.tensors.tensor import _engine_component_matrix  # noqa: E402

TdP = NamedLattices.TdP
TEn = NamedLattices.TEn
Tco = NamedLattices.Tco
UE82 = NamedLattices.U_E8_2


def card(section, tag):
    digest = Path("/repos/sage-extensions/tests/cards/lattice-database-enriques.json")
    return json.loads(digest.read_text(encoding="utf-8"))[section][tag]


def gram(lattice):
    return _engine_component_matrix(lattice.gram_tensor()).change_ring(QQ)


def coordinates(lattice, vector):
    labels = tuple(lattice.module_generating_set())
    given = vector.to_vector()
    return [int(given(label)) for label in labels]


def family_gram(lattice, vectors):
    rows = [coordinates(lattice, vector) for vector in vectors]
    C = matrix(SageZZ, rows)
    return C * gram(lattice) * C.transpose()


def lift_class(line, reduction, class_vector):
    frame = reduction.coordinate_frame()
    given = class_vector.to_vector()
    lift = None
    for label in reduction.module_generating_set():
        coefficient = int(given(label))
        if coefficient:
            piece = coefficient * frame[label]
            lift = piece if lift is None else lift + piece
    assert lift is not None
    assert reduction.projection()(lift) == class_vector
    return line.isotropic_perpendicular().inclusion()(lift)


names = ["e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]
rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
cusp_vectors_en = Sterk.selected_isotropic_vectors()
labels_ten = tuple(TEn.module_generating_set())
basis_ten = {label: TEn.module_generator(label) for label in labels_ten}
delta = basis_ten["e"] - basis_ten["f"]


def report(number, vectors):
    print("=" * 20, f"cusp {number}")
    eta = cusp_vectors_en[f"Sterk_{number}"]
    line = TEn.primitive_isotropic_subobject(eta)
    reduction = line.isotropic_reduction()
    classes = [lift_class(line, reduction, reduction.projection().codomain()(0)) for _ in ()]
    print("  eta pairings of the lifted vectors", [TEn.b(vector, eta) for vector in vectors])
    inside = [vector for vector in vectors if TEn.b(vector, delta) == ZZ.zero()]
    print("  vectors lying in T_Co", len(inside), "squares", [TEn.q(vector) for vector in inside])
    negative_two = [vector for vector in inside if TEn.q(vector) == -ZZ(2)]
    print("  of those, (-2)", len(negative_two))


# ---- G1: cusp 5 through the library embedding --------------------------------------
print("G1: cusp 5")
model5, printed5 = Sterk.sterk5_in_U_E8_2()
eta5 = cusp_vectors_en["Sterk_5"]
line5 = TEn.primitive_isotropic_subobject(eta5)
reduction5 = line5.isotropic_reduction()
into_ten = Embeddings.U_E8_2_into_TEn
images5 = [into_ten(root) for root in printed5]
print("  model Gram == image Gram:", family_gram(model5, printed5) == family_gram(TEn, images5))
print("  det model", family_gram(model5, printed5).det(), "det images",
      family_gram(TEn, images5).det())
print("  is_isometric_to(model5, K_J):", reduction5.is_isometric_to(model5))
report(5, images5)

# ---- G2: cusp 4 through sublattice_from and the embedding Mor ----------------------
print("G2: cusp 4")
printed4 = tuple(Sterk.sterk_roots()["Sterk_4"])
start = time.time()
span = TdP.sublattice_from(printed4)
stamp(f"  sublattice_from in {round(time.time() - start, 2)}s rank {int(span.module_rank())} "
      f"det {span.determinant()} signature {tuple(map(int, span.signature_pair()))}")
eta4 = cusp_vectors_en["Sterk_4"]
line4 = TEn.primitive_isotropic_subobject(eta4)
reduction4 = line4.isotropic_reduction()
start = time.time()
embeddings = span.Emb(reduction4)
print("  is_empty:", embeddings.is_empty(), "in", round(time.time() - start, 2), "s")
start = time.time()
identification = embeddings.an_element()
stamp(f"  an_element in {round(time.time() - start, 2)}s")

labels_span = tuple(span.module_generating_set())
labels_reduction = tuple(reduction4.module_generating_set())
columns = []
for label in labels_span:
    given = identification(span.module_generator(label)).to_vector()
    columns.append([int(given(target)) for target in labels_reduction])
transport = matrix(SageZZ, [[column[row] for column in columns] for row in range(len(labels_reduction))])
print("  transport det", transport.det())

span_basis = [coordinates(TdP, span.inclusion()(span.module_generator(label))) for label in labels_span]
system = matrix(QQ, [[column[row] for column in span_basis] for row in range(len(labels_ten) + 8)])
images4 = []
for root in printed4:
    target = matrix(QQ, 20, 1, coordinates(TdP, root))
    solution = system.solve_right(target)
    assert all(entry.denominator() == 1 for entry in solution.list())
    transported = [sum(int(transport[row, column]) * int(solution[column, 0])
                       for column in range(len(labels_span)))
                   for row in range(len(labels_reduction))]
    class_ = reduction4.linear_combination(
        {label: reduction4.base_ring()(value)
         for label, value in zip(labels_reduction, transported) if value}
    )
    images4.append(lift_class(line4, reduction4, class_))
print("  printed Gram == transported Gram:",
      family_gram(TdP, printed4) == family_gram(TEn, images4))
report(4, images4)
stamp("done")
