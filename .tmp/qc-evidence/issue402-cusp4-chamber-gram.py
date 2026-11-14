r"""The chamber returned from a vertex of card 029J's 4.3.8 polyhedron against the card's walls, in N (#402)

``N = v^perp/Zv`` at ``2e' + f' + alpha-bar_1`` (H. Sterk, Math. Z. 207 (1991), (4.3.8),
p. 23), in the frame of the reduction's generators.  ``printed`` are the classes of card
029J's eleven walls, ``walk`` the eleven walls of ``issue402-cusp4-chamber-at-vertex.log``.
For each: the Gram matrix of the walls, the rays of the cone they cut out, and the pairings
with the controlling vector ``p_0``.
"""
import itertools
from sage_extensions.all import *  # noqa
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector
from sage.rings.rational_field import QQ
from sage.geometry.polyhedron.constructor import Polyhedron
from sage_extensions.sterk import Sterk
L=NamedLattices.TEn; v=Sterk.sterk4_cusp_vector()
red=L.primitive_isotropic_subobject(v).isotropic_reduction()
labels=tuple(red.module_generating_set()); gens=[red.module_generator(l) for l in labels]
G=matrix(QQ,[[int(red.b(x,y)) for y in gens] for x in gens]); print(G)
printed=[vector(QQ,w) for w in [(1,-2,-4,-6,-8,-10,-7,2,0,0),(1,-4,-7,-10,-13,-16,-11,4,0,0),(0,1,0,0,0,0,0,0,0,0),(0,0,1,0,0,0,0,0,0,0),(0,0,0,1,0,0,0,0,0,0),(0,0,0,0,1,0,0,0,0,0),(0,0,0,0,0,1,0,0,0,0),(0,0,0,0,0,0,1,0,0,0),(0,0,0,0,0,0,0,0,1,-1),(-2,4,9,14,19,24,17,-6,0,2),(-2,4,8,12,16,20,14,-5,1,1)]]
walk=printed[:9]+[vector(QQ,w) for w in [(-2,4,9,14,19,24,17,-6,-2,0),(-2,4,8,12,16,20,14,-5,-1,-1)]]
for name,W in (("printed",printed),("walk",walk)):
    g=matrix(QQ,[[a*G*b for b in W] for a in W]); print(name); print(g)
    P=Polyhedron(ieqs=[[0]+list(w*G) for w in W]); rays=[vector(QQ,r) for r in P.rays()]
    print(name,"rays",len(rays),"lines",len(P.lines()),"squares",sorted({r*G*r for r in rays}))
p0=vector(QQ,(0,0,0,0,0,0,0,0,1,1)); print("p0 pairings printed",[w*G*p0 for w in printed]); print("p0 pairings walk",[w*G*p0 for w in walk])
