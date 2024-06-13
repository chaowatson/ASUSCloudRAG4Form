import pandas as pd
import os.path
import json
from ast import literal_eval

def readFile(file_path: str, arg: str='') -> pd.DataFrame:
    # Map for reading different file type
    READER_MAP = {
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
    }
    #get file type
    _, ext = os.path.splitext(file_path)
    try:
        reader = READER_MAP[ext]
    except KeyError:
        raise ValueError(f'Unsupported filetype: {ext}')
    print(f'\nReading from file: {file_path} with argumet: {arg}\n')
    return reader(file_path, **literal_eval(arg))

def AdjustValidHeaders(df: pd.DataFrame)-> pd.DataFrame:
    headers = list(df.columns.values)
    null_counter = 0
    for i,header in enumerate(headers):
        header = str(header)
        if header.startswith("Unnamed") or header.startswith("nan"):
            index = df.columns[i]
            df = df.rename(columns={index:"Unnamed"+ str(i)})
            null_counter += 1
    if null_counter > len(headers)/2:
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header
        return AdjustValidHeaders(df)
    else:
        return df

def mergeDF(df: dict) -> pd.DataFrame:
    # merge sheets based on header of first sheet
    for key, value in df.items() :
        value['sheet'] = key
        index = list(value.columns.values)
        break
    for key, value in list(df.items()) :
        value = value.dropna(axis='columns', how='all')
        value = AdjustValidHeaders(value)
        value['sheet'] = key
        df[key]['sheet'] = key
        if list(value.columns.values) != index:
            del df[key]
    df = pd.concat(df.values(), axis=0, ignore_index=True)
    return df

def jsonConverter(file_path: str, arg: str='') -> list:
    df = readFile(file_path, arg)
    index = []
    if type(df) == dict:
        print("\nMerging dataframes\n")
        df = mergeDF(df)
    else:
        df = df.dropna(axis='columns', how='all')
        df = AdjustValidHeaders(df)
    df = df.assign( **df.select_dtypes(['object', 'datetime','datetime64']).astype(str))
    # Convert DataFrame to JSON
    json_data = df.to_json(orient='records', indent=4)

    # Convert JSON to list
    json_dict_list = json.loads(json_data)

    return json_dict_list

