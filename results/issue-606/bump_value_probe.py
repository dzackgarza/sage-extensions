import sage.all, sage.all_cmdline, traceback
from sage_extensions.all import *
from sage.symbolic.ring import SR
from sage_extensions.categories.functions.real_functions import flat_exponential
x = SR.var('x')
circle = SmoothManifolds().sphere(1)
north = circle.atlas()["U_N"]; south = circle.atlas()["U_S"]
frame = circle.tangent_bundle().sections().section({"U_N": (north.function_ring().one() + north.coordinate(0) ** 2,), "U_S": (-(south.function_ring().one() + south.coordinate(0) ** 2),)})
bump = circle.chart_bump("U_N", sage.all.Integer(2), sage.all.Integer(3))
try:
    print("value", bump(circle.point((sage.all.Integer(1),), "U_N")))
except Exception:
    traceback.print_exc()
