# Data Processing and Tokenization

## Overview

This project provides a set of tools for processing and tokenizing data from various file formats. It includes functionalities for:

- Reading and converting data from Excel, CSV, and other formats into JSON.
- Chunking data based on a token limit to fit specific constraints.
- Splitting DataFrames based on empty columns or rows.
- Adjusting headers and ensuring data consistency.

## Files

### 1. `form2chunk.py`

This script handles the following:

- **Command-Line Arguments**: Parses arguments to determine input/output file paths, token limit, and options for splitting and rotating forms.
- **Data Processing**: Reads data from the source file, processes it into chunks based on token limits, and writes the output to the destination file.
- **Functions**:
  - `parseArguments()`: Parses command-line arguments and sets global variables.
  - `process_data_list(data_list, max_tokens)`: Processes data into chunks based on token limits.
  - `chunk(file_path, file_extension, max_tokens, sheet_split, rotate, model)`: Main function for chunking data.
  - `main()`: Executes the chunking process and saves the output.

### 2. `form2json.py`

This module provides functionality for converting data to JSON format and manipulating DataFrames:

- **Functions**:
  - `readFile(file_path, arg)`: Reads a file into a DataFrame based on its extension.
  - `AdjustValidHeaders(df)`: Adjusts DataFrame headers to ensure they are valid.
  - `check_empty_column(df)`: Checks for empty columns.
  - `check_empty_row(df)`: Checks for empty rows.
  - `split_column(df)`: Splits the DataFrame into multiple DataFrames based on empty columns.
  - `split_row(df)`: Splits the DataFrame into multiple DataFrames based on empty rows.
  - `split_form(df_list)`: Recursively splits DataFrames based on empty columns and rows.
  - `jsonConverter(file_path, file_type, arg, rotate)`: Converts data from a file to a list of JSON objects, with options for rotating and adjusting headers.

### 3. `token_size.py`

This module contains a function for calculating the tokenized size of a string:

- **Functions**:
  - `getTokenizedSize(string)`: Returns the number of tokens in the given string using the `tiktoken` library.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Install required Python libraries:
    ```bash
    pip install pandas tiktoken
    ```

## Usage

### Chunk Data

To process and chunk data from an Excel or CSV file:

```bash
python form2chunk.py <source_file> <destination_file> [--token_limit <limit>] [--split] [--rotate]
```

- `<source_file>`: Path to the source file (e.g., `./src.xlsx`).
- `<destination_file>`: Path to the output file (e.g., `./output.txt`).
- `--token_limit`: Token limit for chunking (default is 1000).
- `--split`: Flag to split sheets with identical forms.
- `--rotate`: Flag to rotate the form and use column 1 as headers.

## Author
This project is authored by Watson Chao.
