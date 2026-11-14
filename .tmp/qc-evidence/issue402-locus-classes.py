r"""Is every class of ``integral_parameter_classes`` the class of an integral lift? (T_En, Sterk (4.3.8) line)

The identity marking of the reduction of ``T_En = U + U(2) + E8(-2)`` at the line through
``2e' + f' + alpha-bar_1`` (H. Sterk, Math. Z. 207 (1991), (4.3.8), p. 23).  The locus is
documented as the residues of integral lifts.  This takes its classes in iteration order
and asks, for each, whether the lift at ``residue.preimage(class)`` restricts to an
integral isometry, stopping at the first that does not.
"""
import time
from sage_extensions.all import *  # noqa
from sage_extensions.sterk import Sterk
T0=time.time()
def say(*a): print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)
L=NamedLattices.TEn
line=L.primitive_isotropic_subobject(Sterk.sterk4_cusp_vector()); red=line.isotropic_reduction()
t=red.rational_lifts(red, red.Aut().one())
residue=t.integral_parameter_quotient(); inc=residue.domain().inclusion()
target=t.target_reduction().isotropic_embedding().codomain(); phi=t.parameterization()
classes=t.integral_parameter_classes(); say("locus built")
for count, c in enumerate(classes):
    lift=phi(inc(residue.preimage(c)).underlying_element())
    if lift.integral_restriction(target, target) is None:
        say("class", count, c, "is in the locus and its lift is not integral"); break
    if count % 200 == 0: say("checked", count + 1)
say("done")
