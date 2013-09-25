#!/bin/bash

# Command to make jpegs from Oxford diffraction ccdc frames
#for f in `ls -1 $DIR/*.img`; do diff2jpeg $f; done

# Resize all images to 20%
for f in `ls *.jpg`; do convert -resize 50% $f $f; done
#python rename_jpgs.py

# Make a mpeg movie Radi!
#jpeg2yuv -f 25 -I p -j 2%02d.jpg | mpeg2enc -o movie.mpeg

# Make a avi movie NE RADI!
#jpeg2yuv -b 1 -f 25 -I p -n 60 -j exp_686_1_%02d.jpg │ yuv2lav > movie.avi

# Make an animated gif RADI!!
convert -delay 5 -loop 0 *.jpg animated.gif
