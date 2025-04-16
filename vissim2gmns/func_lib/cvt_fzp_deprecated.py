'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''


import contextlib
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
from pyufunc import func_running_time
from .geocoding_vissim_coord import cvt_vissim_to_wgs1984


@func_running_time
def vissim_fzp(path_vissim_fzp: str,
               x_refmap: float, y_refmap: float,
               x_refnet: float, y_refnet: float,
               x_col_name: str = "POS", y_col_name: str = "POSLAT") -> GeoDataFrame:
    """Convert vissim fzp file to geopandas dataframe.

    Args:
        path_vissim_fzp (str): the path to the vissim fzp file.
        x_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to -9772674.016.
        y_refmap (float): coordinates of the reference point of the background map(Mercator). Defaults to 5317775.409.
        x_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        y_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        x_col_name (str): the longitude column name in fzp file to convert fzp file to geojson. Defaults to "POS".
        y_col_name (str): the latitude column name in fzp file to convert fzp file to geojson. Defaults to "POSLAT".

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_fzp = "./vissim_data/xl_002_001.fzp"
        >>> x_refmap = -9772674.016  # You can get this value from VISSIM software.
        >>> y_refmap = 5317775.409  # You can get this value from VISSIM software.
        >>> x_refnet = 0  # You can get this value from VISSIM software.
        >>> y_refnet = 0  # You can get this value from VISSIM software.
        >>> df_fzp = vg.vissim_fzp(path_vissim_fzp, x_refmap, y_refmap, x_refnet, y_refnet)
        >>> # Save the results to geojson and csv files.
        >>> df_fzp.to_file("vissim_fzp.geojson", driver="GeoJSON")
        >>> df_fzp.to_csv("vissim_fzp.csv", index=False)

    Returns:
        GeoDataFrame: converted geopandas dataframe.
    """

    df_fzp = ""
    with open(path_vissim_fzp, 'rb') as ff:
        df_fzp = pd.DataFrame(ff.readlines())

    fzp_date = str(df_fzp.iloc[3, :])  # Get the vissim running time(date)

    start_fzp = next((i for i in range(len(df_fzp)) if str(df_fzp.iloc[i, 0])[3:10] == "VEHICLE"), 0)

    # fzp file starts from start_fzp(row 28)
    vissim_fzpdata = df_fzp.iloc[start_fzp:]
    fzp_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fzpdata.iloc[:, 0]])

    columns_pre = []
    columns_pre = list(fzp_data.iloc[0])
    for i in columns_pre:
        if "\\r\\n'" in i:
            columns_pre[columns_pre.index(i)] = i[:-5]

    fzp_data.columns = columns_pre

    fzp_data = fzp_data.iloc[1:]
    fzp_data = fzp_data.reset_index(drop=True)
    fzp_data.iloc[:, 0] = [i.split("'")[1] for i in fzp_data.iloc[:, 0]]

    fzp_data.iloc[:, 0] = fzp_data.iloc[:, 0].astype(float)

    fzp_data["datetime"] = pd.to_datetime(fzp_date.split("\\")[0].split(
        "Date: ")[1]) + pd.to_timedelta(fzp_data.iloc[:, 0], unit='s')

    fzp_data[y_col_name] = fzp_data[y_col_name].apply(lambda x: x[:-5])

    for coor in range(len(fzp_data[x_col_name])):
        # "COORDREARX"
        with contextlib.suppress(Exception):
            (
                fzp_data.loc[coor, f"{x_col_name}_wgs"],
                fzp_data.loc[coor, f"{y_col_name}_wgs"],
            ) = cvt_vissim_to_wgs1984(
                float(fzp_data.loc[coor, x_col_name]),
                float(fzp_data.loc[coor, y_col_name]),
                x_refmap,
                y_refmap,
                x_refnet,
                y_refnet,
            )

    x_col_name_lonlat = f"{x_col_name}_wgs"
    y_col_name_lonlat = f"{y_col_name}_wgs"

    geometry = [Point(xy) for xy in zip(fzp_data[x_col_name_lonlat], fzp_data[y_col_name_lonlat])]
    return GeoDataFrame(fzp_data, crs="EPSG:4326", geometry=geometry)
