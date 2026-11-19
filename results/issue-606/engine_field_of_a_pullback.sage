# What engine field pullback_of attaches to a rank-two section over the circle (#606 item 4).
from sage_extensions.all import *
circle = SmoothManifolds().sphere(1)
sphere = SmoothManifolds().sphere(2)
n, s = sphere.atlas()["U_N"], sphere.atlas()["U_S"]
def at(label):
    ring = circle.atlas()[label].function_ring()
    return (ring.one(), ring.zero())
f = circle.Mor(sphere)({("U_N", "U_N"): at("U_N"), ("U_S", "U_N"): at("U_S")})
euler = sphere.tangent_bundle().sections().section({"U_N": (n.coordinate(0), n.coordinate(1)), "U_S": (-s.coordinate(0), -s.coordinate(1))})
pulled = sphere.tangent_bundle().pullback_along(f).sections().pullback_of(euler)
field = pulled._engine_field
print("engine field:", field)
for chart in field.domain().atlas():
    print(chart, field.restrict(chart.domain()).comp(chart.frame())[:])
