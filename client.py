import httpx
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()
SESSION_ID = os.getenv("POE_SESSION_ID")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")

headers = {
    "User-Agent": "testapp (contact: astepnio@gmail.com) -private test app not for public distribution",
    "Cookie": f"POESESSID={SESSION_ID}"
}

'''
CACHE FUNCTIONS

this program uses caching to avoid repeated calls to the poe api. 

caches .json data it pulls in {project directory}/cache/... [CACHE_DIR]
'''

def clear_cache():
    '''
    Delete all cached files from the cache folder
    '''
    if not os.path.exists(CACHE_DIR):
        return
    
    for file in os.listdir(CACHE_DIR):
        if file.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, file))
    
    print("Cache cleared")

def fetch_cached(key: str, fetch_fn, max_age_seconds: int = None):
    '''
    Generic cache function.
    
    key            - the filename to store the cache as e.g. "profile"
    fetch_fn       - the function to call if cache doesn't exist
    max_age_seconds - optionally expire the cache after this many seconds
    '''

    # create cache folder if it doesn't exist
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_file = os.path.join(CACHE_DIR, f"{key}.json")

    # if cache exists
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached = json.load(f)

        # check if cache has expired
        if max_age_seconds is not None:
            age = time.time() - cached["cached_at"]
            if age > max_age_seconds:
                print(f"Cache expired for {key}, fetching fresh data...")
                os.remove(cache_file)
            else:
                print(f"Using cached {key} ({int(age)}s old)")
                return cached["data"]
        else:
            print(f"Using cached {key}")
            return cached["data"]

    # fetch fresh data
    print(f"Fetching fresh {key}...")
    data = fetch_fn()

    # save to cache with a timestamp
    with open(cache_file, "w") as f:
        json.dump({"cached_at": time.time(), "data": data}, f, indent=2)

    return data

'''
API FUNCTIONS

make calls to poe api to retrieve data,
each function = one endpoint.

all requests are cached, and optionally automatically expire based on age
'''
def query_endpoint(endpoint: str):
    response = httpx.get(
        endpoint,
        headers=headers
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    profile = fetch_cached("profile", lambda: query_endpoint("https://api.pathofexile.com/profile"))   
    account_name = profile["name"]

    print(json.dumps(stashes, indent=2))