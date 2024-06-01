# Playlist Processing Tool

This repository contains a Python script designed to process M3U playlists. It includes features for parsing, formatting, removing duplicates, sorting, checking URLs for availability, and determining the video resolution of each channel.

## Features

- **Parsing Playlist**: Reads and parses M3U playlist files.
- **Formatting**: Formats group titles and channel names based on a predefined translation dictionary and character rules.
- **Removing Duplicates**: Identifies and removes duplicate entries based on URLs.
- **Sorting Entries**: Sorts the playlist entries alphabetically by channel name and URL.
- **Checking URLs**: Verifies if the URLs in the playlist are working.
- **Determining Resolution**: Checks the video resolution (SD, HD, FHD) of each channel and appends this information to the channel name.
- **Multithreading**: Uses multithreading to speed up the checking of URLs and resolutions.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/playlist-processing-tool.git
    cd playlist-processing-tool
    ```

2. **Install dependencies**:
    The script requires `requests`, `tqdm`, and `concurrent.futures` (included in Python 3.2+). You can install `requests` and `tqdm` using pip:
    ```sh
    pip install requests tqdm
    ```

## Usage

1. **Prepare your playlist file**:
    Ensure your M3U playlist file is ready and note its path.

2. **Run the script**:
    Edit the `input_path` and `output_path` variables in the `main()` function to point to your input and output files. Then, run the script:
    ```sh
    python Dupl_Sort_Rename_Check_Resolution.py
    ```

3. **Output**:
    The script processes the playlist and writes the sorted, formatted, and verified playlist to the specified output path.

## Detailed Description of Functions

- **is_channel_working(url, timeout=6)**:
  Checks if a channel URL is working by sending a HEAD request.

- **get_video_resolution(url, timeout=20)**:
  Determines the video resolution by analyzing the content of the response from the URL.

- **format_group_title(line)**:
  Formats the group title using a predefined translation dictionary.

- **format_channel_name(line)**:
  Formats the channel name by removing unwanted characters.

- **parse_playlist(file_path)**:
  Parses the M3U playlist file into individual entries.

- **remove_duplicates(entries)**:
  Removes duplicate entries based on URLs.

- **sort_entries(entries)**:
  Sorts entries alphabetically by channel name and URL.

- **check_url(url)**:
  Checks if a URL is working.

- **check_resolution(url)**:
  Checks the resolution of a video URL.

- **check_and_filter_entries(entries)**:
  Checks URLs and their resolutions, filtering out non-working URLs and appending resolution information.

- **write_playlist(file_path, entries)**:
  Writes the processed entries back to a new M3U playlist file.

- **main()**:
  The main function that orchestrates the processing of the playlist.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.

## Acknowledgments

- Thanks to the developers of `requests` and `tqdm` for their amazing libraries.
- Special thanks to the open-source community for their valuable contributions and feedback.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

For any questions or issues, please open an issue on GitHub or contact the repository owner.
