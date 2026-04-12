'''
##############################################################
# Created Date: Thursday, April 9th 2026
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

from loguru import logger
from shapely import wkt
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import linemerge
from pyproj import Geod


def point_on_wkt_line_by_distance(
    link_geom: str | LineString | MultiLineString,
    distance_in_meters: float
) -> Point:
    """Generate a WGS84 point on a line at a given distance from the start.

    Args:
        link_geom (str | LineString | MultiLineString): WKT string or Shapely geometry representing a LINESTRING or mergeable MULTILINESTRING.
        distance_in_meters (float): Distance along the line in meters from the start point.

    Returns:
        Point: A Shapely Point object representing the location on the line at the specified distance.

    Raises:
        ValueError: If the input WKT is not a valid LINESTRING or mergeable MULTILINESTRING, or if the distance is negative or exceeds the line length.
    """

    if distance_in_meters < 0:
        distance_in_meters = 0
        logger.warning("Distance cannot be negative. Set to 0.")

    geom = wkt.loads(link_geom) if isinstance(link_geom, str) else link_geom

    # Support LINESTRING and mergeable MULTILINESTRING
    if isinstance(geom, MultiLineString):
        geom = linemerge(geom)

    if not isinstance(geom, LineString):
        raise ValueError(
            "Input WKT must be a LINESTRING or mergeable MULTILINESTRING.")

    coords = list(geom.coords)
    if len(coords) < 2:
        raise ValueError("Line must contain at least two coordinates.")

    geod = Geod(ellps="WGS84")

    # Distance = 0, return the first point
    if distance_in_meters == 0:
        x0, y0 = coords[0]
        return Point(x0, y0)

    accumulated = 0.0

    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]

        az12, az21, seg_len = geod.inv(lon1, lat1, lon2, lat2)

        if accumulated + seg_len >= distance_in_meters:
            remaining = distance_in_meters - accumulated
            lon, lat, _ = geod.fwd(lon1, lat1, az12, remaining)
            return Point(lon, lat)

        accumulated += seg_len

    # If distance exceeds total line length, return the last point
    return Point(coords[-1])


if __name__ == "__main__":
    link_wkt = "LINESTRING (-111.935 33.421, -111.934 33.422, -111.933 33.423)"
    distance_in_meters = 120

    pt = point_on_wkt_line_by_distance(link_wkt, distance_in_meters)

    print(pt)         # POINT (lon lat)
    print(pt.wkt)     # WKT format
    print(pt.x, pt.y)  # longitude, latitude
