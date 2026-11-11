"""The block basis after the cokernel-completion repair, and the T_Co parabolic's factors."""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.integer_ring import ZZ as SageZZ


def stamp(label, start):
    print(f"[{time.strftime('%H:%M:%S')}] {label}: {round(time.time() - start, 1)} s", flush=True)


def stage(label, function):
    start = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] {label} ...", flush=True)
    try:
        value = function()
    except Exception as error:  # noqa: BLE001
        stamp(f"{label} RAISED {type(error).__name__}: {error}", start)
        return None
    text = repr(value)
    if len(text) > 400:
        text = text[:400] + " ..."
    stamp(f"{label} = {text}", start)
    return value


def index_of_block_basis(plane):
    basis = plane.plane_block_basis()
    rows = [plane.coordinates(vector) for vector in basis]
    return len(rows), abs(int(sage_matrix(SageZZ, rows).determinant()))


start = time.time()
enriques = NamedLattices.TEn
labels = tuple(enriques.module_generating_set())
first, second, third = (enriques.module_generator(labels[position]) for position in (0, 1, 2))
w = enriques.module_generator(labels[4]) + enriques.module_generator(labels[5])
for name, plane in (("T_En P1", enriques.primitive_isotropic_subobject(first, third)),
                    ("T_En P2", enriques.primitive_isotropic_subobject(2 * first + 2 * second + w, third))):
    stage(f"{name} block basis (rows, |det|)", lambda plane=plane: index_of_block_basis(plane))
stamp("T_En", start)

start = time.time()
coble = NamedLattices.Tco
c_labels = tuple(coble.module_generating_set())


def vector(coefficients):
    total = coble.zero()
    for label, coefficient in zip(c_labels, coefficients, strict=True):
        if coefficient:
            total = total + coefficient * coble.module_generator(label)
    return total


plane = coble.primitive_isotropic_subobject(
    vector([0, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1]),
    vector([2, 0, 0, -1, -1, -2, -2, -2, -2, -2, 0]),
)
print("plane primitive", plane.is_primitive(), flush=True)
stage("T_Co block basis (rows, |det|)", lambda: index_of_block_basis(plane))
stage("T_Co splitting_complement", lambda: plane.splitting_complement())
stage("T_Co plane_block_gram", lambda: plane.plane_block_gram())
stage("T_Co unipotent_radical_index", lambda: plane.unipotent_radical_index())
stage("T_Co levi_plane_action_index(trivial_on_quotient=True)",
      lambda: plane.levi_plane_action_index(trivial_on_quotient=True))
stage("T_Co levi_quotient_image_index(trivial_on_plane=True)",
      lambda: plane.levi_quotient_image_index(trivial_on_plane=True))
decision = stage("T_Co parabolic_completeness_decision", lambda: plane.parabolic_completeness_decision())
if decision is not None:
    print("COMPLETE:", decision[0], flush=True)
    print("OBSTRUCTION:", decision[1], flush=True)
stage("T_Co stabilizer_discriminant_image_orders", lambda: plane.stabilizer_discriminant_image_orders())
stage("T_Co stabilizer_discriminant_image_index", lambda: plane.stabilizer_discriminant_image_index())
stage("T_Co number of parabolic stabilizer generators",
      lambda: len(plane.parabolic_stabilizer_generators()))
print("O(q) order", int(coble.discriminant_group().orthogonal_group().order()), flush=True)
stamp("whole probe", start)
