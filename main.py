from concurrent.futures import ThreadPoolExecutor, as_completed
import requests, pathlib, tempfile, json, time, re

class UserBeatmaps:
    BASE_URL = 'https://osu.ppy.sh/users'
    
    def __init__(self, user: str):
        self.user = user if user.isdigit() else self.parse_user(user)
        self.beatmaps = self.fetch_beatmaps()

    def parse_user(self, user) -> str:
        url = f'https://osu.ppy.sh/users/{user}'
        r = requests.get(url, allow_redirects=False)
        pattern = r'Redirecting to https://osu\.ppy\.sh/users/(\d+)'
        match = re.search(pattern, r.text).group(1)
        return match
    
    def fetch_beatmaps(self) -> list:
        count = self.get_play_counts()
        beatmaps = self.get_beatmaps(count)
        return beatmaps
    
    def get_play_counts(self) -> int:
        url = f'{self.BASE_URL}/{self.user}/extra-pages/historical?mode=osu'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            count = data['beatmap_playcounts']['count']
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            print(f"Error fetching play counts: {e}")
            count = 0
        return count

    def get_beatmaps(self, count: int) -> list:
        beatmaps = []
        seen_ids = set()

        for offset in range(0, count, 100):
            url = f'{self.BASE_URL}/{self.user}/beatmapsets/most_played?limit=100&offset={offset}'
            try:
                print(f'Remaining Beatmaps to extract: {count-offset}')
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for beatmap in data:
                    beatmap_id = beatmap['beatmap']['beatmapset_id']
                    if beatmap_id and beatmap_id not in seen_ids:
                        seen_ids.add(beatmap_id)
                        beatmaps.append(beatmap)
                time.sleep(1)
            except (requests.RequestException, json.JSONDecodeError) as e:
                print(f"Error fetching beatmaps at offset {offset}: {e}")
                break
        return beatmaps
    
class Downloader:
    def __init__(self, beatmaps: list, path: str):
        self.beatmaps = beatmaps
        self.path = path
    
    def run(self) -> None:
        beatmaps = {
            beatmap['beatmap']['beatmapset_id']:
            beatmap['beatmapset']['title']
            for beatmap in self.beatmaps
        }
        self.download_beatmaps(beatmaps, self.path)

    def sanitize_filename(self, filename: str) -> str:
        forbidden_chars = '<>:"/\\|?*'
        return ''.join(c for c in filename if c not in forbidden_chars)

    def download_beatmap(self, id: str, title: str, path: str, mirrors: list) -> str:
        name_osz = f'{id} - {title}.osz'
        filename = path.joinpath(self.sanitize_filename(name_osz))
        if not pathlib.Path.exists(path):
            pathlib.Path(path).mkdir()
        if filename.exists():
            return None
        for m in mirrors:
            url = mirrors[m].format(id)
            try:
                response = requests.get(url, stream=True)
            except requests.exceptions.ConnectionError:
                continue
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    for data in response.iter_content(chunk_size=1024):
                        file.write(data)
                if filename.exists():
                    print(f"Downloaded {id} - {title}")
                    return filename
                break
        return None

    def download_beatmaps(self, beatmaps: list, path: str) -> list:
        downloaded = []
        mirrors = {
            "nerinyan.moe": "https://api.nerinyan.moe/d/{}",
            "beatconnect.io": "https://beatconnect.io/b/{}",
            "catboy.best": "https://catboy.best/d/{}",
            "osu.direct": "https://osu.direct/api/d/{}",
        }
        if not path:
            temp_dir = tempfile.TemporaryDirectory()
            print("Using temporary directory {}".format(temp_dir.name))
            path = pathlib.Path(temp_dir.name)
        else:
            path = pathlib.Path(path)

        print('Downloading beatmaps...')
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {
                executor.submit(self.download_beatmap, id, title, path, mirrors): (id, title)
                for id, title in beatmaps.items()
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    downloaded.append(result)
        print("Finished downloading!")
        return downloaded

def main():
    user = input("Enter Username/ID: ")
    start_time = time.time()
    user = UserBeatmaps(user)
    beatmaps = user.beatmaps
    download = Downloader(beatmaps, 'downloads')
    download.run()
    print(time.time() - start_time)

if __name__ == "__main__":
    main()