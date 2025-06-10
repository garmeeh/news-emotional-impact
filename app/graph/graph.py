import logging
from typing import List, Optional, TypedDict, cast
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from app.config.prompt_config import PromptConfig
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.services.category_analyzer import CategoryAnalyzer
from app.services.emotional_impact_analyzer import EmotionalImpactAnalyzer
from app.services.clickbait_analyzer import ClickbaitAnalyzer
from app.db import Database

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SentimentData(TypedDict):
    sentiment: str
    confidence: int
    prompt_config: PromptConfig


class ClickbaitData(TypedDict):
    score: str
    prompt_config: PromptConfig


class TagData(TypedDict):
    primary_tag: str
    secondary_tags: List[str]
    prompt_config: PromptConfig


class InputState(TypedDict):
    headline: str
    description: Optional[str]
    news_article_id: int


class OverallState(InputState):
    sentiment: SentimentData
    clickbait: ClickbaitData
    emotional_impact: TagData
    categories: TagData


async def handle_get_sentiment(state: OverallState) -> OverallState:
    """Process sentiment analysis for the headline."""
    try:
        analyzer = SentimentAnalyzer()
        sentiment_result, prompt_config = await analyzer.analyze_headline(
            state["headline"]
        )
        logger.info(
            f"Sentiment analysis completed for headline: {state['headline'][:50]}..."
        )

        return {
            **state,
            "sentiment": {
                "sentiment": sentiment_result.sentiment,
                "confidence": sentiment_result.confidence,
                "prompt_config": prompt_config,
            },
        }
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
        raise


async def handle_get_category(state: OverallState) -> OverallState:
    """Process category analysis for the headline."""
    try:
        analyzer = CategoryAnalyzer()
        description = state.get("description", None)
        category_result, prompt_config = await analyzer.analyze_headline(
            state["headline"], description
        )
        logger.info(
            f"Category analysis completed for headline: {state['headline'][:50]}..."
        )

        return {
            **state,
            "categories": {
                "primary_tag": category_result.primary_tag,
                "secondary_tags": category_result.secondary_tags,
                "prompt_config": prompt_config,
            },
        }
    except Exception as e:
        logger.error(f"Error in category analysis: {str(e)}", exc_info=True)
        raise


async def handle_get_emotional_impact(state: OverallState) -> OverallState:
    """Process emotional impact analysis for the headline."""
    try:
        analyzer = EmotionalImpactAnalyzer()
        emotional_result, prompt_config = await analyzer.analyze_headline(
            state["headline"]
        )
        logger.info(
            f"Emotional impact analysis completed for headline: {state['headline'][:50]}..."
        )

        return {
            **state,
            "emotional_impact": {
                "primary_tag": emotional_result.primary_tag,
                "secondary_tags": emotional_result.secondary_tags,
                "prompt_config": prompt_config,
            },
        }
    except Exception as e:
        logger.error(f"Error in emotional impact analysis: {str(e)}", exc_info=True)
        raise


async def handle_get_clickbait(state: OverallState) -> OverallState:
    """Process clickbait analysis for the headline."""
    try:
        analyzer = ClickbaitAnalyzer()
        clickbait_result, prompt_config = await analyzer.analyze_headline(
            state["headline"]
        )
        logger.info(
            f"Clickbait analysis completed for headline: {state['headline'][:50]}..."
        )

        return {
            **state,
            "clickbait": {
                "score": clickbait_result.score,
                "prompt_config": prompt_config,
            },
        }
    except Exception as e:
        logger.error(f"Error in clickbait analysis: {str(e)}", exc_info=True)
        raise


async def return_news_sentiment(state: OverallState) -> OverallState:
    """Return the state"""
    return state


async def save_news_sentiment(state: OverallState) -> bool:
    """Add news sentiment to the state."""
    try:
        db = Database()
        news_article_id = state["news_article_id"]
        logger.info(f"Saving sentiment analysis for article ID: {news_article_id}")

        version_info = {
            "sentiment": state["sentiment"]["prompt_config"].model_dump(
                exclude={"content"}
            ),
            "categories": state["categories"]["prompt_config"].model_dump(
                exclude={"content"}
            ),
            "emotional_impact": state["emotional_impact"]["prompt_config"].model_dump(
                exclude={"content"}
            ),
            "clickbait": state["clickbait"]["prompt_config"].model_dump(
                exclude={"content"}
            ),
        }

        sentiment_result = await db.insert_article_sentiment(
            news_article_id=news_article_id,
            sentiment_label=state["sentiment"]["sentiment"],
            sentiment_confidence=state["sentiment"]["confidence"],
            clickbait_level=int(state["clickbait"]["score"]),
            version_info=version_info,
        )

        if sentiment_result:
            logger.info(
                f"Inserted sentiment analysis with ID: {sentiment_result['id']}"
            )

            await db.insert_emotional_impact_tags(
                news_article_sentiment_id=sentiment_result["id"],
                primary_tag=state["emotional_impact"]["primary_tag"],
                secondary_tags=state["emotional_impact"]["secondary_tags"],
            )
            logger.info("Inserted emotional impact tags")

            await db.insert_category_tags(
                news_article_sentiment_id=sentiment_result["id"],
                primary_tag=state["categories"]["primary_tag"],
                secondary_tags=state["categories"]["secondary_tags"],
            )
            logger.info("Inserted category tags")
            return True

        logger.error(
            f"Failed to insert sentiment analysis for article ID: {news_article_id}"
        )
        return False

    except Exception as e:
        logger.error(f"Error saving news sentiment: {str(e)}", exc_info=True)
        return False


# Build graph
builder = StateGraph(
    OverallState,
    input=InputState,
)

builder.add_node("get_sentiment", handle_get_sentiment)
builder.add_node("get_category", handle_get_category)
builder.add_node("get_emotional_impact", handle_get_emotional_impact)
builder.add_node("get_clickbait", handle_get_clickbait)
builder.add_node("return_news_sentiment", return_news_sentiment)
# Logic
builder.add_edge(START, "get_sentiment")
builder.add_edge("get_sentiment", "get_category")
builder.add_edge("get_category", "get_emotional_impact")
builder.add_edge("get_emotional_impact", "get_clickbait")
builder.add_edge("get_clickbait", "return_news_sentiment")
builder.add_edge("return_news_sentiment", END)

# Add
graph: CompiledStateGraph = builder.compile()


async def run_graph(app_input: InputState):
    try:
        if not app_input:
            raise ValueError("No input provided")

        logger.info(f"Starting analysis for article ID: {app_input['news_article_id']}")

        result: OverallState = cast(
            OverallState,
            await graph.ainvoke(
                input=app_input,
                config={"configurable": {"thread_id": "1"}},
                debug=True,
            ),
        )

        logger.info("Analysis completed. Result Attached", extra={"result": result})

        save_result = await save_news_sentiment(result)
        if save_result:
            logger.info(
                f"Successfully saved analysis for article ID: {app_input['news_article_id']}"
            )
        else:
            logger.error(
                f"Failed to save analysis for article ID: {app_input['news_article_id']}"
            )

    except Exception as e:
        logger.error(f"Error running analysis graph: {str(e)}", exc_info=True)
        raise
