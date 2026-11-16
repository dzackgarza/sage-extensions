"""The scope a load writes into is repaired with the session's own rings (#521)."""

import pathlib

import sage.all_cmdline  # noqa: F401
import sage_extensions.all as session

source = pathlib.Path("/tmp/probe521_load.sage")
source.write_text("value = 41 + 1\n")

scope = dict(vars(session))
scope["ZZ"] = "an engine spelling a loaded file left"
scope["Integers"] = "and another"
session.load(str(source), scope)

print(f"loaded value: {scope['value']} of parent {scope['value'].parent}")
print(f"ZZ is the session's: {scope['ZZ'] is session.ZZ}")
print(f"AA is the session's: {scope['AA'] is session.AA}")
print(f"RDF is the session's: {scope['RDF'] is session.RDF}")
print(f"GF is the session's: {scope['GF'] is session.GF}")
print(f"load itself is bound: {scope['load'] is session.load}")
print(f"removed spellings still gone: {sorted(n for n in ('Integers', 'FiniteField', 'IntegerModRing') if n not in scope)}")
source.unlink()
