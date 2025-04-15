# -*- coding:utf-8 -*-
##############################################################
# Created Date: Monday, February 19th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

from __future__ import absolute_import
from pathlib import Path
import pytest

try:
    import vissim2gmns as vg
except Exception:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    import vissim2gmns as vg


# test the inputs of the vissim2geojson
def test_invalid_inputs():
    with pytest.raises(AssertionError, match="vissim_file_path should be a folder"):
        vg.VISSIM2GMNS("test_data/invalid.inpx")
