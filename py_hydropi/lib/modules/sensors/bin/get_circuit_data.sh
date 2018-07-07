#!/bin/bash

echo "Content-Type: application/json;charset=utf-8";
echo

# read EEPROM data & return in json format
# data - according Spec ver 1.x & ver 2.0

cd "$(dirname "$0")" #  change to file's directory

. ./main_config.sh
PATH=$PATH":"$i2c_files_path

#  To ensure the readarray command executes in the current shell use process substitution in place of the pipeline. syntax for treating a pipeline as a file descriptor. < <(...)
readarray arr1 < <(printf 0x0"%x\n" {10..15})
readarray arr2 < <(printf 0x"%x\n" {16..39})
arr=("${arr1[@]}" "${arr2[@]}") # length 30
for val in "${arr[@]}"
do
	data=("${data[@]}" "$(i2cget -y $i2c_bus_number $i2c_eeprom_address $val | cut -c3-4)")
	if [ -z "${data[0]}" ]; then
		echo '{"taskStatus":"error: No board or no board data"}'
		exit 1
	fi
done
id_string=$(echo -e "\x"${data[0]})$(echo -e "\x"${data[1]})
if [ "$id_string" != "HL" ]; then
	echo '{"taskStatus":"error: Wrong id-string"}'
	exit 1
fi
spec_version=$(printf '%d' ${data[2]})
if [ "$spec_version" -lt 1 ] || [ "$spec_version" -gt 2 ]; then
	echo '{"taskStatus":"error: Invalid spec version"}'
	exit 1
fi
boardId=$(echo ${data[3]}${data[4]}${data[5]}${data[6]}${data[7]})
data3=()
for (( i = 8 ; i < 30 ; i++ )) # length 17
do
	data3=("${data3[@]}" "$(echo -e "\x"${data[$i]})")
done
offset=$(echo ${data3[1]}${data3[2]}.${data3[3]}${data3[4]} | sed 's/^0//') # remove leading 0
offset=${data3[0]}$offset
if [ "$spec_version" -eq 1 ]; then
	mult=$(echo ${data3[5]}.${data3[6]}${data3[7]}${data3[8]}${data3[9]}${data3[10]})
	R1=$(echo ${data3[11]}${data3[12]}${data3[13]}.${data3[14]}${data3[15]})
else
	mult=$(echo ${data3[5]}.${data3[6]}${data3[7]}${data3[8]}${data3[9]})
	R1=$(echo ${data3[10]}${data3[11]}${data3[12]}.${data3[13]}${data3[14]})
	RII=$(echo ${data3[15]}${data3[16]}${data3[17]}.${data3[18]}${data3[19]})
fi
case ${data[4]} in # board revision
11*)
	printf "\nLEDoff='high'\nLEDon='low'\nbutton_not_pressed=0\nbutton_pressed=1" > $data_path/load_time_config.sh
	;;
*)
	printf "\nLEDoff='low'\nLEDon='high'\nbutton_not_pressed=1\nbutton_pressed=0" > $data_path/load_time_config.sh
	;;
esac
chmod 755 $data_path/load_time_config.sh
echo '{'
echo '"taskStatus":"ok",'
echo '"offset":"'$offset'",' # bug??: does not return zero before the decimal point
echo '"mult":"'$mult'",'
echo '"idString":"'$id_string'",'
echo '"specVersion":"'$spec_version'",'
echo '"R1":"'$R1'",'
if [ "$spec_version" -eq 2 ]; then echo '"RII":"'$RII'",'; fi
echo '"boardId":"'$boardId'"'
echo '}'
