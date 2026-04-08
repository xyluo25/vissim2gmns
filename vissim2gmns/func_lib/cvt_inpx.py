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
import pandas as pd
from pyufunc import func_running_time

try:
    from .geocoding_vissim_coord import cvt_vissim_to_wgs1984
except ImportError:
    from geocoding_vissim_coord import cvt_vissim_to_wgs1984


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
    links_iter = root.findall("links")[0]
    link_list = links_iter.findall("link")

    # link_data_lonlat = []  # transfered x, y multistring data
    links_dict = {}
    lanes_dict = {}
    print(f"  :Converting {len(link_list)} links in inpx file to lonlat coordinates...")
    for link in link_list:
        link_attr_dict = link.attrib
        link_no = link_attr_dict["no"]
        temp2 = []

        with contextlib.suppress(Exception):
        # link[0] -> geometry; link[0][0] -> linkPolyPts inside geometry; link[0][0] -> lanes
            for each_pt in link[0][0]:
                vissim_x_val = float(each_pt.attrib["x"])
                vissim_y_val = float(each_pt.attrib["y"])
                temp2.append(cvt_vissim_to_wgs1984(vissim_x_val,
                                                   vissim_y_val,
                                                   x_refmap,
                                                   y_refmap,
                                                   x_refnet,
                                                   y_refnet))

        link_attr_dict["num_lanes"] = len(link[1])
        link_attr_dict["geom"] = LineString(temp2)

        links_dict[link_no] = link_attr_dict

        with contextlib.suppress(Exception):
            # link[0][1] -> lanes
            lane_idx = 0
            for lane in link[1]:
                lane_attr_dict = lane.attrib
                # print(f"  :Processing lane {lane_attr_dict}...")
                lane_attr_dict["link_id"] = link_no
                lane_attr_dict["lane_index"] = lane_idx

                # skip lanes with only 2 attributes within the dictionary
                if len(lane_attr_dict) == 2:
                    continue
                lane_idx += 1
                lanes_dict[f"{link_no}_{lane_idx}"] = lane_attr_dict

    # create line series
    df_links = pd.DataFrame.from_dict(links_dict, orient="index").reset_index(drop=True)
    df_lanes = pd.DataFrame.from_dict(lanes_dict, orient="index").reset_index(drop=True)
    # line_series = gpd.GeoSeries(link_linestring_lst)
    # line_df = gpd.GeoDataFrame({"geometry": line_series}, crs="EPSG:4326")

    gdf_links = gpd.GeoDataFrame(df_links, geometry="geom", crs="EPSG:4326")

    # add link id column at the first column
    gdf_links.insert(0, "link_id", gdf_links["no"])

    if output_fname:
        output_fname_csv = Path(output_fname).with_suffix(
            f"{Path(output_fname).suffix}.csv"
        )
        gdf_links.to_csv(output_fname_csv, index=False)
        print(f"  :Successfully saved inpx file to csv: {output_fname}")

        output_fname_geojson = Path(output_fname).with_suffix(
            f"{Path(output_fname).suffix}.geojson"
        )
        gdf_links.to_file(output_fname_geojson, driver="GeoJSON")
        print(f"  Successfully saved inpx file to geojson: {output_fname_geojson}")

    return gdf_links
