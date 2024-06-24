import requests
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import subprocess
import time

# Configuration values
INPUT_PATH = r'C:\\Users\\Admin\\Downloads\\IPTV\\Output Tarik Data.txt'
OUTPUT_PATH = r'C:\\Users\\Admin\\Downloads\\IPTV\\Output Playlist.txt'
TIMEOUT = 10  # Timeout for checking channel availability
FFPROBE_TIMEOUT = 60  # Timeout for ffprobe response time check
CHECK_CHANNEL_WORKING = False  # Flag to turn on/off channel working check

def is_channel_working(url, timeout=TIMEOUT):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_ffprobe_response_time(url, timeout=FFPROBE_TIMEOUT):
    try:
        start_time = time.time()
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'default=nw=1:nk=1', url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        if result.returncode == 0:
            response_time = time.time() - start_time
            return response_time
    except Exception:
        return None
    return None

def format_group_title(line):
    match = re.search(r'group-title="([^"]+)"', line)
    if match:
        group_title = match.group(1)
        group_title = re.sub(r'\s+', ' ', group_title)
        line = line.replace(match.group(1), group_title)
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
        elif line.strip():
            entry.append(line)

    if entry:
        entries.append(entry)

    return entries

def remove_duplicates(entries):
    url_to_entry = {}
    for entry in entries:
        url = entry[-1].strip()
        url_to_entry[url] = entry
    return list(url_to_entry.values())

def sort_entries(entries):
    def sort_key(entry):
        # Check for tvg-id
        tvg_id_match = re.search(r'tvg-id="([^"]+)"', entry[0])
        tvg_id_filled = bool(tvg_id_match and tvg_id_match.group(1).strip())
        
        # Extract response time
        response_time_match = re.search(r'\((\d+\.\d+)s\)', entry[0])
        response_time = float(response_time_match.group(1)) if response_time_match else float('inf')
        
        return (not tvg_id_filled, response_time)
    
    return sorted(entries, key=sort_key)

def check_url(url):
    return url, is_channel_working(url)

def check_and_filter_entries(entries):
    if not CHECK_CHANNEL_WORKING:
        return entries

    urls = [entry[-1].strip() for entry in entries]

    with ThreadPoolExecutor(max_workers=1000) as executor:
        results = list(tqdm(executor.map(check_url, urls), total=len(urls), desc="Checking Channels"))

    valid_entries = [entry for entry, (url, is_valid) in zip(entries, results) if is_valid]

    return valid_entries

