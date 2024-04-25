import argparse
from raise_search.api.utils import get_opensearch_client


def delete_index(index_name):
    client = get_opensearch_client()

    client.indices.delete(index_name)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "index_name", type=str,
        help="opensearch index name")

    args = parser.parse_args()
    index_name = args.index_name
    delete_index(index_name)


if __name__ == "__main__":  # pragma: no cover
    main()
