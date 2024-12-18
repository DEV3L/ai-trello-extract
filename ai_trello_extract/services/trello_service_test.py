from datetime import datetime
from unittest.mock import MagicMock

import pytest
from trello import Board, Card, Label
from trello import List as TrelloList

from ai_trello_extract.env_variables import ENV_VARIABLES

from .trello_service import TrelloService


def test_extract_cards_info(
    trello_service: TrelloService, mock_board: Board, mock_trello_list: MagicMock, mock_card: Card
):
    categorized_lists = trello_service.extract_cards_info(mock_board)

    assert len(categorized_lists.backlog) == 1
    assert len(categorized_lists.todo) == 1
    assert len(categorized_lists.doing) == 1
    assert len(categorized_lists.done) == 1

    card_info = categorized_lists.todo[0]
    assert card_info.list_name == "Todo"
    assert card_info.description == "Test card description"
    assert card_info.labels == ["Label1", "Label2"]
    assert card_info.comments == ["Test comment"]
    assert card_info.done_date == datetime(2023, 1, 1)


def test_categorize_lists(trello_service: TrelloService, mock_board: Board):
    categorized = trello_service.categorize_lists(mock_board)

    assert len(categorized.backlog) == 1
    assert len(categorized.todo) == 1
    assert len(categorized.doing) == 1
    assert len(categorized.done) == 1
    assert all("_" not in lst.name for lst in categorized.todo)
    assert all("_" not in lst.name for lst in categorized.todo)
    assert all("_" not in lst.name for lst in categorized.doing)
    assert all("_" not in lst.name for lst in categorized.done)


def test_get_board_by_name_found(mock_trello_client: MagicMock):
    mock_board = MagicMock(spec=Board)
    mock_board.name = "Test Board"

    mock_trello_client.list_boards.return_value = [mock_board]

    service = TrelloService(client=mock_trello_client)

    result = service.get_board_by_name("Test Board")

    assert result == mock_board


def test_get_board_by_name_not_found(mock_trello_client: MagicMock):
    mock_trello_client.list_boards.return_value = []

    service = TrelloService(client=mock_trello_client)

    with pytest.raises(RuntimeError, match="Board with name 'Nonexistent Board' not found."):
        service.get_board_by_name("Nonexistent Board")


def test_get_lists_for_board(trello_service: TrelloService):
    mock_board = MagicMock(spec=Board)
    mock_board.name = "Test Board"

    mock_lists = [MagicMock(spec=TrelloList) for _ in range(3)]
    mock_board.all_lists.return_value = mock_lists

    lists = trello_service.get_lists_for_board(mock_board)

    assert lists == mock_lists
    mock_board.all_lists.assert_called_once()


def test_add_card_to_board(trello_service: TrelloService, mock_board: Board, mock_trello_list: MagicMock):
    mock_board.name = "Test Board"
    mock_trello_list.name = "Test List"
    mock_trello_list.add_card = MagicMock()

    ENV_VARIABLES.trello_board_add_column_name = "Test List"

    trello_service.get_board_by_name = MagicMock(return_value=mock_board)
    trello_service.get_lists_for_board = MagicMock(return_value=[mock_trello_list])
    trello_service.get_labels_for_board = MagicMock(return_value=[])

    trello_service.add_card_to_board("Test Board", "Test Card", "Test Description", [])

    mock_trello_list.add_card.assert_called_once_with(name="Test Card", desc="Test Description", labels=[])


def test_add_card_to_board_no_list_found(trello_service: TrelloService, mock_board: Board):
    mock_board.name = "Test Board"

    ENV_VARIABLES.trello_board_add_column_name = "Nonexistent List"

    trello_service.get_board_by_name = MagicMock(return_value=mock_board)
    trello_service.get_lists_for_board = MagicMock(return_value=[])

    with pytest.raises(RuntimeError, match="No lists found on board 'Test Board'."):
        trello_service.add_card_to_board("Test Board", "Test Card", "Test Description", [])


def test_get_labels_for_board(trello_service: TrelloService, mock_board: Board):
    mock_board.name = "Test Board"
    mock_labels = [MagicMock(spec=Label) for _ in range(3)]
    mock_board.get_labels = MagicMock(return_value=mock_labels)

    labels = trello_service.get_labels_for_board(mock_board)

    assert labels == mock_labels
    mock_board.get_labels.assert_called_once()
