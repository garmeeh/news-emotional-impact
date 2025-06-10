from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.config.prompt_config import PromptConfig, prompt_config
from app.config.category_tags import CategoryTags
from app.llm.llm import create_llm

from dotenv import load_dotenv

load_dotenv()


class CategoryTagResponse(BaseModel):
    """Response model for category tag analysis"""

    primary_tag: str = Field(description="The primary category tag")
    secondary_tags: List[str] = Field(description="The secondary category tags, max 2")


class CategoryAnalyzer:
    def __init__(self) -> None:
        # Load prompts if not already loaded
        if prompt_config.category_tag.content is None:
            prompt_config.load_prompt("category_tag")

        if prompt_config.category_tag.content is None:
            raise ValueError("Category tag prompt is not loaded")

        self.category_prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(
            prompt_config.category_tag.content
        )

        self.category_analyzer = create_llm(
            model=prompt_config.category_tag.model,
            temperature=prompt_config.category_tag.temperature,
            response_model=CategoryTagResponse,
        )

        # Create the chain
        self.category_chain = self.category_prompt | self.category_analyzer

        # Get all available category tags
        self.available_tags = [tag.name for tag in CategoryTags.CATEGORY_TAGS]

    async def analyze_headline(
        self, headline: str, description: Optional[str] = None
    ) -> Tuple[CategoryTagResponse, PromptConfig]:
        """Analyze the category tags for a single headline"""
        result = CategoryTagResponse.model_validate(
            self.category_chain.invoke(
                {
                    "headline": headline,
                    "description": description or "",
                    "category_tags_list": CategoryTags.to_text_list(),
                }
            )
        )

        # Validate that returned tags exist in our available tags
        validated_tags = [
            tag for tag in result.secondary_tags if tag in self.available_tags
        ]
        response = CategoryTagResponse(
            primary_tag=result.primary_tag, secondary_tags=validated_tags
        )

        return response, prompt_config.category_tag
