import requests
import concurrent.futures
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fungsi untuk memeriksa apakah URL channel berfungsi menggunakan HEAD
def check_channel_head(url, timeout=6):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Fungsi untuk mendapatkan konten channel menggunakan GET
def check_channel_get(url, timeout=6):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except requests.RequestException:
        return None

# Fungsi untuk memeriksa resolusi video
def get_video_resolution(content):
    # Simplified resolution check for demonstration purposes
    if b'resolution="1920x1080"' in content or b'1920x1080' in content:
        return "FHD"
    elif b'resolution="1280x720"' in content or b'1280x720' in content:
        return "HD"
    elif b'resolution="640x360"' in content or b'640x360' in content:
        return "SD"
    else:
        return "Unknown"

# Fungsi untuk memproses setiap channel
def process_channel(channel_lines):
    url = channel_lines[0].strip()
    logging.info(f"Processing channel: {url}")

    # Skip URL that contains "mac"
    if "mac=" in url:
        logging.info(f"Skipping channel containing 'mac': {url}")
        return None
    
    if check_channel_head(url):
        content = check_channel_get(url)
        if content:
            resolution = get_video_resolution(content)
            # Jika resolusi bukan "Unavailable" atau "Unknown", tambahkan informasi resolusi pada nama channel
            if resolution not in ["Unavailable", "Unknown"]:
                for i, line in enumerate(channel_lines):
                    if line.startswith("#EXTINF"):
                        channel_lines[i] = line.strip() + f" [{resolution}]\n"
            return channel_lines
    return None

# Fungsi utama untuk memproses playlist
def process_playlist(input_file, output_file):
    # Membaca file playlist
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(input_file, 'r', encoding='latin-1') as file:
            lines = file.readlines()

    # Membagi lines menjadi blok channel
    channels = []
    current_channel = []
    for line in lines:
        if line.startswith("http"):
            if current_channel:
                channels.append(current_channel)
                current_channel = []
        current_channel.append(line)
    if current_channel:
        channels.append(current_channel)

    valid_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_channel, channel): channel for channel in channels}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=6)
                if result:
                    valid_channels.extend(result)
            except concurrent.futures.TimeoutError:
                logging.error(f"Skipping channel due to timeout: {futures[future][0].strip()}")
            except Exception as e:
                logging.error(f"Error processing channel: {e}")

    # Menyimpan channel yang valid ke file baru
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(valid_channels)

if __name__ == "__main__":
    input_file = "C:\\Users\\Admin\\Downloads\\Playlist Novan.txt"
    output_file = "C:\\Users\\Admin\\Downloads\\sorterfixed.txt"
    process_playlist(input_file, output_file)
