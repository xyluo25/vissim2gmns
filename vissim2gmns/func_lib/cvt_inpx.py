'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

from pathlib import Path
from shapely.geometry import LineString
from shapely.ops import linemerge, transform
from geopandas import GeoDataFrame
import geopandas as gpd
import pandas as pd
from pyproj import CRS, Transformer
import xmltodict
from loguru import logger

# ignore RuntimeWarning, UserWarning
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from .geocoding_vissim_coord import cvt_vissim_to_wgs1984
except ImportError:
    from geocoding_vissim_coord import cvt_vissim_to_wgs1984


SELECTED_INPX_FIELDS = {
    "@vissimVersion": None,
    "@version": None,
    "simulation": None,
    "netPara": None,
    "links": "link",
    "nodes": "node",

    "signalHeads": "signalHead",
    "signalControllers": "signalController",

    "laneMarkingTypes": "laneMarkingType",
    "levels": "level",
    "linkBehaviorTypes": "linkBehaviorType",

    "drivingBehaviors": "drivingBehavior",
    "occupancyDistributions": "occupancyDistribution",
    "pedestrianClasses": "pedestrianClass",
    "pedestrianTypes": "pedestrianType",
    "parkLotGrps": "parkLotGrp",
    "parkingLots": "parkingLot",
    "stopSigns": "stopSign",
    "vehicleClasses": "vehicleClass",
    "vehicleInputs": "vehicleInput",
    "vehicleTypes": "vehicleType",
    "walkingBehaviors": "walkingBehavior",
}

ADDITIONAL_INPX_FIELDS = {
    "anmDefaults": None,
    "areaBehaviorTypes": "areaBehaviorType",
    "backgroundImages": "backgroundImage",
    "colorDistributions": "colorDistribution",
    "conflictAreas": "conflictArea",
    "desAccelerationFunctions": "desAccelerationFunction",
    "desDecelerationFunctions": "desDecelerationFunction",
    "desSpeedDecisions": "desSpeedDecision",
    "desSpeedDistributions": "desSpeedDistribution",
    "displayTypes": "displayType",
    "dynamicAssignment": None,
    "evaluation": None,
    "pedestrianCompositions": "pedestrianComposition",
    "locationDistributions": "locationDistribution",
    "maxAccelerationFunctions": "maxAccelerationFunction",
    "maxDecelerationFunctions": "maxDecelerationFunction",
    "model2D3DDistributions": "model2D3DDistribution",
    "models2D3D": "model2D3D",
    "powerDistributions": "powerDistribution",
    "reducedSpeedAreas": "reducedSpeedArea",
    "timeDistributions": "timeDistribution",
    "timeIntervalSets": "timeIntervalSet",
    "vehicleCompositions": "vehicleComposition",
    "vehicleRoutingDecisionsParking": "vehicleRoutingDecisionParking",
    "vehicleRoutingDecisionsStatic": "vehicleRoutingDecisionStatic",
    "weightDistributions": "weightDistribution",
}


