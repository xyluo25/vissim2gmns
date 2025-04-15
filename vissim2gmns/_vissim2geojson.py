# -*- coding:utf-8 -*-
##############################################################
# Created Date: Tuesday, June 14th 2022
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
import os
from os.path import isdir
from pyufunc import get_filenames_by_ext, func_running_time, path2linux
from pathlib import Path
from vissim2gmns.func_lib.cvt_inpx import vissim_inpx
from vissim2gmns.func_lib.cvt_fhz import vissim_fhz
from vissim2gmns.func_lib.cvt_fzp import vissim_fzp


class VISSIM2GMNS:
    """A tool to convert vissim files to geojson and csv.

    Specifically:

    - convert .inpx file to geopandas dataframe and csv/geojson file
    - convert .fzp file to geopandas dataframe and csv/geojson file
    - convert .fhz file to csv file

    Args:
        vissim_file_path (str): the folder or file path to the vissim file
        x_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to -9772674.016.
        y_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to 5317775.409.
        x_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        y_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        x_col_name (str): the longitude column name in fzp file to convert fzp file to geojson. Defaults to "POS".
        y_col_name (str): the latitude column name in fzp file to convert fzp file to geojson. Defaults to "POSLAT".

    """

    def __init__(self,
                 input_dir: str,
                 x_refmap: float = -9772674.016,
                 y_refmap: float = 5317775.409,
                 x_refnet: float = 0,
                 y_refnet: float = 0,
                 x_col_name: str = "POS",
                 y_col_name: str = "POSLAT"):
        """Initialize the VISSIM2GMNS class."""

        print("Please check and correctly input x_refmap, y_refmap, x_refnet and y_refnet from your vissim software!")

        # TDD: test the inputs of the vissim2geojson
        assert isinstance(input_dir, str), "The input vissim_file_path should be a string."
        assert isdir(input_dir), "The input vissim_file_path should be a folder."

        self._input_files = [Path(each_path) for each_path in get_filenames_by_ext(input_dir, file_ext="*")]
        print("  :Input files: ", self.vissim_file_path)

        self._output_dir = path2linux(os.path.join(input_dir, "output"))
        os.makedirs(self._output_dir, exist_ok=True)

        self.x_refmap = x_refmap
        self.y_refmap = y_refmap
        self.x_refnet = x_refnet
        self.y_refnet = y_refnet
        self.x_col_name = x_col_name
        self.y_col_name = y_col_name

    @func_running_time
    def vissim_to_gmns(self) -> bool:
        """Convert vissim files to csv files in GMNS format.

        1. Convert .inpx file to geopandas dataframe and save to csv file.
        2. Convert .fzp file to geopandas dataframe and save to csv file.
        3. Convert .fhz file to pandas dataframe and save to csv file.

        See Also:
            GMNS: General Modeling Network Specification(https://github.com/zephyr-data-specs/GMNS)

        Example:
            >>> from vissim2gmns import VISSIM2GMNS
            >>> x_refmap = -9772674.016  # change to your own value from VISSIM
            >>> y_refmap = 5317775.409  # change to your own value from VISSIM
            >>> x_refnet = 0  # change to your own value from VISSIM
            >>> y_refnet = 0  # change to your own value from VISSIM
            >>> vissim = VISSIM2GMNS("./vissim_data", x_refmap, y_refmap, x_refnet, y_refnet)
            >>> vissim.vissim_to_gmns()
            >>> Successfully save inpx file to csv: ...
            >>> Successfully save fzp file to csv: ...
            >>> Successfully save fhz file to csv: ...
        """

        for i in self._input_files:
            if i.suffix == ".inpx":
                print("############## Begin to process inpx file! ######################\n")

                path_output = Path(path2linux(os.path.join(self._output_dir, i.name)))
                self.inpx_data = vissim_inpx(i,
                                             self.x_refmap, self.y_refmap,
                                             self.x_refnet, self.y_refnet,
                                             path_output)

            elif i.suffix == ".fzp":
                print("############## Begin to process fzp file! ######################\n")

                self.fzp_data = vissim_fzp(i,
                                           self.x_refmap, self.y_refmap,
                                           self.x_refnet, self.y_refnet,
                                           self.x_col_name, self.y_col_name)

                path_output = Path(path2linux(os.path.join(self._output_dir, i.name)))
                path_output_geojson = path_output.with_suffix(".geojson")
                self.fzp_data.to_file(path_output_geojson, driver="GeoJSON")

                path_output_csv = path_output.with_suffix(".csv")
                self.fzp_data.to_csv(path_output_csv, index=False)
                print(f"Successfully Save fzp file to geojson: {self.output_filename}\n")

            elif i.suffix == ".fhz":
                print("############## Begin to process fhz file! ######################\n")

                self.fhz_data = vissim_fhz(i)

                path_output = Path(path2linux(os.path.join(self._output_dir, i.name)))
                path_output = path_output.with_suffix(".csv")
                self.fhz_data.to_csv(path_output, header=True, index=False, encoding="utf_8_sig")

                print(f"Successfully Save fhz file to: {self.output_filename}\n",
                      "fhz file is a vissim output file don't need to transfer to geojson\n")

            else:
                print(f"Invalid Input File or Folder: {str(i)}.")
        return True
