"""Where does qfsolve's own bound actually sit?"""
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.quadratic_forms.qfsolve import qfsolve

for size in range(2, 12):
    gram = sage_matrix(SageQQ, size)
    for position in range(size):
        gram[position, position] = SageQQ(1) if position else SageQQ(-1)
    try:
        answer = qfsolve(gram)
        print(size, "ok", answer, flush=True)
    except Exception as error:
        print(size, "RAISED", type(error).__name__, error, flush=True)
