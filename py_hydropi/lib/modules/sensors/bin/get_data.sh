#!/bin/bash

function send_response {
	if [[ $v_raw ]]; then
		resp=$resp', "v":"'$v_raw'"'
	else
		if [[ $errorV ]]; then errors=$errors",\"$errorV\""; fi
	fi
	if [[ $tmpr_str ]]; then
		resp=$resp', "tmpr_str":"'$tmpr_str'"'
	else
		if [[ $errorT ]]; then errors=$errors",\"$errorT\""; fi
	fi
	if [[ $time ]]; then resp=$resp', "time":"'$time'"'; fi

	if [ "$errors" == "$noerrors" ]; then # no errors
		echo "$resp}"
	else
		echo $resp', "errors":'$errors']}'
	fi
	exit
}

function main {
	times_run+=1
	START=$(date +%s.%N)
	while IFS='' read -r line; do eval "$line"; done < $data_buffer #set data variables
	if [[ $? -eq 0 && $time ]]; then
		delta=$(echo "$START - $time" | bc -l)
		if [[ $(echo "$delta > 0" | bc -l) -eq 1 && $(echo "$delta < $time_diff_limit" | bc -l) -eq 1 ]]; then
			if [ $caller == 'apache2' ]; then send_response; fi
			return
		fi
	else
		conv_time=$(date -r $conv_buffer +%s.%N) # last modification time of conv_buffer
		if [[ $? -eq 0 ]]; then
			delta=$(echo "$START - $conv_time" | bc -l)
			if [[ $(echo "$delta > 0" | bc -l) -eq 1 && $(echo "$delta < $lpvc" | bc -l) -eq 1 ]]; then
				if [[ $times_run -lt 3 ]]; then
					sleep $lpvc
					main
				else
					errors=$errors",\"can not access data\"";
					if [ $caller == 'apache2' ]; then send_response; fi
					return
				fi
			fi
		fi
	fi
}

# init
. ./main_config.sh # sets $i2c_bus_number, $homelab_root, $one_wire_path

# const
conv_buffer=$homelab_root'/cgi-bin/data2/conv_buffer'
data_buffer=$homelab_root'/cgi-bin/data2/data_buffer'
err_dlmt='::>' # errors list delimiter
PATH=$PATH":"$i2c_files_path
time_diff_limit=0.4 # threshold voltage age in seconds, value>=0 
lpvc=0.18 # longest possible voltage conversion in seconds, value>=0 

# init
resp='{"a":""' # first - no comma in front, otherwise is meaningless
errors='["'$err_dlmt'"'
noerrors=$errors
times_run=0 # init times main func. is run

caller=$(ps -o comm= $PPID)
if [ $caller == 'apache2' ]; then
	. ./get_client_request.sh # get t-sensor id
	echo "Content-Type: application/json;charset=utf-8";
	echo
fi
t_sensor_id=$request

main

echo '' > $conv_buffer # init the buffer
(. ./get_adcd01.sh) & (. ./get_DS_temp.sh) & wait
cp -f $conv_buffer $data_buffer
while IFS='' read -r line; do eval "$line"; done < $data_buffer #set data variables
if [ $caller == 'apache2' ]; then send_response; fi