def standardize_group_titles(entries, similarity_threshold=0.5):
    indo_to_eng = {
  'Anak': 'Kids',
        'Berita': 'News',
        'Brunai': 'Brunei',
        'CHANNEL | BRI LIGA 1': 'Sports',
        'CHANNEL | ENTERTAIMENT & LIFESTYLE': 'Entertainment',
        'CHANNEL | HBO GROUP': 'Movies',
        'CHANNEL | INDONESIA': 'National',
        'CHANNEL | KOREA': 'Korean Channels',
        'CHANNEL | TAIWAN': 'Taiwan Channels',
        'CHANNEL | VISION+': 'Vision+',
        'CHANNEL | SPORT': 'Sports',
        'Christian Channels': 'Religious',
        'Daerah': 'Regional',
        'Dakwah': 'Religious',
        'Dokumenter': 'Documentary',
        'Film': 'Movies',
        'Gaya Hidup': 'Lifestyle',
        'HBO GROUP': 'Movies',
        'Hiburan': 'Entertainment',
        'INDIHOME': 'Entertainment',
        'ISLAMI': 'Religious',
        'Indonesia Channels': 'National',
        'Informasi': 'Information',
        'Internet Radio': 'Internet Radio',
        'KUALIFIKASI WORLD CUP 2026': 'Sports',
        'SPORT ASEAN': 'Sports',
        'Korean Channels': 'Korean Channels',
        'LIFESTYLE': 'Lifestyle',
        'LIGA CHAMPION': 'Sports',
        'LIGA EROPA': 'Sports',
        'LIGA INGGRIS': 'Sports',
        'Lokal': 'Regional',
        'Malaysia': 'Malaysia',
        'Musik': 'Music',
        'NASIONAL': 'National',
        'Nasional': 'National',
        'Olahraga': 'Sports',
        'Pengetahuan': 'Knowledge',
        'RELIGI': 'Religious',
        'Radio': 'Radio',
        'SINGAPORE': 'Singapore',
        'Singapura': 'Singapore',
        'VOD INDO': 'Indonesian VOD',
        '🇲🇾 MALAYSIA': 'Malaysia',
        '🌀 Dens TV': 'Dens TV',
        '🎥 HBO | MGTV': 'Movies',
        '💡 PENGETAHUAN': 'Knowledge',
        '🛐 KEAGAMAAN': 'Religious',
        '📰 BERITA': 'News',
        'BADMINTON': 'Sports',
        'BRI LIGA 1': 'Sports',
        'NATIONAL': 'National',
        'HBO GROUP': 'Movies',
        'MOVIES': 'Movies',
        'KIDS': 'Kids',
        'ENTERTAINMENT': 'Entertainment',
        'LIFESTYLE': 'Lifestyle',
        'DOCUMENTARY': 'Documentary',
        'NEWS': 'News',
        'RELIGION': 'Religious',
        'MUSIC': 'Music',
        'FTA International': 'International',
        'SPORTS': 'Sports',
        'INDIHOME': 'Entertainment',
        'Malaysia': 'Malaysia',
        'Brunei': 'Brunei',
        'Sports Special': 'Sports',
        'ASTRO': 'Entertainment',
        'SONY SPORT': 'Sports',
        'DAZN SPORTS': 'Sports',
        'FRENCH SPORTS': 'Sports',
        '#🇬🇧 UK Sport 🇬🇧#': 'Sports',
        'Live Stream': 'Live',
        'Bics COPA EURO': 'Sports',
        'Bics COPA AMERICA': 'Sports',
        'NATIONAL NEWS': 'News',
        'PARLIAMENTARY': 'News',
        'LOKAL': 'Regional',
        'TVRI DAERAH': 'Regional',
        'NATIONAL ENTERTAINMENT': 'Entertainment',
        'GENERAL ENTERTAINMENT': 'Entertainment',
        'KOREAN ENTERTAINMENT': 'Entertainment',
        'JAPANESE ENTERTAINMENT': 'Entertainment',
        'FRENCH ENTERTAINMENT': 'Entertainment',
        'BRITISH ENTERTAINMENT': 'Entertainment',
        'AMERICAN ENTERTAINMENT': 'Entertainment',
        'CHINESE ENTERTAINMENT': 'Entertainment',
        'WORLD ENTERTAINMENT': 'Entertainment',
        'EUROPEAN ENTERTAINMENT': 'Entertainment',
        'NATIONAL MUSIC': 'Music',
        'WORLD MUSIC': 'Music',
        'EUROPEAN MUSIC': 'Music',
        'NATIONAL MOVIES': 'Movies',
        'GENERAL MOVIES': 'Movies',
        'ASIAN MOVIES': 'Movies',
        'CHINESE MOVIES': 'Movies',
        'HINDI MOVIES': 'Movies',
        'PINOY MOVIES': 'Movies',
        'BRITISH MOVIES': 'Movies',
        'SPANISH MOVIES': 'Movies',
        'WORLD SERIES': 'Movies',
        'SPANISH SERIES': 'Movies',
        'PORTUGUESE SERIES': 'Movies',
        'SCIENCE & DOCUMENTARY': 'Documentary',
        'WORLD NEWS': 'News',
        'AFRICAN NEWS': 'News',
        'AMERICAN NEWS': 'News',
        'BRITISH NEWS': 'News',
        'AUSTRALIAN NEWS': 'News',
        'ARABIC NEWS': 'News',
        'MALAY NEWS': 'News',
        'PORTUGUESE NEWS': 'News',
        'SPANISH NEWS': 'News',
        'FRENCH NEWS': 'News',
        'GERMAN NEWS': 'News',
        'ITALIAN NEWS': 'News',
        'BRASILIAN NEWS': 'News',
        'INDIAN NEWS': 'News',
        'HINDI NEWS': 'News',
        'PINOY NEWS': 'News',
        'CANADIAN NEWS': 'News',
        'TURKISH NEWS': 'News',
        'MANDARIN NEWS': 'News',
        'KOREAN NEWS': 'News',
        'LATINO NEWS': 'News',
        'THAI NEWS': 'News',
        'NATIONAL SPORTS': 'Sports',
        'BRITISH SPORTS': 'Sports',
        'IRISH SPORTS': 'Sports',
        'PORTUGUESE SPORTS': 'Sports',
        'THAI SPORTS': 'Sports',
        'MALAY SPORTS': 'Sports',
        'GERMAN SPORTS': 'Sports',
        'ITALIAN SPORTS': 'Sports',
        'SPANISH SPORTS': 'Sports',
        'INDIAN SPORTS': 'Sports',
        'BELGIAN SPORTS': 'Sports',
        'DUTCH SPORTS': 'Sports',
        'SERBIAN SPORTS': 'Sports',
        'ROMANIAN SPORTS': 'Sports',
        'BRASILIAN SPORTS': 'Sports',
        'AMERICAN SPORTS': 'Sports',
        'CANADIAN SPORTS': 'Sports',
        'TAIWANESE SPORTS': 'Sports',
        'NORDIC SPORTS': 'Sports',
        'ARABIC SPORTS': 'Sports',
        'LATINO SPORTS': 'Sports',
        'TURKISH SPORTS': 'Sports',
        'ASIAN SPORTS': 'Sports',
        'PINOY SPORTS': 'Sports',
        'CLUBS OF SPORTS': 'Sports',
        'WORLD SPORTS': 'Sports',
        'FASHION': 'Fashion',
        'VISUAL RADIO': 'Internet Radio',
        'MALAYSIA': 'Malaysia',
        'SINGAPORE': 'Singapore',
        'USA': 'USA',
        'UK': 'UK',
        'AUSTRALIA': 'Australia',
        'BRASIL': 'Brasil',
        'FRANCE': 'France',
        'GERMANY': 'Germany',
        'BELGIUM': 'Belgium',
        'INDIA': 'India',
        'ITALY': 'Italy',
        'JAPAN': 'Japan',
        'KOREA': 'Korea',
        'NETHERLANDS': 'Netherlands',
        'PHILIPPINES': 'Philippines',
        'PORTUGAL': 'Portugal',
        'ROMANIA': 'Romania',
        'SPAIN': 'Spain',
        'THAILAND': 'Thailand',
        'TÜRKIYE': 'Turkey',
        'RADIO INDONESIA': 'Internet Radio',
        'PINOY RADIO': 'Internet Radio',
        'MALAY RADIO': 'Internet Radio',
        'RRI RADIO': 'Internet Radio',
        'PORTUGUESE RADIO': 'Internet Radio',
        'SINGAPOREAN RADIO': 'Internet Radio',
        'BRITISH RADIO': 'Internet Radio',
        'AUSTRALIAN RADIO': 'Internet Radio',
        'SPANISH RADIO': 'Internet Radio',
        'WORLD RADIO': 'Internet Radio',
        '[LIVE] Liga INDO': 'Sports',
        'AFC LIVE': 'Sports',
        'FIFA+': 'Sports',
        'Indonesia Channels': 'National',
        'Lokal': 'Regional',
        'Music': 'Music',
        'Premium Movies': 'Movies',
        'Korean Channels': 'Korean Channels',
        'Knowledge & Documentary': 'Knowledge',
        'Entertainment & LifeStyle': 'Entertainment',
        'Kids': 'Kids',
        'Sports': 'Sports',
        'LIGA CHAMPION': 'Sports',
        'LIGA EROPA': 'Sports',
        'LIGA INGGRIS': 'Sports',
        'News': 'News',
        'RELIGI': 'Religious',
        'Christian Channels': 'Religious',
        'Singapore': 'Singapore',
        'TVRI Group': 'TVRI',
        'Local Channels': 'Regional',
        'HBO Group': 'Movies',
        'Internet Radio': 'Internet Radio',
        'SPORTS2': 'Sports',
        'SOOKA TV': 'Sooka TV',
        'SPORT BACKUP': 'Sports',
        'ARABIC CHANNEL': 'International',
        'UNIFI': 'Unifi',
        'INDIAN': 'Indian Channels',
        'CHINESE': 'Chinese Channels',
        'KOREAN': 'Korean Channels',
        'ANOTHER SPORTS': 'Sports',
        'INDONESIA': 'National',
        'RADIO': 'Radio',
        '🇮🇩 NASIONAL | MGTV.png': 'National',
        '⚠️ INFORMASI': 'Information',
        '💡 PENGETAHUAN': 'Knowledge',
        'OLAHRAGA LOKAL': 'Local Sports',
        '🏍️EVENT MOTO GP🏍️': 'MotoGP',
        'CHANNEL | BRI LIGA 1': 'Sports',
        '🧭 DAERAH': 'Regional',
        '🎥 FILM': 'Movies',
        'KUALIFIKASI WORLD CUP 2026': 'Sports',
        '🏆 OLAHRAGA LUAR': 'International Sports',
        'EURO 2024': 'Sports',
        '🏅OLAHRAGA': 'Sports',
        '🇲🇾 MALAYSIA': 'Malaysia',
        '🇨🇳 CHINA': 'China',
        'ANAK': 'Kids',
        '🇸🇬 SINGAPURA': 'Singapore',
        '📰 BERITA': 'News',
        '🎥 HBO | MGTV': 'Movies',
        '🛐 KEAGAMAAN': 'Religious',
        '🤖 GAYA HIDUP': 'Lifestyle',
        '🎵 MUSIC': 'Music',
        '🇯🇵 JEPANG': 'Japan',
        '🇰🇷 KOREA': 'Korea',
        'CHANNEL | SPORT 2': 'Sports',
        'CHANNEL | KNOWLEDGE': 'Knowledge',
        'CHANNEL | SPORT INDO': 'Indonesian Sports',
        '👑EVENT MOTO GP👑': 'MotoGP',
        'CHANNEL | SPORTS INDO': 'Indonesian Sports',
        '⚽️Liga Champions⚽️': 'Sports',
        '⚽️Europa league⚽️': 'Sports',
        'CHANNEL | INDONESIA': 'Indonesia Channels',
        'CHANNEL | DAERAH': 'Regional',
        'CHANNEL | MOVIES': 'Movies',
        'Movies': 'Movies',
        'CHANNEL | SPORT': 'Sports',
        'Qingsports': 'Qingsports',
        'CHANNEL | KIDS': 'Kids',
        'CHANNEL | SINGAPORE': 'Singapore',
        'CHANNEL | NEWS': 'News',
        'VOD INDO': 'Indonesian VOD',
        'CHANNEL | HBO GROUP': 'Movies',
        'CHANNEL | RELIGI': 'Religious',
        'CHANNEL | ENTERTAIMENT & LIFESTYLE': 'Entertainment & Lifestyle',
        'CHANNEL | MUSIC': 'Music',
        'CHANNEL | JAPAN': 'Japan',
        'CHANNEL | VISION+': 'Vision+',
        'CHANNEL | CHINA': 'China',
        'CHANNEL | KOREA': 'Korea',
        'CHANNEL | TAIWAN': 'Taiwan Channels',
        'HCHANNEL | TAIWAN': 'Taiwan Channels',
        'CHANNEL | BEIN SPORTS': 'Bein Sports',
        'therium`': 'Therium',
        'GRATIS': 'Free',
        'F1': 'Formula 1',
        'FORMULA E': 'Formula E',
        'MotoGP': 'MotoGP',
        'WSBK': 'WSBK',
        'KNOWLEDGE': 'Knowledge',
        'DAERAH': 'Regional',
        'WORLD TV': 'World TV'
    }

    standard_group_titles = {
        'Sports': ['sports', 'football', 'liga', 'cup', 'champion'],
        'News': ['news', 'berita', 'informasi'],
        'Movies': ['movies', 'film', 'cinema', 'hbo'],
        'Entertainment': ['entertainment', 'hiburan'],
        'Kids': ['kids', 'anak'],
        'Music': ['music', 'musik'],
        'Documentary': ['documentary', 'dokumenter'],
        'Regional': ['regional', 'daerah', 'lokal'],
        'International': ['international', 'internasional', 'global'],
        'Adult': ['adult', 'dewasa'],
        'Religious': ['religious', 'islami', 'dakwah', 'keagamaan'],
        'Knowledge': ['knowledge', 'pengetahuan'],
        'Lifestyle': ['lifestyle', 'gaya hidup'],
        'Internet Radio': ['internet radio', 'radio'],
        'Indonesia Channels': ['indonesia'],
        'Malaysia': ['malaysia'],
        'Singapore': ['singapore'],
        'Taiwan': ['taiwan'],
        'Dens TV': ['dens tv'],
        'Vision+': ['vision+'],
        'HBO | MGTV': ['hbo', 'mgtv'],
        'Indonesian VOD': ['vod indo']
    }

    country_names = [
        'Indonesia', 'Malaysia', 'Singapore', 'Brunei', 'Taiwan', 'Korea', 'Japan', 'China',
        'India', 'Thailand', 'Vietnam', 'Philippines', 'Australia', 'New Zealand', 'USA',
        'Canada', 'Mexico', 'Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela',
        'Russia', 'Germany', 'France', 'UK', 'Italy', 'Spain', 'Netherlands', 'Belgium',
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Poland', 'Ukraine', 'Czech Republic',
        'Austria', 'Switzerland', 'Portugal', 'Greece', 'Turkey', 'Saudi Arabia', 'UAE',
        'Israel', 'South Africa', 'Nigeria', 'Egypt', 'Kenya', 'Morocco'
    ]

    def translate_to_english(group_title):
        for indo, eng in indo_to_eng.items():
            if indo.lower() in group_title.lower():
                return eng
        return group_title

    def find_standard_group_title(group_title):
        group_title_lower = group_title.lower()
        for standard_title, keywords in standard_group_titles.items():
            if any(keyword in group_title_lower for keyword in keywords):
                return standard_title
        return group_title  # return original if no match

    def classify_as_international(group_title):
        for country in country_names:
            if country.lower() in group_title.lower():
                return 'International'
        return None

    for entry in entries:
        extinf_line = entry[0]
        group_title_match = re.search(r'group-title="([^"]+)"', extinf_line)
        if group_title_match:
            group_title = group_title_match.group(1)
            english_title = translate_to_english(group_title)
            international_classification = classify_as_international(english_title)
            if international_classification:
                standardized_title = international_classification
            else:
                standardized_title = find_standard_group_title(english_title)
            entry[0] = extinf_line.replace(group_title, standardized_title)
    
    return entries


