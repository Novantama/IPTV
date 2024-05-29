import os

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

def remove_duplicates_and_sort(entries):
    unique_entries = []
    seen_urls = set()
    for entry in entries:
        url = entry[-1].strip()
        if url not in seen_urls:
            seen_urls.add(url)
            unique_entries.append(entry)

    # Extract the Channel Name and URL for sorting
    def sort_key(entry):
        # Assuming channel name is in the #EXTINF line, after the last comma
        channel_name = entry[0].split(',')[-1].strip()
        url = entry[-1].strip()
        return (channel_name, url)

    sorted_entries = sorted(unique_entries, key=sort_key)
    return sorted_entries

def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            for line in entry:
                file.write(line)
            file.write('\n')

def main():
    input_path = r'C:\\Users\\Admin\\Downloads\\Playlist Novan.txt'
    output_path = r'C:\\Users\\Admin\\Downloads\\unic.txt'

    entries = parse_playlist(input_path)
    sorted_entries = remove_duplicates_and_sort(entries)
    write_playlist(output_path, sorted_entries)

if __name__ == '__main__':
    main()
