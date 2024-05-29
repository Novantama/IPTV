import requests
from tqdm import tqdm
import concurrent.futures

# Fungsi untuk memeriksa apakah URL channel berfungsi
def check_channel(url, timeout=6):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response
        else:
            return None
    except requests.RequestException:
        return None

# Fungsi untuk memeriksa resolusi video
def get_video_resolution(url):
    response = check_channel(url)
    if response:
        content = response.content
        # Simplified resolution check for demonstration purposes
        if b'resolution="1920x1080"' in content or b'1920x1080' in content:
            return "FHD"
        elif b'resolution="1280x720"' in content or b'1280x720' in content:
            return "HD"
        elif b'resolution="640x360"' in content or b'640x360' in content:
            return "SD"
        else:
            return "Unknown"
    return "Unavailable"

# Membaca file playlist
input_file_path = "C:\\Users\\Admin\\Downloads\\Playlist Novan.txt"
output_file_path = "C:\\Users\\Admin\\Downloads\\sorterfixed.txt"

# Menggunakan encoding utf-8 atau latin-1 untuk membaca file
try:
    with open(input_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
except UnicodeDecodeError:
    with open(input_file_path, "r", encoding="latin-1") as file:
        lines = file.readlines()

# Fungsi untuk memproses setiap channel
def process_channel(channel_lines):
    url = channel_lines[0].strip()
    response = check_channel(url)
    if response:
        resolution = get_video_resolution(url)
        # Jika resolusi bukan "Unavailable" atau "Unknown", tambahkan informasi resolusi pada nama channel
        if resolution not in ["Unavailable", "Unknown"]:
            for i, line in enumerate(channel_lines):
                if line.startswith("#EXTINF"):
                    channel_lines[i] = line.strip() + f" [{resolution}]\n"
        return channel_lines
    return None

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

# Memproses channel secara paralel
valid_channels = []
with tqdm(total=len(channels), desc="Processing channels") as pbar:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_channel, channel): channel for channel in channels}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_channels.extend(result)
            pbar.update(1)  # Update progress bar for each completed channel

# Menyimpan channel yang valid ke file baru
with open(output_file_path, "w", encoding="utf-8") as file:
    file.writelines(valid_channels)

print(f"Proses selesai. File disimpan di {output_file_path}")
