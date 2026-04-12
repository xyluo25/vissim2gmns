'''
##############################################################
# Created Date: Tuesday, April 15th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''


from pathlib import Path

from loguru import logger
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import numpy as np
from pyufunc import str_strip

# ignore RuntimeWarning
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    # from .geocoding_vissim_coord import cvt_vissim_to_wgs1984
    from .cvt_inpx import vissim_inpx
    from .link_projection import point_on_wkt_line_by_distance
except ImportError:
    # from geocoding_vissim_coord import cvt_vissim_to_wgs1984
    from cvt_inpx import vissim_inpx
    from link_projection import point_on_wkt_line_by_distance


def remove_stripe_values(value):
    """Remove stripe values from a string."""
    if isinstance(value, str):
        return value.replace("\\r", "").replace("\\n", "").replace("\n", "").replace("b'", "").replace("'", "")
    return value


def vissim_fzp(path_vissim_fzp: str,
               path_vissim_inpx: str,
               *,
               x_col_name: str = "POS",
               y_col_name: str = "POSLAT",
               output_dir: str = "",
               **kwargs) -> GeoDataFrame:
    """Convert vissim fzp file to geopandas dataframe.

    Args:
        path_vissim_fzp (str): the path to the vissim fzp file.
        path_vissim_inpx (str): the path to the vissim inpx file.
        x_col_name (str): the longitude column name in fzp file to convert fzp file to geojson.
        y_col_name (str): the latitude column name in fzp file to convert fzp file to geojson.
        output_dir (str): the directory to save the output files. Defaults to "".
        **kwargs: other parameters for the conversion, such as isShp, isGeojson, isCsv.

    Notes:
        - output_dir: if not provide no data will be saved.
        - isShp: whether to save the output as shapefile. Default is False.
        - isGeojson: whether to save the output as geojson. Default is False.
        - isCsv: whether to save the output as csv. Default is True.

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_fzp = "./vissim_data/xl_002_001.fzp"
        >>> path_vissim_inpx = "./vissim_data/xl_002_001.inpx"
        >>> output_dir = "./output"
        >>> x_col_name = "POS"
        >>> y_col_name = "POSLAT"
        >>>
        >>> # get the fzp data as a geopandas dataframe without saving to file.
        >>> df_fzp = vg.vissim_fzp(path_vissim_fzp, path_vissim_inpx)
        >>>
        >>> # get the fzp data as a geopandas dataframe and save shp files (default) to the output_dir.
        >>> df_fzp = vg.vissim_fzp(path_vissim_fzp, path_vissim_inpx, output_dir=output_dir)
        >>>
        >>> # get the fzp data as a geopandas dataframe and control the output file format by setting isShp, isGeojson and isCsv parameters.
        >>> df_fzp = vg.vissim_fzp(path_vissim_fzp, path_vissim_inpx, output_dir=output_dir, isShp=True, isGeojson=True, isCsv=True)

    Returns:
        GeoDataFrame: converted geopandas dataframe.
    """

    # Get inpx data (specially the link geometry) to use for mapping the vehicles on the link geometry.
    inpx_dict = vissim_inpx(path_vissim_inpx)

    # extract refPoint coordinates from inpx file
    ref_point_map = inpx_dict.get("netPara", {}).get("refPointMap", {})
    ref_point_net = inpx_dict.get("netPara", {}).get("refPointNet", {})
    x_refmap = float(ref_point_map.get("@x"))
    y_refmap = float(ref_point_map.get("@y"))
    x_refnet = float(ref_point_net.get("@x"))
    y_refnet = float(ref_point_net.get("@y"))

    # Read fzp file as binary and create a DataFrame of byte lines.
    with open(path_vissim_fzp, 'rb') as ff:
        df_fzp = pd.DataFrame(ff.readlines())

    logger.info(f"Total {len(df_fzp)} vehicle points in fzp file")

    # Retrieve the VISSIM running date from a specific row.
    fzp_date = str(df_fzp.iloc[3, :])

    # remove \\r and \\n, \n characters from staring values
    fzp_date = remove_stripe_values(fzp_date)

    start_fzp = next((i for i in range(len(df_fzp)) if str(df_fzp.iloc[i, 0])[3:10] == "VEHICLE"), 0)

    # fzp file starts from the identified start position.
    vissim_fzpdata = df_fzp.iloc[start_fzp:]
    fzp_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fzpdata.iloc[:, 0]])

    # Clean up and assign column names.
    fzp_data = fzp_data.map(remove_stripe_values)

    # Clean up and assign column names.
    columns_pre = list(fzp_data.iloc[0])
    for i in columns_pre:
        if "\\r\\n'" in i:
            columns_pre[columns_pre.index(i)] = i[:-5]
    fzp_data.columns = columns_pre

    # Process the data rows.
    fzp_data = fzp_data.iloc[1:].reset_index(drop=True)
    # fzp_data.iloc[:, 0] = [i.split("'")[1] for i in fzp_data.iloc[:, 0]]
    # fzp_data.iloc[:, 0] = fzp_data.iloc[:, 0].astype(float)
    time_col = fzp_data.columns[0]
    fzp_data[time_col] = pd.to_numeric(fzp_data[time_col], errors="coerce")

    # Create a datetime column based on the fzp file's date and time offset.
    fzp_data["datetime"] = pd.to_datetime(
        fzp_date.split("Name")[0].split("Date:")[1].lstrip(),
        # format="%d/%m/%Y %H:%M:%S",
        # errors="coerce"
    ) + pd.to_timedelta(fzp_data.iloc[:, 0], unit="s")
    # format datetime to "%d/%m/%Y %H:%M:%S"
    # fzp_data["datetime"] = fzp_data["datetime"].dt.strftime("%d/%m/%Y %H:%M:%S")

    # Clean the y-coordinate column values.
    fzp_data[x_col_name] = fzp_data[x_col_name].map(str_strip)
    fzp_data[y_col_name] = fzp_data[y_col_name].map(str_strip)

    # add new columns for wgs84 coordinates
    fzp_data[f"{x_col_name}_wgs"] = np.nan
    fzp_data[f"{y_col_name}_wgs"] = np.nan

    logger.info("Start projecting vehicle points on the lane geometry to get accurate coordinates in wgs84...")
    # update x_wgs and y_wgs from table
    for idx, row in fzp_data.iterrows():
        # get the link id that column starts with "LANE\\LINK" in fzp file
        link_id = row.get(r"LANE\\LINK")
        # if not get link id, fine column starts with "LANE\\Link" and get link id
        if pd.isna(link_id):
            col_link = [col for col in fzp_data.columns if "lane" in col.lower() and "link" in col.lower()]
            if col_link:
                link_id = row.get(col_link[0])

        lane_index = row.get("LANE")
        if pd.isna(lane_index):
            col_lane = [col for col in fzp_data.columns if "lane" in col.lower() and "link" not in col.lower()]
            if col_lane:
                lane_index = row.get(col_lane[0])

        if "-" in lane_index:
            # extract lane geometry from inpx_dict
            lane_id = lane_index.replace("-", "_")
        else:
            lane_id = rf"{link_id}_{lane_index}"

        lane_geom = inpx_dict.get("lanes", {}).get(lane_id, {}).get("geom")
        if lane_geom:
            # get the distance of the vehicle on the lane from the start point of the lane
            distance_on_lane = row.get(f"{x_col_name}")
            if pd.notna(distance_on_lane):
                # project the vehicle point on the lane geometry to get the accurate x and y coordinates in wgs84
                projected_point = point_on_wkt_line_by_distance(lane_geom,
                                                                float(distance_on_lane))
                if projected_point:
                    fzp_data.at[idx, f"{x_col_name}_wgs"] = projected_point.x
                    fzp_data.at[idx, f"{y_col_name}_wgs"] = projected_point.y

    # Create geometry for the GeoDataFrame.
    geometry = [Point(xy) for xy in zip(fzp_data[f"{x_col_name}_wgs"], fzp_data[f"{y_col_name}_wgs"])]

    gdf_fzp = GeoDataFrame(fzp_data, crs="EPSG:4326", geometry=geometry)

    if output_dir:
        isCsv = kwargs.get("isCsv", False)
        isGeojson = kwargs.get("isGeojson", True)
        isShp = kwargs.get("isShp", False)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_fzp = output_dir / f"{Path(path_vissim_fzp).stem}_fzp"

        # save to csv file
        if isCsv:
            output_fzp_csv = output_fzp.with_suffix(f"{output_fzp.suffix}.csv")
            gdf_fzp.to_csv(output_fzp_csv, index=False)
            logger.info(f"Successfully saved fzp file to csv: {output_dir}")

        # save to geojson file
        if isGeojson:
            output_fzp_geojson = output_fzp.with_suffix(f"{output_fzp.suffix}.geojson")
            gdf_fzp.to_file(output_fzp_geojson,
                            driver="GeoJSON")
            logger.info(f"Successfully saved fzp file to geojson: {output_dir}")

        # save to shapefile
        if isShp:
            output_fzp_shp = output_fzp.with_suffix(".shp")
            gdf_fzp.to_file(output_fzp_shp,
                            driver="ESRI Shapefile")
            logger.info(f"Successfully saved fzp file to shapefile: {output_dir}")

    return gdf_fzp


if __name__ == "__main__":
    path_vissim_inpx = r"C:\Users\xyluo25\anaconda3_workspace\001_GitHub\vissim2gmns\datasets\one_intersection\xl_002_001.inpx"
    path_vissim_fzp = r"C:\Users\xyluo25\anaconda3_workspace\001_GitHub\vissim2gmns\datasets\one_intersection\xl_002_001.fzp"

    x_col_name: str = "POS"
    y_col_name: str = "POSLAT"

    gdf_fzp = vissim_fzp(path_vissim_fzp, path_vissim_inpx)
    gdf_fzp_1000 = gdf_fzp.head(1000)
    gdf_fzp_1000.to_file("vissim_fzp_1000.geojson", driver="GeoJSON")

    # save to shp file
    gdf_fzp_1000.to_file("vissim_fzp_1000.shp", driver="ESRI Shapefile")
    # gdf_fzp.to_file("vissim_fzp.geojson", driver="GeoJSON")