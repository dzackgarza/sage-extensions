"""#365: the parameter lattice at Sterk's P_2 and P_1 of T_En, decided class by class.

At P_2 -- the plane that does not split -- the modulus, the admissible classes, the
lattice's rank and index, the translations, the transvections' parameters, the centre's
generator and the radical's index.  At P_1 -- the plane that does split -- the same
calls, because the centre's generator is a lattice generator there too and it is not the
skew matrix the skew parameter of `unipotent_block_solution` reaches.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage.all import ZZ as SageZZ, matrix as engine_matrix

t0 = time.time()


def say(*args):
    print(f"[{time.time() - t0:7.1f}s]", *args, flush=True)


lattice = NamedLattices.TEn
elements = list(lattice.module_generators())
second = lattice.primitive_isotropic_subobject(
    2 * elements[0] + 2 * elements[1] + elements[4] + elements[5], elements[2]
)
first = lattice.primitive_isotropic_subobject(elements[0], elements[2])

for name, plane in (("P_2", second), ("P_1", first)):
    rows = int(plane.plane_block_gram()[5].nrows())
    order = 2 * rows
    basis = tuple(
        plane.inclusion()(plane.module_generator(label))
        for label in plane.module_generating_set()
    )

    def fixes_pointwise(automorphism):
        return all(automorphism(vector) == vector for vector in basis)

    say("")
    say(f"==== {name}: splits = {plane.splitting_complement() is not None}")
    say("  J =", [int(entry) for entry in plane.plane_block_gram()[3].list()],
        "| K = b(U,K) has",
        sum(1 for entry in plane.plane_block_gram()[4].list() if int(entry)), "nonzero entries")
    say("  unipotent_parameter_modulus() =", plane.unipotent_parameter_modulus())
    say("  unipotent_parameter_class_counts() =", plane.unipotent_parameter_class_counts())
    parameters = plane.unipotent_parameter_lattice()
    span = engine_matrix(SageZZ, [list(row) for row in parameters])
    say("  |unipotent_parameter_lattice| =", len(parameters),
        "| rank =", int(span.rank()), "| index =", abs(int(span.determinant())))
    for row in parameters:
        say("    ", list(row))
    translations = plane.unipotent_translation_basis()
    flat = engine_matrix(
        SageZZ,
        [[int(entry) for entry in engine_matrix(translation).list()] for translation in translations],
    )
    say("  |unipotent_translation_basis| =", len(translations),
        "| rank =", int(flat.rank()) if translations else 0,
        "| covolume in the coordinate lattice of Hom(K, P) =",
        abs(int(flat.determinant())) if translations else "n/a")
    say("  unipotent_translation_rank() =", plane.unipotent_translation_rank())
    say("  unipotent_radical_rank() =", plane.unipotent_radical_rank(),
        "| unipotent_translation_kernel_rank() =", plane.unipotent_translation_kernel_rank())

    central = plane.unipotent_central_generator()
    c, tau, a = plane.unipotent_block_coordinates(central)
    say("  central generator: c =", [int(entry) for entry in c.list()],
        "| tau =", [int(entry) for entry in tau.list()],
        "| a =", [int(entry) for entry in a.list()],
        "| coordinate on the centre's lattice =", plane._unipotent_central_coordinate(a))
    say("    fixes the plane pointwise:", fixes_pointwise(central),
        "| trivial on I^perp/I:", plane.acts_trivially_on_isotropic_reduction(central),
        "| not the identity:", central != lattice.Aut().one())
    say("  |unipotent_radical_block_generators| =",
        len(plane.unipotent_radical_block_generators()),
        "| |unipotent_radical_generators| =", len(plane.unipotent_radical_generators()))
    say("  unipotent_radical_index() =", plane.unipotent_radical_index())
    say("  is_parabolic_complete() =", plane.is_parabolic_complete())

    transvections = tuple(
        transvection
        for transvection in plane.parabolic_transvection_generators()
        if fixes_pointwise(transvection)
        and plane.acts_trivially_on_isotropic_reduction(transvection)
    )
    outside = 0
    for transvection in transvections:
        parameter = plane.unipotent_parameter_vector(
            plane.unipotent_block_coordinates(transvection)[0]
        )
        try:
            plane.unipotent_parameter_coordinates(parameter)
        except ValueError:
            outside += 1
    say("  the plane's transvections in U_I:", len(transvections),
        "| outside the parameter lattice:", outside,
        "| their translation rank:", plane.unipotent_translation_rank(transvections))
    unit = []
    for position in range(rows):
        for column in range(2):
            parameter = tuple(
                1 if index == 2 * position + column else 0 for index in range(order)
            )
            unit.append(plane.unipotent_parameter_lifts(plane.unipotent_parameter_matrix(parameter)))
    say("  the sixteen unit parameters lift:", unit)

say("")
say("done")
