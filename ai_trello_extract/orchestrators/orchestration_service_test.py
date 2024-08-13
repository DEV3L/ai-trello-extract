import os
from unittest.mock import MagicMock, patch

from trello import Board

from ai_trello_extract.dataclasses.categorized_list import CategorizedLists
from ai_trello_extract.dataclasses.trello_card import TrelloCard
from ai_trello_extract.orchestrators.orchestration_service import OrchestrationService
from ai_trello_extract.services.trello_service import TrelloService


def test_get_board_markdown(mock_board: Board, trello_card: TrelloCard):
    """
    Test that get_board_markdown correctly generates markdown for a Trello board.
    """
    expected_markdown = """# TODO

This is a list of cards, work items, user stories, and tasks that are in the todo category.

## Title: Title

## List Name: To Do

## Labels

- Label1
- Label2

## Done Date: 2024-01-01 00:00:00

## Description

Test card description

### Comments

Test comment
"""

    # Mock the TrelloService to return predefined values
    mock_trello_service = MagicMock(spec=TrelloService)
    mock_trello_service.get_board_by_name.return_value = mock_board
    mock_trello_service.extract_cards_info.return_value = CategorizedLists(todo=[trello_card])

    # Initialize the OrchestrationService with the mocked TrelloService
    orchestration_service = OrchestrationService(mock_trello_service)
    markdown = orchestration_service.get_board_markdown("Test Board")

    # Verify that the generated markdown matches the expected output
    assert markdown == expected_markdown

    # Ensure the TrelloService methods were called with the correct arguments
    mock_trello_service.get_board_by_name.assert_called_once_with("Test Board")
    mock_trello_service.extract_cards_info.assert_called_once_with(mock_trello_service.get_board_by_name.return_value)


@patch("ai_trello_extract.orchestrators.orchestration_service.generate_markdown")
def test_write_board_markdown_to_file(mock_generate_markdown, tmpdir):
    """
    Test that write_board_markdown_to_file correctly writes markdown to a file.
    """
    mock_generate_markdown.return_value = "# Mock Markdown Content"

    # Mock the TrelloService to return predefined values
    mock_trello_service = MagicMock(spec=TrelloService)
    mock_trello_service.get_board_by_name.return_value = "mock_board"
    mock_trello_service.extract_cards_info.return_value = "mock_cards_info"

    # Initialize the OrchestrationService with the mocked TrelloService
    orchestration_service = OrchestrationService(trello_service=mock_trello_service)

    board_name = "TestBoard"
    directory = tmpdir.mkdir("markdown_files")
    file_path = os.path.join(directory, f"{board_name} Status Trello Board.txt")

    # Call the method to write markdown to a file
    result_path = orchestration_service.write_board_markdown_to_file(board_name, str(directory))

    # Verify that the file path is correct and the content matches the expected output
    assert result_path == file_path
    with open(result_path, "r") as file:
        content = file.read()
    assert content == "# Mock Markdown Content"


def test_write_board_json_to_file(tmpdir):
    """
    Test that write_board_json_to_file correctly writes JSON to a file.
    """
    # Mock the TrelloService to return predefined values
    mock_trello_service = MagicMock(spec=TrelloService)
    mock_trello_service.get_board_by_name.return_value = "mock_board"
    mock_trello_service.extract_cards_info.return_value = MagicMock(to_dict=lambda: {})

    # Initialize the OrchestrationService with the mocked TrelloService
    orchestration_service = OrchestrationService(trello_service=mock_trello_service)

    board_name = "TestBoard"
    directory = tmpdir.mkdir("markdown_files")
    file_path = os.path.join(directory, f"{board_name} Trello.json")

    # Call the method to write JSON to a file
    result_path = orchestration_service.write_board_json_to_file(board_name, str(directory))

    # Verify that the file path is correct and the content matches the expected output
    assert result_path == file_path
    with open(result_path, "r") as file:
        content = file.read()
    assert content == "{}"


def test_get_board_json(mock_board: Board, trello_card: TrelloCard):
    """
    Test that get_board_json correctly generates JSON for a Trello board.
    """
    expected_json = {
        "backlog": [],
        "todo": [
            {
                "title": "Title",
                "list_name": "To Do",
                "description": "Test card description",
                "labels": ["Label1", "Label2"],
                "comments": ["Test comment"],
                "done_date": "2024-01-01T00:00:00",
            }
        ],
        "doing": [],
        "done": [],
    }

    # Mock the TrelloService to return predefined values
    mock_trello_service = MagicMock(spec=TrelloService)
    mock_trello_service.get_board_by_name.return_value = mock_board
    mock_trello_service.extract_cards_info.return_value = CategorizedLists(todo=[trello_card])

    # Initialize the OrchestrationService with the mocked TrelloService
    orchestration_service = OrchestrationService(mock_trello_service)
    board_json = orchestration_service.get_board_json("Test Board")

    # Verify that the generated JSON matches the expected output
    assert board_json == expected_json

    # Ensure the TrelloService methods were called with the correct arguments
    mock_trello_service.get_board_by_name.assert_called_once_with("Test Board")
    mock_trello_service.extract_cards_info.assert_called_once_with(mock_trello_service.get_board_by_name.return_value)
