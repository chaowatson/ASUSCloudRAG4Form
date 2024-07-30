import pandas as pd
import os.path
import json
from ast import literal_eval

def readFile(file_path: str, arg: str = '') -> pd.DataFrame:
    """Read a file into a DataFrame based on its extension.
    
    Args:
        file_path (str): The path to the file.
        arg (str): Additional arguments for the file reader in string format.
    
    Returns:
        pd.DataFrame: The loaded data.
    """
    # Map for reading different file types
    READER_MAP = {
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
        '.ods': pd.read_excel,
        '.csv': pd.read_csv
    }
    # Extract the file extension
    _, ext = os.path.splitext(file_path)
    try:
        # Select the appropriate reader function based on file extension
        reader = READER_MAP[ext]
    except KeyError:
        # Raise an error if the file type is not supported
        raise ValueError(f'Unsupported filetype: {ext}')
    print(f'\nReading from file: {file_path} with argument: {arg}\n')
    # Read the file with additional arguments if provided
    return reader(file_path, **literal_eval(arg)) if arg else reader(file_path)

def AdjustValidHeaders(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all column headers in the DataFrame are valid.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        pd.DataFrame: The DataFrame with adjusted headers.
    """
    headers = list(df.columns.values)  # Get the current headers
    null_counter = 0  # Counter for invalid headers
    for i, header in enumerate(headers):
        header = str(header)
        if header.startswith("Unnamed") or header.startswith("nan"):
            # Rename invalid headers to "Unnamed" followed by the column index
            index = df.columns[i]
            df = df.rename(columns={index: "Unnamed" + str(i)})
            null_counter += 1
    if null_counter > len(headers) / 2:
        # If more than half of the headers are invalid, use the first row as headers
        new_header = df.iloc[0]
        df = df[1:]  # Remove the first row from the data
        df.columns = new_header  # Set the new headers
        return AdjustValidHeaders(df)  # Recursively adjust headers
    return df

def check_empty_column(df: pd.DataFrame) -> bool:
    """Check if there are any completely empty columns in the DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        bool: True if there are empty columns, False otherwise.
    """
    return df.isnull().all(axis=0).any()  # Check if any column is entirely null

def check_empty_row(df: pd.DataFrame) -> bool:
    """Check if there are any completely empty rows in the DataFrame.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        bool: True if there are empty rows, False otherwise.
    """
    return df.isnull().all(axis=1).any()  # Check if any row is entirely null

def split_column(df: pd.DataFrame) -> list:
    """Split the DataFrame into multiple DataFrames based on empty columns.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        list: A list of DataFrames split by empty columns.
    """
    is_empty_column = df.isnull().all(axis=0)  # Identify columns with empty values
    if not is_empty_column.any():
        return [df]  # Return the original DataFrame if no empty columns
    
    empty_col_positions = is_empty_column[is_empty_column].index  # Positions of empty columns
    empty_col_set = set(empty_col_positions)
    
    df_list = []  # List to hold split DataFrames
    current_block = []  # Current block of columns

    for col in df.columns:
        if col in empty_col_set:
            if current_block:
                # Append the current block if it exists
                df_list.append(df[current_block])
                current_block = []
        else:
            if current_block and df[current_block[-1]].isnull().all():
                # If the last column in the current block was empty, append the block
                df_list.append(df[current_block])
                current_block = []
            current_block.append(col)

    if current_block:
        # Append the final block if it exists
        df_list.append(df[current_block])

    return df_list

def split_row(df: pd.DataFrame) -> list:
    """Split the DataFrame into multiple DataFrames based on empty rows.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
    
    Returns:
        list: A list of DataFrames split by empty rows.
    """
    is_empty_row = df.isnull().all(axis=1)  # Identify rows with empty values
    if not is_empty_row.any():
        return [df]  # Return the original DataFrame if no empty rows

    empty_row_positions = is_empty_row[is_empty_row].index  # Positions of empty rows
    empty_row_set = set(empty_row_positions)

    df_list = []  # List to hold split DataFrames
    current_block = []  # Current block of rows

    for idx, row in df.iterrows():
        if idx in empty_row_set:
            if current_block:
                block_df = df.loc[current_block]
                if 0 not in current_block:
                    new_header = block_df.iloc[0]  # Use the first row as headers if row 0 is not in the block
                    block_df = block_df[1:]  # Remove the first row
                    block_df.columns = new_header
                else:
                    block_df.columns = df.columns  # Keep original headers if row 0 is in the block
                df_list.append(block_df)
                current_block = []
        else:
            if current_block and df.loc[current_block[-1]].isnull().all():
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

    if current_block:
        # Append the final block if it exists
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
    """Recursively split the DataFrame list based on empty columns and rows.
    
    Args:
        df_list (list): The list of DataFrames.
    
    Returns:
        list: A list of further split DataFrames.
    """
    splited_df_list = []  # List to hold split DataFrames
    for df in df_list:
        if check_empty_column(df):
            splited_df_list.extend(split_column(df))  # Split by columns if there are empty columns
        elif check_empty_row(df):
            splited_df_list.extend(split_row(df))  # Split by rows if there are empty rows
        else:
            splited_df_list.append(df)  # No empty columns or rows, keep the DataFrame as is

    # Recursively process the newly split DataFrames
    return splited_df_list if len(splited_df_list) == len(df_list) else split_form(splited_df_list)

def jsonConverter(file_path: str, file_type: str, arg: str='', rotate: bool=False) -> list:
    """
    Convert data from a specified file to a list of JSON objects.

    Args:
        file_path (str): Path to the input file.
        file_type (str): Type of the file (e.g., '.xlsx', '.csv').
        arg (str, optional): Additional arguments for reading the file, as a string.
        rotate (bool, optional): If True, rotates the DataFrame to use column 1 as headers.

    Returns:
        list: List of JSON objects representing the data from the file.
    """
    # Read the file into a DataFrame
    df = readFile(file_path, arg)
    
    # Split DataFrame into separate DataFrames based on empty columns/rows
    df_list = split_form([df])
    
    json_dict_list = []
    
    for df in df_list:
        # Rotate DataFrame if specified
        if rotate:
            df = df.transpose()
            df = df.reset_index()
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header
        
        # Add sheet name to DataFrame if the file is an Excel file
        if file_type in ['.xlsx', '.xls']:
            df['sheet'] = json.loads(arg)['sheet_name']
        
        # Drop columns and rows that are completely empty
        df = df.dropna(axis='columns', how='all')
        df = df.dropna(axis='rows', how='all')
        
        # Adjust headers to ensure they are valid
        df = AdjustValidHeaders(df)

        # Convert all object and datetime columns to strings
        df[df.select_dtypes(['object', 'datetime', 'datetime64']).columns] = df.select_dtypes(['object', 'datetime', 'datetime64']).astype(str)
        
        # Convert DataFrame to JSON
        json_data = df.to_json(orient='records', indent=4)
        
        # Append JSON data to list
        json_dict_list += json.loads(json_data)
        
        # Remove None values from JSON data
        for data in json_dict_list:
            new_data = {k: v for k, v in data.items() if v is not None}
            data.clear()
            data.update(new_data)

    return json_dict_list
