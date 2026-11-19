import sage.all
from sage_extensions.all import *
from sage.symbolic.ring import SR
x = SR.var('x')
for label, f in (("SR(9)/SR(5)", lambda: SR(9)/SR(5)), ("SR(9-x)/SR(5)", lambda: SR(9-x)/SR(5)), ("SR(9)*SR(5)**-1", lambda: SR(9)*SR(5)**(-1))):
    try: print(label, f())
    except Exception as e: print(label, "raises", type(e).__name__, e)
