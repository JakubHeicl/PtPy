#!/bin/bash

ext_cut=0.03

function print_elstat {
  id=$1; num=$2; name=$3
  den_type=scf; den_id=s
  if [ ! -f $name.fchk ]; then
    formchk $name.chk >/dev/null 2>&1; fi
  if [ ! -f $name.den ]; then
    cubegen 0 density=$den_type $name.fchk $name.den-$den_id 0 h
  else
    cp $name.den $name.den-$den_id
  fi
  if [ ! -f $name.exp-$den_id ]; then
    ./potmin.exe -m -v -d $name.den-$den_id -p $name.pot > $name.exp-$den_id
    sed 's/potmin\.crd/$name\.vcp-$den_id/' potmin.vmd
    mv potmin.crd $name.vcp-$den_id
    mv potmin.vmd $name.vip-$den_id
    fi
  min=$(grep 'minimum:' $name.exp-$den_id | \
    sed 's/.*minimum: \(.*\) *Hartree.*/\1/')
  max=$(grep 'maximum:' $name.exp-$den_id | \
    sed 's/.*maximum: \(.*\) *Hartree.*/\1/')
}

id=1
for f in *.pot; do
  name=$(echo $f | sed 's/\(.*\)\.\(.*\)/\1/')
  num=$(echo $name | sed 's/\(.*\)_0*\([1-9][0-9]*\)/\2/')
  print_elstat $id $num $name
  id=$(($id+1))
done


