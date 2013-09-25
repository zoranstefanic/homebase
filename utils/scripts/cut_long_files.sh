#!/bin/bash
for f in `find . -size +100M`
do
echo 'Cutting file ' $f
head -10000 $f > tmp
cat >> tmp << end
---------------------------------


FILE WAS OVER 100 MB!
CUT to first and last 10000 lines!


---------------------------------
end
tail -10000 $f >> tmp
mv tmp $f
done
