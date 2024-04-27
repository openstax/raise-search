import pytest
from raise_search.commands import delete_index
from raise_search.commands import create_index
from raise_search.commands import index_content


@pytest.fixture
def mock_opensearch_client(mocker):
    mock_client = mocker.MagicMock()
    return mock_client


def test_create_index_main(mock_opensearch_client, mocker):
    mocker.patch(
        "raise_search.commands.create_index.get_opensearch_client",
        lambda: mock_opensearch_client,
    )
    mocker.patch("sys.argv", ["", "test_index_name"])
    create_index.main()
    body = {"settings": {"index": {"number_of_shards": 1, "number_of_replicas": 1}}}
    mock_opensearch_client.indices.create.assert_called_once_with(
        "test_index_name", body=body
    )


def test_delete_index_main(mock_opensearch_client, mocker):
    mocker.patch(
        "raise_search.commands.delete_index.get_opensearch_client",
        lambda: mock_opensearch_client,
    )

    mocker.patch("sys.argv", ["", "test_index_name"])
    delete_index.main()

    mock_opensearch_client.indices.delete.assert_called_once_with("test_index_name")


def test_index_item_main(mock_opensearch_client, mocker, tmp_path):
    mocker.patch(
        "raise_search.commands.index_content.get_opensearch_client",
        lambda: mock_opensearch_client,
    )

    toc_csv_content = (
        "content_id,section,activity_name,lesson_page,lesson_page_type,visible\n"
        "1,Section A,Activity 1,Page 1,Type 1,1\n"
        "2,Section A,Activity 2,Page 2,Type 1,1"
    )
    html_file_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"

    toc_csv_path = tmp_path / "test_toc.csv"
    toc_csv_path.write_text(toc_csv_content)

    html_directory = tmp_path / "html_files"
    html_directory.mkdir()

    html_file_path = html_directory / "1.html"
    html_file_path.write_text(html_file_content)
    html_file_path = html_directory / "2.html"
    html_file_path.write_text(html_file_content)

    mocker.patch(
        "sys.argv", ["", "test_index_name", str(toc_csv_path), str(html_directory)]
    )

    index_content.main()

    mock_opensearch_client.index.assert_called()
    assert mock_opensearch_client.index.call_count == 2
