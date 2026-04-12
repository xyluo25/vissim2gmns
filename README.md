# vissim2gmns

vissim2gmns converts VISSIM files (.inpx, .fzp, .fhz) into GMNS format with WGS 1984 coordinates for easy GIS visualization and analysis.

Specifically:

1. convert **.inpx** to csv/geojson/shp files
2. convert **.fzp** file to csv/geojson/shp files
3. convert **.fhz** file to .csv file.

> [!Warning]
>
> We have deprecated the development of [vissim2geojson](https://pypi.org/project/vissim2geojson/) and the latest update have move to [vissim2gmns](https://github.com/xyluo25/vissim2gmns)

## Background Knowledge Before Use This Tool

1. **Vissim Simulation**

   This tool is to conver files geneated by PTV Vissim.

   You will get the layer file (.inpx):

   the .inpx can only open by PTV Vissim and you can use this tool to convert layer file to wgs1984 so that you can open  the layer using different platform (QGIS, Kepler.gl, ArcMap...)

   You will get simulation results (such as .fzp and .fhz, these files can open by PTV Vissim but not other platforms). You can use this tool to convert .fzp file to .geojson and .csv, .fhz file to .geojson and .csv, and then perform analysis based on the simulation results.

## How to use the tool

1. install from pypi

   `pip install vissim2gmns`
2. use case

   Sample user case at intersection
   ![1655249626589](https://github.com/xyluo25/vissim2gmns/blob/main/docs/image/README/1655249626589.png)

   ```python
   import  vissim2gmns as vg

   if__name__=="main":

       input_folder ="./datasets/one_intersection/"  # make sure your .inpx or fhz, fzp files are in your input_folder

       vissim = vg.VISSIM2GMNS(input_folder)

       # This will save output files inside your input_folder (geojson files will be generated in default)
       vissim.vissim_to_gmns()

       # You can decide which files to save: csv, geojson and shp

       isCsv = False  # defalut to False, you can change to True to save csv file
       isGeojsion = True  # default to True, you can change to False not to save the file
       isShp = False  # default to False, you can chagne to True to save  ESRI shp file
       vissim.vissim_to_gmns(isCsv=isCsv, isGeojson=isGeojson, isShp=isShp)

   ```

Enjoy it!
