from opensearchpy import NotFoundError
import pytest
from fastapi.testclient import TestClient
from raise_search.api.main import app
from raise_search.api.utils import get_opensearch_client


@pytest.fixture
def test_client():
    return TestClient(app)


def create_mock_response():
    mock_response = {
        "took": 5,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 1, "relation": "eq"},
            "hits": [
                {
                    "_index": "content-1",
                    "_id": "1",
                    "_score": 0.5,
                    "_source": {
                        "content_id": "1",
                        "section": "section1",
                        "activity_name": "Activity 1",
                        "lesson_page": "page1",
                        "lesson_page_type": "type1",
                        "teacher_only": True,
                        "visible_content": ["content"],
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
def mock_opensearch_client(mocker):
    mock_client = mocker.MagicMock()
    mock_response = create_mock_response()
    mock_client.search.return_value = mock_response
    return mock_client


def test_search_v1(mock_opensearch_client, test_client):

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "test query"
    test_version = "1"

    response = test_client.get(f"/v1/search?q={test_query}&version={test_version}")
    data = response.json()

    assert "took" in data
    assert "timed_out" in data
    assert "_shards" in data
    assert "hits" in data

    hits = data["hits"]
    assert "total" in hits
    assert "hits" in hits

    total_hits = hits["total"]
    assert "value" in total_hits
    assert "relation" in total_hits

    assert "max_score" in hits

    first_hit = hits["hits"][0]
    assert "_index" in first_hit
    assert "_id" in first_hit
    assert "_score" in first_hit
    assert "_source" in first_hit
    assert "highlight" in first_hit

    highlight = first_hit["highlight"]
    assert "visible_content" in highlight
    assert "lesson_page" in highlight
    assert "activity_name" in highlight
    assert "text" in highlight["visible_content"]
    assert "page" in highlight["lesson_page"]
    assert "activity" in highlight["activity_name"]

    assert first_hit["_index"] == "content-1"
    assert first_hit["_id"] == "1"
    assert first_hit["_score"] == 0.5

    assert first_hit["_source"]["content_id"] == "1"
    assert first_hit["_source"]["section"] == "section1"
    assert first_hit["_source"]["activity_name"] == "Activity 1"

    assert response.status_code == 200
    mock_opensearch_client.search.assert_called_once_with(
        index="content-1",
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


def test_search_v1_filter_student(mock_opensearch_client, test_client):

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "test query"
    test_version = "1"
    test_filter = "student"

    response = test_client.get(
        f"/v1/search?q={test_query}&version={test_version}&filter={test_filter}"
    )
    assert response.status_code == 200

    mock_opensearch_client.search.assert_called_once_with(
        index="content-1",
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
                    "filter": {"term": {"teacher_only": False}},
                    "must": {
                        "simple_query_string": {
                            "query": test_query,
                            "fields": [
                                "visible_content",
                                "lesson_page",
                                "activity_name",
                            ],
                            "default_operator": "AND",
                        }
                    },
                }
            },
            "size": 100,
        },
    )


def test_search_v1_filter_teacher(mock_opensearch_client, test_client):

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "test query"
    test_version = "1"
    test_filter = "teacher"

    response = test_client.get(
        f"/v1/search?q={test_query}&version={test_version}&filter={test_filter}"
    )
    assert response.status_code == 200

    mock_opensearch_client.search.assert_called_once_with(
        index="content-1",
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
                            "fields": [
                                "visible_content",
                                "lesson_page",
                                "activity_name",
                            ],
                            "default_operator": "AND",
                        }
                    },
                }
            },
            "size": 100,
        },
    )


def test_search_v1_not_found_error(mock_opensearch_client, test_client):
    mock_opensearch_client.search.side_effect = NotFoundError

    app.dependency_overrides[get_opensearch_client] = lambda: mock_opensearch_client

    test_query = "query"
    test_version = "2"

    response = test_client.get(f"/v1/search?q={test_query}&version={test_version}")
    assert response.status_code == 404

    assert response.json()["detail"] == "Content version not found"

    mock_opensearch_client.search.assert_called_once()
