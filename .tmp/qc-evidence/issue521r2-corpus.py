"""Every .sage file in the tree, lowered, as a digest per file."""
import glob
import hashlib

import sage_extensions.all  # noqa: F401
from sageparse.preparser import preparse_file

paths = sorted(glob.glob('/repos/sage-extensions/**/*.sage', recursive=True))
for path in paths:
    source = open(path, encoding='utf-8').read()
    lowered = preparse_file(source)
    print(path, hashlib.sha256(lowered.encode()).hexdigest())
print("files:", len(paths))
