from typing import Optional, Dict, Any, List
import logging
from app.config.settings import settings
from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.utils.html_mods import strip_html

logger = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        """Initialize Supabase client with environment variables."""
        self.supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY,
        )

    async def insert_article(
        self,
        title: str,
        url: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        media_url: Optional[str] = None,
        publish_date: Optional[str] = None,
        source: str = "Unknown",
    ) -> Optional[Dict[str, Any]]:
        """Insert a news article into the news_articles table.

        Args:
            title: Article title
            url: Article URL (must be unique)
            description: Article description (HTML will be stripped)
            category: Article category, defaults to "UNKNOWN"
            media_url: URL of associated media content
            publish_date: Publication date of the article
            source: Source of the article, defaults to "Unknown"

        Returns:
            Dict[str, Any] | None: The inserted article data if successful, None if duplicate URL

        Raises:
            APIError: If there's an API error other than duplicate URL
        """

        try:
            article_data = {
                "title": title.strip(),
                "url": url.strip(),
                "description": strip_html(description),
                "category": category.strip() if category else "UNKNOWN",
                "media_url": media_url.strip() if media_url else None,
                "publish_date": publish_date,
                "source": source.strip() if source else "Unknown",
            }

            response = (
                self.supabase.table("news_articles").insert(article_data).execute()
            )

            return response.data[0] if response.data else None

        except APIError as e:
            # PostgreSQL error code for unique_violation is '23505'
            if hasattr(e, "code") and e.code == "23505":
                logger.info(f"Duplicate article found: {url}")
                return None
            raise

    async def insert_article_sentiment(
        self,
        news_article_id: int,
        sentiment_label: str,
        sentiment_confidence: int,
        clickbait_level: int,
        version_info: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Insert sentiment analysis results for a news article.

        Args:
            news_article_id: ID of the news article
            sentiment_label: The sentiment label (e.g. positive, negative)
            sentiment_confidence: Confidence score (0-100)
            clickbait_level: Clickbait score (0-10)
            version_info: JSONB object containing node results and prompt configs

        Returns:
            Dict[str, Any] | None: The inserted sentiment data if successful
        """

        try:
            sentiment_data = {
                "news_article_id": news_article_id,
                "sentiment_label": sentiment_label,
                "sentiment_confidence": sentiment_confidence,
                "clickbait_level": clickbait_level,
                "version_info": version_info,
            }

            logger.info("Inserting sentiment data", extra={"data": sentiment_data})

            response = (
                self.supabase.table("news_article_sentiments")
                .insert(sentiment_data)
                .execute()
            )

            return response.data[0] if response.data else None
        except APIError as e:
            logger.error(f"Error inserting article sentiment: {e}")
            raise

    async def insert_emotional_impact_tags(
        self,
        news_article_sentiment_id: int,
        primary_tag: str,
        secondary_tags: list[str],
    ) -> None:
        """Insert emotional impact tags for a news article sentiment.

        Args:
            news_article_sentiment_id: ID of the news article sentiment
            primary_tag: The primary emotional impact tag
            secondary_tags: List of secondary emotional impact tags
        """
        try:
            # First ensure all tags exist in emotional_impact_tags table
            all_tags = [primary_tag] + secondary_tags

            # Get tag IDs
            response = (
                self.supabase.table("emotional_impact_tags")
                .select("id, tag_name")
                .in_("tag_name", all_tags)
                .execute()
            )

            tag_id_map = {tag["tag_name"]: tag["id"] for tag in response.data}

            # Insert relationships
            for tag_name in all_tags:
                tag_id = tag_id_map.get(tag_name)
                if tag_id:
                    self.supabase.table("news_article_emotional_impact").insert(
                        {
                            "news_article_sentiment_id": news_article_sentiment_id,
                            "emotional_impact_tag_id": tag_id,
                            "is_primary": tag_name == primary_tag,
                        }
                    ).execute()

        except APIError as e:
            logger.error(f"Error inserting emotional impact tags: {e}")
            raise

    async def insert_category_tags(
        self,
        news_article_sentiment_id: int,
        primary_tag: str,
        secondary_tags: list[str],
    ) -> None:
        """Insert category tags for a news article.

        Args:
            news_article_sentiment_id: ID of the news article sentiment
            primary_tag: The primary category tag
            secondary_tags: List of secondary category tags
        """
        try:
            all_tags = [primary_tag] + secondary_tags

            # Get tag IDs
            response = (
                self.supabase.table("category_tags")
                .select("id, tag_name")
                .in_("tag_name", all_tags)
                .execute()
            )

            tag_id_map = {tag["tag_name"]: tag["id"] for tag in response.data}

            # Insert relationships
            for tag_name in all_tags:
                tag_id = tag_id_map.get(tag_name)
                if tag_id:
                    self.supabase.table("news_article_tags").insert(
                        {
                            "news_article_sentiment_id": news_article_sentiment_id,
                            "category_tag_id": tag_id,
                            "is_primary": tag_name == primary_tag,
                        }
                    ).execute()

        except APIError as e:
            logger.error(f"Error inserting category tags: {e}")
            raise

    async def get_articles_without_sentiment(
        self, limit: int = 100, created_after: Optional[str] = "2024-12-31T00:00:00Z"
    ) -> List[Dict[str, Any]]:
        """
        Get news articles that do not have associated sentiment analysis records,
        were created after a given timestamp, and are not marked as hidden.

        Args:
            created_after (datetime): Only return articles created after this timestamp.
            row_limit (int): Maximum number of articles to return.

        Returns:
            List[Dict[str, Any]]: List of news articles matching the criteria.
        """

        try:
            logger.info(f"Getting {limit} articles without sentiment")
            response = (
                self.supabase.rpc(
                    "get_unlinked_articles",
                    {
                        "created_after": created_after,
                        "row_limit": limit,
                    },
                )
                .limit(limit)
                .execute()
            )

            logger.info(f"Articles without sentiment: {len(response.data)}")
            return response.data if response.data else []

        except APIError as e:
            logger.error(f"Error fetching articles without sentiment: {e}")
            raise

    async def get_latest_articles(
        self,
        limit: int = 500,
        created_after: Optional[str] = "2024-12-31T00:00:00Z",
    ) -> List[Dict[str, Any]]:
        """Get the latest news articles, optionally including sentiment analysis.

        Args:
            limit: Maximum number of articles to return (defaults to 5)

        Returns:
            List[Dict[str, Any]]: List of latest articles matching the criteria

        Raises:
            APIError: If there's an error fetching the articles
        """
        try:
            query = (
                self.supabase.table("news_articles")
                .select("*")
                .order("created_at", desc=True)
                .gte("created_at", created_after)
                .limit(limit)
            )

            response = query.execute()

            return response.data if response.data else []

        except APIError as e:
            logger.error(f"Error fetching latest articles: {e}")
            raise
