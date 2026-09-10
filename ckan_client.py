import time
import requests

BASE_URL = "https://opendata.com.pk/api/3/action"

# --- Simple TTL cache ---
_cache: dict[str, tuple[float, object]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_get(key: str):
    """Return cached value if present and not expired, else None."""
    if key in _cache:
        timestamp, value = _cache[key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return value
        del _cache[key]  # expired, clean it up
    return None


def _cache_set(key: str, value):
    _cache[key] = (time.time(), value)


def _parse_package_summary(pkg: dict) -> dict:
    """Shared helper: turns a raw CKAN package dict into our clean summary shape."""
    return {
        "title": pkg["title"],
        "name": pkg["name"],
        "description": (pkg.get("notes") or "")[:300],
        "organization": pkg["organization"]["title"] if pkg.get("organization") else "Unknown",
        "formats": list({res["format"] for res in pkg["resources"] if res.get("format")}),
    }


def search_datasets(query: str, rows: int = 10) -> list[dict]:
    """Search datasets by keyword. Returns a list of dataset summaries."""
    cache_key = f"search:{query}:{rows}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(f"{BASE_URL}/package_search", params={"q": query, "rows": rows})
    response.raise_for_status()
    data = response.json()["result"]
    result = [_parse_package_summary(pkg) for pkg in data["results"]]

    _cache_set(cache_key, result)
    return result


def browse_by_category(category: str, rows: int = 10) -> list[dict]:
    """Browse datasets by category (CKAN tag). Returns a list of dataset summaries."""
    cache_key = f"category:{category}:{rows}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(f"{BASE_URL}/package_search", params={
        "fq": f"tags:{category}",
        "rows": rows,
    })
    response.raise_for_status()
    data = response.json()["result"]
    result = [_parse_package_summary(pkg) for pkg in data["results"]]

    _cache_set(cache_key, result)
    return result


def get_dataset_details(name: str) -> dict:
    """
    Get full details of a single dataset by its name/id, including download links.
    Raises ValueError if the dataset doesn't exist.
    """
    cache_key = f"details:{name}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(f"{BASE_URL}/package_show", params={"id": name})

    if response.status_code == 404:
        raise ValueError(f"Dataset '{name}' not found.")
    response.raise_for_status()

    pkg = response.json()["result"]

    resources = [
        {
            "name": res.get("name") or "Unnamed file",
            "format": res.get("format") or "Unknown",
            "url": res.get("url"),
        }
        for res in pkg["resources"]
    ]

    result = {
        "title": pkg["title"],
        "description": pkg.get("notes") or "No description available.",
        "organization": pkg["organization"]["title"] if pkg.get("organization") else "Unknown",
        "last_updated": pkg.get("metadata_modified"),
        "resources": resources,
    }

    _cache_set(cache_key, result)
    return result


if __name__ == "__main__":
    results = search_datasets("education", rows=5)
    for r in results:
        print(r["title"], "-", r["organization"], "-", r["formats"])

    print("\n--- DETAILS ---")
    details = get_dataset_details("hies-data-2024-25")
    print("Title:", details["title"])
    print("Last updated:", details["last_updated"])
    print("Organization:", details["organization"])
    for res in details["resources"]:
        print(" -", res["name"], "|", res["format"], "|", res["url"])

    print("\n--- CATEGORY: health ---")
    category_results = browse_by_category("health", rows=5)
    for r in category_results:
        print(r["title"], "-", r["organization"])

    print("\n--- ERROR TEST: fake dataset ---")
    try:
        get_dataset_details("this-does-not-exist-12345")
    except ValueError as e:
        print("Caught expected error:", e)

    print("\n--- ERROR TEST: nonsense search ---")
    empty_results = search_datasets("asdkjhaskjdhaksjdh")
    print("Results found:", len(empty_results))

    print("\n--- CACHE TEST: repeat search should be instant ---")
    start = time.time()
    search_datasets("education", rows=5)
    print(f"Second identical call took {time.time() - start:.4f}s (should be ~0)")