#!/bin/bash

# set $t_sensor_id_file, $one_wire_path
. ./main_config.sh

# the id set by the UI
read t_sensor_id <<< $(cat $t_sensor_id_file 2>/dev/null)

# to array the id-s of the detected sensors
IFS=', ' read -a sensors <<< $(ls -m $one_wire_path)
status='"no sensors"'
for i in "${!sensors[@]}" # refering to array index
do
	if [[ "${sensors[$i]}" =~ "28-" ]]; then status='"ok"'
	else unset sensors[$i]
	fi
	if [ "$t_sensor_id" == "${sensors[$i]}" ]; then match=$t_sensor_id; fi
done

caller=$(ps -o comm= $PPID)
if [[ "$caller" == "apache2" ]]; then
	if [ "${#sensors[@]}" -gt 0 ]; then
		sensors_json=$( IFS=','; echo "${sensors[*]}" ) # join array
		sensors_json='["'${sensors_json//,/\",\"}'"]' # json string; // is needed for global match
	fi

	echo "Content-Type: application/json;charset=utf-8";
	echo
	if [ -z "$match" ]; then rm -f $t_sensor_id_file
	fi
	if [ -z "$sensors_json" ]; then echo '{"status":'$status'}'
	else echo '{"status":'$status',"tSensorID":"'$t_sensor_id'","DSsensors":'$sensors_json'}'
	fi
fi
