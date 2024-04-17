import pytest
from fastapi.testclient import TestClient
from raise_search.api.main import app
from unittest.mock import MagicMock
from raise_search.api.utils import get_opensearch_client
client = TestClient(app)


def create_mock_response():
    mock_response = {
        "took": 5,
        "timed_out": False,
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_index": "test-index2",
                    "_id": "1",
                    "_score": 0.5,
                    "_source": {
                        "content_id": "1",
                        "section": "section1",
                        "activity_name": "Activity 1",
                        "lesson_page": "page1",
                        "lesson_page_type": "type1",
                        "teacher_only": True,
                        "visible_content": ["ahahha"]
                    },
                    "highlight": {
                        "visible_content": ["text"],
                        "lesson_page": ["page"],
                        "activity_name": ["activity"],
                    },
                },
            ],
            "max_score": 1.0,
        },
    }
    return mock_response


@pytest.fixture
def mock_opensearch_client():
    mock_client = MagicMock()
    mock_response = create_mock_response()
    mock_client.search.return_value = mock_response
    return mock_client


def test_search_v1(mock_opensearch_client):
    client = TestClient(app)

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "test query"
    test_version = "1"
    test_filter = "teacher"

    response = client.get(
        f"/v1/search?q={test_query}&version={test_version}&filter={test_filter}"
    )

    assert response.status_code == 200

    mock_opensearch_client.search.assert_called_once_with(
        index="test-index2",
        body={
            "highlight": {
                "fields": {
                    "visible_content": {},
                    "lesson_page": {},
                    "activity_name": {},
                },
                "pre_tags": ["<strong>"],
                "post_tags": ["</strong>"],
            },
            "query": {
                "bool": {
                    "filter": {"term": {"teacher_only": True}},
                    "must": {
                        "simple_query_string": {
                            "query": test_query,
                            "fields": ["visible_content", "lesson_page",
                                       "activity_name"],
                            "default_operator": "AND",
                        }
                    },
                }
            },
            "size": 100,
        },
    )


def test_search_v1_no_filter(mock_opensearch_client):
    client = TestClient(app)

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "test query"
    test_version = "1"

    response = client.get(
        f"/v1/search?q={test_query}&version={test_version}"
    )

    assert response.status_code == 200

    mock_opensearch_client.search.assert_called_once_with(
        index="test-index2",
        body={
            "highlight": {
                "fields": {
                    "visible_content": {},
                    "lesson_page": {},
                    "activity_name": {},
                },
                "pre_tags": ["<strong>"],
                "post_tags": ["</strong>"],
            },
            "query": {
                "simple_query_string": {
                    "query": test_query,
                    "fields": ["visible_content", "lesson_page", "activity_name"],
                    "default_operator": "AND",
                }
            },
            "size": 100,
        },
    )
