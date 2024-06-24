import requests
import re

playlist_urls = [
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/Urfan%20TV.txt',    
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/DENSTV.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/GM-Vision.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/Jeje%20Vision%20TV.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/JustryuzTV.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/MAGELIFE.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/Sanya%20TV.txt',
     #'https://raw.githubusercontent.com/Novantama/IPTV/Main/Playlist/Therium%20TV.txt',
      'https://iptv-org.github.io/iptv/index.m3u',
]

output_path = r'C:\\Users\\Admin\\Downloads\\IPTV\\Output Tarik Data.txt'

output_lines = []

def process_playlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        playlist_content = response.text

        # Split the content into lines
        lines = playlist_content.splitlines()

        # Remove excessive blank lines and ensure correct format
        cleaned_lines = []
        blank_line = False
        extinf_pattern = re.compile(r'#EXTINF:-1.*')

        for line in lines:
            if line.strip() == '':
                if not blank_line:
                    cleaned_lines.append(line)
                blank_line = True
            else:
                if extinf_pattern.match(line):
                    line = ensure_extinf_format(line)
                cleaned_lines.append(line)
                blank_line = False
        
        output_lines.extend(cleaned_lines)
        output_lines.append('')  # Ensure there's a blank line between different playlists

    except requests.exceptions.RequestException as e:
        print(f'Error fetching playlist from {url}: {str(e)}')

def ensure_extinf_format(extinf_line):
    # Ensure the extinf line has all necessary fields with empty values if missing
    tvg_logo = re.search(r'tvg-logo="[^"]*"', extinf_line)
    tvg_id = re.search(r'tvg-id="[^"]*"', extinf_line)
    tvg_name = re.search(r'tvg-name="[^"]*"', extinf_line)
    group_title = re.search(r'group-title="[^"]*"', extinf_line)

    if not tvg_logo:
        extinf_line = extinf_line.replace('#EXTINF:-1', '#EXTINF:-1 tvg-logo=""')
    if not tvg_id:
        extinf_line = extinf_line.replace('#EXTINF:-1', '#EXTINF:-1 tvg-id=""', 1)
    if not tvg_name:
        extinf_line = extinf_line.replace('#EXTINF:-1', '#EXTINF:-1 tvg-name=""', 1)
    if not group_title:
        extinf_line = extinf_line.replace('#EXTINF:-1', '#EXTINF:-1 group-title=""', 1)
    
    return extinf_line

def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        for entry in entries:
            file.write(entry + '\n')

for url in playlist_urls:
    process_playlist(url)

# Remove the last unnecessary blank line
if output_lines and output_lines[-1] == '':
    output_lines.pop()

write_playlist(output_path, output_lines)

print(f'Output playlist telah disimpan ke {output_path}')