def create_lane_geometries(link_geometry: str | list | LineString,
                           num_lanes: int,
                           lane_width: float | list[float]):
    """Create lane centerline geometries from a link geometry.

    Args:
        link_geometry: A Shapely LineString or an iterable of (x, y) coordinate pairs.
        num_lanes (int): Number of lanes to generate.
        lane_width (float | list[float]): Lane width in meters. A single value is applied to
            every lane. A list must have the same length as ``num_lanes`` and is interpreted
            from rightmost lane to leftmost lane.

    Returns:
        list[LineString]: Lane geometries ordered from rightmost to leftmost relative to the link direction.
    """

    if num_lanes < 1:
        raise ValueError("num_lanes must be at least 1.")

    if isinstance(lane_width, (int, float)):
        lane_widths = [float(lane_width)] * num_lanes
    else:
        lane_widths = [float(width) for width in lane_width]
        if len(lane_widths) == 1:
            lane_widths *= num_lanes
        elif len(lane_widths) != num_lanes:
            # use the first value if lane_width is a list but have different length with num_lanes
            lane_widths = [lane_widths[0]] * num_lanes
            logger.warning(f"  :Length of lane_width list does not match num_lanes. Using the first value {lane_widths[0]} for all lanes.")

    if any(width <= 0 for width in lane_widths):
        raise ValueError("All lane widths must be greater than 0.")

    if isinstance(link_geometry, LineString):
        link_line = link_geometry
    else:
        link_line = LineString(link_geometry)

    if len(link_line.coords) < 2:
        raise ValueError("link_geometry must contain at least two points.")

    centroid = link_line.centroid
    local_crs = CRS.from_proj4(
        f"+proj=aeqd +lat_0={centroid.y} +lon_0={centroid.x} +datum=WGS84 +units=m +no_defs"
    )
    to_local = Transformer.from_crs("EPSG:4326", local_crs, always_xy=True).transform
    to_wgs84 = Transformer.from_crs(local_crs, "EPSG:4326", always_xy=True).transform

    link_local = transform(to_local, link_line)
    lane_geometries = {}
    total_lane_width = sum(lane_widths)
    left_edge_offset = -total_lane_width / 2.0
    accumulated_width = 0.0

    for lane_idx in range(num_lanes):
        offset_distance = left_edge_offset + accumulated_width + lane_widths[lane_idx] / 2.0
        accumulated_width += lane_widths[lane_idx]

        if abs(offset_distance) < 1e-9:
            lane_local = link_local
        else:
            side = "left" if offset_distance > 0 else "right"
            lane_local = link_local.parallel_offset(
                abs(offset_distance),
                side,
                join_style=2,
            )

            if lane_local.geom_type == "MultiLineString":
                lane_local = linemerge(lane_local)
            if lane_local.geom_type != "LineString":
                lane_local = max(
                    (
                        geom
                        for geom in getattr(lane_local, "geoms", [])
                        if geom.geom_type == "LineString"
                    ),
                    key=lambda geom: geom.length,
                    default=link_local,
                )

        lane_geometries[num_lanes - lane_idx] = transform(to_wgs84, lane_local)

    return lane_geometries


@logger.catch
def extract_inpx_data(path_vissim_inpx: str, inc_fields: list = None) -> dict:
    """Extract data from vissim inpx file.

    Args:
        path_vissim_inpx (str): the path to the vissim inpx file.
        inc_fields (list): the fields to be extracted from inpx file. Defaults to None, which means only minimum fields will be extracted.

    Notes:
        - The inpx file is an XML file, and the data is stored in a hierarchical structure. We need to parse the XML file and extract the relevant data. The data is stored in a dictionary format, where the keys are the names of the elements and attributes in the XML file, and the values are the corresponding values.

        - keys starting with "@" are attributes in the original xml file and keys without "@" are elements in the original xml file.

        - the inc_fields include: ["anmDefaults", "areaBehaviorTypes", "backgroundImages", "colorDistributions", "conflictAreas", "desAccelerationFunctions", "desDecelerationFunctions", "desSpeedDecisions", "desSpeedDistributions", "displayTypes",  "dynamicAssignment", "evaluation", "locationDistributions", "maxAccelerationFunctions", "maxDecelerationFunctions", "model2D3DDistributions", "models2D3D", "powerDistributions", "reducedSpeedAreas", "timeDistributions", "timeIntervalSets", "vehicleCompositions", "vehicleRoutingDecisionsParking", "vehicleRoutingDecisionsStatic", "weightDistributions"]

        - default fields include: ["drivingBehaviors", "laneMarkingTypes", "levels", "linkBehaviorTypes", "links", "netPara", "nodes", "occupancyDistributions", "parkLotGrps", "parkingLots", "simulation", "stopSigns", "vehicleClasses", "vehicleInputs", "vehicleTypes", "walkingBehaviors"]

    Returns:
        dict: extracted data from inpx file.
    """

    inpx_dict = {}
    with open(path_vissim_inpx, "r") as f:
        xmlstring = f.read()

    root_dict = xmltodict.parse(xmlstring, encoding="utf-8", process_namespaces=True)
    root_network = root_dict.get("network", {})

    if not root_network:
        logger.error(f"  :Failed to extract network data from inpx file: {path_vissim_inpx}")
        return {}

    # use SELECTED_INPX_FIELDS as default fields to be extracted from inpx file,
    if inc_fields is None:
        INC_INPX_FIELDS = SELECTED_INPX_FIELDS
    else:
        ALL_INPX_FIELDS = {**SELECTED_INPX_FIELDS, **ADDITIONAL_INPX_FIELDS}
        INC_INPX_FIELDS = {
            **SELECTED_INPX_FIELDS,
            **{
                field: ADDITIONAL_INPX_FIELDS[field]
                for field in inc_fields
                if field in ALL_INPX_FIELDS
            },
        }

    # add vissim version
    for each_field in INC_INPX_FIELDS:

        # skip fields that are not in the inpx file
        field_data = root_network.get(each_field, {})
        if not field_data:
            continue

        # load the field data into the inpx_dict
        if INC_INPX_FIELDS[each_field]:
            each_field_data = field_data.get(INC_INPX_FIELDS[each_field], {})

            # only one item within the field
            if isinstance(each_field_data, dict):
                inpx_dict[each_field] = each_field_data
            # multiple items within the field
            elif isinstance(each_field_data, list):
                # record the data by no attribute of each field
                inpx_dict[each_field] = {}
                for each_item in each_field_data:
                    item_id = each_item.get("@no", None)
                    if item_id is not None:
                        inpx_dict[each_field][item_id] = each_item
                    else:
                        logger.warning(f"  :Failed to extract {each_field} data from inpx file: {path_vissim_inpx}. Missing @no attribute in one of the items.")
        else:
            inpx_dict[each_field] = field_data

    return inpx_dict


