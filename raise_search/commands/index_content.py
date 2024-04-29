import argparse
import csv
from raise_search.api.utils import get_opensearch_client
from pathlib import Path
from bs4 import BeautifulSoup
from opensearchpy.exceptions import ConnectionTimeout


MAX_RETRY_COUNT = 10


def index_content(index, toc_csv_path, html_directory):
    client = get_opensearch_client()

    with toc_csv_path.open() as csv_file:
        items = csv.DictReader(csv_file)
        for item in items:
            index_item(item, index, html_directory, client)


def index_item(item, index, html_directory, client):
    html_content = (
        Path(f"{html_directory}/{item['content_id']}.html")
        .resolve(strict=True)
        .read_text()
    )
    soup = BeautifulSoup(html_content, "html.parser")

    doc = {
        "content_id": item["content_id"],
        "section": item["section"],
        "activity_name": item["activity_name"],
        "lesson_page": item["lesson_page"],
        "lesson_page_type": item["lesson_page_type"],
        "teacher_only": item["visible"] == "0",
        "visible_content": soup.get_text(),
    }

    doc_id = doc["content_id"]

    for attempt in range(1, MAX_RETRY_COUNT + 1):
        try:
            client.index(
                index=index,
                body=doc,
                id=doc_id,
                refresh=True,
            )
            break
        except ConnectionTimeout:
            if attempt < MAX_RETRY_COUNT:
                print(f"Timeout {attempt} for ID {doc_id}...retrying")
                continue
            else:
                print(f"Timeout {attempt} for ID {doc_id}...giving up")
                raise


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "index",
        type=str,
        help="opensearch index name",
    )
    parser.add_argument(
        "toc_csv_path",
        type=str,
        help="path to toc csv",
    )
    parser.add_argument(
        "html_directory",
        type=str,
        help="path to html directory",
    )

    args = parser.parse_args()
    toc_csv_path = Path(args.toc_csv_path).resolve(strict=True)
    html_directory = Path(args.html_directory).resolve(strict=True)
    index = args.index
    index_content(index, toc_csv_path, html_directory)


if __name__ == "__main__":  # pragma: no cover
    main()
