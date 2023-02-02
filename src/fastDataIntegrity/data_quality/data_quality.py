import pandas as pd
import numpy as np
import warnings
from itertools import compress
import matplotlib.pyplot as plt

def get_correct_type(data):
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, pd.Series):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
       return pd.DataFrame(data, index = range(len(list(data.keys()))))
    else:
        raise TypeError("Please provde a pandas.DataFrame, pandas.Series or dict.")

def auto_data_quality(df, path_to_save = None):
    """Performs a preliminary data quality assessment.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        path_to_save (str, optional): path to save the assessment results. Defaults to None.

    Returns:
        pd.DataFrame: if a path is not indicated, the function returns the assessment results in table form. Otherwise, an excel file is generated.
    """
    var_types = get_var_types(df)
    unique_counts = compute_unique_count(df)
    duplicate_counts = compute_duplicates_count(df)
    na_counts = compute_na_count(df)
    result = var_types.join([unique_counts, duplicate_counts, na_counts])
    if path_to_save is not None:
        result.to_excel(path_to_save)
        print(f"Results save at {path_to_save}")
    else:
        return result

def get_var_types(df):
    """Checks the data type for each column in the dataset provided.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pd.DataFrame: table containing the data type of each column (as detected by pandas), the data types found and the data types that the column can be converted to.
    """
    data = get_correct_type(df)
    table = pd.DataFrame(data.dtypes, columns = ['dtype'])
    table['types found'] = ""
    table['can be converted to'] = ""
    data_types = ["str", "bool", "int", "float", "datetime.datetime"]
    for col in data.columns:
        df = data[col].dropna()
        # Count data types in column
        if len(df) > 1:
            try:
                count = df.apply(lambda x:type(x)).reset_index(name = 'type').drop('index', axis=1)
                count = count.astype(str).groupby('type').size().reset_index(name = 'count')
                count['%'] = round(100 * count['count'] / len(df),2)
                message = ""
                for i in range(len(count)):
                    message += f"{count.iloc[i]['type']}: {count.iloc[i]['count']} ({count.iloc[i]['%']}), "
                    table.loc[col, 'types found'] = message
            except Exception as err:
                warnings.warn(f"Encountered an error in {col} iteration. Error {err}")
                
            # Calculate data types that can be converted to
            try:
                index = [is_string(df), is_bool(df), is_int(df),
                         is_float(df),  is_datetime(df)]
                types = list(compress(data_types, index))
                if types != []:
                    table.loc[col, 'can be converted to'] = ",".join(types)
            except Exception as err:
                warnings.warn(f"Encountered an error in {col} iteration. Error {err}")
    return table

def compute_unique_count(df):
    """Computes the unique count of elements in each column of the dataset provided.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pd.DataFrame: table containing the unique count, as number and percentage, for each column in the dataset.
    """
    data = get_correct_type(df)
    table = pd.DataFrame(data.nunique(), columns = ['nunique'])
    table["nunique (% of total)"] = round(100 * table['nunique'] / len(data), 4)
    return table

def compute_duplicates_count(df):
    """Computes the duplicates of each column in the dataset provided.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pd.DataFrame: table containing the duplicates count, as number and percentage, for each column in the dataset.
    """
    data = get_correct_type(df)
    duplicates_count = (len(df) - df.isna().sum()) - df.nunique()
    table = pd.DataFrame(duplicates_count, columns = ['nduplicates'])
    table['nduplicates (% of total)'] = round(100 * table['nduplicates'] / len(data), 4)
    return table

def compute_na_count(df):
    """Computes the NaNs count for each column of the dataset provided.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pd.DataFrame: table containing the NaNs count, as number and percentage, and other types of NaNs in str form.
    """
    data = get_correct_type(df)
    # np.nan or None
    table = pd.DataFrame(data.isna().sum(), columns = ['nNANs'])
    table["nNANs (% of total)"] = round(100 * table['nNANs'] / len(data), 4)
    # Str NaNs
    common_na_str = ["NaN", "N/A", "\\NA", "\\N", "/N", "//N", "None", "nan", "NA"]        
    temp = pd.DataFrame(index = table.index)
    for na in common_na_str:
        count = (data == na).sum()
        temp[na] = count

    def internal_func(x):
        filter = x > 0
        keys = list(compress(common_na_str, filter))
        values = list(x[filter])
        return dict(zip(keys, values))

    table['other NaN types'] = temp.astype(int).apply(lambda row:internal_func(row), axis=1)
    return table

def get_duplicates(df, cols = None):
    """Return duplicated rows of a dataset.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        cols (list, optional): list of columns. Defaults to None.

    Returns:
         pd.DataFrame: table containing duplicated values of dataframe.
    """
    if cols is not None:
        return df[df[cols].duplicated()]
    else:
        return df[df.duplicated()]

def get_nans(df, cols = None):
    """Returns NaN rows of a dataset.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        cols (list, optional): list of columns. Defaults to None.

    Returns:
        pd.DataFrame: table containing NaN values of dataframe.
    """
    if cols is None:
        result = df.loc[df.isna()]
    else:
        result = df.loc[df[cols].isna()]
    common_na_str = ["NaN", "N/A", "\\NA", "\\N", "/N", "//N", "None", "nan", "NA"]        
    for na in common_na_str:
        if cols is None:
            result = pd.concat([result, df.loc[df == na]])
        else:  
            result = pd.concat([result, df.loc[df[cols] == na]])
    return result

