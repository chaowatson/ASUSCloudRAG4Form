#!/usr/bin/env python

# Import necessary libraries and modules
from token_size import getTokenizedSize  # Function to get the size of a tokenized string
from form2json import jsonConverter  # Function to convert forms to JSON
import pandas as pd  # Library for data manipulation
import math  # Library for mathematical operations
import json  # Library for handling JSON data
import argparse  # Library for command-line argument parsing
import os  # Library for interacting with the operating system

# Define global variables with default values
TOKEN_LIMIT = 1000  # Default token limit for slicing
SRC_FILE_PATH = None  # Source file path, to be set from command-line arguments
DES_FILE_PATH = None  # Destination file path, to be set from command-line arguments
FILE_TYPE = None  # File type extension, to be determined from the source file path
arg_split = False  # Flag to indicate whether to split sheets with identical forms
arg_rotate = False  # Flag to indicate whether to rotate the form (use column 1 as headers)

def parseArguments():
    """Parse and handle command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', help="Path of source file to be sliced. Ex: ./src.xlsx")
    parser.add_argument('destination_file', help="Path of output file. Ex: ./output.txt")
    parser.add_argument('-t', '--token_limit', type=int, default=1000, help="Token limit for slicing, default value is 1000")
    parser.add_argument('-s', '--split', action='store_true', help="Split each Excel sheet even if the content form is exactly the same.")
    parser.add_argument('-r', '--rotate', action='store_true', help="Rotate the form to make column 1 as headers.")
    args = parser.parse_args()
    
    # Set global variables based on parsed arguments
    global TOKEN_LIMIT
    global SRC_FILE_PATH
    global DES_FILE_PATH
    global FILE_TYPE
    global arg_split 
    global arg_rotate
    
    arg_split = args.split
    arg_rotate = args.rotate
    TOKEN_LIMIT = args.token_limit
    SRC_FILE_PATH = args.source_file
    DES_FILE_PATH = args.destination_file
    _, ext = os.path.splitext(SRC_FILE_PATH)
    FILE_TYPE = ext

def process_data_list(data_list: list, max_tokens: int) -> list:
    """Process the data list to generate chunks based on the token limit.
    
    Args:
        data_list (list): List of data rows.
        max_tokens (int): Maximum tokens per chunk.
    
    Returns:
        list: List of data chunks.
    """
    data_string = ''
    chunk_list = []
    token_counter = 0
    
    for row in data_list:
        tokenized_size = getTokenizedSize(str(row))
        token_counter += tokenized_size
        if token_counter > max_tokens:
            token_counter = 0
            chunk_list.append(data_string)
            data_string = ''
        data_string += str(row)
    
    if data_string:
        chunk_list.append(data_string)
    
    return chunk_list

def chunk(file_path: str, file_extension: str = FILE_TYPE, max_tokens: int = TOKEN_LIMIT, sheet_split: bool = arg_split, rotate: bool = arg_rotate, model: str = "gpt-4") -> list:
    """Split the data from the given file into chunks based on token limits.
    
    Args:
        file_path (str): Path to the input file.
        file_extension (str): Extension of the file.
        max_tokens (int): Maximum tokens per chunk.
        sheet_split (bool): Flag to indicate whether to split sheets.
        rotate (bool): Flag to indicate whether to rotate the form.
        model (str): Model name for processing.
    
    Returns:
        list: List of data chunks.
    """
    chunk_list = []

    # Handle Excel and similar files
    if file_extension in ['.xlsx', '.xls', '.ods']:
        sheets = pd.ExcelFile(file_path).sheet_names
        last_headers = ''  # For comparing headers in different sheets 

        for sheet in sheets:
            data_list = jsonConverter(file_path, file_extension, f'{{"sheet_name": "{sheet}"}}', rotate)
            if not data_list:
                continue

            headers = str(data_list[0].keys())

            # Generate output string in chunks
            print("\nCalculating tokens\n")
            chunk_list.extend(process_data_list(data_list, max_tokens))
            last_headers = headers

    # Handle other file types
    else:
        data_list = jsonConverter(file_path, FILE_TYPE)

        # Generate output string in chunks
        print("\nCalculating tokens\n")
        chunk_list.extend(process_data_list(data_list, max_tokens))

    return chunk_list

def main() -> None:
    """Main function to execute the chunking process and save the output."""
    result = chunk(SRC_FILE_PATH, FILE_TYPE, TOKEN_LIMIT, arg_split, arg_rotate)
    print(result)
    with open(DES_FILE_PATH, "w") as text_file:
        text_file.write(str(result))

# Execute the script by parsing arguments and running the main function
if __name__ == '__main__':
    parseArguments()
    main()
