# -*- coding:utf-8 -*-
##############################################################
# Created Date: Monday, February 19th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################


from vissim2gmns import vissim2geojson as v2g
import pytest


# test the inputs of the vissim2geojson
def test_invalid_inputs():
    with pytest.raises(AssertionError, match="vissim_file_path should be a folder"):
        v2g.vissim2wgs1984("test_data/invalid.inpx")

