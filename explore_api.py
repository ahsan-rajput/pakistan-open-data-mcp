import requests
import json

BASE_URL = "https://opendata.com.pk/api/3/action"

# 1. Confirm the site is reachable and is CKAN
response = requests.get(f"{BASE_URL}/status_show")
print("Status code:", response.status_code)
print(json.dumps(response.json(), indent=2))

# 2. Search for datasets matching a keyword
print("\n--- SEARCH: 'health' ---")
response = requests.get(f"{BASE_URL}/package_search", params={"q": "health", "rows": 3})
data = response.json()
print("Number of results found:", data["result"]["count"])

for pkg in data["result"]["results"]:
    print("\nTitle:", pkg["title"])
    print("Name (id):", pkg["name"])
    print("Notes:", (pkg.get("notes") or "")[:150])
    print("Organization:", pkg["organization"]["title"] if pkg.get("organization") else None)
    print("Formats:", list({res["format"] for res in pkg["resources"]}))


# 3. Get full details of ONE specific dataset (using the "name" id we saw above)
print("\n--- PACKAGE_SHOW: 'hies-data-2024-25' ---")
response = requests.get(f"{BASE_URL}/package_show", params={"id": "hies-data-2024-25"})
data = response.json()["result"]

print("Title:", data["title"])
print("Last modified:", data.get("metadata_modified"))
print("Organization:", data["organization"]["title"])
print("\nResources (downloadable files):")
for res in data["resources"]:
    print(f"  - Name: {res.get('name')}")
    print(f"    Format: {res.get('format')}")
    print(f"    URL: {res.get('url')}")

# 4. Check if "groups" (categories) exist on this portal
print("\n--- GROUP_LIST (categories) ---")
response = requests.get(f"{BASE_URL}/group_list")
print(json.dumps(response.json(), indent=2))