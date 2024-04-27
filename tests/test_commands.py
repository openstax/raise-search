import pytest
from raise_search.commands import delete_index, create_index, index_content, cat_indices
from opensearchpy.exceptions import ConnectionTimeout


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


def test_cat_indices_main(mock_opensearch_client, mocker):
    mocker.patch(
        "raise_search.commands.cat_indices.get_opensearch_client",
        lambda: mock_opensearch_client,
    )

    cat_indices.main()

    mock_opensearch_client.cat.indices.assert_called_once_with(v=True)


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


def test_index_item_timeout_main(mock_opensearch_client, mocker, tmp_path):
    mock_opensearch_client.index.side_effect = [
        {},
        ConnectionTimeout("Mock timeout"),
        {},
    ]

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
    assert mock_opensearch_client.index.call_count == 3
    assert mock_opensearch_client.index.call_args_list[0].kwargs["id"] == "1"
    assert mock_opensearch_client.index.call_args_list[1].kwargs["id"] == "2"
    assert mock_opensearch_client.index.call_args_list[2].kwargs["id"] == "2"


def test_index_item_max_retries_main(mock_opensearch_client, mocker, tmp_path):
    mock_opensearch_client.index.side_effect = ConnectionTimeout("Mock timeout")

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

    with pytest.raises(ConnectionTimeout):
        index_content.main()

    mock_opensearch_client.index.assert_called()
    assert mock_opensearch_client.index.call_count == index_content.MAX_RETRY_COUNT
    for call in mock_opensearch_client.index.call_args_list:
        assert call.kwargs["id"] == "1"
