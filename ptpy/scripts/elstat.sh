#!/bin/bash

# WHAT TO PRINT OUT
#
# 1 ... total energy
# 2 ... el.stat. extrems
# 3 ... alip extrems
# 4 ... HOMO-LUMO gap
job_type=2

# WHICH DENSITY TO USE
#
# 1 ... SCF
# 2 ... MP2
# 3 ... MP3
# 4 ... CC
en_type=1

# POTENTIAL EXTREMS DISTANCE CUT-OFF
#
ext_cut=0.03

function print_energy {
  id=$1; num=$2; name=$3
  case $en_type in
    1) energy=$(grep 'SCF Done' $name.log | \
         sed 's/.*\(-[1-9][0-9]*\.[0-9]*\).*/\1/') ;;
    2) energy=$(grep 'EUMP2' $name.log | \
         sed 's/.*\(-0\.[0-9]*D+[0-9]*\).*/\1/' | sed 's/D/E/') ;;
    3) energy=$(grep 'EUMP3' $name.log | \
         sed 's/.*\(-0\.[0-9]*D+[0-9]*\).*/\1/' | sed 's/D/E/') ;;
    4) energy=$(grep 'CI/CC converged' -B 2 -m 1 $name.log | \
         head -n 1 | sed 's/.*\(-[1-9][0-9]*\.[0-9]*\) *Delta.*/\1/') ;;
    *) energy="0.0" ;;
  esac
  printf "%5d %5d %15.9f\n" $id $num $energy
  }

function print_elstat {
  id=$1; num=$2; name=$3
  echo "Zpracovavam " $name
  case $en_type in
    1) den_type=scf; den_id=s; ;;
    2) den_type=mp2; den_id=m; ;;
    3) den_type=mp2; den_id=m; ;;
    4) den_type=cc; den_id=c; ;;
  esac
  if [ ! -f $name.fchk ]; then
    formchk $name.chk >/dev/null 2>&1; fi
  if [ ! -f $name.den ]; then
    cubegen 0 density=$den_type $name.fchk $name.den-$den_id 0 h
  else
    cp $name.den $name.den-$den_id
  fi
  if [ ! -f $name.exp-$den_id ]; then
#    potmin.exe -m -v -c $ext_cut -d $name.den-$den_id -p $name.pot > $name.exp-$den_id
    potmin.exe -m -v -d $name.den-$den_id -p $name.pot > $name.exp-$den_id
    sed -i "s/potmin\.crd/$name\.vcp-$den_id/" potmin.vmd
    mv potmin.crd $name.vcp-$den_id
    mv potmin.vmd $name.vip-$den_id
    fi
  min=$(grep 'minimum:' $name.exp-$den_id | \
    sed 's/.*minimum: \(.*\) *Hartree.*/\1/')
  max=$(grep 'maximum:' $name.exp-$den_id | \
    sed 's/.*maximum: \(.*\) *Hartree.*/\1/')
#  printf "%5d %5d %12.6f %12.6f\n" $id $num $min $max
  }

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
  case $en_type in
    1) den_type=scf; den_id=s; ;;
    2) den_type=mp2; den_id=m; ;;
    3) den_type=mp2; den_id=m; ;;
    4) den_type=cc; den_id=c; ;;
  esac
  if [ ! -f $name.fchk ]; then
    formchk $name.chk >/dev/null 2>&1; fi
  if [ ! -f $name.den ]; then
    cubegen 0 density=$den_type $name.fchk $name.den-$den_id 0 h 
  else  
    cp $name.den $name.den-$den_id ;fi  
  if [ ! -f $name.cfg-$den_id ]; then
    write_config $name $den_id; fi
  if [ ! -f $name.alip-$den_id ]; then
    alip -w -c $name.cfg-$den_id -o $name.out $name.fchk; fi
#    alip.exe -w -c $name.cfg-$den_id -o $name.out-$den_id -i $name.fchk -t fchk; fi
#    mv out.den $name.den-$den_id
#    mv out.alip $name.alip-$den_id
  if [ ! -f $name.exa-$den_id ]; then
#    potmin -m -v -c $ext_cut -d $name.den-$den_id -p $name.ali-$den_id > $name.exa-$den_id
    potmin.exe -m -v -d $name.den-$den_id -p $name.ali-$den_id > $name.exa-$den_id
    sed -i "s/potmin\.crd/$name\.vca-$den_id/" potmin.vmd
    mv potmin.crd $name.vca-$den_id
    mv potmin.vmd $name.via-$den_id
    fi
  min=$(grep 'minimum:' $name.exa-$den_id | \
    sed 's/.*minimum: \(.*\) *Hartree.*/\1/')
  max=$(grep 'maximum:' $name.exa-$den_id | \
    sed 's/.*maximum: \(.*\) *Hartree.*/\1/')
#  printf "%5d %5d %12.6f %12.6f\n" $id $num $min $max
  }

function print_hlgap {
  id=$1; num=$2; name=$3
  if [ ! -f $name.fchk ]; then
    formchk $name.chk >/dev/null 2>&1; fi
  hlgap=$(homo_lumo $name.fchk)
  printf "%5d %5d %14.8f %14.8f %14.8f\n" $id $num $hlgap
  }

id=1
for f in ar16*.pot; do
  name=$(echo $f | sed 's/\(.*\)\.\(.*\)/\1/')
  num=$(echo $name | sed 's/\(.*\)_0*\([1-9][0-9]*\)/\2/')
  case $job_type in 
    1) print_energy $id $num $name ;;
    2) print_elstat $id $num $name ;;
    3) print_alip $id $num $name ;;
    4) print_hlgap $id $num $name ;;
  esac
  id=$(($id+1))
done


