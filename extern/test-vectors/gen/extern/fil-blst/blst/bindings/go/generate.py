#!/usr/bin/env python3

import os
import sys
import re

here = re.split(r'/(?=[^/]*$)', sys.argv[0])
if len(here) > 1:
  os.chdir(here[0])

for dir in re.split(r':', os.getenv("GOPATH")):
  goimports = dir + "/bin/goimports"
  if os.path.isfile(goimports) and os.access(goimports, os.X_OK):
    break
  goimports = None

if goimports is None:
  print("goimports is not found on $GOPATH",                      file=sys.stderr)
  print("install with 'go get golang.org/x/tools/cmd/goimports'", file=sys.stderr)
  sys.exit(1)

outFile = 'blst.go'


def concatFile(fout, fin, removeImports):
  for line in fin:
    if removeImports and 'import' in line:
      while ')' not in line:
        line = fin.readline()
      continue
    print(line, file=fout, end='')


def remap(fout, fin, mapping, dont_touch, removeImports):
  for line in fin:
    if removeImports and 'import' in line:
      while ')' not in line:
        line = fin.readline()
      continue
    for (a, b) in dont_touch:
      line = line.replace(a, b)

    for (a, b) in mapping:
      line = line.replace(a, a+"_tmp")
      line = line.replace(b, b+"_tmp")
      line = line.replace(a+"_tmp", b)
      line = line.replace(b+"_tmp", a)

    for (a, b) in dont_touch:
      line = line.replace(b, a)
    print(line, file=fout, end='')

fout = open(outFile, "w")

print("//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", file=fout)
print("// DO NOT EDIT THIS FILE!!",                          file=fout)
print("// The file is generated from *.tgo by " + here[-1],  file=fout)
print("//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", file=fout)

fin = open('blst.tgo', "r")
concatFile(fout, fin, False)
fin.close()

# min-pk
print("//", file=fout)
print("// MIN-PK", file=fout)
print("//", file=fout)

fin = open('blst_minpk.tgo', "r")
concatFile(fout, fin, True)
fin.close()

# These are strings that overlap with the mapping names but we don't
# actually want to change. The second value should be a unique string.
dont_touch = (('Fp12', 'foo1234'),)

# We're going to swap these names to get from min-pk to min-sig
mapping = [('P1', 'P2'),
           ('p1', 'p2'),
           ('G1', 'G2'),
           ('g1', 'g2')
          ]

# min-sig
print("//", file=fout)
print("// MIN-SIG", file=fout)
print("//", file=fout)

with open('blst_minpk.tgo', "r") as fin:
  remap(fout, fin, mapping, dont_touch, True)

# serdes and other functions
fin = open('blst_px.tgo', "r")
concatFile(fout, fin, True)
fin.close()

with open('blst_px.tgo', "r") as fin:
  remap(fout, fin, mapping, dont_touch, True)

# final code
fin = open('blst_misc.tgo', "r")
concatFile(fout, fin, True)
fin.close()

fout.close()

# Use goimports to generate the import list
os.system(goimports + " -w blst.go")

# Generate min-sig tests
fout = open('blst_minsig_test.go', "w")
print("//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", file=fout)
print("// DO NOT EDIT THIS FILE!!",                          file=fout)
print("// The file is generated from blst_minpk_test.go by " + here[-1],  file=fout)
print("//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", file=fout)

mapping.append(('MinPk', 'MinSig'))

with open('blst_minpk_test.go', "r") as fin:
  remap(fout, fin, mapping, dont_touch, False)
fout.close()