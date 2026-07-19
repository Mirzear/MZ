import unittest

from app.tools.tool_decorator import tool
from app.tools.tool_loader import (
    ToolLoader,
)
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)
from app.tools.tool_registry import (
    ToolRegistry,
)


class TestToolLoader(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.loader = ToolLoader(
            self.registry
        )

    def test_load_registers_decorated_method(
        self,
    ) -> None:
        class ExampleTools:

            @tool(
                name="example",
                description=(
                    "Herramienta de ejemplo."
                ),
            )
            def example(self) -> str:
                return "resultado"

        loaded_count = self.loader.load(
            ExampleTools()
        )

        self.assertEqual(
            loaded_count,
            1,
        )
        self.assertTrue(
            self.registry.exists(
                "example"
            )
        )

    def test_load_ignores_undecorated_method(
        self,
    ) -> None:
        class ExampleTools:

            def ordinary_method(
                self,
            ) -> str:
                return "resultado"

        loaded_count = self.loader.load(
            ExampleTools()
        )

        self.assertEqual(
            loaded_count,
            0,
        )
        self.assertEqual(
            self.registry.count(),
            0,
        )

    def test_registered_handler_is_bound(
        self,
    ) -> None:
        class ExampleTools:

            def __init__(self) -> None:
                self.value = "resultado"

            @tool(
                name="example",
                description=(
                    "Herramienta de ejemplo."
                ),
            )
            def example(self) -> str:
                return self.value

        provider = ExampleTools()

        self.loader.load(provider)

        handler = self.registry.get(
            "example"
        )

        self.assertIsNotNone(handler)

        if handler is None:
            self.fail(
                "La herramienta no fue "
                "registrada."
            )

        self.assertEqual(
            handler(),
            "resultado",
        )

    def test_metadata_is_registered(
        self,
    ) -> None:
        class ExampleTools:

            @tool(
                name="example",
                description=(
                    "Herramienta de ejemplo."
                ),
            )
            def example(self) -> str:
                return "resultado"

        self.loader.load(
            ExampleTools()
        )

        metadata = (
            self.registry.get_metadata(
                "example"
            )
        )

        self.assertIsNotNone(metadata)

        if metadata is None:
            self.fail(
                "Los metadatos no fueron "
                "registrados."
            )

        self.assertEqual(
            metadata.description,
            "Herramienta de ejemplo.",
        )

    def test_load_many_registers_providers(
        self,
    ) -> None:
        class FirstTools:

            @tool(
                name="first",
                description=(
                    "Primera herramienta."
                ),
            )
            def first(self) -> str:
                return "first"

        class SecondTools:

            @tool(
                name="second",
                description=(
                    "Segunda herramienta."
                ),
            )
            def second(self) -> str:
                return "second"

        loaded_count = (
            self.loader.load_many(
                (
                    FirstTools(),
                    SecondTools(),
                )
            )
        )

        self.assertEqual(
            loaded_count,
            2,
        )
        self.assertTrue(
            self.registry.exists(
                "first"
            )
        )
        self.assertTrue(
            self.registry.exists(
                "second"
            )
        )

    def test_duplicate_discovery_raises_error(
        self,
    ) -> None:
        class FirstTools:

            @tool(
                name="duplicate",
                description=(
                    "Primera herramienta."
                ),
            )
            def first(self) -> str:
                return "first"

        class SecondTools:

            @tool(
                name="duplicate",
                description=(
                    "Segunda herramienta."
                ),
            )
            def second(self) -> str:
                return "second"

        with self.assertRaises(
            ValueError
        ):
            self.loader.load_many(
                (
                    FirstTools(),
                    SecondTools(),
                )
            )

        self.assertEqual(
            self.registry.count(),
            0,
        )

    def test_registered_duplicate_raises_error(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="example",
            description=(
                "Herramienta registrada."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        self.registry.register(
            metadata=metadata,
            handler=lambda: None,
        )

        class ExampleTools:

            @tool(
                name="example",
                description=(
                    "Herramienta duplicada."
                ),
            )
            def example(self) -> str:
                return "resultado"

        with self.assertRaises(
            ValueError
        ):
            self.loader.load(
                ExampleTools()
            )

        self.assertEqual(
            self.registry.count(),
            1,
        )

    def test_empty_provider_loads_nothing(
        self,
    ) -> None:
        class EmptyProvider:
            pass

        loaded_count = self.loader.load(
            EmptyProvider()
        )

        self.assertEqual(
            loaded_count,
            0,
        )
        self.assertEqual(
            self.registry.count(),
            0,
        )


if __name__ == "__main__":
    unittest.main()