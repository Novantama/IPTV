import requests
from tqdm import tqdm
import re
from concurrent.futures import ThreadPoolExecutor

def is_channel_working(url, timeout=6):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def format_group_title(line):
    match = re.search(r'group-title="([^"]*)"', line)
    if match:
        group_title = match.group(1)
        if group_title.isupper():
            formatted_title = re.sub(r'[^A-Za-z]', '', group_title).title()
            line = line.replace(group_title, formatted_title)
    return line

def parse_playlist(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entries = []
    entry = []
    for line in lines:
        if line.startswith('#EXTINF'):
            line = format_group_title(line)
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

def remove_duplicates(entries):
    unique_entries = []
    seen_urls = set()
    for entry in entries:
        url = entry[-1].strip()
        if url not in seen_urls:
            seen_urls.add(url)
            unique_entries.append(entry)
    return unique_entries

def sort_entries(entries):
    def sort_key(entry):
        channel_name = entry[0].split(',')[-1].strip()
        url = entry[-1].strip()
        return (channel_name, url)

    return sorted(entries, key=sort_key)

def check_url(url):
    return url, is_channel_working(url)

def check_and_filter_entries(entries):
    urls = [entry[-1].strip() for entry in entries]
    valid_urls = set()

    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(check_url, urls), total=len(urls), desc="Checking Channels"))

    valid_entries = [entry for entry, (url, is_valid) in zip(entries, results) if is_valid]
    return valid_entries

def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            for line in entry:
                file.write(line)
            file.write('\n')

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
