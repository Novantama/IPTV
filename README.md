
# M3U Playlist Processor

This repository contains a set of Python scripts designed to process M3U playlists. These scripts provide functionalities for fetching and cleaning playlist data, sorting and eliminating duplicates, and updating TVG IDs using EPG data. Each script addresses a specific aspect of playlist management, ensuring your M3U playlists are well-organized and up-to-date.

## Features

### 1. `01. tarikdatamodif.py`

#### Overview

The `01. tarikdatamodif.py` script is responsible for fetching M3U playlists from specified URLs, cleaning the data to ensure it is well-structured, and then writing the cleaned data to an output file. This script is essential for preparing raw playlist data for further processing.

#### Key Features

- **Fetching Playlist Data**: The script downloads playlist data from a list of URLs specified in the `playlist_urls` variable.
- **Data Cleaning**: 
  - Removes excessive blank lines from the playlist data.
  - Ensures the `#EXTINF` lines are correctly formatted with necessary fields such as `tvg-logo`, `tvg-id`, `tvg-name`, and `group-title`.
- **Output Writing**: Saves the cleaned playlist data to a file specified by the `output_path` variable.

#### Detailed Functionality

1. **Process Playlist**

   The `process_playlist(url)` function is the core of this script. It takes a URL as an argument, fetches the playlist content from the URL, and cleans it before appending it to `output_lines`.

   ```python
   def process_playlist(url):
       response = requests.get(url)
       playlist_content = response.text
       playlist_lines = playlist_content.splitlines()
       output_lines = []

       for line in playlist_lines:
           if line.startswith("#EXTINF"):
               line = ensure_extinf_format(line)
           output_lines.append(line)

       return output_lines
   ```

2. **Ensure EXTINF Format**

   The `ensure_extinf_format(extinf_line)` function ensures that each `#EXTINF` line contains all required fields. If any field is missing, it adds the field with an empty value.

   ```python
   def ensure_extinf_format(extinf_line):
       required_fields = ["tvg-logo", "tvg-id", "tvg-name", "group-title"]
       for field in required_fields:
           if field not in extinf_line:
               extinf_line += f' {field}=""'
       return extinf_line
   ```

3. **Write Playlist**

   The `write_playlist(file_path, entries)` function writes the cleaned playlist data to the specified output file.

   ```python
   def write_playlist(file_path, entries):
       with open(file_path, "w", encoding="utf-8") as file:
           for entry in entries:
               file.write(entry + "\n")
   ```

### 2. `02. Time-Sort-duplicate.py`

#### Overview

The `02. Time-Sort-duplicate.py` script focuses on sorting playlist entries by their time and eliminating duplicate entries based on specified criteria. This ensures that the playlist is not only organized chronologically but also free of redundant entries.

#### Key Features

- **Sorting Entries**: The script sorts the playlist entries based on the time information extracted from the `#EXTINF` line.
- **Eliminating Duplicates**: Removes duplicate entries based on the URL or other criteria, ensuring each entry is unique.
- **Output Writing**: Saves the sorted and de-duplicated playlist data to a specified file.

#### Detailed Functionality

1. **Parse Playlist**

   The script reads the playlist data and parses it into individual entries. This parsing is crucial for both sorting and de-duplication processes.

   ```python
   def parse_playlist(file_path):
       with open(file_path, "r", encoding="utf-8") as file:
           lines = file.readlines()
       
       entries = []
       entry = []

       for line in lines:
           if line.strip() and line.startswith("#EXTINF"):
               if entry:
                   entries.append(entry)
                   entry = []
           entry.append(line.strip())

       if entry:
           entries.append(entry)
       
       return entries
   ```

2. **Sort Entries**

   The sorting functionality ensures that entries are ordered based on the time information found in the `#EXTINF` lines.

   ```python
   def sort_entries(entries):
       def extract_time(extinf_line):
           match = re.search(r"#EXTINF:(-?\d+)", extinf_line)
           return int(match.group(1)) if match else 0

       return sorted(entries, key=lambda entry: extract_time(entry[0]))
   ```

