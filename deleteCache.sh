#!/bin/bash
dir=~/myFilm/fonts //需要清空的目录名称
files=`ls ${dir}`
for file in $files
do
if [ -e ${dir}/${file} ];then
rm -f ${dir}/${file}
fi
done