def append_ffprobe_time(entries):
    urls = [entry[-1].strip() for entry in entries]

    def process_url(url):
        response_time = get_ffprobe_response_time(url)
        return url, response_time

    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(tqdm(executor.map(process_url, urls), total=len(urls), desc="Getting FFprobe Response Times"))

    for entry, (url, response_time) in zip(entries, results):
        if response_time is not None:
            extinf_line = entry[0]
            channel_name_match = re.search(r'#EXTINF[^,]*,(.*)', extinf_line)
            if channel_name_match:
                channel_name = channel_name_match.group(1).strip()
                new_channel_name = f'{channel_name} ({response_time:.1f}s)'
                entry[0] = extinf_line.replace(channel_name, new_channel_name)

    return entries

def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            extinf_line = entry[0]
            url_line = entry[-1].strip()
            additional_lines = entry[1:-1]

            tvg_id = re.search(r'tvg-id="([^"]*)"', extinf_line)
            tvg_name = re.search(r'tvg-name="([^"]*)"', extinf_line)
            tvg_logo = re.search(r'tvg-logo="([^"]*)"', extinf_line)
            group_title = re.search(r'group-title="([^"]*)"', extinf_line)
            channel_name = re.search(r'#EXTINF[^,]*,(.*)', extinf_line)

            tvg_id_str = f'tvg-id="{tvg_id.group(1)}"' if tvg_id else ''
            tvg_name_str = f'tvg-name="{tvg_name.group(1)}"' if tvg_name else ''
            tvg_logo_str = f'tvg-logo="{tvg_logo.group(1)}"' if tvg_logo else ''
            group_title_str = f'group-title="{group_title.group(1)}"' if group_title else ''
            channel_name_str = channel_name.group(1).strip() if channel_name else ''

            attributes = [tvg_name_str, tvg_id_str, tvg_logo_str, group_title_str]
            attributes = [attr for attr in attributes if attr]  # Filter out empty strings
            formatted_extinf = f'#EXTINF:-1 {" ".join(attributes)},{channel_name_str}\n'

            file.write(formatted_extinf)
            
            for additional_line in additional_lines:
                file.write(additional_line.strip() + '\n')
            
            file.write(url_line + '\n\n')  # Add an extra newline for separation

def main():
    print("Parsing playlist...")
    entries = parse_playlist(INPUT_PATH)

    print("Removing duplicates...")
    entries = remove_duplicates(entries)

    print("Standardizing group titles...")
    entries = standardize_group_titles(entries)

    print("Getting FFprobe response times...")
    entries = append_ffprobe_time(entries)

    print("Sorting entries...")
    entries = sort_entries(entries)

    if CHECK_CHANNEL_WORKING:
        print("Checking URLs...")
        entries = check_and_filter_entries(entries)

    print("Writing sorted playlist...")
    write_playlist(OUTPUT_PATH, entries)

    print("Process completed.")

if __name__ == '__main__':
    main()
