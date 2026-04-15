#!/bin/bash

ext_cut=0.03

function write_config {
  name=$1; den_id=$2
  file=$name.cfg-$den_id
  printf "PRINT_COORD 1\n" > $file
  printf "PRINT_SHELL 1\n" >> $file
  printf "PRINT_CUBE_PAR 1\n\n" >> $file
  printf "PRINT_CUBE 1\n" >> $file
  printf "CUBE_FILE_ALIP $name.ali-$den_id\n" >> $file
  printf "CUBE_TOT_DENSITY 0\n" >> $file
  printf "CUBE_ALIP 1\n\n" >> $file
  printf "DEFINE_CUBE 1\n" >> $file
  set $(head -n 3 $name.den-$den_id | tail -n 1)
  np=$1; p1=$2; p2=$3; p3=$4
  set $(head -n 4 $name.den-$den_id | tail -n 1)
  nx=$1; x1=$2; x2=$3; x3=$4
  set $(head -n 5 $name.den-$den_id | tail -n 1)
  ny=$1; y1=$2; y2=$3; y3=$4
  set $(head -n 6 $name.den-$den_id | tail -n 1)
  nz=$1; z1=$2; z2=$3; z3=$4
  printf "%12.6f %12.6f %12.6f\n" $p1 $p2 $p3 >> $file
  printf "%12.6f %12.6f %12.6f\n" $x1 $x2 $x3 >> $file
  printf "%12.6f %12.6f %12.6f\n" $y1 $y2 $y3 >> $file
  printf "%12.6f %12.6f %12.6f\n" $z1 $z2 $z3 >> $file
  printf "%5d %5d %5d\n\n" $nx $ny $nz >> $file
  }

function print_alip {
  id=$1; num=$2; name=$3
  den_type=scf; den_id=s
  if [ ! -f $name.fchk ]; then
    formchk $name.chk >/dev/null 2>&1; fi
  if [ ! -f $name.den ]; then
    cubegen 0 density=$den_type $name.fchk $name.den-$den_id 0 h 
  else  
    cp $name.den $name.den-$den_id ;fi  
  if [ ! -f $name.cfg-$den_id ]; then
    write_config $name $den_id; fi
  if [ ! -f $name.alip-$den_id ]; then
    ./alip.exe -w -c $name.cfg-$den_id -o $name.out-$den_id -i $name.fchk -t fchk; fi
    mv out.den $name.den-$den_id
    mv out.alip $name.alip-$den_id
  if [ ! -f $name.exa-$den_id ]; then
    ./potmin.exe -m -v -d $name.den-$den_id -p $name.alip-$den_id > $name.exa-$den_id
    sed 's/potmin\.crd/$name\.vca-$den_id/' potmin.vmd
    mv potmin.crd $name.vca-$den_id
    mv potmin.vmd $name.via-$den_id
    fi
  min=$(grep 'minimum:' $name.exa-$den_id | \
    sed 's/.*minimum: \(.*\) *Hartree.*/\1/')
  max=$(grep 'maximum:' $name.exa-$den_id | \
    sed 's/.*maximum: \(.*\) *Hartree.*/\1/')
  }

id=1
for f in *.pot; do
  name=$(echo $f | sed 's/\(.*\)\.\(.*\)/\1/')
  num=$(echo $name | sed 's/\(.*\)_0*\([1-9][0-9]*\)/\2/')
  print_alip $id $num $name
  id=$(($id+1))
done


