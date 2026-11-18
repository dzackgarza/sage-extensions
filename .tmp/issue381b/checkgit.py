import subprocess
print(subprocess.run(("git","-C","/repos/sage-extensions","rev-parse","HEAD"),capture_output=True,text=True))
