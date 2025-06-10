from app.config.prompt_config import PromptConfig, PromptsConfig

VERSION = 2
TEMPERATURE = 1.0
MODEL = "openai/gpt-4o"

prompt_config: PromptsConfig = PromptsConfig(
    headline_sentiment=PromptConfig(
        version=VERSION,
        path="prompts/headline-sentiment-v1.txt",
        model=MODEL,
        temperature=TEMPERATURE,
    ),
    clickbait_score=PromptConfig(
        version=VERSION,
        path="prompts/clickbait-score-v1.txt",
        model=MODEL,
        temperature=TEMPERATURE,
    ),
    emotional_impact=PromptConfig(
        version=VERSION,
        path="prompts/emotional-impact-tag-v1.txt",
        model=MODEL,
        temperature=TEMPERATURE,
    ),
    category_tag=PromptConfig(
        version=VERSION,
        path="prompts/category-tag-v1.txt",
        model=MODEL,
        temperature=TEMPERATURE,
    ),
)
