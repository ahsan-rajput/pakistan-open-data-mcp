import os
from mcp.server import MCPServer
from ckan_client import search_datasets, get_dataset_details, browse_by_category

mcp = MCPServer("Pakistan Open Data")


@mcp.tool()
def search_open_data(query: str, max_results: int = 10) -> list[dict]:
    """
    Search Pakistan's National Open Data Portal for datasets matching a keyword.

    Use this when the user wants to find data on a topic (e.g. "health", "floods",
    "trade", "education") but doesn't know the exact dataset name. Returns a list
    of matching datasets with title, description, publishing organization, and
    available file formats.
    """
    return search_datasets(query, rows=max_results)


@mcp.tool()
def get_dataset_info(dataset_name: str) -> dict:
    """
    Get full details of one specific dataset from Pakistan's Open Data Portal,
    including its description, publishing organization, when it was last updated,
    and a list of its downloadable files with direct URLs.

    Use this after search_open_data or browse_open_data_by_category has identified
    a dataset the user is interested in. The dataset_name should be the exact
    'name' (id) field from those results, not the display title.
    """
    return get_dataset_details(dataset_name)


@mcp.tool()
def browse_open_data_by_category(category: str, max_results: int = 10) -> list[dict]:
    """
    Browse datasets on Pakistan's Open Data Portal by category, such as
    health, education, economy, trade, employment, or population.

    Use this when the user wants an overview of what's available in a topic
    area rather than searching for a specific keyword.
    """
    return browse_by_category(category, rows=max_results)


@mcp.tool()
def get_download_links(dataset_name: str) -> list[dict]:
    """
    Get direct download URLs for a specific dataset's data files.

    Use this when the user has identified a dataset and specifically wants
    the actual file links to download the data, rather than a description.
    The dataset_name should be the exact 'name' (id) field from search or
    browse results.
    """
    details = get_dataset_details(dataset_name)
    return [
        {"file_name": r["name"], "format": r["format"], "url": r["url"]}
        for r in details["resources"]
    ]



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)