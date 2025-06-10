from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from app.config.prompt_config import PromptConfig, prompt_config
from app.llm.llm import create_llm

from dotenv import load_dotenv

load_dotenv()

ClickbaitScoreType = Literal["1", "2", "3", "4", "5"]


class ClickbaitScore(BaseModel):
    """Classification model for news headline clickbait analysis"""

    score: ClickbaitScoreType = Field(
        description="The clickbait score from 1 (not clickbait) to 5 (extremely clickbait)"
    )


class ClickbaitAnalyzer:
    def __init__(self) -> None:
        # Load prompts if not already loaded
        if prompt_config.clickbait_score.content is None:
            prompt_config.load_prompt("clickbait_score")

        if prompt_config.clickbait_score.content is None:
            raise ValueError("Clickbait score prompt is not loaded")

        self.clickbait_prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(
            prompt_config.clickbait_score.content
        )

        self.clickbait_analyzer = create_llm(
            model=prompt_config.clickbait_score.model,
            temperature=prompt_config.clickbait_score.temperature,
            response_model=ClickbaitScore,
        )

        self.clickbait_chain = self.clickbait_prompt | self.clickbait_analyzer

    async def analyze_headline(
        self, headline: str
    ) -> tuple[ClickbaitScore, PromptConfig]:
        """Analyze the clickbait score of a single headline"""
        result = self.clickbait_chain.invoke({"headline": headline})

        return ClickbaitScore.model_validate(result), prompt_config.clickbait_score

