import requests

BASE_URL = "https://opendata.com.pk/api/3/action"


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
    response = requests.get(f"{BASE_URL}/package_search", params={"q": query, "rows": rows})
    response.raise_for_status()
    data = response.json()["result"]
    return [_parse_package_summary(pkg) for pkg in data["results"]]


def browse_by_category(category: str, rows: int = 10) -> list[dict]:
    """Browse datasets by category (CKAN tag). Returns a list of dataset summaries."""
    response = requests.get(f"{BASE_URL}/package_search", params={
        "fq": f"tags:{category}",
        "rows": rows,
    })
    response.raise_for_status()
    data = response.json()["result"]
    return [_parse_package_summary(pkg) for pkg in data["results"]]


def get_dataset_details(name: str) -> dict:
    """
    Get full details of a single dataset by its name/id, including download links.
    Raises ValueError if the dataset doesn't exist.
    """
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

    return {
        "title": pkg["title"],
        "description": pkg.get("notes") or "No description available.",
        "organization": pkg["organization"]["title"] if pkg.get("organization") else "Unknown",
        "last_updated": pkg.get("metadata_modified"),
        "resources": resources,
    }


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