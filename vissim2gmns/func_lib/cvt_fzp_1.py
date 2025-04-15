'''
##############################################################
# Created Date: Tuesday, April 15th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''


import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
from joblib import Parallel, delayed
import contextlib
from .geocoding_vissim_coord import cvt_vissim_to_wgs1984
import numpy as np
import contextlib


def vissim_fzp_t(path_vissim_fzp: str,
               x_refmap: float, y_refmap: float,
               x_refnet: float, y_refnet: float,
               x_col_name: str = "POS", y_col_name: str = "POSLAT") -> GeoDataFrame:
    """Convert vissim fzp file to geopandas dataframe.

    Args:
        path_vissim_fzp (str): the path to the vissim fzp file.
        x_refmap (float): coordinates of the reference point of the background map (Mercator).
        y_refmap (float): coordinates of the reference point of the background map (Mercator).
        x_refnet (int): coordinates of the reference point of the network (Cartesian Vissim System).
        y_refnet (int): coordinates of the reference point of the network (Cartesian Vissim System).
        x_col_name (str): the longitude column name in fzp file to convert fzp file to geojson.
        y_col_name (str): the latitude column name in fzp file to convert fzp file to geojson.

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_fzp = "./vissim_data/xl_002_001.fzp"
        >>> x_refmap = -9772674.016  # You can get this value from VISSIM software.
        >>> y_refmap = 5317775.409   # You can get this value from VISSIM software.
        >>> x_refnet = 0            # You can get this value from VISSIM software.
        >>> y_refnet = 0            # You can get this value from VISSIM software.
        >>> df_fzp = vg.vissim_fzp(path_vissim_fzp, x_refmap, y_refmap, x_refnet, y_refnet)
        >>> # Save the results to geojson and csv files.
        >>> df_fzp.to_file("vissim_fzp.geojson", driver="GeoJSON")
        >>> df_fzp.to_csv("vissim_fzp.csv", index=False)

    Returns:
        GeoDataFrame: converted geopandas dataframe.
    """

    # Read fzp file as binary and create a DataFrame of byte lines.
    with open(path_vissim_fzp, 'rb') as ff:
        df_fzp = pd.DataFrame(ff.readlines())

    # Retrieve the VISSIM running date from a specific row.
    fzp_date = str(df_fzp.iloc[3, :])

    start_fzp = next((i for i in range(len(df_fzp)) if str(df_fzp.iloc[i, 0])[3:10] == "VEHICLE"), 0)

    # fzp file starts from the identified start position.
    vissim_fzpdata = df_fzp.iloc[start_fzp:]
    fzp_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fzpdata.iloc[:, 0]])

    # Clean up and assign column names.
    columns_pre = list(fzp_data.iloc[0])
    for i in columns_pre:
        if "\\r\\n'" in i:
            columns_pre[columns_pre.index(i)] = i[:-5]
    fzp_data.columns = columns_pre

    # Process the data rows.
    fzp_data = fzp_data.iloc[1:].reset_index(drop=True)
    fzp_data.iloc[:, 0] = [i.split("'")[1] for i in fzp_data.iloc[:, 0]]
    fzp_data.iloc[:, 0] = fzp_data.iloc[:, 0].astype(float)

    # Create a datetime column based on the fzp file's date and time offset.
    fzp_data["datetime"] = pd.to_datetime(
        fzp_date.split("\\")[0].split("Date: ")[1]
    ) + pd.to_timedelta(fzp_data.iloc[:, 0], unit='s')

    # Clean the y-coordinate column values.
    fzp_data[y_col_name] = fzp_data[y_col_name].apply(lambda x: x[:-5])

    # Convert the x and y columns to NumPy arrays of floats.
    x_vals = fzp_data[x_col_name].astype(float).to_numpy()
    y_vals = fzp_data[y_col_name].astype(float).to_numpy()

    # Create a vectorized version of the cvt_vissim_to_wgs1984 function.
    vec_cvt = np.vectorize(cvt_vissim_to_wgs1984, otypes=[float, float])

    # Apply the vectorized function to compute new coordinates.
    x_wgs, y_wgs = vec_cvt(x_vals, y_vals, x_refmap, y_refmap, x_refnet, y_refnet)
    fzp_data[f"{x_col_name}_wgs"] = x_wgs
    fzp_data[f"{y_col_name}_wgs"] = y_wgs

    # ----------------------------------------------------------------------------

    # Create geometry for the GeoDataFrame.
    geometry = [Point(xy) for xy in zip(fzp_data[f"{x_col_name}_wgs"], fzp_data[f"{y_col_name}_wgs"])]

    return GeoDataFrame(fzp_data, crs="EPSG:4326", geometry=geometry)