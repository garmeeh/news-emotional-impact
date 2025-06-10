from typing import List
import feedparser  # type: ignore
import logging
import json
from datetime import datetime
from pathlib import Path
from app.db import Database
from app.feed_sources import FeedSource, NewsFeedSources
from app.utils.html_mods import strip_html
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class FeedParserService:
    def __init__(self, store_json: bool = False):
        self.db = Database()
        self.store_json = store_json
        self.data_dir = Path("data")
        if store_json:
            self.data_dir.mkdir(exist_ok=True)

    async def parse_all_feeds(self) -> dict[str, str | int]:
        """
        Parse RSS/Atom feeds from various sources and store in database.
        Returns dict with status message and number of articles inserted.
        """
        sources: List[FeedSource] = NewsFeedSources.get_all_sources()
        logger.info(f"Starting to parse {len(sources)} feeds")
        logger.info(f"Sources: {sources}")

        total_articles: int = 0
        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for source in sources:
            logger.info(f"Parsing feed: {source.id}")
            d = feedparser.parse(source.url)

            if hasattr(d, "bozo_exception"):
                logger.error(f"Error parsing {source.id}: {d.bozo_exception}")
                error_count += 1
                continue

            if self.store_json:
                json_path: Path = self.data_dir / f"{source.id}.json"
                try:
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(d.entries, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved {len(d.entries)} entries to {json_path}")
                except Exception as e:
                    logger.error(f"Error saving JSON file for {source.id}: {str(e)}")

            logger.info(f"Found {len(d.entries)} articles in {source.id}")
            total_articles += len(d.entries)
            for entry in d.entries:
                title: str | None = getattr(entry, "title", None)
                url: str | None = getattr(entry, "link", None)
                description: str | None = getattr(entry, "description", None)

                # If no description, try to get content
                if not description:
                    content_array = getattr(entry, "content", [])
                    content = (
                        content_array[0].get("value", None) if content_array else None
                    )
                    if content:
                        description = strip_html(content)

                category: str | None = getattr(entry, "category", None)
                media_url: str | None = None

                # Media or thumbnail if available
                if hasattr(entry, "media_content"):
                    media: dict | None = (
                        entry.media_content[0] if entry.media_content else None
                    )
                    media_url = media["url"] if media else None
                elif hasattr(entry, "media_thumbnail"):
                    media_thumb: dict | None = (
                        entry.media_thumbnail[0] if entry.media_thumbnail else None
                    )
                    media_url = media_thumb["url"] if media_thumb else None

                # Parse date if present
                publish_date: str | None = None

                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        parsed_date = datetime(*entry.published_parsed[:6])
                        publish_date = parsed_date.isoformat()
                    except Exception as e:
                        logger.warning(
                            f"Error parsing published_parsed date. Error: {str(e)}"
                        )
                        publish_date = None

                # If title or url is missing, skip
                if not title or not url or not publish_date:
                    logger.warning(
                        f"Skipping article from {source.id} - missing required fields: {' and '.join(field for field, value in [('title', title), ('url', url), ('publish_date', publish_date)] if not value)}"
                    )
                    continue

                # Insert into DB
                try:
                    inserted_article = await self.db.insert_article(
                        title=title,
                        url=url,
                        description=description,
                        category=category,
                        media_url=media_url,
                        publish_date=publish_date,
                        source=source.name,
                    )

                    if inserted_article:
                        inserted_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error inserting article from {source.id}: {str(e)}")

        logger.info(
            f"Finished parsing feeds. Inserted {inserted_count} articles, skipped {skipped_count} articles, errors {error_count} out of {total_articles}"
        )
        return {
            "message": "Feeds parsed successfully",
            "articles_inserted": inserted_count,
            "articles_skipped": skipped_count,
            "articles_errors": error_count,
            "total_articles": total_articles,
        }


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        parser = FeedParserService(store_json=False)
        result: dict[str, str | int] = await parser.parse_all_feeds()

        message = (
            "📰 *Feed Parser Report* 📰\n\n"
            f"✅ *Successfully Inserted:* {result['articles_inserted']}\n"
            f"⏭️ *Skipped:* {result['articles_skipped']}\n"
            f"❌ *Errors:* {result['articles_errors']}\n"
            f"📊 *Total Articles:* {result['total_articles']}\n\n"
        )
        print(message)

    asyncio.run(main())
