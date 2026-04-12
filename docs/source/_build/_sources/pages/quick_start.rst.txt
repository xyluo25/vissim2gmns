=================
Quick Start Guide
=================

Quick Python Example
====================

.. note::
    - This quick start guide assumes you have a valid inpx file and the required dependencies installed.

Prepare your Input file
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    input_dir = "datasets/one_intersection/"


Automatically Convert .inpx, .fzp, .fhz to GMNS Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    if __name__ == "__main__":

        input_dir = "datasets/one_intersection/"  # Path to your input directory

        vissim = vg.VISSIM2GMNS(input_dir)
        # results will be saved in the same input directory by default.
        vissim.vissim_to_gmns()

        # if you want to specify the output directory, you can use the following code:
        # output_dir = "path/to/your/output/directory/"
        # net.vissim_to_gmns(output_dir=output_dir)


Control output files
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    if __name__ == "__main__":

        input_dir = "datasets/one_intersection/"  # Path to your input directory

        vissim = vg.VISSIM2GMNS(input_dir)

        isCsv = False  # Set to True if you want to save the output as csv files
        isGeojson = True  # Set to True if you want to save the output as geojson files
        isShp = False  # Set to True if you want to save the output as shp files

        vissim.vissim_to_gmns(isCsv=isCsv, isGeojson=isGeojson, isShp=isShp)


Convert Single File: .inpx to .csv, .geojson and shp files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    if __name__ == "__main__":
        inpx_file = "datasets/one_intersection/Net.inpx"  # Path to your .inpx file
        output_dir = "datasets/one_intersection/output/"  # Path to your output directory

        # this will convert to geojson file by default
        vg.vissim_inpx(inpx_file, output_dir=output_dir)

        # if you want to specify the output file format, you can use the following code:
        isCsv = False  # Set to True if you want to save the output as csv files
        isGeojson = True  # Set to True if you want to save the output as geojson files
        isShp = False  # Set to True if you want to save the output as shp files
        vg.vissim_inpx(inpx_file, output_dir=output_dir, isCsv=isCsv, isGeojson=isGeojson, isShp=isShp)


Convert Single File: .fzp to .csv, .geojson and shp files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    if __name__ == "__main__":
        inpx_file = "datasets/one_intersection/Net.inpx"  # Path to your .inpx file
        fzp_file = "datasets/one_intersection/Net.fzp"  # Path to your .fzp file
        output_dir = "datasets/one_intersection/output/"  # Path to your output directory

        # this will convert to geojson file by default
        vg.vissim_fzp(fzp_file, output_dir=output_dir)

        # if you want to specify the output file format, you can use the following code:
        isCsv = False  # Set to True if you want to save the output as csv files
        isGeojson = True  # Set to True if you want to save the output as geojson files
        isShp = False  # Set to True if you want to save the output as shp files
        vg.vissim_fzp(fzp_file, output_dir=output_dir, isCsv=isCsv, isGeojson=isGeojson, isShp=isShp)


Convert Single File: .fhz to .csv file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import vissim2gmns as vg

    if __name__ == "__main__":
        fhz_file = "datasets/one_intersection/Net.fhz"  # Path to your .fhz file
        output_dir = "datasets/one_intersection/output/"  # Path to your output directory

        # this will convert to csv file by default
        vg.vissim_fhz(fhz_file, output_dir=output_dir)
