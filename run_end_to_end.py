from loguru import logger

from ai_trello_extract.clients.trello_client import get_trello_client
from ai_trello_extract.orchestrators.orchestration_service import OrchestrationService
from ai_trello_extract.services.trello_service import TrelloService
from ai_trello_extract.settings import get_settings


def main():
    settings = get_settings()
    logger.info(settings.trello_api_key)
    orchestration_service = OrchestrationService(TrelloService(get_trello_client(settings)))

    try:
        markdown_file_name = orchestration_service.write_board_markdown_to_file(settings.trello_board_name, "bin")
        logger.info(f"Markdown file written to {markdown_file_name}")
        # logger.info(orchestration_service.write_board_json_to_file(settings.trello_board_name, "bin"))
    except RuntimeError as e:
        logger.error(e)


if __name__ == "__main__":
    main()
