r"""Does ``admits_root`` decide a class of ``N`` independently of its lift? (#402)

At card 029J row 4.3.8 (H. Sterk, Math. Z. 207 (1991), (4.3.8) with Fig. 10,
p. 23) each printed wall is a vector of ``v^perp``.  For each, this compares the
frame lift ``class_lift`` of its class with the printed vector, and the
decision of ``contains_lift`` on the reflection in each.  It then forms
``g = s_(a2+v) s_a2``, which fixes ``v`` and acts trivially on ``N``, so lies in
the kernel ``K_v`` of the Levi map, and asks whether ``rho(g)`` is trivial,
against ``kernel_discriminant_image`` built from the Eichler transvections over
a basis of ``v^perp``.
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
say("rho(K_v) from the basis transvections: order", image.kernel_discriminant_image().cardinality())
for n,w in zip(names,card):
    printed=L([int(t) for t in w.to_vector()])
    lift=image.class_lift(cls(w))
    diff=[int(a)-int(b) for a,b in zip(lift.to_vector(),printed.to_vector())]
    k=[d//c for d,c in zip(diff,vc) if c!=0]
    say(n,"class_lift - printed =",k[0] if k else 0,"* v;",
        "printed lift admitted:",image.contains_lift(image.root_reflection(printed)),
        "class lift admitted:",image.admits_root(cls(w)))
a2=L([int(t) for t in card[0].to_vector()])
import itertools
# the transvection E(v,-a2/2) = s_{a2+v} s_{a2}
g=image.root_reflection(a2+v)*image.root_reflection(a2)
say("g = s_(a2+v) s_a2 fixes v:",g(v)==v,"acts trivially on N:",image._line.acts_trivially_on_isotropic_reduction(g))
rho=image._discriminant_representation()
say("rho(g) is the identity:", rho(g)==rho(g).parent().one())
say("rho(g) in rho(Gamma):", image.discriminant_image_membership().contains(rho(g)))
say("done")
