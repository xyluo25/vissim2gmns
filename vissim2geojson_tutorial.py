# -*- coding:utf-8 -*-
##############################################################
# Created Date: Sunday, February 18th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

from __future__ import absolute_import
import vissim2gmns as vg


file_folder = "./datasets/one_intersection"
# file_folder = "./datasets/aveiro_port_net"
# for covert fzp files, if you don't need to convert fzp file, leave these value to default values.
x_col_name = "POS"
y_col_name = "POSLAT"

# Automatically convert all files (.inpx, .fzp, .fhz) in the folder
vissim = vg.VISSIM2GMNS(file_folder, x_col_name=x_col_name, y_col_name=y_col_name)
vissim.vissim_to_gmns(isCsv=True, isGeojson=True, isShp=True)
