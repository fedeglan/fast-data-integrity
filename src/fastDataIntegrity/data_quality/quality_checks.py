import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.stats import chi2

def get_correct_type(data):
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, pd.Series):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
       return pd.DataFrame(data, index = range(len(list(data.keys()))))
    else:
        raise TypeError("Please provde a pandas.DataFrame, pandas.Series or dict.")

def check_duplicates(data, columns = None):
    # Transform data to pandas
    data = get_correct_type(data)
    if columns is not None:
        return data[columns][data[columns].duplicated()]
    else:
        return data[data.duplicated()]

def check_customer_identifier(data, id_cols):
    df = data.copy()
    for col in id_cols:
        df = df.loc[df[col].isna()]
    return df

def check_future_dates(data, date_cols, current_date):
    results = pd.DataFrame()
    if isinstance(current_date, str):
        current_date =  pd.to_datetime(current_date)
    for col in date_cols:
        data[col] = pd.to_datetime(data[col])
        results = pd.concat([results, data.loc[data[col] > current_date]])
    return results

def check_missing_values(data, col):
    return data.loc[data[col].isna()]

def check_volume_anomaly(data, col_name, thd):
    values = (round(100 * abs(data[col_name]) / abs(data[col_name]).sum(),
            2).sort_values(ascending=False))
    return data.loc[values > thd]

def check_numeric_anomaly(data, col_name, thd, plot = False):
    var = data[col_name].astype(float)
    norm_var = abs((var - var.mean()) / var.std())
    if plot:
        fig,ax = plt.subplots(2,1)
        var.plot.kde(ax=ax[0])
        ax[0].set_title(f"{col_name} distribution")
        plt.tight_layout()
        ax[1].boxplot(norm_var)
        ax[1].axhline(thd, color = "black", linestyle = "--")
        ax[1].set_title("Absolute Normalized boxplot")
        plt.show()
    return data.loc[(norm_var > thd)]

def check_type(data, col):
    type_check = data[col].apply(lambda x:type(x))
    count = type_check.value_counts().reset_index()
    count["%"] = 100 * count[col] / count[col].sum()
    count.columns = ["data_type", "count", "%"]
    return count

def check_data_manipulation(data, col, conf_level = 0.05):
    benford_distr = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
    # Frequency of first digit
    first_digit = data[col].apply(lambda x:int(re.sub("[0.]","",str(x))[0]))
    first_digit = first_digit.loc[first_digit > 0]
    count = first_digit.value_counts().reset_index().sort_values(by = "index")[col]
    obs_distr = count.values / np.sum(count)
    #X2 test
    chi_square_stat = np.sum(((obs_distr - benford_distr)**2) / benford_distr)
    critical_val = chi2.ppf(conf_level, df = 8)
    if chi_square_stat < critical_val:
        return "distributions are equal"
    else:
        return "distributions are not equal"