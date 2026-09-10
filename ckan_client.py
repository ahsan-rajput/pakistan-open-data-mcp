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


if __name__ == "__main__":
    # quick manual test
    results = search_datasets("education", rows=5)
    for r in results:
        print(r["title"], "-", r["organization"], "-", r["formats"])