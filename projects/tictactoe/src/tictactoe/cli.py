from __future__ import annotations

import logging.config
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import click

from tictactoe.runner import TicTacToeApp

log = logging.getLogger(__name__)


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase log level. '-v' will output INFO messages. "
    "More than -vv is useless.",
)
@click.option(
    "-q",
    "--quiet",
    count=True,
    help="Reduce log level. '-q' will suppress WARNING messages. "
    "More than -qq is useless.",
)
@click.option(
    "-l",
    "--log-file",
    help="Reduce log level. '-q' will suppress WARNING messages. "
    "More than -qq is useless.",
)
def main(verbose: int, quiet: int, log_file: str) -> None:
    """Point d'entrée de l'application."""
    verbosity: int = int(logging.INFO / 10) + verbose - quiet

    logging.config.dictConfig(
        logging_configuration(verbosity, Path(log_file) if log_file else None)
    )

    log.debug(verbosity)

    app = TicTacToeApp()
    app.run()


def logging_configuration(
    verbosity: int, logfile: Path | None = None
) -> dict[str, Any]:
    """
    Build logging configuration based on a verbosity level.

    Args:
        verbosity:
            Verbosity 0 is means "CRITICAL", and each increments move
            toward "DEBUG".
        logfile:
            Optional log file.

    """
    level = max(logging.CRITICAL - logging.DEBUG * verbosity, logging.DEBUG)

    formatters = {
        "standard": {"format": "%(levelname)8s: %(message)s"},
        "debug": {"format": "%(levelname)8s %(name)-16s:%(funcName)-12s> %(message)s"},
    }

    active_formatter = "debug" if level <= logging.DEBUG else "standard"

    handlers = {
        "console": {
            "level": level,
            "formatter": active_formatter,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",  # Default is stderr
        },
    }

    if logfile:
        handlers["file"] = {
            "level": level,
            "formatter": active_formatter,
            "class": "logging.FileHandler",
            "filename": str(logfile),
        }

    loggers = {
        "": {
            # root logger
            "handlers": handlers.keys(),
            "level": level,
            "propagate": True,
        }
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
    }
