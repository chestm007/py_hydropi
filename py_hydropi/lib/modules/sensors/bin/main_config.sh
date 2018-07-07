#!/bin/bash

# config data

button_request_interval=60 # not implemented
i2c_eeprom_address=0x51 # redundant

# dir paths
homelab_root='/var/www/homelab' # may it be removed?
data_path=$homelab_root'/cgi-bin/data'
log_path=$data_path'/log'

# file paths
user_list_file=$data_path'/button_requests_list' # todo: change name to button_users_file
curr_calib_file=$data_path'/ccalib_data'
calib_userid_file=$data_path'/calib_user_id'
user_defaults_file=$data_path'/user_defaults'
t_sensor_id_file=$data_path'/t_sensor_id'

# to be added during installation
gpio_path='/sys/class/gpio' # change to include GPIO name 'button_gpio_path='/sys/class/gpio/gpio15' or 'PA14', change all affected files
i2c_files_path='/usr/sbin'
one_wire_path='/sys/bus/w1/devices'
