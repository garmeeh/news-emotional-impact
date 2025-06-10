import asyncio
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from app.config.prompt_config import PromptConfig, prompt_config
from app.llm.llm import create_llm
from dotenv import load_dotenv

load_dotenv()

SentimentType = Literal[
    "Very Negative", "Negative", "Neutral", "Positive", "Very Positive"
]
SENTIMENT_CATEGORIES = list(SentimentType.__args__)


class HeadlineSentiment(BaseModel):
    """Classification model for news headline sentiment analysis"""

    sentiment: SentimentType = Field(
        description="The sentiment category of the headline"
    )
    confidence: int = Field(description="Confidence score from 0 to 100")


class SentimentAnalyzer:
    def __init__(self) -> None:
        # Load prompts if not already loaded
        if prompt_config.headline_sentiment.content is None:
            prompt_config.load_prompt("headline_sentiment")

        if prompt_config.headline_sentiment.content is None:
            raise ValueError("Headline sentiment prompt is not loaded")

        self.sentiment_prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(
            prompt_config.headline_sentiment.content
        )

        self.sentiment_analyzer = create_llm(
            model=prompt_config.headline_sentiment.model,
            temperature=prompt_config.headline_sentiment.temperature,
            response_model=HeadlineSentiment,
        )

        self.sentiment_chain = self.sentiment_prompt | self.sentiment_analyzer

    async def analyze_headline(
        self, headline: str
    ) -> tuple[HeadlineSentiment, PromptConfig]:
        """Analyze the sentiment of a single headline"""
        result = self.sentiment_chain.invoke(
            {"headline": headline, "categories": SENTIMENT_CATEGORIES}
        )

        return HeadlineSentiment.model_validate(
            result
        ), prompt_config.headline_sentiment

