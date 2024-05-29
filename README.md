# Playlist Sorter Script

This Python script processes an M3U playlist file to remove duplicate entries and sort them by channel name and URL. The script maintains the integrity of each playlist entry, ensuring that all related lines are kept together.

## Features
- Parses an M3U playlist file.
- Removes duplicate entries based on the URL.
- Sorts the entries by channel name and URL.
- Writes the cleaned and sorted playlist to a new file.

## Requirements
- Python 3.x

## Usage

### 1. Clone the Repository

First, clone the repository to your local machine.

```bash
git clone https://github.com/yourusername/playlist-sorter.git
cd playlist-sorter
```

### 2. Prepare Your Playlist

Ensure your M3U playlist file is ready. Place it in a known directory, and note the file path. For example, `C:\Users\Admin\Downloads\Playlist Novan.txt`.

### 3. Update Script Paths

Open the `sorter.py` script and update the `input_path` and `output_path` variables in the `main` function to match your environment.

```python
def main():
    input_path = r'C:\\Users\\Admin\\Downloads\\Playlist Novan.txt'
    output_path = r'C:\\Users\\Admin\\Downloads\\unic.txt'
```

### 4. Run the Script

Run the script using Python:

```bash
python sorter.py
```

### 5. Check the Output

The script will create a new file with the sorted playlist at the specified `output_path`. Open and verify the output file.

## Code Explanation

### parse_playlist Function

```python
def parse_playlist(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entries = []
    entry = []
    for line in lines:
        if line.startswith('#EXTINF'):
            if entry:
                entries.append(entry)
            entry = [line]
        elif line.strip() and not line.startswith('#'):
            entry.append(line)
        elif line.startswith('#KODIPROP:inputstream.adaptive.license_type') or line.startswith('#KODIPROP:inputstream.adaptive.license_key') or line.startswith('#EXTVLCOPT:'):
            if entry:
                entry.append(line)

    if entry:
        entries.append(entry)

    return entries
```

- **Purpose**: Reads and parses the M3U playlist file, grouping related lines into entries.
- **Input**: Path to the M3U playlist file.
- **Output**: A list of entries, where each entry is a list of lines.

### remove_duplicates_and_sort Function

```python
def remove_duplicates_and_sort(entries):
    unique_entries = []
    seen_urls = set()
    for entry in entries:
        url = entry[-1].strip()
        if url not in seen_urls:
            seen_urls.add(url)
            unique_entries.append(entry)

    def sort_key(entry):
        channel_name = entry[0].split(',')[-1].strip()
        url = entry[-1].strip()
        return (channel_name, url)

    sorted_entries = sorted(unique_entries, key=sort_key)
    return sorted_entries
```

- **Purpose**: Removes duplicate entries and sorts them by channel name and URL.
- **Input**: A list of entries.
- **Output**: A list of unique and sorted entries.

### write_playlist Function

```python
def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            for line in entry:
                file.write(line)
            file.write('\n')
```

- **Purpose**: Writes the sorted entries back to a new M3U playlist file.
- **Input**: Path to the output file and the list of sorted entries.
- **Output**: None (writes to file).

### main Function

```python
def main():
    input_path = r'C:\\Users\\Admin\\Downloads\\Playlist Novan.txt'
    output_path = r'C:\\Users\\Admin\\Downloads\\unic.txt'

    entries = parse_playlist(input_path)
    sorted_entries = remove_duplicates_and_sort(entries)
    write_playlist(output_path, sorted_entries)

if __name__ == '__main__':
    main()
```

- **Purpose**: Orchestrates the parsing, sorting, and writing of the playlist.
- **Steps**:
  1. Reads the input playlist file.
  2. Parses the file into entries.
  3. Removes duplicates and sorts the entries.
  4. Writes the sorted entries to the output file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## Acknowledgments

- Inspiration, code snippets, etc.

---

This README should provide a comprehensive guide to using and understanding the script. Adjust paths and filenames as necessary for your specific use case.
