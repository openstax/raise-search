import argparse
from raise_search.api.utils import get_opensearch_client


def create_index(index_name):
    client = get_opensearch_client()

    index_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }
    }

    client.indices.create(index_name, body=index_body)


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "index_name", type=str,
        help="opensearch index name")

    args = parser.parse_args()
    index_name = args.index_name
    create_index(index_name)


if __name__ == "__main__":  # pragma: no cover
    main()
