from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from raise_search.api.settings import OPENSEARCH_HOST_ENDPOINT, AWS_REGION
import boto3


def get_opensearch_client():

    if AWS_REGION:
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, AWS_REGION, "es")

        client = OpenSearch(
            hosts=[{"host": OPENSEARCH_HOST_ENDPOINT, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=20,
            timeout=15,
        )
    else:
        port = 9200
        auth = ("admin", "admin")
        client = OpenSearch(
            hosts=[{"host": OPENSEARCH_HOST_ENDPOINT, "port": port}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
        )
    return client
