from sage.all import *
from sage_extensions.all import *
import cProfile, pstats
from time import monotonic
from sage_extensions.categories.orthogonal_quotients import _isotropic_divided_class_set
L=Lattices(ZZ)([[2]])+(NamedLattices.U+NamedLattices.E8).twist(2)
h,e,f,*_=L.module_generators()
vectors=tuple(e+2*n*h-2*n*n*f for n in range(1,33))
assert all(v.q()==0 for v in vectors)
t=monotonic()
A=L.discriminant_group()
print("discriminant setup",monotonic()-t,flush=True)
pr=cProfile.Profile()
pr.enable()
t=monotonic()
lines=tuple(L.primitive_isotropic_subobject(v) for v in vectors)
print("32 lines",monotonic()-t,flush=True)
t=monotonic()
classes=tuple(_isotropic_divided_class_set(L,line) for line in lines)
print("32 class sets",monotonic()-t,flush=True)
t=monotonic()
assert all(line.is_primitive() for line in lines)
assert all(L.div(v)==2 for v in vectors)
assert all(L.divided_discriminant_class(v) in c for v,c in zip(vectors,classes))
print("32 validation",monotonic()-t,flush=True)
pr.disable()
pstats.Stats(pr).strip_dirs().sort_stats("cumulative").print_stats(45)
