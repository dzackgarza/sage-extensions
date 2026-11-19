# Probe: a symbolic primitive E(i, j, a, b) = d^i/da^i d^j/db^j exp(-a/b) for b > 0, 0 for b <= 0,
# differentiated by SageManifolds on the two-chart circle.
from sage.all import SR, var, exp, function, QQ, Manifold
A, B = var('A B')
def _ev(self, i, j, a, b):
    if b in QQ or (hasattr(b, 'is_constant') and SR(b).is_constant() and SR(a).is_constant()):
        if bool(SR(b) <= 0):
            return SR.zero()
        return exp(-A/B).diff(A, int(i)).diff(B, int(j)).subs({A: a, B: b})
    return None
def _de(self, i, j, a, b, diff_param):
    return [None, None, E(i+1, j, a, b), E(i, j+1, a, b)][diff_param]
E = function('flat_exponential', nargs=4, eval_func=_ev, derivative_func=_de)
M = Manifold(1, 'C'); UN = M.open_subset('UN'); US = M.open_subset('US')
cx = UN.chart('x'); cy = US.chart('y'); x, = cx[:]; y, = cy[:]
cx.transition_map(cy, (1/x,), intersection_name='W', restrictions1=x!=0, restrictions2=y!=0)
M.declare_union(UN, US)
H = lambda a, b1, b2: E(0,0,a,b1)/(E(0,0,a,b1)+E(0,0,a,b2))
f = M.scalar_field({cx: H(5, 9-x**2, x**2-4), cy: H(5*y**2, 9*y**2-1, 1-4*y**2)})
v = M.vector_field({cx.frame(): [1+x**2], cy.frame(): [-(1+y**2)]})
d = v(f)
print("on x:", d.expr(cx)); print("on y:", d.expr(cy))
print("f(x=1)", f.expr(cx).subs(x=1), " f(y=1/4)", f.expr(cy).subs(y=QQ(1)/4))
print("df(y=0)", d.expr(cy).subs(y=0), " df(x=1)", d.expr(cx).subs(x=1))
