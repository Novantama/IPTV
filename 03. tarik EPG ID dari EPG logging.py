import requests
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_standard_tvg_ids(epg_url, timeout=30):
    try:
        response = requests.get(epg_url, timeout=timeout)
        response.raise_for_status()
        epg_data = response.text
        tvg_ids = {}
        for match in re.finditer(r'<channel id="([^"]+)">\s*<display-name>([^<]+)</display-name>', epg_data):
            tvg_id = match.group(1).strip()
            display_name = match.group(2).strip().lower()
            tvg_ids[display_name] = tvg_id
        return tvg_ids
    except requests.RequestException as e:
        logging.error(f"Error fetching standard tvg-ids from {epg_url}: {e}")
        return {}

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def clean_channel_name(name):
    return re.sub(r'\s*\([^)]*\)', '', name).strip().lower()

def update_tvg_ids(entries, tvg_ids, similarity_threshold=0.80):
    updated_entries = []
    unmatched_entries = []

    logging.info("Updating tvg-ids...")
    for entry in tqdm(entries, desc="Processing entries"):
        match = re.search(r'#EXTINF[^,]*,(.*)', entry[0])
        if match:
            channel_name = clean_channel_name(match.group(1).strip())
            best_match = None
            best_similarity = 0

            for name in tvg_ids:
                similarity = similar(channel_name, name)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = name

            if best_match and best_similarity >= similarity_threshold:
                tvg_id = tvg_ids[best_match]
                if 'tvg-id="' in entry[0]:
                    entry[0] = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{tvg_id}"', entry[0])
                else:
                    entry[0] = entry[0].strip() + f' tvg-id="{tvg_id}"'
            else:
                unmatched_entries.append((channel_name, best_match, best_similarity))
        
        updated_entries.append(entry)

    return updated_entries, unmatched_entries

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
        elif line.strip():
            entry.append(line)

    if entry:
        entries.append(entry)

    return entries

