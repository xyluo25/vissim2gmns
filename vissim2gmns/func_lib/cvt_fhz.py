'''
##############################################################
# Created Date: Monday, April 14th 2025
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
'''

import pandas as pd
from pyufunc import func_running_time, str_strip


@func_running_time
def vissim_fhz(path_vissim_fhz: str) -> pd.DataFrame:
    """Convert vissim fhz file to pandas dataframe.

    Args:
        path_vissim_fhz (str): the path to the vissim fhz file.

    Example:
        >>> import vissim2gmns as vg
        >>> path_vissim_fhz = "./vissim_data/xl_002_001.fhz"
        >>> df_fhz = vg.vissim_fhz(path_vissim_fhz)
        >>> df_fhz.to_csv("vissim_fhz.csv", index=False)

    Returns:
        pd.DataFrame: converted pandas dataframe.
    """

    with open(path_vissim_fhz, 'rb') as f:
        df_fhz = pd.DataFrame(f.readlines())

    fhz_date = str(df_fhz.iloc[5, :])
    start_fhz = next((i for i in range(len(df_fhz)) if str(df_fhz.iloc[i, :])[11:15] == "Time"), 0)

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

    # remove \\r and \\n, \n characters from staring values
    fhz_date = fhz_date.replace("\\r", "").replace("\\n", "").replace("\n", "")

    fhz_data["datetime"] = pd.to_datetime(fhz_date.split("Name")[0].split(
        "Date:")[1].lstrip()) + pd.to_timedelta(fhz_data[time_col], unit="s")

    return fhz_data


if __name__ == "__main__":
    path_vissim_fhz = r"C:\Users\xh8\ORNL_Work\github_workspace\vissim2gmns\datasets\aveiro_port_net\Aveiro_Port_Train_Network_25_03_2026_001.fhz"
    df_fhz = vissim_fhz(path_vissim_fhz)
