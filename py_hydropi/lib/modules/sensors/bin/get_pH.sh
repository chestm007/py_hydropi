#!/bin/bash

# Filters Homelab-pH data output and prints either console or json formated strings
# Homelab.link; v.170611

# Notes:
# file location: /var/www/homelab/cgi-bin/  
# file permissions: 0555
#	
# Exits if no board found
# Outputs json-formated data if the first argument is -json or -j
#
# 't' is in Celsius
# 'v' is in mV
# 'time' is UNIX Epoch time in seconds
#
#	'bc' module has to be available

cd "$(dirname "$0")" # all links are local to the file location
export LC_NUMERIC="C" # decimal separator (dot) to be independant of host locale; for printf

# init vars
# -----------
ouputFormat='console'
if [ "$1" == "-json" ] || [ "$1" == "-j" ]; then ouputFormat='json'; fi # will print json-formated string
initStr='skipped'
[[ $ouputFormat == 'json' ]] && initStr='false' # !'false' - boolean for numericals while string for strings
NERNST=0.19842
ABSZERO=273.15

# output vars
taskStatus=ok
errorStrings=''
time=$initStr
v=$initStr
t=$initStr
calibID=$initStr
pH=$initStr
calibDate=$initStr

# functions
# -----------

function addError {
	errStr=$1
	if [ "${#errorStrings}" -gt "1" ]; then
		errorStrings=$errorStrings',"'$errStr'"'
	else
		[[ $ouputFormat == 'json' ]] && errorStrings='['
		errorStrings=$errorStrings'"'$errStr'"'
	fi
}

function writeOutput { # $1 taskStatus
	if [[ $ouputFormat == 'json' ]]; then
		outputJson $1
	else
		ouputConsole $1
	fi
}

function ouputConsole {
	[ ! -z "$1" ] && taskStatus=$1 # $1 taskStatus not an empty string
	echo "taskStatus=$taskStatus"
	[ "${#errorStrings}" -gt "0" ] && echo "errorStrings=$errorStrings"
	echo "time=$time"
	echo "v=$v"
	echo "t=$t"
	echo "pH=$pH"
	echo "calibID=$calibID"
	echo "calibDate=$calibDate"
}

function outputJson {
	[ "${#errorStrings}" -gt "0" ] && jsonError='"errorStrings":'$errorStrings'],'
	[ ! -z "$1" ] && taskStatus=$1 # $1 taskStatus not an empty string
	echo '{"taskStatus":"'$taskStatus'",'$jsonError'"time":'$time',"v":'$v',"t":'$t',"pH":'$pH',"calibID":'$calibID',"calibDate":'$calibDate'}'
}

# get and validate data
# -----------

board=$(. ./get_circuit_data.sh 2>/dev/null) # error due to changed dir; to be corrected in get_circuit_data.sh
if [[ $board != *'"taskStatus":"ok"'* ]]; then # board data is not ok
	boardStr=${board/*Status\":\"/} # delete from start
	boardStr=${boardStr/\"*/} # delete end
	addError "$boardStr"
	writeOutput bad
	exit 1
fi

# offset string
offset=${board/*offset\":\"/}
offset=${offset/\"*/}
offset=${offset/*\+/} # delete plus sign

# mult string
mult=${board/*mult\":\"/}
mult=${mult/\"*/}

. ./get_t_sensors.sh # sets $status, $sensors, $match; calls also main_config.sh

if [[ "$status" == *"no sensors"* ]]; then # test sensor is attached
	addError 'warning: No temperature sensor found'
else
#	request="" # sensor id
	if [ "${#sensors[@]}" -gt "1" ]; then
		warn="warning: Multiple temperature sensors found."
		if [[ $match ]]; then request=$match # $request is used by get_data.sh
		else warn=$warn" Select by the visual interface."
		fi
		addError "$warn"
	else request=${sensors[0]}
	fi
fi

. ./get_data.sh # needs $request

if [ ! -f ./data/ccalib_data ]; then
	addError "warning: No calibration data file"
else
	calibData=$(cat ./data/ccalib_data)

	# calibID string
	calibID=${calibData/*id\":\"/}
	calibID=${calibID/\"*/}

	# coef_B float
	coef_B=${calibData/*coef_B\":/}
	coef_B=${coef_B/,*/}

	# iso_pH float
	iso_pH=${calibData/*iso_pH\":/}
	iso_pH=${iso_pH/,*/}

	# iso_v float
	iso_v=${calibData/*iso_v\":/}
	iso_v=${iso_v/,*/}

	# iso_v float
	calibDate=${calibData/*date\":\"/}
	calibDate=${calibDate/\"*/}

	if [[ $ouputFormat == 'json' ]]; then
		calibID='"'$calibID'"'
		calibDate='"'$calibDate'"'
	fi
fi

# calculate 
# -----------

# voltage
v=$(bc -l <<< "scale=6;($v_raw- $offset)/$mult") # space matters
v=$(printf "%.*f\n" 1 $v) # print floats<0 with prepaded zero

if [ -z "$errorT" ]; then 

	# temperature
	t=$(echo "$tmpr_str/1000" | bc -l)
	t=$(printf "%.*f\n" 1 $t)

	if [ -f ./data/ccalib_data ]; then
		# pH
		pH=$(echo "( $v - $iso_v ) / ( $coef_B * $NERNST * ( $t + $ABSZERO ) ) + $iso_pH" | bc -l)
		pH=$(printf "%.*f\n" 2 $pH)
	fi

else addError "error: $errorT"
fi

writeOutput
exit 0