import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.ai.ai_provider_factory import (
    AIProviderFactory,
)
from app.ai.fallback_ai_provider import (
    FallbackAIProvider,
)
from app.ai.gemini_ai_provider import (
    GeminiAIProvider,
)
from app.ai.mock_ai_provider import (
    MockAIProvider,
)
from app.core.config_manager import (
    ConfigManager,
)
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)


class TestAIProviderFactory(
    unittest.TestCase
):
    def _create_config(
        self,
        providers: object,
    ) -> tuple[
        tempfile.TemporaryDirectory,
        ConfigManager,
    ]:
        temporary_directory = (
            tempfile.TemporaryDirectory()
        )
        config_path = (
            Path(temporary_directory.name)
            / "config.json"
        )

        with config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                {
                    "ai": {
                        "providers": providers,
                    }
                },
                file,
            )

        manager = ConfigManager(
            config_path=config_path
        )

        return (
            temporary_directory,
            manager,
        )

    @staticmethod
    def _create_tool_metadata(
    ) -> ToolMetadata:
        return ToolMetadata(
            name="count_words",
            description=(
                "Cuenta las palabras de un texto."
            ),
            parameters={
                "text": {
                    "type": "string",
                    "description": (
                        "Texto que será analizado."
                    ),
                    "required": True,
                }
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def test_creates_mock_provider(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "mock",
                        "enabled": True,
                    }
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={},
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            MockAIProvider,
        )

    def test_skips_gemini_without_api_key(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "model": (
                            "gemini-2.5-flash"
                        ),
                    },
                    {
                        "name": "mock",
                        "enabled": True,
                    },
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={},
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            MockAIProvider,
        )

    def test_creates_fallback_with_gemini_key(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "model": (
                            "gemini-2.5-flash"
                        ),
                    },
                    {
                        "name": "mock",
                        "enabled": True,
                    },
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={
                "GEMINI_API_KEY": (
                    "test-api-key"
                ),
            },
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            FallbackAIProvider,
        )
        self.assertEqual(
            provider
            .get_available_provider_names(),
            [
                "gemini",
                "mock",
            ],
        )

    def test_uses_google_api_key_first(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "model": "test-model",
                    }
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={
                "GOOGLE_API_KEY": (
                    "google-key"
                ),
                "GEMINI_API_KEY": (
                    "gemini-key"
                ),
            },
        )

        with patch(
            "app.ai.ai_provider_factory"
            ".GeminiAIProvider"
        ) as provider_class:
            provider_class.return_value = (
                MockAIProvider()
            )

            factory.create()

            provider_class.assert_called_once_with(
                api_key="google-key",
                model="test-model",
                tools=(),
            )

    def test_passes_tools_to_gemini_provider(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "model": "test-model",
                    }
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        metadata = (
            self._create_tool_metadata()
        )

        factory = AIProviderFactory(
            config=config,
            tools=(metadata,),
            environ={
                "GEMINI_API_KEY": (
                    "test-api-key"
                ),
            },
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            GeminiAIProvider,
        )
        self.assertEqual(
            provider.tools,
            (metadata,),
        )

    def test_tools_property_returns_metadata(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config([])
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        metadata = (
            self._create_tool_metadata()
        )

        factory = AIProviderFactory(
            config=config,
            tools=(metadata,),
            environ={},
        )

        self.assertEqual(
            factory.tools,
            (metadata,),
        )

    def test_rejects_invalid_tools(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config([])
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        with self.assertRaises(TypeError):
            AIProviderFactory(
                config=config,
                tools=(
                    object(),  # type: ignore[arg-type]
                ),
                environ={},
            )

    def test_rejects_non_iterable_tools(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config([])
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        with self.assertRaises(TypeError):
            AIProviderFactory(
                config=config,
                tools=object(),  # type: ignore[arg-type]
                environ={},
            )

    def test_disabled_provider_is_skipped(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": False,
                        "model": (
                            "gemini-2.5-flash"
                        ),
                    },
                    {
                        "name": "mock",
                        "enabled": True,
                    },
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={
                "GEMINI_API_KEY": (
                    "test-api-key"
                ),
            },
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            MockAIProvider,
        )

    def test_unknown_provider_is_skipped(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "unknown",
                        "enabled": True,
                    },
                    {
                        "name": "mock",
                        "enabled": True,
                    },
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={},
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            MockAIProvider,
        )

    def test_uses_mock_when_configuration_is_empty(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config([])
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={},
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            MockAIProvider,
        )

    def test_created_gemini_provider_uses_model(
        self,
    ) -> None:
        temporary_directory, config = (
            self._create_config(
                [
                    {
                        "name": "gemini",
                        "enabled": True,
                        "model": (
                            "gemini-2.5-flash"
                        ),
                    }
                ]
            )
        )
        self.addCleanup(
            temporary_directory.cleanup
        )

        factory = AIProviderFactory(
            config=config,
            environ={
                "GEMINI_API_KEY": (
                    "test-api-key"
                ),
            },
        )

        provider = factory.create()

        self.assertIsInstance(
            provider,
            GeminiAIProvider,
        )
        self.assertEqual(
            provider.model,
            "gemini-2.5-flash",
        )


if __name__ == "__main__":
    unittest.main()