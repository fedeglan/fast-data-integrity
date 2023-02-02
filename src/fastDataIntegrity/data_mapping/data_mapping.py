import pandas as pd

def get_correct_type(data):
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, pd.Series):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
       return pd.DataFrame(data, index = range(len(list(data.keys()))))
    else:
        raise TypeError("Please provde a pandas.DataFrame, pandas.Series or dict.")


def integrity_check(source, output, id_col, 
                    how = "source", drop_duplicates = True,
                    dropna = True):
    """Performs integrity between two tabular datasets.

    Args:
        source (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        output (object): dataset in form of pd.DataFrame, pd.Series or python Dict.
        id_col (_type_): column to perform matching. Can be a list of columns also.
        how (str, optional): "source" or "output". Defaults to "source".
        drop_duplicates (bool, optional): boolean to indicate if duplicates must be drop in both datasets. Defaults to True.
        dropna (bool, optional): boolean to indicate if NaNs must be drop in both datasets. Defaults to True.

    Raises:
        Exception: is raised when id_col is not a str or a list.

    Returns:
        dict: dictionary containing matches, source mismatches and output mismatches.
    """
    # Check type of df1 and df2
    df1 = get_correct_type(df1)
    df2 = get_correct_type(df2)

    # Check var type of id_col
    if isinstance(id_col, list):
        source["ID"] = ""
        output["ID"] = ""
        for col in id_col:
            source["ID"] += source[col].astype(str)
            output["ID"] += output[col].astype(str)
    elif isinstance(id_col, str):
        source["ID"] = source[id_col].values
        output["ID"] = output[id_col].values
    else:
        raise Exception("Please provide a str or a list as id_col.")

    # Some cleaning
    source = source.drop(id_col, axis=1)
    output = output.drop(id_col, axis=1)
    if dropna:
        source = source.dropna()
        output = output.dropna()
    
    if drop_duplicates:
        source = source.drop_duplicates()
        output = output.drop_duplicates()

    # Merge datasets
    matches = pd.merge(source, output, on = "ID", how = "left").dropna().drop_duplicates()
    source_mismatches = source.loc[~source["ID"].isin(matches["ID"].to_list())]
    output_mismatches = output.loc[~output["ID"].isin(matches["ID"].to_list())]

    # Results
    print(f"Matches = {len(matches)}", 
          f"\nMismatches in source = {len(source_mismatches)}",
          f"\nMismatches in output = {len(output_mismatches)}")

    return {"matches":matches, 
            "source_mismatches":source_mismatches,
            "output_mismatches":output_mismatches}