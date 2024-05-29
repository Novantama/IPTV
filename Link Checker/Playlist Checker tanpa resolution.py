import requests
from tqdm import tqdm

def is_channel_working(url, timeout=6):
    try:
        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def process_playlist(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    i = 0

    with tqdm(total=len(lines), desc="Processing Channels") as pbar:
        while i < len(lines):
            line = lines[i]
            if line.startswith('http://') or line.startswith('https://'):
                url = line.strip()
                if is_channel_working(url):
                    while i < len(lines) and not lines[i].strip() == '':
                        new_lines.append(lines[i])
                        i += 1
                else:
                    while i < len(lines) and not lines[i].strip() == '':
                        i += 1
            else:
                new_lines.append(line)
                i += 1
            pbar.update(1)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

if __name__ == "__main__":
    input_file = "C:\\Users\\Admin\\Downloads\\Playlist Novan.txt"
    output_file = "C:\\Users\\Admin\\Downloads\\sorterfixed.txt"
    process_playlist(input_file, output_file)
