'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

import contextlib
from pathlib import Path
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
from geopandas import GeoDataFrame
import geopandas as gpd
from pyufunc import func_running_time

from .geocoding_vissim_coord import cvt_vissim_to_wgs1984


@func_running_time
def vissim_inpx(path_vissim_inpx: str,
                x_refmap: float, y_refmap: float,
                x_refnet: float, y_refnet: float,
                output_fname: str = "") -> GeoDataFrame:
    """Convert vissim inpx file to geopandas dataframe.

    Args:
        path_vissim_inpx (str): the path to the vissim inpx file.
        x_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to -9772674.016.
        y_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to 5317775.409.
        x_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        y_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        output_fname (str): save results to GMNS formatted csv and geojson files. Defaults to "".

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_inpx = "path/to/vissim.inpx"
        >>> x_refmap = -9772674.016  # You can get this value from VISSIM software.
        >>> y_refmap = 5317775.409  # You can get this value from VISSIM software.
        >>> x_refnet = 0  # You can get this value from VISSIM software.
        >>> y_refnet = 0  # You can get this value from VISSIM software.
        >>> output_fname = "vissim_inpx"
        >>> df_inpx = vg.vissim_inpx(path_vissim_inpx, x_refmap, y_refmap, x_refnet, y_refnet)
        >>> df_inpx.to_file("vissim_inpx.geojson", driver="GeoJSON")
        >>> df_inpx.to_csv("vissim_inpx.csv", index=False)
        >>> # Or your can use the output_fname parameter to save the results.
        >>> df_inpx = vg.vissim_inpx(path_vissim_inpx, x_refmap, y_refmap, x_refnet, y_refnet, output_fname=output_fname)
        >>> # df_inpx will be saved as "vissim_inpx.csv" and "vissim_inpx.geojson" in the output folder.

    Returns:
        GeoDataFrame: converted geopandas dataframe.
    """

    with open(path_vissim_inpx, "r") as f:
        xmlstring = f.read()

    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    link = root.findall("links")[0]

    # link_data_lonlat = []  # transfered x, y multistring data
    link_linestring_lst = []
    print(f"  :Converting {len(link)} links in inpx file to lonlat coordinates...")
    for i in range(len(link)):
        temp2 = []  # transferred single x, y data
        for j in range(len(link[i])):
            for k in range(len(link[i][j])):
                with contextlib.suppress(Exception):
                    for m in range(len(link[i][j][k])):
                        vissim_x_val = float(link[i][j][k][m].attrib["x"])
                        vissim_y_val = float(link[i][j][k][m].attrib["y"])
                        temp2.append(cvt_vissim_to_wgs1984(vissim_x_val,
                                                           vissim_y_val,
                                                           x_refmap,
                                                           y_refmap,
                                                           x_refnet,
                                                           y_refnet))

        link_linestring_lst.append(LineString(temp2))  # link transferred
        # link transferred

    # create line series
    line_series = gpd.GeoSeries(link_linestring_lst)
    line_df = gpd.GeoDataFrame({"geometry": line_series}, crs="EPSG:4326")

    if output_fname:
        output_fname = Path(output_fname).with_suffix(".csv")
        line_df.to_csv(output_fname, index=False)
        print(f"  :Successfully saved inpx file to csv: {output_fname}")

        output_fname_geojson = Path(output_fname).with_suffix(".geojson")
        line_df.to_file(output_fname_geojson, driver="GeoJSON")
        print(f"  Successfully saved inpx file to geojson: {output_fname_geojson}")

    return line_df