3. **Eliminate Duplicates**

   The script identifies and removes duplicate entries, which is essential for maintaining a clean and concise playlist.

   ```python
   def eliminate_duplicates(entries):
       seen_urls = set()
       unique_entries = []

       for entry in entries:
           url_line = next((line for line in entry if not line.startswith("#")), None)
           if url_line and url_line not in seen_urls:
               seen_urls.add(url_line)
               unique_entries.append(entry)
       
       return unique_entries
   ```

4. **Write Playlist**

   After sorting and de-duplicating, the script writes the processed data to the output file.

   ```python
   def write_playlist(file_path, entries):
       with open(file_path, "w", encoding="utf-8") as file:
           for entry in entries:
               for line in entry:
                   file.write(line + "\n")
   ```

### 3. `03. tarik EPG ID dari EPG logging.py`

#### Overview

The `03. tarik EPG ID dari EPG logging.py` script updates the TVG IDs in the playlist entries using EPG data from various sources. This script ensures that the TVG IDs in the playlist are accurate and up-to-date, which is essential for providing correct program guide information.

#### Key Features

- **Fetching EPG Data**: Downloads EPG data from a list of URLs specified in the `epg_urls` variable.
- **Updating TVG IDs**: Matches the playlist entries with the EPG data and updates the TVG IDs in the entries.
- **Handling Unmatched Entries**: Logs and optionally writes unmatched entries with their best match and similarity score.
- **Output Writing**: Saves the updated playlist data to a specified file.

#### Detailed Functionality

1. **Fetch Standard TVG IDs**

   The `fetch_standard_tvg_ids(epg_url, timeout=30)` function fetches EPG data from a given URL and extracts the TVG IDs. This function ensures that the EPG data is available for matching with the playlist entries.

   ```python
   def fetch_standard_tvg_ids(epg_url, timeout=30):
       response = requests.get(epg_url, timeout=timeout)
       tvg_data = response.json()  # Assuming the EPG data is in JSON format
       tvg_ids = {entry['tvg-id']: entry for entry in tvg_data}
       return tvg_ids
   ```

2. **Update TVG IDs**

   The `update_tvg_ids(entries, tvg_ids, similarity_threshold=0.80)` function matches the playlist entries with the EPG data and updates the TVG IDs in the entries.

   ```python
   def update_tvg_ids(entries, tvg_ids, similarity_threshold=0.80):
       updated_entries = []

       for entry in entries:
           extinf_line = entry[0]
           tvg_name_match = re.search(r'tvg-name="([^"]+)"', extinf_line)
           if tvg_name_match:
               tvg_name = tvg_name_match.group(1)
               best_match, best_score = None, 0

               for tvg_id, epg_entry in tvg_ids.items():
                   score = difflib.SequenceMatcher(None, tvg_name, epg_entry['name']).ratio()
                   if score > best_score:
                       best_match, best_score = tvg_id, score

               if best_score >= similarity_threshold:
                   extinf_line = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{best_match}"', extinf_line)
               entry[0] = extinf_line
           updated_entries.append(entry)

       return updated_entries
   ```

3. **Parse Playlist**

   Similar to the previous scripts, this function reads and parses the playlist data into individual entries.

   ```python
   def parse_playlist(file_path):
       with open(file_path, "r", encoding="utf-8") as file:
           lines = file.readlines()
       
       entries = []
       entry = []

       for line in lines:
           if line.strip() and line.startswith("#EXTINF"):
               if entry:
                   entries.append(entry)
                   entry = []
           entry.append(line.strip())

       if entry:
           entries.append(entry)
       
       return entries
   ```

4. **Write Playlist**

   The script writes the updated playlist data, including updated TVG IDs, to the output file.

   ```python
   def write_playlist(file_path, entries):
       with open(file_path, "w", encoding="utf-8") as file:
           for entry in entries:
               for line in entry:
                   file.write(line + "\n")
   ```

## Requirements

To run these scripts, you need Python 3.x and the following libraries:

- `requests`: For making HTTP requests.
- `re`: For regular expression operations.
- `logging`: For logging information.
- `concurrent.futures`: For concurrent execution of tasks.
- `tqdm`: For showing progress bars.


- `difflib`: For comparing sequences.

Install the necessary libraries using pip:

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
