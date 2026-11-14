"""#353: what the parabolic at P_2 reports, and the ranks behind it."""
import time

from sage_extensions.all import *  # noqa: F401,F403

t0 = time.time()


def say(*args):
    print(f"[{time.time() - t0:7.1f}s]", *args, flush=True)


lattice = NamedLattices.TEn
elements = list(lattice.module_generators())
plane = lattice.primitive_isotropic_subobject(
    2 * elements[0] + 2 * elements[1] + elements[4] + elements[5], elements[2]
)
say("plane", plane)
say("splitting complement:", plane.splitting_complement())
say("rank U =", plane.unipotent_radical_rank())
say("rank Z =", plane.unipotent_translation_kernel_rank())
say("translation rank (returned family) =", plane.unipotent_translation_rank())
say("|unipotent_radical_generators| =", len(tuple(plane.unipotent_radical_generators())))
say("unipotent_radical_index() =", plane.unipotent_radical_index())
say("is_parabolic_complete() =", plane.is_parabolic_complete())
say("")
say("parabolic_obstruction() =")
say(plane.parabolic_obstruction())
say("")
say("done")
