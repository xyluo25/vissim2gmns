'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

from pathlib import Path
from loguru import logger

import pandas as pd
from pyufunc import str_strip


def remove_stripe_values(value):
    """Remove stripe values from a string."""
    if isinstance(value, str):
        return (
            value.replace("\\r", "")
            .replace("\\n", "")
            .replace("\n", "")
            .replace("b'", "")
            .replace("'", "")
        )
    return value


def vissim_fhz(path_vissim_fhz: str, output_dir: str = "") -> pd.DataFrame:
    """Convert vissim fhz file to pandas dataframe.

    Args:
        path_vissim_fhz (str): the path to the vissim fhz file.
        output_dir (str): the directory to save the output file. Defaults to "".

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_fhz = "./vissim_data/xl_002_001.fhz"
        >>> output_dir = "./output"
        >>> # get the fhz data as a pandas dataframe without saving to file.
        >>> df_fhz = vg.vissim_fhz(path_vissim_fhz)
        >>>
        >>> # get the fhz data as a pandas dataframe and save to csv file in the output_dir.
        >>> df_fhz = vg.vissim_fhz(path_vissim_fhz, output_dir=output_dir)

    Returns:
        pd.DataFrame: converted pandas dataframe.
    """

    with open(path_vissim_fhz, 'rb') as f:
        df_fhz = pd.DataFrame(f.readlines())

    # Retrieve the VISSIM running date from a specific row.
    fhz_date = str(df_fhz.iloc[5, :])
    start_fhz = next((i for i in range(len(df_fhz)) if str(df_fhz.iloc[i, :])[11:15] == "Time"), 0)
    # remove \\r and \\n, \n characters from staring values
    fhz_date = remove_stripe_values(fhz_date)

    vissim_fhz_data = df_fhz.iloc[start_fhz:]  # fhz file starts from row 8
    fhz_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fhz_data.iloc[:, 0]])
    fhz_data.columns = fhz_data.iloc[0]
    fhz_data = fhz_data.iloc[1:]
    fhz_data = fhz_data.reset_index(drop=True)
    for j in range(len(fhz_data.iloc[:, 0])):
        fhz_data.iloc[j, 0] = str(fhz_data.iloc[j, 0]).split("'")[1]

    # strip values for the whole table
    fhz_data = fhz_data.map(str_strip)

    # Convert the first (time offset) column to numeric safely.
    time_col = fhz_data.columns[0]
    fhz_data[time_col] = pd.to_numeric(fhz_data[time_col], errors="coerce")

    # add datetime
    fhz_data["datetime"] = pd.to_datetime(
        fhz_date.split("Name")[0].split("Date:")[1].lstrip()) + pd.to_timedelta(fhz_data[time_col], unit="s")

    # Save to csv file if output_dir is provided
    if output_dir:
        output_fhz_csv = pd.DataFrame(fhz_data)
        output_fhz_csv.to_csv(f"{output_dir}/{Path(path_vissim_fhz).stem}_fhz.csv", index=False)
        logger.info(f"Successfully save fhz file to csv: {output_dir}\n")

    return fhz_data


if __name__ == "__main__":
    path_vissim_fhz = r"C:\Users\xyluo25\anaconda3_workspace\001_GitHub\vissim2gmns\datasets\aveiro_port_net\Aveiro_Port_Train_Network_25_03_2026_001.fhz"
    output_dir = "./"
    df_fhz = vissim_fhz(path_vissim_fhz, output_dir=output_dir)