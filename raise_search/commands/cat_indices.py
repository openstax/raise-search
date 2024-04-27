from raise_search.api.utils import get_opensearch_client


def main():
    client = get_opensearch_client()
    print(client.cat.indices(v=True))


if __name__ == "__main__":  # pragma: no cover
    main()