def is_string(df):
    """Outputs true or false if a pd.Series is a string.

    Args:
        df (pd.Series): single-column dataset in pandas series form.

    Returns:
        bool: True if the series elements are strings, False otherwise.
    """
    try:
        # Check if there are characters
        condition = df.apply(lambda x:x.isalnum())
        is_all, is_any = all(condition), any(condition)
        if is_all:
            return True
        elif (is_any) & (np.mean(condition) > 0.01):
            return True
        else:
            return False
    except:
        return False

def is_bool(df):
    """Outputs true or false if a pd.Series is bool.

    Args:
        df (pd.Series): single-column dataset in pandas series form.

    Returns:
        bool: True if the series elements are booleans, False otherwise.
    """
    unique_vals = list(df.unique())
    if (len(unique_vals) == 2):
        try:
            df.astype(int)
            return True
        except:
            return False
    else:
        return False

def is_int(df, eps = 1e-4):
    """Outputs true or false if a pd.Series is integer.

    Args:
        df (pd.Series): single-column dataset in pandas series form.

    Returns:
        bool: True if the series elements are integers, False otherwise.
    """
    # Float transformation
    try:
        float_transform = df.astype(float)
    except:
        try:
            int_transform = df.astype(int)
            return True
        except:
            return False
    # Int transformation
    try:
        int_transform = df.astype(int)
    except:
        return False  
    # Comparison
    if np.sum(abs(float_transform - int_transform)) < eps:
        return True
    else:
        return False

def is_float(df, eps = 1e-04):
    """Outputs true or false if a pd.Series is float.

    Args:
        df (pd.Series): single-column dataset in pandas series form.

    Returns:
        bool: True if the series elements are floats, False otherwise.
    """
    try:
        # Compare float to int
        float_transform = df.astype(float)
        int_transform = df.astype(int)
        if np.sum(abs(float_transform - int_transform)) > eps:
            return True
        else:
            return False
    except:
        return False

def is_datetime(df, eps = 60):
    """Outputs true or false if a pd.Series is datetime.

    Args:
        df (pd.Series): single-column dataset in pandas series form.

    Returns:
        bool: True if the series elements are datetime objects, False otherwise.
    """
    try:
        # Check if dates std is above threshold
        dates = pd.to_datetime(df)
        stdev = np.std(dates).total_seconds()
        if stdev > eps:
            return True
        else:
            return False
    except:
        return False

def to_categorical(df):
    """Converts str columns to categories.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pandas DataFrame: dataset transformed.
    """
    data = get_correct_type(df)
    dtypes = pd.DataFrame(data.dtypes)
    cols = list(dtypes[dtypes == 'O'].dropna().index)
    for col in cols:
        data[col] = data[col].astype('category').cat.codes
    return data

def correlation_pairs(df):
    """Computes correlation between variables

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.

    Returns:
        pandas DataFrame: correlation pairs as dataframe.
    """
    data = get_correct_type(df)
    data = to_categorical(data)
    corr = data.corr().unstack()
    corr = corr.dropna().drop_duplicates()
    corr = pd.DataFrame(corr).reset_index()
    corr['id'] = corr['level_0'] + corr['level_1']
    corr = corr.drop_duplicates('id')
    corr = corr.loc[corr[0] != 1].sort_values(by = 0, ascending = False)
    corr = corr.reset_index().drop(['id', 'index'], axis=1)
    corr.columns = ['var1', 'var2', 'corr']
    return corr

def plot_distributions(df, grid_size, fig_size):
    """Outputs a grid plot with the distributions of df's columns.

    Args:
        df (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        grid_size (tuple): size of plot grid.
        fig_size (tuple): size of each distribution plot.
    """
    data = get_correct_type(df)
    fig, ax = plt.subplots(grid_size[0], grid_size[1], figsize = fig_size)
    if (grid_size[0] == 1) or (grid_size[1] == 1):
        ax = ax.reshape(-1,1) 
    plt.tight_layout()

    i,j = 0,0
    i_max, j_max = grid_size[0], grid_size[1]
    for col in df.columns:
        try:
            plt.tight_layout()
            ax[i,j].set_title(col)
            df = data[col].dropna()
            if is_float(df):
                data[col].astype(float).plot(kind = 'hist', bins = 100, ax = ax[i,j])
            else:
                count = df.value_counts().sort_values(ascending = False)
            if len(count) > 20:
                others_df = pd.Series({'Others':count.iloc[20:].sum()})
                count = pd.concat([count.iloc[:20], others_df])
            count.plot(kind = 'bar', ax = ax[i,j])
        except Exception as err:
            warnings.warn(f"Couldn't plot {col}. Please check grid_size is adequate. Error:{err}")
        
        if i < i_max:
            i += 1
        elif i >= i_max:
            j += 1
            i = 0
        elif (i >= i_max) & (j >= j_max):
            break