# @func_running_time
@logger.catch
def vissim_inpx(path_vissim_inpx: str,
                output_dir: str = "", **kwargs) -> dict:
    """Convert vissim inpx file to geopandas dataframe.

    Args:
        path_vissim_inpx (str): the path to the vissim inpx file.
        output_dir (str): the directory to save the output files. Defaults to "".
        **kwargs: other parameters for the conversion, such as isShp, isGeojson, isCsv.

    Notes:
        - output_dir: if not provide no data will be saved.
        - isShp: whether to save the output as shapefile. Default is False.
        - isGeojson: whether to save the output as geojson. Default is True.
        - isCsv: whether to save the output as csv. Default is True.

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_inpx = "path/to/vissim.inpx"
        >>> output_dir = "path/to/output"

        >>> inpx_dict = vg.vissim_inpx(path_vissim_inpx)  # get the inpx data as a dictionary
        >>> inpx_dict = vg.vissim_inpx(path_vissim_inpx, output_dir=output_dir) # get inpx data and save csv and geojson files to the output_dir.
        >>> inpx_dict = vg.vissim_inpx(path_vissim_inpx, output_dir=output_dir, isShp=True, isGeojson=True, isCsv=True)
        >>>     # get inpx data and save csv, geojson and shapefile to the output_dir.

    Returns:
        dict: the inpx data as a dictionary.
    """

    inpx_dict = extract_inpx_data(path_vissim_inpx, inc_fields=None)

    # extract refPoint coordinates from inpx file
    ref_point_map = inpx_dict.get("netPara", {}).get("refPointMap", {})
    ref_point_net = inpx_dict.get("netPara", {}).get("refPointNet", {})
    x_refmap = float(ref_point_map.get("@x"))
    y_refmap = float(ref_point_map.get("@y"))
    x_refnet = float(ref_point_net.get("@x"))
    y_refnet = float(ref_point_net.get("@y"))

    # Extract link data from inpx file and convert the coordinates to lonlat
    inpx_links = inpx_dict.get("links", {})
    lanes_dict = {}

    for link_id, link_data in inpx_links.items():
        # extract link geometry and convert to lonlat coordinates
        link_geometry = link_data.get("geometry").get("linkPolyPts").get("linkPolyPoint", [])
        points_lst = []
        for point in link_geometry:
            vissim_x = float(point.get("@x"))
            vissim_y = float(point.get("@y"))
            lon, lat = cvt_vissim_to_wgs1984(vissim_x, vissim_y,
                                             x_refmap, y_refmap,
                                             x_refnet, y_refnet)
            points_lst.append((lon, lat))

        # convert LineString to WKT format
        # link_data["geom"] = LineString(points_lst)
        link_data["geom"] = LineString(points_lst)
        link_data["geom_points"] = points_lst

        # extract lane data and add link_id to each lane
        # lane index in leftmost to rightmost order with index starting from 1.
        link_lanes = link_data.get("lanes").get("lane")
        if link_lanes:
            if isinstance(link_lanes, dict):
                link_data["num_lanes"] = 1
                link_lanes["link_id"] = link_id
                link_lanes["lane_index"] = 1
                link_lanes["lane_id"] = f"{link_id}_1"
                link_lanes["geom"] = link_data["geom"]
                # link_lanes["geom_points"] = link_data["geom_points"]

                lanes_dict[f"{link_id}_1"] = link_lanes
            elif isinstance(link_lanes, list):

                # update num_lanes in link_data, which will be used to create lane geometries later
                link_data["num_lanes"] = len(link_lanes)

                # get lane width from link_lanes, if lane width is not specified, use the default lane width of 3.0 meters
                lane_width = [float(lane.get("@width", 3.0)) for lane in link_lanes]
                lane_geometries = create_lane_geometries(
                    link_data["geom"],
                    len(link_lanes),
                    lane_width,
                )
                # update link_data geom with MultiplineString geometry created from lane geometries, which will be used for mapping the vehicles on the link geometry later
                link_data["geom"] = linemerge(list(lane_geometries.values()))

                for lane_idx, lane_data in enumerate(link_lanes):
                    add_on = {"link_id": link_id, "lane_index": lane_idx + 1, "lane_id": f"{link_id}_{lane_idx + 1}"}
                    lane_data.update(add_on)
                    lane_data["geom"] = lane_geometries[lane_idx + 1]
                    # lane_data["geom_points"] = list(lane_geometries[lane_idx].coords)

                    lanes_dict[f"{link_id}_{lane_idx + 1}"] = lane_data
        else:
            continue

    # remove geometry and lanes attribute from inpx_links, since they are not needed in the final output
    for link_id, link_data in inpx_links.items():
        link_data.pop("geometry", None)
        link_data.pop("lanes", None)

    # create line series
    df_links = pd.DataFrame.from_dict(inpx_links, orient="index").reset_index(drop=True)
    df_lanes = pd.DataFrame.from_dict(lanes_dict, orient="index").reset_index(drop=True)

    # line_series = gpd.GeoSeries(link_linestring_lst)
    # line_df = gpd.GeoDataFrame({"geometry": line_series}, crs="EPSG:4326")

    gdf_links = gpd.GeoDataFrame(df_links, geometry="geom", crs="EPSG:4326")
    gdf_lanes = gpd.GeoDataFrame(df_lanes, geometry="geom", crs="EPSG:4326")

    # add link id column at the first column
    gdf_links.insert(0, "link_id", gdf_links["@no"])

    # save the results to csv and geojson files if output_dir is specified
    if output_dir:

        isCsv = kwargs.get("isCsv", False)
        isGeojson = kwargs.get("isGeojson", True)
        isShp = kwargs.get("isShp", False)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # get input inpx file name without suffix to use as output file name
        output_link = output_dir / f"{Path(path_vissim_inpx).stem}_inpx_links"
        output_lane = output_dir / f"{Path(path_vissim_inpx).stem}_inpx_lanes"

        # save to csv file
        if isCsv:
            output_link_csv = output_link.with_suffix(f"{output_link.suffix}.csv")
            output_lane_csv = output_lane.with_suffix(f"{output_lane.suffix}.csv")
            gdf_links.to_csv(output_link_csv, index=False)
            gdf_lanes.to_csv(output_lane_csv, index=False)
            logger.info(f"Successfully saved inpx file to csv: {output_dir}")

        # save to geojson file
        if isGeojson:
            output_link_geojson = output_link.with_suffix(f"{output_link.suffix}.geojson")
            output_lane_geojson = output_lane.with_suffix(f"{output_lane.suffix}.geojson")

            gdf_links.to_file(output_link_geojson, driver="GeoJSON")
            gdf_lanes.to_file(output_lane_geojson, driver="GeoJSON")
            logger.info(f"Successfully saved inpx file to geojson: {output_dir}")

        # save to shapefile
        if isShp:
            output_link_shp = output_link.with_suffix(".shp")
            output_lane_shp = output_lane.with_suffix(".shp")
            gdf_links.to_file(output_link_shp, driver="ESRI Shapefile")
            gdf_lanes.to_file(output_lane_shp, driver="ESRI Shapefile")
            logger.info(f"Successfully saved inpx file to shapefile: {output_dir}")

    # add lanes data to inpx_dict
    inpx_dict["lanes"] = lanes_dict
    return inpx_dict


if __name__ == "__main__":
    path_vissim_inpx = r"C:\Users\xyluo25\anaconda3_workspace\001_GitHub\vissim2gmns\datasets\aveiro_port_net\Aveiro_Port_Train_Network_25_03_2026.inpx"
    inpx_dict = vissim_inpx(path_vissim_inpx, output_dir=Path.cwd())