def write_playlist(file_path, entries, unmatched_entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            for line in entry:
                file.write(line)
            file.write('\n')  # Ensure there is a single newline after each

        if unmatched_entries:
            file.write("\n# Unmatched Channels:\n")
            unmatched_entries.sort(key=lambda x: -x[2])  # Sort by similarity in descending order
            for channel_name, best_match, similarity in unmatched_entries:
                if similarity > 0.75:
                    file.write(f"# Channel: {channel_name}, Best Match: {best_match}, Similarity: {similarity:.2f}\n")

def main():
    input_path = r'C:\\Users\\Admin\\Downloads\\IPTV\\Output Playlist.txt'
    output_path = r'C:\\Users\\Admin\\Downloads\\IPTV\\Output EPG.txt'
    epg_urls = [
    "https://www.bevy.be/bevyfiles/indonesia.xml",
    "https://www.bevy.be/bevyfiles/indonesiapremium1.xml",
    "https://www.bevy.be/bevyfiles/indonesiapremium2.xml",
    "https://www.bevy.be/bevyfiles/indonesiapremium3.xml",
    "https://www.bevy.be/bevyfiles/indonesiapremium4.xml",
    "https://www.bevy.be/bevyfiles/malaysia.xml",
    "https://www.bevy.be/bevyfiles/malaysiapremium1.xml",
    "https://www.bevy.be/bevyfiles/malaysiapremium2.xml",
    "https://s.urfan.web.id/epgxmlgz",
    #"https://i.mjh.nz/all/epg.xml",
    #"https://i.mjh.nz/PlutoTV/all.xml",
    #"https://i.mjh.nz/SamsungTVPlus/all.xml",
    #"https://epg.ninja/epg/MISC/AUSoptus.xml",
    "https://www.bevy.be/bevyfiles/singaporepremium.xml",
    "https://www.bevy.be/bevyfiles/sportspremium1.xml",
    "https://www.bevy.be/bevyfiles/sportspremium2.xml",
    "https://www.bevy.be/bevyfiles/sportspremium3.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdom.xml",
    "https://www.bevy.be/bevyfiles/unitedkingdompremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedstates.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium1.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium2.xml",
    "https://www.bevy.be/bevyfiles/unitedstatespremium3.xml",
    #"https://raw.githubusercontent.com/azimabid00/epg/main/unifi_epg.xml",
    #"https://raw.githubusercontent.com/AqFad2811/epg/main/singapore.xml",
    #"https://raw.githubusercontent.com/azimabid00/epg/main/astro_epg.xml",
    #"https://www.bevy.be/bevyfiles/portugal.xml",
    #"https://raw.githubusercontent.com/Newbiect/epg/master/guide.xml",
    #"https://www.bevy.be/bevyfiles/unitedstatespremium4.xml",
    #"https://raw.githubusercontent.com/luizoliveira1970/epg/main/epg_ripper_BR1.xml",
    #"https://raw.githubusercontent.com/joao1967/epg/main/guide.xml",
    #"https://www.bevy.be/bevyfiles/norway.xml",
    #"https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SkyGo/epg.xml",
    #"https://www.bevy.be/bevyfiles/switzerland.xml",
    #"https://raw.githubusercontent.com/soju6jan/epg2/main/file/xmltv_all2.xml",
    #"https://raw.githubusercontent.com/Nomenteros/Nomentero_Epg/master/Nomenteroguide.xml",
    #"https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/SkySportNow/epg.xml",
    #"https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/DStv/za.xml",
    #"https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/PlutoTV/us.xml",
    #"https://raw.githubusercontent.com/skutyborsuk/IPTV/master/epg_v5.xml",
    #"https://epgtvku.000webhostapp.com/EPG/oxygen/VTV.xml",
    #"https://raw.githubusercontent.com/bebawy6/EPG/master/arEPG.xml",
    #"https://www.bevy.be/bevyfiles/arabia.xml",
    #"https://www.bevy.be/bevyfiles/arabiapremiumar.xml",
    #"https://www.bevy.be/bevyfiles/arabiapremiumeng.xml",
    #"https://www.bevy.be/bevyfiles/arabiapremium2.xml",
    #"https://www.bevy.be/bevyfiles/australia.xml",
    #"https://www.bevy.be/bevyfiles/australiapremium.xml",
    #"https://www.bevy.be/bevyfiles/brazil.xml",
    #"https://www.bevy.be/bevyfiles/bulgaria.xml",
    #"https://www.bevy.be/bevyfiles/canada.xml",
    #"https://www.bevy.be/bevyfiles/canadapremium.xml",
    #"https://www.bevy.be/bevyfiles/china.xml",
    #"https://www.bevy.be/bevyfiles/chinapremium.xml",
    #"https://www.bevy.be/bevyfiles/chinapremium1.xml",
    #"https://www.bevy.be/bevyfiles/chinapremium2.xml",
    #"https://www.bevy.be/bevyfiles/france.xml",
    #"https://www.bevy.be/bevyfiles/germanypremium.xml",
    #"https://www.bevy.be/bevyfiles/germanypremium2.xml",
    #"https://www.bevy.be/bevyfiles/hongkong.xml",
    #"https://www.bevy.be/bevyfiles/hongkongpremium.xml",
    #"https://www.bevy.be/bevyfiles/hongkongpremium2.xml",
    #"https://www.bevy.be/bevyfiles/india.xml",
    #"https://www.bevy.be/bevyfiles/indiapremium1.xml",
    #"https://www.bevy.be/bevyfiles/indiapremium2.xml",
    #"https://www.bevy.be/bevyfiles/indiapremium3.xml",
    #"https://www.bevy.be/bevyfiles/indiapremium4.xml",
    #"https://www.bevy.be/bevyfiles/indiapremium5.xml",
    #"https://www.bevy.be/bevyfiles/ireland.xml",
    #"https://www.bevy.be/bevyfiles/irelandpremium.xml",
    #"https://www.bevy.be/bevyfiles/italy.xml",
    #"https://www.bevy.be/bevyfiles/italypremium.xml",
    #"https://www.bevy.be/bevyfiles/italypremium2.xml",
    #"https://www.bevy.be/bevyfiles/japan.xml",
    #"https://www.bevy.be/bevyfiles/korea.xml",
    #"https://www.bevy.be/bevyfiles/koreapremium.xml",
    #"https://www.bevy.be/bevyfiles/macaupremium.xml",
    #"https://www.bevy.be/bevyfiles/mexico.xml",
    #"https://www.bevy.be/bevyfiles/mexicopremium.xml",
    #"https://www.bevy.be/bevyfiles/netherlands.xml",
    #"https://www.bevy.be/bevyfiles/netherlandspremium.xml",
    #"https://www.bevy.be/bevyfiles/philippinespremium.xml",
    #"https://www.bevy.be/bevyfiles/poland.xml",
    #"https://www.bevy.be/bevyfiles/qatar.xml",
    #"https://www.bevy.be/bevyfiles/romania.xml",
    #"https://www.bevy.be/bevyfiles/russia.xml",
    #"https://www.bevy.be/bevyfiles/russiapremium1.xml",
    #"https://www.bevy.be/bevyfiles/serbia.xml",
    #"https://www.bevy.be/bevyfiles/serbiapremium.xml",
    #"https://www.bevy.be/bevyfiles/southafrica.xml",
    #"https://www.bevy.be/bevyfiles/southafricapremium.xml",
    #"https://www.bevy.be/bevyfiles/spain.xml",
    #"https://www.bevy.be/bevyfiles/sweden.xml",
    #"https://www.bevy.be/bevyfiles/taiwanpremium.xml",
    #"https://www.bevy.be/bevyfiles/thailand.xml",
    #"https://www.bevy.be/bevyfiles/thailandpremium.xml",
    #"https://www.bevy.be/bevyfiles/turkey.xml",
    #"https://www.bevy.be/bevyfiles/turkeypremium1.xml",
    #"https://www.bevy.be/bevyfiles/turkeypremium2.xml",
    #"https://www.bevy.be/bevyfiles/uae.xml",
    #"https://www.bevy.be/bevyfiles/uaepremium1.xml",
    #"https://www.bevy.be/bevyfiles/vietnam.xml",
    #"https://raw.githubusercontent.com/AqFad2811/epg/main/starhubtv.xml",
    #"https://www.bevy.be/bevyfiles/denmark.xml",
    #"https://www.bevy.be/bevyfiles/argentina.xml",
    #"https://www.bevy.be/bevyfiles/chile.xml",
    #"https://www.bevy.be/bevyfiles/belgium.xml",
    #"https://www.bevy.be/bevyfiles/belgiumpremium.xml"
    ]

    logging.info("Parsing playlist...")
    entries = parse_playlist(input_path)

    logging.info("Fetching standard tvg-ids from multiple EPG sources...")
    with ThreadPoolExecutor(max_workers=100) as executor:  # Adjusted max_workers
        future_to_url = {executor.submit(fetch_standard_tvg_ids, url): url for url in epg_urls}
        tvg_ids = {}
        for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc="Fetching EPG data"):
            url = future_to_url[future]
            try:
                result = future.result()
                tvg_ids.update(result)
            except Exception as e:
                logging.error(f"Error fetching tvg-ids from {url}: {e}")

    entries, unmatched_entries = update_tvg_ids(entries, tvg_ids)

    logging.info("Writing updated playlist...")
    write_playlist(output_path, entries, unmatched_entries)

    logging.info("Process completed.")

if __name__ == '__main__':
    main()
