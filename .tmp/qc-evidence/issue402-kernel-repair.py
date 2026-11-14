r"""``K_v`` and the eleven printed walls at card 029J row 4.3.8's cusp, after the repair (#402)

Generators of ``K_v`` from the parameter group of the integral Eichler transvections, the
order of their discriminant image, and ``admits_root`` of the class of each printed wall of
H. Sterk, Math. Z. 207 (1991), (4.3.8) with Fig. 10, p. 23.
"""
import time
from sage_extensions.all import *  # noqa
from sage.matrix.constructor import matrix
from sage.rings.rational_field import QQ
from sage_extensions.sterk import Sterk
T0=time.time()
def say(*a): print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)
def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [(l, r) for l in labels for r in labels if l <= r
        and invariant.q(invariant.module_generator(l)) == ZZ.zero()
        and invariant.q(invariant.module_generator(r)) == ZZ.zero()
        and invariant.b(invariant.module_generator(l), invariant.module_generator(r)) == ZZ(2)]
    l, r = marks[0]
    pol = invariant.module_generator(l) + invariant.module_generator(r)
    return Involutions.I_En.polarized(invariant.inclusion()(pol)).coinvariant_extension_subgroup()
sub=gamma_en_2(); image=sub.isotropic_vector_reduction_image(Sterk.sterk4_cusp_vector())
L=image.lattice(); red=image.reduction(); perp=red.orthogonal_complement()
v=image.vector(); vc=[int(t) for t in v.to_vector()]
def cls(w): return red.projection()(perp.inclusion().lift(L([int(t) for t in w.to_vector()])))
card=Sterk.cusp_roots_in_TEn("Sterk_4"); names=['a2','a3','a4','a5','a6','a7','a8','a9','a10','a11','a12']
say("building kernel generators")
gens=image.kernel_generators(); say("kernel generators", len(gens))
say("rho(K_v) order", image.kernel_discriminant_image().cardinality())
for n,w in zip(names,card):
    say(n,"class admitted:",image.admits_root(cls(w)))
say("done")
