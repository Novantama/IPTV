import requests
from tqdm import tqdm
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_channel_working(url, timeout=6):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_video_resolution(url, timeout=20):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        content_type = response.headers.get('content-type', '')
        if 'video' in content_type:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    resolution_match = re.search(r'(\d{3,4})[pi]', line)
                    if resolution_match:
                        resolution = int(resolution_match.group(1))
                        if resolution < 720:
                            return "SD"
                        elif resolution < 1080:
                            return "HD"
                        else:
                            return "FHD"
        return "Unknown"
    except requests.RequestException:
        return "Unknown"

def format_group_title(line):
    translation_dict = {
        "pengetahuan": "Knowledge",
        "olahraga": "Sports",
        "musik": "Music",
        "korean": "Korea",
        "animasi": "Animation",
        "berita": "News",
        "bisnis": "Business",
        "anak": "Kids",
        "gaya hidup": "Lifestyle",
        "keagamaan": "Religion",
        "belanja": "Shop",
        "film": "Movies",
        "islami": "Religion",
        "keluarga": "Family",
        "hiburan": "Entertainment",
        "lokal": "Regional",
        "daerah": "Regional",
        "dens tv": "General",
        "hbo mgtv": "HBO Group",
        "malaysia": "Malaysia",
        "music": "Music",
        "olahraga lokal": "Local Sports",
        "singapura": "Singapore",
        "nasional mgtvpng": "Nasional MGTV",
        "afc u23": "AFC U23",
        "brunei": "Brunei",
        "channel bri liga 1": "BRI Liga 1",
        "channel entertaiment lifestyle": "Lifestyle",
        "channel hbo group": "HBO Group",
        "channel korea": "Korea",
        "channel movies": "Movies",
        "channel sport": "Sport",
        "channel sport indo": "Local Sports",
        "channel sports 2": "Sports",
        "channel taiwan": "Taiwan",
        "channel vision+": "Vision+",
        "christian channels": "Christian",
        "entertainment": "Entertainment",
        "entertainment lifestyle": "Lifestyle",
        "f1": "F1",
        "general": "General",
        "indihome": "Indihome",
        "indonesia channels": "Regional",
        "internet radio": "Internet Radio",
        "kids": "Kids",
        "knowledge documentary": "Knowledge",
        "korean channels": "Korea",
        "kualifikasi world cup 2026": "World Cup 2026 Qualifiers",
        "lifestyle": "Lifestyle",
        "liga champion": "Champions League",
        "liga eropa": "Europa League",
        "liga inggris": "Premier League",
        "local channels": "Regional",
        "malaysia": "Malaysia",
        "movies": "Movies",
        "music": "Music",
        "nasional": "Regional",
        "news": "News",
        "premium movies": "Premium Movies",
        "religi": "Religion",
        "religion": "Religion",
        "singapore": "Singapore",
        "sony sport": "Sports",
        "sport asean": "Sports",
        "sports": "Sports",
        "sports2": "Sports",
        "ucl": "UCL",
        "vod indo": "VOD Indo",
        "world tv": "World TV"
    }

    match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
    if match:
        group_title = match.group(1)
        # Hapus spasi di depan
        group_title = group_title.strip()
        # Ambil kata depan jika dipisahkan dengan koma atau titik koma
        if ',' in group_title or ';' in group_title:
            group_title = re.split(r'[;,]', group_title)[0].strip()
        cleaned_group_title = re.sub(r'[^A-Za-z0-9\s\+\-\*\/]', '', group_title)
        lower_case_title = cleaned_group_title.lower()
        translated_title = translation_dict.get(lower_case_title, cleaned_group_title).title()
        line = line.replace(group_title, translated_title)
    return line

def format_channel_name(line):
    match = re.search(r'#EXTINF[^,]*,(.*)', line)
    if match:
        channel_name = match.group(1)
        # Rentang Unicode untuk karakter Jepang, Cina, Korea, Thailand, dan Vietnam
        allowed_unicode_ranges = (
            r'\u4E00-\u9FFF'  # CJK Unified Ideographs (Cina, Jepang, Korea)
            r'\u3040-\u309F'  # Hiragana (Jepang)
            r'\u30A0-\u30FF'  # Katakana (Jepang)
            r'\uAC00-\uD7AF'  # Hangul Syllables (Korea)
            r'\u0E00-\u0E7F'  # Thai (Thailand)
            r'\u1A00-\u1AFF'  # Tai Viet (Vietnam)
        )
        # Ekspresi reguler yang menghapus semua karakter kecuali yang diizinkan
        formatted_name = re.sub(fr'[^\w\s\+\-\*\/{allowed_unicode_ranges}]', '', channel_name)
        line = line.replace(channel_name, formatted_name)
    return line

def parse_playlist(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entries = []
    entry = []
    for line in lines:
        if line.startswith('#EXTINF'):
            line = format_group_title(line)
            line = format_channel_name(line)
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

def check_resolution(url):
    return url, get_video_resolution(url)

def check_and_filter_entries(entries):
    urls = [entry[-1].strip() for entry in entries]
    valid_urls = set()
    resolution_dict = {}

    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(check_url, urls), total=len(urls), desc="Checking Channels"))

    valid_entries = [entry for entry, (url, is_valid) in zip(entries, results) if is_valid]
    valid_urls = [entry[-1].strip() for entry in valid_entries]

    with ThreadPoolExecutor(max_workers=1000) as executor:
        future_to_url = {executor.submit(check_resolution, url): url for url in valid_urls}
        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="Checking Resolutions"):
            url = future_to_url[future]
            try:
                _, resolution = future.result()
                if resolution != "Unknown":
                    resolution_dict[url] = resolution
            except Exception:
                resolution_dict[url] = "Unknown"

    for entry in valid_entries:
        url = entry[-1].strip()
        if url in resolution_dict and resolution_dict[url] != "Unknown":
            resolution = resolution_dict[url]
            channel_name_match = re.search(r'#EXTINF[^,]*,(.*)', entry[0])
            if channel_name_match:
                channel_name = channel_name_match.group(1)
                new_channel_name = f"{channel_name} ({resolution})"
                entry[0] = entry[0].replace(channel_name, new_channel_name)

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
    
    print("Sorting entries...")
    sorted_entries = sort_entries(unique_entries)
    
    print("Checking URLs...")
    valid_entries = check_and_filter_entries(sorted_entries)
    
    print("Writing sorted playlist...")
    write_playlist(output_path, valid_entries)
    print("Process completed.")

if __name__ == '__main__':
    main()
