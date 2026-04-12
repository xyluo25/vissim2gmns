# -*- coding:utf-8 -*-
##############################################################
# Created Date: Tuesday, June 14th 2022
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
import os
from os.path import isdir
from loguru import logger
from pyufunc import get_filenames_by_ext, func_running_time, path2linux
from pathlib import Path
from vissim2gmns.func_lib.cvt_inpx import vissim_inpx
from vissim2gmns.func_lib.cvt_fhz import vissim_fhz
from vissim2gmns.func_lib.cvt_fzp import vissim_fzp

# ignore RuntimeWarning
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class VISSIM2GMNS:
    """A tool to convert vissim files to geojson and csv.

    Specifically:

    - convert .inpx file to geopandas dataframe and csv/geojson/shp file
    - convert .fzp file to geopandas dataframe and csv/geojson/shp file
    - convert .fhz file to csv file

    Args:
        vissim_file_path (str): the folder or file path to the vissim file
        x_col_name (str): the longitude column name in fzp file to convert fzp file to geojson. Defaults to "POS".
        y_col_name (str): the latitude column name in fzp file to convert fzp file to geojson. Defaults to "POSLAT".

    """

    def __init__(self,
                 input_dir: str,
                 *,
                 x_col_name: str = "POS",
                 y_col_name: str = "POSLAT"):
        """Initialize the VISSIM2GMNS class."""

        # TDD: test the inputs of the vissim2geojson
        assert isinstance(input_dir, str), "The input vissim_file_path should be a string."
        assert isdir(input_dir), "The input vissim_file_path should be a folder."

        self._input_files = [Path(each_path) for each_path in get_filenames_by_ext(input_dir, file_ext="*")]

        self._output_dir = path2linux(os.path.join(input_dir, "output"))
        os.makedirs(self._output_dir, exist_ok=True)

        self.x_col_name = x_col_name
        self.y_col_name = y_col_name

    @func_running_time
    def vissim_to_gmns(self, **kwargs) -> bool:
        """Convert vissim files to csv files in GMNS format.

        1. Convert .inpx file to geopandas dataframe and save to csv/geojson/shp file.
        2. Convert .fzp file to geopandas dataframe and save to csv/geojson/shp file.
        3. Convert .fhz file to pandas dataframe and save to csv file.

        Args:
            **kwargs: other parameters for the conversion, such as isShp, isGeojson, isCsv, output_dir.

        See Also:
            GMNS: General Modeling Network Specification(https://github.com/zephyr-data-specs/GMNS)

        Example:
            >>> from vissim2gmns import VISSIM2GMNS
            >>> vissim = VISSIM2GMNS("./vissim_data/dir")
            >>> vissim.vissim_to_gmns()
            >>> Successfully save inpx file to csv: ...
            >>> Successfully save fzp file to csv: ...
            >>> Successfully save fhz file to csv: ...
            >>> vissim.vissim_to_gmns(output_dir="./output", isShp=True, isGeojson=True, isCsv=True)
            >>> Successfully save vissim files to csv / geojson / shp under output_dir ...

        Return:
            bool: True if the conversion is successful, False otherwise.
        """
        # Control the output format and output directory by kwargs
        output_dir = kwargs.get("output_dir")
        self._output_dir = path2linux(output_dir) if output_dir else self._output_dir
        isCsv = kwargs.get("isCsv", False)
        isGeojson = kwargs.get("isGeojson", True)
        isShp = kwargs.get("isShp", False)

        for i in self._input_files:
            if i.suffix == ".inpx":
                logger.info("############## Begin to process inpx file! ######################\n")

                # path_output = Path(path2linux(os.path.join(self._output_dir, i.name)))
                self.inpx_dict = vissim_inpx(i, output_dir=self._output_dir, isCsv=isCsv, isGeojson=isGeojson, isShp=isShp)

            elif i.suffix == ".fzp":
                logger.info("############## Begin to process fzp file! ######################\n")
                path_vissim_inpx = next((j for j in self._input_files if j.suffix == ".inpx"), None)
                self.fzp_data = vissim_fzp(i,
                                           path_vissim_inpx,
                                           x_col_name=self.x_col_name,
                                           y_col_name=self.y_col_name,
                                           output_dir=self._output_dir,
                                           isCsv=isCsv,
                                           isGeojson=isGeojson,
                                           isShp=isShp)

            elif i.suffix == ".fhz":
                logger.info("############## Begin to process fhz file! ######################\n")

                self.fhz_data = vissim_fhz(i, output_dir=self._output_dir)
            else:
                logger.warning(f"Invalid Input File or Folder: {str(i)}.")
                continue
        return True
