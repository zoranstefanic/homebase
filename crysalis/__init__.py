"""
Fri Oct 15 14:24:48 CEST 2010
This module is used to synchronize the data and files in Crysalis XCALIBURDIR
with the main database, as well as to copy most of the files to the local directory (runable module synchronize.py)
and to make local media files such as crystal jpegs and data collection flash movies (movies.py).

Top main directory where all the data collections are stored
It is mounted locally but is otherwise located on the machine 
operating the diffractometer.
Here how this could be specified in the /etc/fstab file:
//172.16.128.200/xcalibur_C/ /mnt/xcalibur_C/  cifs	(rw,uid=1000,gid=100,file_mode=0755,dir_mode=0755) 0 0
"""
