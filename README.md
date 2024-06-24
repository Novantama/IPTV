Here is a README for the provided scripts, tailored for a GitHub repository:

---

# M3U Playlist Processor

This repository contains a set of Python scripts for processing M3U playlists. The scripts can perform various tasks such as fetching and cleaning playlist data, sorting and eliminating duplicates, and updating TVG IDs using EPG data. 

## Contents

1. **[01. tarikdatamodif.py](01.%20tarikdatamodif.py)**: This script fetches M3U playlists from specified URLs, cleans the data, and writes the output to a file.
2. **[02. Time-Sort-duplicate.py](02.%20Time-Sort-duplicate.py)**: This script sorts the playlist entries and eliminates duplicate entries based on certain criteria.
3. **[03. tarik EPG ID dari EPG logging.py](03.%20tarik%20EPG%20ID%20dari%20EPG%20logging.py)**: This script updates the TVG IDs in the playlist entries using EPG data from various sources.

## Requirements

- Python 3.x
- `requests` library
- `re` library
- `logging` library
- `concurrent.futures` library
- `tqdm` library
- `difflib` library

You can install the necessary libraries using pip:
```bash
pip install requests tqdm
```

## Usage

### 1. Fetch and Clean Playlist Data

Run the `01. tarikdatamodif.py` script to fetch M3U playlists from specified URLs and clean the data. 

#### Example:
```bash
python 01. tarikdatamodif.py
```

The script processes the playlists from the URLs defined in the `playlist_urls` list, cleans the data, and saves it to the specified `output_path`.

### 2. Sort and Eliminate Duplicates

Run the `02. Time-Sort-duplicate.py` script to sort the playlist entries and eliminate duplicates.

#### Example:
```bash
python 02. Time-Sort-duplicate.py
```

The script reads the cleaned playlist data, sorts it based on time, eliminates duplicates, and saves the sorted data.

### 3. Update TVG IDs Using EPG Data

Run the `03. tarik EPG ID dari EPG logging.py` script to update the TVG IDs in the playlist entries using EPG data from various sources.

#### Example:
```bash
python 03. tarik EPG ID dari EPG logging.py
```

The script fetches EPG data from multiple URLs, matches the TVG IDs with the playlist entries, updates the entries, and writes the updated playlist to the specified `output_path`.

## Configuration

You can configure the scripts by modifying the following variables:

- `playlist_urls` in `01. tarikdatamodif.py`: List of URLs to fetch the playlists from.
- `output_path` in `01. tarikdatamodif.py` and `03. tarik EPG ID dari EPG logging.py`: Path to save the output files.
- `epg_urls` in `03. tarik EPG ID dari EPG logging.py`: List of URLs to fetch the EPG data from.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to adjust the README as needed to better fit your project's specifics.
