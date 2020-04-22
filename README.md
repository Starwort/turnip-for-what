# Turnip for What

## Overview

Turnip for What? is a pair of tools used for determining your island's random turnip seed, and then using it to determine your future turnip prices.

## Usage

### Seed Dataminer (C version)

Ensure you use a version compatible with your system (or compile the code yourself)

#### Linux/MacOS

```bash
./dataminer BUY_PRICE [SELL_PRICES]...
```

#### Windows

```cmd
dataminer BUY_PRICE [SELL_PRICES]...
```

#### Notes on parameters

`BUY_PRICE` must be a number (it will always be between 90 and 110) - it is the price at which you bought the turnips on Sunday  
`SELL_PRICES` is the list of sell prices throughout the week. -1 can be used to mark a day as unknown. Only the first 12 values will be used. The value order is:

- Monday Morning
- Monday Afternoon
- Tuesday Morning
- Tuesday Afternoon
- Wednesday Morning
- Wednesday Afternoon
- Thursday Morning
- Thursday Afternoon
- Friday Morning
- Friday Afternoon
- Saturday Morning
- Saturday Afternoon

You do not have to provide every value; `./dataminer 101 -1 101`, for example, is a valid usage of the program.

#### Files and Compilation System Architecture

| File Name | 32/64-bit | Compilation System Information | Compiler Version | LibC version | OS Name |
| --------- | ----------------------------------------------- | --- | --- | --- | --- |
| dataminer-2020-04-17-0 | 64-bit | Linux 4.15.0-96-generic x86_64 | gcc (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0 | 2.27-3ubuntu | Ubuntu 18.04.4 LTS |
| dataminer-2020-04-21-0 | 64-bit | Linux 3.10.0-693.17.1.el7.x86_64 x86_64 | gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-36) | glibc-2.17-260.el7_6.5.x86_64 | CentOS Linux 7 (Core) |
| dataminer-2020-04-21-0.exe | 64-bit | Not provided | x86_64-w64-mingw32-gcc version 8.3.0 | Not provided | Fedora 30
| dataminer-2020-04-21-1.exe | 32-bit | Not provided | i686-w64-mingw32-gcc version 8.3.0 | Not provided | Fedora 30

If you would like to submit a compiled version of the dataminer, submit a pull request with the new dataminer compiled file as well as a new entry in this table. The filename should be `dataminer-YYYY-MM-DD-nEXT` where YYYY is the year of compilation, MM is the month of compilation, DD is the day of compilation, and n is the lowest non-negative integer for the day. EXT should be the extension for the system - nothing on non-Windows systems, and `.exe` on Windows systems.

Compilation System Information can be obtained on Linux systems via `uname -srm`, and OS name via the PRETTY_NAME property in /etc/os-release

### Seed Dataminer and Turnip Predictor (Python version)

Note: It is **not** recommended to use this for mining your seed from scratch. It is very slow compared to the C version.

#### Prerequisites

Python 3  
PyPI package `click` (install via pip)

#### Command usage

If on Windows, replace `python3` with `py`. If on Linux, `python3` may be omitted.

```bash
# Brute-force from scratch. You should be using the C version for this
python3 dataminer.py brute-force BUY_PRICE [SELL_PRICES]...
# Brute-force based on previous week's brute-force results
python3 dataminer.py brute-force --input-file results_file BUY_PRICE [SELL_PRICES]...
python3 dataminer.py brute-force -i results_file BUY_PRICE [SELL_PRICES]...
# Brute-forcing options
-o FILENAME | --out-file FILENAME # send output to the specified file. STDOUT by default
-c | --check-current | --check # use the previous set of results as data for the current week (e.g. to narrow down results based on new data). Opposite of -n | --next. Requires -i | --in-file
-n | --next # use the previous set of results as data for last week. Default mode. Opposite of -c | --check-current | --check
-p COUNT | --processes COUNT # Number of processes to use. Defaults to 1. Disables progress bars if you do not provide -P | --process
-P PROCESS_ID | --process PROCESS_ID # Process ID to run. If not provided, runs all processes. If provided an invalid process ID, runs no processes.

# Predict the next week of sales (as well as the next seeds) using your previous pattern and previous seeds (or single-seed, if you know it)
python3 dataminer.py predict PATTERN SEED --seeds SEED2 SEED3 SEED4
```

It is, in most circumstances, recommended to use the -o flag in combination with a filename.
