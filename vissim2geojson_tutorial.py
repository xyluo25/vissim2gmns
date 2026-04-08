# -*- coding:utf-8 -*-
##############################################################
# Created Date: Sunday, February 18th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

from __future__ import absolute_import
import vissim2gmns as vg

file_inpx = "./datasets/one_intersection/xl_002_001.inpx"
file_fhz = "./datasets/one_intersection/xl_002_001.fhz"
file_fzp = "./datasets/one_intersection/xl_002_001.fzp"
file_folder = "./datasets/one_intersection/"

# prepare map reference data from Vissim
x_refmap = -9772791.018
y_refmap = 5317836.791
x_refnet = 0
y_refnet = 0

# file_inpx = "./datasets/aveiro_port_net/Aveiro_Port_Train_Network_25_03_2026.inpx"
# file_fhz = "./datasets/aveiro_port_net/Aveiro_Port_Train_Network_25_03_2026_001.fhz"
# file_fzp = "./datasets/aveiro_port_net/Aveiro_Port_Train_Network_25_03_2026_001.fzp"
# file_folder = "./datasets/aveiro_port_net"
#
# x_refmap = -970628.702
# y_refmap = 4954726.007
# x_refnet = 0
# y_refnet = 0

# for covert fzp files, if you don't need to convert fzp file, leave these value to default values.
x_col_name = "POS"
y_col_name = "POSLAT"

# Automatically convert all files (.inpx, .fzp, .fhz) in the folder
net = vg.VISSIM2GMNS(file_folder, x_refmap, y_refmap, x_refnet, y_refnet, x_col_name, y_col_name)
net.vissim_to_gmns()
