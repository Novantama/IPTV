# IPTV Playlist Processor

This repository contains a Python script to process and clean up IPTV playlists. The script performs the following tasks:
1. Parses the playlist and groups lines belonging to the same channel entry.
2. Removes duplicate channel entries.
3. Checks if the URLs are working.
4. Sorts the playlist by channel names and URLs.
5. Formats the `group-title` attribute to be properly capitalized and removes non-alphabet characters.

## Features

- **Duplicate Removal**: Ensures that only unique channel entries are retained.
- **URL Validation**: Checks if the channel URLs are reachable and valid.
- **Sorting**: Sorts the playlist entries by channel name and URL.
- **Title Formatting**: Formats `group-title` attributes to be properly capitalized and cleans up non-alphabet characters.
- **Parallel URL Checking**: Uses parallel processing to speed up URL validation.

## Requirements

- Python 3.x
- `requests` library
- `tqdm` library

You can install the required libraries using pip:
```sh
pip install requests tqdm
```



---

## Usage

1. **Clone the Repository**
    ```sh
    git clone https://github.com/Novantama/IPTV.git
    cd IPTV
    ```

2. **Prepare Your Playlist File**
    Ensure your playlist file is in the correct format and place it in the desired directory. Update the `input_path` and `output_path` variables in the script as necessary.

3. **Run the Script**
    ```sh
    python IPTV_Playlist_Processor.py
    ```

## Script Overview

The script, `IPTV_Playlist_Processor.py`, contains the following functions:

- **is_channel_working(url, timeout=6)**: Checks if a given URL is reachable within the specified timeout.
- **format_group_title(line)**: Formats the `group-title` attribute to be capitalized correctly and removes non-alphabet characters.
- **parse_playlist(file_path)**: Parses the playlist file and groups lines into channel entries.
- **remove_duplicates(entries)**: Removes duplicate channel entries based on the URL.
- **sort_entries(entries)**: Sorts the entries by channel name and URL.
- **check_url(url)**: Checks if a single URL is valid.
- **check_and_filter_entries(entries)**: Checks all URLs in parallel and filters out the invalid ones.
- **write_playlist(file_path, entries)**: Writes the cleaned and sorted playlist back to a file.
- **main()**: Main function to orchestrate the script execution.

## Example

Make sure to update the file paths in the `main()` function:
```python
def main():
    input_path = r'C:\\Users\\Admin\\Downloads\\Playlist Novan.txt'
    output_path = r'C:\\Users\\Admin\\Downloads\\sorted_playlist.txt'

    print("Parsing playlist...")
    entries = parse_playlist(input_path)
    
    print("Removing duplicates...")
    unique_entries = remove_duplicates(entries)
    
    print("Checking URLs...")
    valid_entries = check_and_filter_entries(unique_entries)
    
    print("Sorting entries...")
    sorted_entries = sort_entries(valid_entries)
    
    print("Writing sorted playlist...")
    write_playlist(output_path, sorted_entries)
    print("Process completed.")

if __name__ == '__main__':
    main()
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## Acknowledgments

- Inspiration, code snippets, etc.

---

This README should provide a comprehensive guide to using and understanding the script. Adjust paths and filenames as necessary for your specific use case.
