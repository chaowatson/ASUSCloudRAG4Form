import pandas as pd
import os.path
import json
from ast import literal_eval

def readFile(file_path: str, arg: str='') -> pd.DataFrame:
    # Map for reading different file type
    READER_MAP = {
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
        '.ods': pd.read_excel,
        '.csv': pd.read_csv
    }
    #get file type
    _, ext = os.path.splitext(file_path)
    try:
        reader = READER_MAP[ext]
    except KeyError:
        raise ValueError(f'Unsupported filetype: {ext}')
    print(f'\nReading from file: {file_path} with argumet: {arg}\n')
    if arg:
        return reader(file_path, **literal_eval(arg))
    else: 
        return reader(file_path)

def AdjustValidHeaders(df: pd.DataFrame) -> pd.DataFrame:
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

def check_empty_column(df: pd.DataFrame) -> bool:
    return df.isnull().all(axis=0).any()

def check_empty_row(df: pd.DataFrame) -> bool:
    return df.isnull().all(axis=1).any()

def split_column(df: pd.DataFrame) -> list:
    # Identify columns with empty values
    is_empty_column = df.isnull().all(axis=0)
    
    if not is_empty_column.any():
        return [df]  # No empty columns, return the original DataFrame
    
    # Find positions of empty columns
    empty_col_positions = is_empty_column[is_empty_column].index
    empty_col_set = set(empty_col_positions)
    
    # Split columns into non-empty and empty groups
    df_list = []
    current_block = []
    
    for col in df.columns:
        if col in empty_col_set:
            if current_block:
                # Append DataFrame for the current block of non-empty columns
                df_list.append(df[current_block])
                current_block = []
        else:
            if current_block and df[current_block[-1]].isnull().all():
                # If the last column in the current block was empty, append it first
                df_list.append(df[current_block])
                current_block = []
            current_block.append(col)
    
    # Append the final block if it exists
    if current_block:
        df_list.append(df[current_block])
    
    return df_list

def split_row(df: pd.DataFrame) -> list:
    # Identify rows with all empty values
    is_empty_row = df.isnull().all(axis=1)

    if not is_empty_row.any():
        return [df]  # No empty rows, return the original DataFrame

    # Find positions of empty rows
    empty_row_positions = is_empty_row[is_empty_row].index
    empty_row_set = set(empty_row_positions)

    # Split rows into non-empty and empty groups
    df_list = []
    current_block = []

    for idx, row in df.iterrows():
        if idx in empty_row_set:
            if current_block:
                # Extract the current block DataFrame
                block_df = df.loc[current_block]
                if 0 not in current_block:
                    # Use the first row of the block as headers if row 0 is not in the block
                    new_header = block_df.iloc[0]
                    block_df = block_df[1:]  # Drop the first row
                    block_df.columns = new_header
                else:
                    # Keep the original headers if row 0 is in the block
                    block_df.columns = df.columns
                df_list.append(block_df)
                current_block = []
        else:
            if current_block and df.loc[current_block[-1]].isnull().all():
                # If the last row in the current block was empty, append it first
                block_df = df.loc[current_block]
                if 0 not in current_block:
                    new_header = block_df.iloc[0]
                    block_df = block_df[1:]
                    block_df.columns = new_header
                else:
                    block_df.columns = df.columns
                df_list.append(block_df)
                current_block = []
            current_block.append(idx)
    
    # Append the final block if it exists
    if current_block:
        block_df = df.loc[current_block]
        if 0 not in current_block:
            new_header = block_df.iloc[0]
            block_df = block_df[1:]
            block_df.columns = new_header
        else:
            block_df.columns = df.columns
        df_list.append(block_df)
    
    return df_list


def split_form(df_list: list) -> list:
    splited_df_list = []
    for df in df_list:
        if check_empty_column(df):
            splited_df_list.extend(split_column(df))  # Use extend to merge lists
        elif check_empty_row(df):
            splited_df_list.extend(split_row(df))  # Use extend to merge lists
        else:
            splited_df_list.append(df)

    # Recursively process the newly split dataframes
    return splited_df_list if len(splited_df_list) == len(df_list) else split_form(splited_df_list)

def jsonConverter(file_path: str, file_type: str, arg: str='', rotate: bool=False) -> list:
    #if file_type == "csv":
        #arg += " on_bad_lines='skip'"
    df = readFile(file_path, arg)
    df_list = split_form([df])
    json_dict_list = []
    for df in df_list:
        if rotate :
            df = df.transpose()
            df = df.reset_index()
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header
        if file_type in ['.xlsx', '.xls']:
            df['sheet'] = json.loads(arg)['sheet_name']
        df = df.dropna(axis='columns', how='all')
        df = df.dropna(axis='rows', how='all')
        df = AdjustValidHeaders(df)

        df[df.select_dtypes(['object', 'datetime', 'datetime64']).columns] = df.select_dtypes(['object', 'datetime', 'datetime64']).astype(str)
        # Convert DataFrame to JSON
        json_data = df.to_json(orient='records', indent=4)

        # Convert JSON to list
        json_dict_list += json.loads(json_data)

    return json_dict_list


