import logging
from pathlib import Path
import shutil
import unittest

from manipulator_framework.infrastructure.logging import (
    LoggingConfig,
    get_logger,
    setup_logging,
)


class TestOperationalLogging(unittest.TestCase):
    def _test_dir(self, name: str) -> Path:
        directory = Path("manipulator_framework/tests/_tmp_logging") / name
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def setUp(self) -> None:
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=False,
            )
        )

    def tearDown(self) -> None:
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=False,
            )
        )
        shutil.rmtree(
            Path("manipulator_framework/tests/_tmp_logging"),
            ignore_errors=True,
        )

    def test_setup_logging_creates_log_file(self) -> None:
        log_path = self._test_dir("create_log_file") / "operational.log"
        if log_path.exists():
            log_path.unlink()
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=True,
                log_file_path=log_path,
            )
        )

        logger = get_logger("manipulator_framework.tests.infrastructure")
        logger.info("hello from test")

        self.assertTrue(log_path.exists())
        self.assertIn("hello from test", log_path.read_text(encoding="utf-8"))
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=False,
            )
        )

    def test_setup_logging_does_not_duplicate_handlers(self) -> None:
        log_path = self._test_dir("deduplicate_handlers") / "operational.log"
        if log_path.exists():
            log_path.unlink()
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=True,
                log_to_file=True,
                log_file_path=log_path,
            )
        )
        package_logger = logging.getLogger("manipulator_framework")
        handlers_after_first_setup = len(package_logger.handlers)

        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=True,
                log_to_file=True,
                log_file_path=log_path,
            )
        )
        handlers_after_second_setup = len(package_logger.handlers)

        logger = get_logger("manipulator_framework.tests.infrastructure")
        logger.info("single line")

        file_lines = [
            line for line in log_path.read_text(encoding="utf-8").splitlines()
            if "single line" in line
        ]
        self.assertEqual(handlers_after_first_setup, 2)
        self.assertEqual(handlers_after_second_setup, 2)
        self.assertEqual(len(file_lines), 1)
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=False,
            )
        )

    def test_setup_logging_respects_level(self) -> None:
        log_path = self._test_dir("respects_level") / "operational.log"
        if log_path.exists():
            log_path.unlink()
        setup_logging(
            LoggingConfig(
                level="WARNING",
                log_to_console=False,
                log_to_file=True,
                log_file_path=log_path,
            )
        )

        logger = get_logger("manipulator_framework.tests.infrastructure")
        logger.info("should not be logged")
        logger.warning("should be logged")

        contents = log_path.read_text(encoding="utf-8")
        self.assertNotIn("should not be logged", contents)
        self.assertIn("should be logged", contents)
        setup_logging(
            LoggingConfig(
                level="INFO",
                log_to_console=False,
                log_to_file=False,
            )
        )


if __name__ == "__main__":
    unittest.main()
