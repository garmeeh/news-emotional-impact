from typing import List, Tuple

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.config.prompt_config import PromptConfig, prompt_config
from app.config.emotional_impact_tags import EmotionalImpactTags
from app.llm.llm import create_llm

from dotenv import load_dotenv

load_dotenv()


class EmotionalImpactResponse(BaseModel):
    """Response model for emotional impact analysis"""

    primary_tag: str = Field(
        description="The primary emotional impact tag that applies to the headline"
    )

    secondary_tags: List[str] = Field(
        description="The secondary emotional impact tags that apply to the headline, max 2"
    )


class EmotionalImpactAnalyzer:
    def __init__(self) -> None:
        # Load prompts if not already loaded
        if prompt_config.emotional_impact.content is None:
            prompt_config.load_prompt("emotional_impact")

        if prompt_config.emotional_impact.content is None:
            raise ValueError("Emotional impact prompt is not loaded")

        self.emotional_impact_prompt: ChatPromptTemplate = (
            ChatPromptTemplate.from_template(prompt_config.emotional_impact.content)
        )

        self.emotional_impact_analyzer = create_llm(
            model=prompt_config.emotional_impact.model,
            temperature=prompt_config.emotional_impact.temperature,
            response_model=EmotionalImpactResponse,
        )

        self.emotional_impact_chain = (
            self.emotional_impact_prompt | self.emotional_impact_analyzer
        )

        # Get valid tags from config
        self.valid_tags: List[str] = [
            tag.name for tag in EmotionalImpactTags.EMOTIONAL_IMPACT_TAGS
        ]

    async def analyze_headline(
        self, headline: str
    ) -> Tuple[EmotionalImpactResponse, PromptConfig]:
        """Analyze the emotional impact of a single headline"""
        result = EmotionalImpactResponse.model_validate(
            self.emotional_impact_chain.invoke(
                {
                    "headline": headline,
                    "emotional_impact_tags_list": EmotionalImpactTags.to_text_list(),
                }
            )
        )

        # Validate that returned tags exist in our config
        validated_tags: List[str] = [
            tag for tag in result.secondary_tags if tag in self.valid_tags
        ]
        response = EmotionalImpactResponse(
            primary_tag=result.primary_tag,
            secondary_tags=validated_tags,
        )

        return response, prompt_config.emotional_impact
