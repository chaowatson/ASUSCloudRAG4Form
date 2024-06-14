from token_size import getTokenizedSize
from form2json import jsonConverter
import pandas as pd
import math
import json
import argparse
import os

TOKEN_LIMIT = None
SRC_FILE_PATH = None
DES_FILE_PATH = None
FILE_TYPE = None
ARGS = None

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_file', help="path of source file to be sliced. Ex: ./src.xlsx")
    parser.add_argument('destination_file', help="path of output file. Ex: ./output.txt")
    parser.add_argument('-t','--token_limit', type=int, default=1000, help="token limit for slicing, default value is 1000")
    parser.add_argument('-s','--split', action='store_true', help="Split each excel sheet even if the content form is exactly the same.")
    args = parser.parse_args()
    global TOKEN_LIMIT
    global SRC_FILE_PATH
    global DES_FILE_PATH
    global FILE_TYPE
    global ARGS
    TOKEN_LIMIT = args.token_limit
    SRC_FILE_PATH = args.source_file
    DES_FILE_PATH = args.destination_file
    ARGS = args
    _, ext = os.path.splitext(SRC_FILE_PATH)
    FILE_TYPE = ext

def generateChunk(file_path: str, token_limit: int) -> str:
    data_string = ''
    new_line = '\n'
    token_counter = 0
    if FILE_TYPE in ['.xlsx', '.xls']:
        sheets = pd.ExcelFile(file_path).sheet_names
        last_headers = '' # For comparing headers in different sheets 

        for sheet in sheets:
            data_list = jsonConverter(file_path, FILE_TYPE, f'{{"sheet_name": "{sheet}"}}')
            headers = str(data_list[0].keys())

            # Add new line before next sheet
            if (headers != last_headers or ARGS.split) and last_headers:
                data_string += new_line
                token_counter = 0

            print("\nCalculating tokens\n")
            for row in data_list:
                tokenized_size = getTokenizedSize(str(row))
                token_counter += tokenized_size
                if token_counter > token_limit:
                    token_counter = 0
                    data_string += new_line
                data_string += str(row)
            last_headers = headers
    else:
        data_list = jsonConverter(file_path, FILE_TYPE)
        print("\nCalculating tokens\n")
        for row in data_list:
            tokenized_size = getTokenizedSize(str(row))
            token_counter += tokenized_size
            if token_counter > token_limit:
                token_counter = 0
                data_string += new_line
            data_string += str(row)

    return data_string

def main() -> None:
    result = generateChunk(SRC_FILE_PATH, TOKEN_LIMIT)
    print(result)
    with open(DES_FILE_PATH, "w") as text_file:
        text_file.write(result)

if __name__ == '__main__':
    parseArguments()
    main()
