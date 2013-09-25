#!/bin/bash

days=$1

ls -1rt `find .. -mtime -$days -name *_XrayChiller.dat` > XrayChiller.out

for f in `cat XrayChiller.out`; do cat $f; done > out

grep -v 'CcdChiller' out > out1
grep -v 'time' out1 > out

# Print only every 10th line
sed -n '0~10p' out > out1

mv out1 out
