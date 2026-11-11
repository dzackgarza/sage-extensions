"""#366: the parabolic's completeness decision at P_2 and P_1, and the public family.

At Sterk's P_2 of T_En (not split) and P_1 (split): the three factors
`parabolic_completeness_decision()` computes, the answer `is_parabolic_complete()` gives,
the obstruction it reports, and — at P_2 — what
`L.Aut().stabilizer(P, action="setwise").group_generators()` returns: its size, whether it
carries every radical block generator and the centre's generator, the translation rank of
its radical members, and the coordinate of its central members on the centre's generator.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

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
    say("")
    say(f"==== {name}: splits = {plane.splitting_complement() is not None}")
    say("  unipotent_radical_index() =", plane.unipotent_radical_index())
    say("  levi_plane_action_index(trivial_on_quotient=True) =",
        plane.levi_plane_action_index(trivial_on_quotient=True))
    say("  levi_plane_action_index() =", plane.levi_plane_action_index())
    try:
        say("  levi_quotient_image_index(trivial_on_plane=True) =",
            plane.levi_quotient_image_index(trivial_on_plane=True))
    except Exception as error:  # noqa: BLE001
        say("  levi_quotient_image_index(trivial_on_plane=True) raised",
            type(error).__name__, ":", error)
    say("  levi_quotient_image_index() =", plane.levi_quotient_image_index())
    say("  parabolic_completeness_decision() =", plane.parabolic_completeness_decision())
    say("  is_parabolic_complete() =", plane.is_parabolic_complete())
    say("  parabolic_obstruction() =", plane.parabolic_obstruction())
    say("  |parabolic_stabilizer_generators()| =", len(plane.parabolic_stabilizer_generators()))

say("")
say("==== the public call at P_2")
plane_basis = tuple(
    second.inclusion()(second.module_generator(label)) for label in second.module_generating_set()
)
perpendicular = second.isotropic_perpendicular()
perpendicular_basis = tuple(
    perpendicular.inclusion()(perpendicular.module_generator(label))
    for label in perpendicular.module_generating_set()
)
stabilizer = lattice.Aut().stabilizer(second, action="setwise")
start = time.time()
family = tuple(stabilizer.group_generators())
say(f"|L.Aut().stabilizer(P_2, action=\"setwise\").group_generators()| = {len(family)} "
    f"in {time.time() - start:.1f}s")
radical = tuple(second.unipotent_radical_block_generators())
say("  |unipotent_radical_block_generators()| =", len(radical),
    "| members of the family:", sum(1 for element in radical if element in family))
say("  the centre's generator is in the family:", second.unipotent_central_generator() in family)
members = tuple(
    element
    for element in family
    if all(element(vector) == vector for vector in plane_basis)
    and second.acts_trivially_on_isotropic_reduction(element)
)
say("  members of the family in the radical:", len(members),
    "| their translation rank:", second.unipotent_translation_rank(members),
    "| the radical's:", second.unipotent_radical_rank()
    - second.unipotent_translation_kernel_rank())
central = tuple(
    element
    for element in members
    if all(element(vector) == vector for vector in perpendicular_basis)
)
say("  central members:", len(central),
    "| coordinates on the centre's generator:",
    [second.unipotent_central_coordinate(element) for element in central])
say("done")
