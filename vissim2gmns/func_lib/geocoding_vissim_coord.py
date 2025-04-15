'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

import math


def cvt_vissim_to_wgs1984(x_vissim: float, y_vissim: float,
                          x_refmap: float, y_refmap: float,
                          x_refnet: float, y_refnet: float) -> list:
    """Convert single coordinate from VISSIM to WGS 1984.

    Local coordinates in PTV Vissim use a cartesian coordinate system,
    with a reference to a background position in Mercator coordinates.

    Args:
        x_vissim (float): the x coordinate in VISSIM
        y_vissim (float): the y coordinate in VISSIM
        x_refmap (float): coordinates of the reference point of the background map(Mercator).
        y_refmap (float): coordinates of the reference point of the background map(Mercator).
        x_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System).
        y_refnet (int): coordinates of the reference point of the network(Cartesian Vissim System).

    Example:
        >>> from vissim2geojson import cvt_vissim_to_wgs1842
        >>> x_refmap = -9772674.016  # You can get this value from VISSIM software.
        >>> y_refmap = 5317775.409  # You can get this value from VISSIM software.
        >>> x_refnet = 0  # You can get this value from VISSIM software.
        >>> y_refnet = 0  # You can get this value from VISSIM software.
        >>> x_vissim = -0.255  # The x coordinate in .inpx file (coordinate in VISSIM)
        >>> y_vissim = 39.368  # The y coordinate in .inpx file (coordinate in VISSIM)
        >>> # Convert VISSIM coordinates to WGS 1984 coordinates.
        >>> cvt_vissim_to_wgs1842(x_vissim, y_vissim, x_refmap, y_refmap, x_refnet, y_refnet)
        >>> # return the converted coordinate in WGS 1984, [Longitude, Latitude]

    Returns:
        list: the converted coordinate in WGS 1984, [Longitude, Latitude]
    """
    Pi = 3.14159265358979  # vissim system
    Pi_this = 3.14159265358979323846264338  # our detailed pi
    EarthRadius = 6378137  # vissim system earth radius

    # CorrectionFactorMercator,
    # the correction factor is required for transforming the latitude of a sphere(Mercator) to the WGS 84 ellipse.
    # CorrectionFactorMercator = 1.001120232
    CorrectionFactorMercator = 1.0011202320000001

    # WGS84 latitude coordinate for the reference point map.  Base map -> Network Setting -> Display
    LatitudeRefPointMap = (
        2 * math.atan(math.exp(CorrectionFactorMercator * y_refmap / EarthRadius)) - Pi_this / 2) / (Pi_this / 180)

    LocalScale = 1 / math.cos(LatitudeRefPointMap * Pi_this / 180)

    # MercatorXFront  #Mercator coordinate X of the front of the vehicle
    MercatorX = (x_vissim - x_refnet) * LocalScale + x_refmap
    MercatorY = (y_vissim - y_refnet) * LocalScale + y_refmap

    a_cor = CorrectionFactorMercator
    r = EarthRadius
    Longitude = a_cor * MercatorX / (Pi * r / 180)
    Latitude = (2 * math.atan(math.exp(CorrectionFactorMercator * MercatorY / EarthRadius)) - Pi / 2) / (Pi / 180)

    return [Longitude, Latitude]
