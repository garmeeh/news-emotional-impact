import os
import importlib
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class PromptConfig(BaseModel):
    """Configuration for a specific prompt"""

    version: int
    path: str
    model: str
    temperature: float = 0.0
    content: Optional[str] = None

    def load_content(self, base_path: Path) -> str:
        """Load the prompt content from file"""
        if self.content is None:
            full_path = base_path / self.path
            self.content = full_path.read_text()
        return self.content


class PromptsConfig(BaseModel):
    """Central configuration for all prompts"""

    headline_sentiment: PromptConfig
    clickbait_score: PromptConfig
    emotional_impact: PromptConfig
    category_tag: PromptConfig

    def load_prompt(self, prompt_name: str, base_path: Path = Path("app")) -> None:
        """Load a specific prompt by name"""
        if not hasattr(self, prompt_name):
            raise ValueError(f"Unknown prompt: {prompt_name}")
        prompt = getattr(self, prompt_name)
        if isinstance(prompt, PromptConfig):
            prompt.load_content(base_path)

    def load_prompts(self, base_path: Path = Path("app")) -> None:
        """Load all prompt contents"""
        for prompt in self.__dict__.values():
            if isinstance(prompt, PromptConfig):
                prompt.load_content(base_path)


def load_versioned_prompt_config() -> PromptsConfig:
    """
    Dynamically load a versioned prompt config based on the
    PROMPT_CONFIG_VERSION environment variable.
    Defaults to version '9' if not specified.
    """
    version_str: str = os.getenv("PROMPT_CONFIG_VERSION", "1")
    module_name: str = f"app.config.prompt_versions.v{version_str}_config"
    module = importlib.import_module(module_name)
    return module.prompt_config


# Global instance loaded based on version.
prompt_config: PromptsConfig = load_versioned_prompt_config()
