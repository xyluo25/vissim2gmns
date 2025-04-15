'''
##############################################################
# Created Date: Tuesday, April 15th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    # if have requirements.txt file inside the folder
    with open("requirements.txt", "r", encoding="utf-8") as f:
        modules_needed = [i.strip() for i in fh.readlines()]
except Exception:
    modules_needed = []

setuptools.setup(
    name="vissim2gmns",
    version="1.5.5",
    author="Xiangyong Luo",
    author_email="luoxiangyong01@gmail.com",

    description="vissim2gmns converts VISSIM files (.inpx, .fzp, .fhz) into GMNS format with WGS 1984 coordinates for easy GIS visualization and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    python_requires='>=3.10',

    install_requires=modules_needed,
    packages=setuptools.find_packages(),
    include_package_data=True,

    package_data={'': ['*.txt', '*.xls', '*.xlsx', '*.csv', '*.png',
                       "*.inpx", "*.fhz", "*.fzp", "*.db", "*.geojson",
                       "*.err", "*.knr", "*.lsa", "*.mer", "*.ovw", "*.rsr", "*.inp0", "*.layx", "*.sig"],
                  "test_data": ['*.txt', '*.png', "*.inpx", "*.fhz", "*.fzp"]},
    # data_files=[("vissim_data", ["vissim_data/*"])]
)
