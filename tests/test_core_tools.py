import unittest
from datetime import datetime, timezone

from app.tools.core_tools import (
    CoreTools,
)
from app.tools.tool_decorator import (
    get_tool_metadata,
)
from app.tools.tool_metadata import (
    ToolRiskLevel,
)


class TestCoreTools(unittest.TestCase):

    def test_get_current_datetime(
        self,
    ) -> None:
        fixed_datetime = datetime(
            year=2026,
            month=7,
            day=19,
            hour=10,
            minute=30,
            second=45,
            tzinfo=timezone.utc,
        )

        tools = CoreTools(
            datetime_provider=(
                lambda: fixed_datetime
            )
        )

        result = (
            tools.get_current_datetime()
        )

        self.assertEqual(
            result,
            "2026-07-19T10:30:45+00:00",
        )

    def test_invalid_datetime_provider_result(
        self,
    ) -> None:
        tools = CoreTools(
            datetime_provider=(
                lambda: "invalid"
                # type: ignore[return-value]
            )
        )

        with self.assertRaises(
            TypeError
        ):
            tools.get_current_datetime()

    def test_count_words(
        self,
    ) -> None:
        tools = CoreTools()

        result = tools.count_words(
            "MZ puede utilizar herramientas"
        )

        self.assertEqual(
            result,
            4,
        )

    def test_count_words_ignores_extra_spaces(
        self,
    ) -> None:
        tools = CoreTools()

        result = tools.count_words(
            "  una   frase  corta  "
        )

        self.assertEqual(
            result,
            3,
        )

    def test_count_words_empty_text(
        self,
    ) -> None:
        tools = CoreTools()

        result = tools.count_words("")

        self.assertEqual(
            result,
            0,
        )

    def test_count_words_rejects_invalid_type(
        self,
    ) -> None:
        tools = CoreTools()

        with self.assertRaises(
            TypeError
        ):
            tools.count_words(
                123
                # type: ignore[arg-type]
            )

    def test_tool_metadata(
        self,
    ) -> None:
        tools = CoreTools()

        datetime_metadata = (
            get_tool_metadata(
                tools.get_current_datetime
            )
        )
        count_metadata = (
            get_tool_metadata(
                tools.count_words
            )
        )

        self.assertIsNotNone(
            datetime_metadata
        )
        self.assertIsNotNone(
            count_metadata
        )

        if (
            datetime_metadata is None
            or count_metadata is None
        ):
            self.fail(
                "No se encontraron los "
                "metadatos esperados."
            )

        self.assertEqual(
            datetime_metadata.name,
            "get_current_datetime",
        )
        self.assertEqual(
            count_metadata.name,
            "count_words",
        )
        self.assertEqual(
            datetime_metadata.risk_level,
            ToolRiskLevel.LOW,
        )
        self.assertFalse(
            datetime_metadata
            .requires_confirmation
        )


if __name__ == "__main__":
    unittest.main()