import requests

BASE_URL = "https://opendata.com.pk/api/3/action"


def search_datasets(query: str, rows: int = 10) -> list[dict]:
    """
    Search datasets by keyword.
    Returns a list of dicts with: title, name, description, organization, formats.
    """
    response = requests.get(f"{BASE_URL}/package_search", params={"q": query, "rows": rows})
    response.raise_for_status()
    data = response.json()["result"]

    results = []
    for pkg in data["results"]:
        results.append({
            "title": pkg["title"],
            "name": pkg["name"],
            "description": (pkg.get("notes") or "")[:300],
            "organization": pkg["organization"]["title"] if pkg.get("organization") else "Unknown",
            "formats": list({res["format"] for res in pkg["resources"] if res.get("format")}),
        })
    return results

def get_dataset_details(name: str) -> dict:
    """
    Get full details of a single dataset by its name/id.
    Returns dict with: title, description, organization, last_updated, resources (list of files with name/format/url).
    Raises an exception if the dataset doesn't exist.
    """
    response = requests.get(f"{BASE_URL}/package_show", params={"id": name})

    if response.status_code == 404:
        raise ValueError(f"Dataset '{name}' not found.")
    response.raise_for_status()

    pkg = response.json()["result"]

    resources = []
    for res in pkg["resources"]:
        resources.append({
            "name": res.get("name") or "Unnamed file",
            "format": res.get("format") or "Unknown",
            "url": res.get("url"),
        })

    return {
        "title": pkg["title"],
        "description": pkg.get("notes") or "No description available.",
        "organization": pkg["organization"]["title"] if pkg.get("organization") else "Unknown",
        "last_updated": pkg.get("metadata_modified"),
        "resources": resources,
    }

if __name__ == "__main__":
    # test search_datasets
    results = search_datasets("education", rows=5)
    for r in results:
        print(r["title"], "-", r["organization"], "-", r["formats"])

    # test get_dataset_details
    print("\n--- DETAILS ---")
    details = get_dataset_details("hies-data-2024-25")
    print("Title:", details["title"])
    print("Last updated:", details["last_updated"])
    print("Organization:", details["organization"])
    for res in details["resources"]:
        print(" -", res["name"], "|", res["format"], "|", res["url"])