from typing import Dict, Any, List
import logging
import asyncio
import time
from collections import deque

from app.db import Database
from app.graph.graph import run_graph, InputState
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()


MAX_REQUESTS_PER_RUN = 7500
MAX_RUN_TIME_HOURS = 8


class SentimentAnalysisService:
    def __init__(self, batch_size: int = 100):
        """Initialize service with configurable batch size.

        Args:
            batch_size: Number of articles to process in one batch (default: 10)
        """
        self.db = Database()
        self.batch_size = batch_size

    async def process_article(self, article: Dict[str, Any]) -> bool:
        """Process a single article through the sentiment analysis graph.

        Args:
            article: Article data from database

        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            input_state: InputState = {
                "headline": article["title"],
                "description": article["description"],
                "news_article_id": article["id"],
            }

            await run_graph(input_state)
            logger.info(f"Successfully processed article {article['id']}")
            return True

        except Exception as e:
            logger.error(
                f"Error processing article {article['id']}: {str(e)}", exc_info=True
            )
            return False

    async def run_sentiment_analysis(self) -> Dict[str, int]:
        """Run sentiment analysis on articles without sentiment, with no rate limiting.

        Returns:
            Dict with summary statistics of the processing run
        """
        logger.info(
            f"Starting sentiment analysis run with batch size {self.batch_size}"
        )

        try:
            articles: List[
                Dict[str, Any]
            ] = await self.db.get_articles_without_sentiment(limit=self.batch_size)

            if not articles:
                logger.info("No articles found without sentiment analysis")
                return {"total_articles": 0, "successful": 0, "failed": 0}

            logger.info(f"Found {len(articles)} articles to process")

            successful_count = 0
            failed_count = 0
            total_processed = 0

            for article in articles:
                success = await self.process_article(article)
                total_processed += 1
                logger.info(f"PROCESSED {total_processed} of {len(articles)}")
                if success:
                    logger.info(
                        f"Successfully processed article {article['id']}: {article['title']}"
                    )
                    successful_count += 1
                else:
                    logger.error(
                        f"Failed to process article {article['id']}: {article['title']}"
                    )
                    failed_count += 1

                if total_processed >= self.batch_size:
                    logger.info(f"Stopping as max limit reached of {self.batch_size}")
                    break

            return {
                "total_articles": len(articles),
                "successful": successful_count,
                "failed": failed_count,
            }

        except Exception as e:
            logger.error(f"Error in sentiment analysis run: {str(e)}", exc_info=True)
            raise

    async def run_rate_limited_sentiment_analysis(self) -> Dict[str, int]:
        """
        Run sentiment analysis on articles without sentiment, with rate limiting.

        Processes 7 articles per minute to stay under API rate limits
        (each article makes 4 requests, so at most 28 requests/minute).
        Will stop processing if MAX_RUN_TIME_HOURS is reached.

        Returns:
            Dict[str, int]: Summary statistics of the processing run
        """
        logger.info(
            f"Starting rate-limited sentiment analysis run with batch size {self.batch_size}"
        )

        try:
            start_time = time.time()
            articles: List[
                Dict[str, Any]
            ] = await self.db.get_articles_without_sentiment(limit=self.batch_size)

            if not articles:
                logger.info("No articles found without sentiment analysis")
                return {"total_articles": 0, "successful": 0, "failed": 0}

            logger.info(f"Found {len(articles)} articles to process")

            successful_count = 0
            failed_count = 0
            total_processed = 0

            # Keep last 7 article timestamps (since each article makes 4 requests)
            request_times: deque[float] = deque(maxlen=7)
            WINDOW_SECONDS = 60

            for article in articles:
                # Check if we've exceeded max run time
                if (time.time() - start_time) > (MAX_RUN_TIME_HOURS * 3600):
                    logger.info(
                        f"Stopping as max run time of {MAX_RUN_TIME_HOURS} hours reached"
                    )
                    break

                current_time = time.time()

                # If we have 7 articles in our window, check timing
                if len(request_times) == 7:
                    oldest_request = request_times[0]
                    time_since_oldest = current_time - oldest_request

                    # If less than 60 seconds have passed since oldest request
                    if time_since_oldest < WINDOW_SECONDS:
                        wait_time = WINDOW_SECONDS - time_since_oldest
                        logger.info(
                            f"Rate limit: waiting {wait_time:.2f}s to maintain max 28 requests/minute (7 articles)"
                        )
                        await asyncio.sleep(wait_time)

                # Record this article's timestamp
                request_times.append(time.time())

                # Process article
                success = await self.process_article(article)
                total_processed += 1
                if success:
                    logger.info(
                        f"Successfully processed article {article['id']}: {article['title']}"
                    )
                    successful_count += 1
                else:
                    logger.error(
                        f"Failed to process article {article['id']}: {article['title']}"
                    )
                    failed_count += 1

                if total_processed >= self.batch_size:
                    logger.info(f"Stopping as max limit reached of {self.batch_size}")
                    break

            return {
                "total_articles": len(articles),
                "successful": successful_count,
                "failed": failed_count,
            }

        except Exception as e:
            logger.error(f"Error in sentiment analysis run: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":

    async def main() -> None:
        start_time = int(time.time())
        service = SentimentAnalysisService(batch_size=100)
        result = await service.run_sentiment_analysis()
        run_duration = int(time.time() - start_time)
        duration_str = f"{run_duration // 60}m {run_duration % 60}s"

        message = (
            "🤖 *Sentiment Analysis Report* 🤖\n\n"
            f"📊 *Articles:* {result['total_articles']}\n"
            f"✅ *Successfully Processed:* {result['successful']}\n"
            f"❌ *Failed:* {result['failed']}\n"
            f"⏱ *Duration:* {duration_str}\n"
        )
        logger.info(message)

    asyncio.run(main())
