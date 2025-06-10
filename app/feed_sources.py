from dataclasses import dataclass
from typing import List


@dataclass
class FeedSource:
    id: str
    name: str
    url: str


# NOTE:
# If using this I would suggest giving a unique name to each feed source. 
class NewsFeedSources:
    """Class containing all news feed sources"""

    SOURCES: List[FeedSource] = [
        FeedSource(
            "Irish_Mirror",
            "Irish Mirror",
            "https://www.irishmirror.ie/?service=rss",
        ),
        FeedSource(
            "The_Journal",
            "The Journal",
            "https://www.thejournal.ie/feed/",
        ),
        FeedSource(
            "RTE_News",
            "RTE News",
            "https://www.rte.ie/feeds/rss/?index=/news",
        ),
        FeedSource(
            "BBC_News",
            "BBC News",
            "https://feeds.bbci.co.uk/news/rss.xml",
        ),
        FeedSource(
            "Irish_Independent_Top_Stories",
            "Irish Independent",
            "https://feeds.feedburner.com/ietopstories",
        ),
        FeedSource(
            "Irish_Independent_Ireland",
            "Irish Independent",
            "https://feeds.feedburner.com/ieireland",
        ),
        FeedSource(
            "Irish_Independent_Sport",
            "Irish Independent",
            "https://feeds.feedburner.com/iesport",
        ),
        FeedSource(
            "Irish_Independent_World",
            "Irish Independent",
            "https://feeds.feedburner.com/ieworld",
        ),
        FeedSource(
            "Irish_Independent_Business",
            "Irish Independent",
            "https://feeds.feedburner.com/iebusiness",
        ),
        FeedSource(
            "Irish_Independent_Lifestyle",
            "Irish Independent",
            "https://feeds.feedburner.com/ielifestyle",
        ),
        FeedSource(
            "Irish_Independent_Viewpoints",
            "Irish Independent",
            "https://feeds.feedburner.com/ieviewpoints",
        ),
        FeedSource(
            "Irish_Independent_Special_Reports",
            "Irish Independent",
            "https://feeds.feedburner.com/iespecialreports",
        ),
        FeedSource(
            "Irish_Independent_News",
            "Irish Independent",
            "https://www.independent.ie/rss/section/ada62966-6b00-4ead-a0ba-2c179a0730b0",
        ),
        FeedSource(
            "Breaking_News_Top_Stories",
            "Breaking News",
            "https://feeds.breakingnews.ie/bntopstories?format=xml",
        ),
        FeedSource(
            "Breaking_News_Ireland",
            "Breaking News",
            "https://feeds.breakingnews.ie/bnireland?format=xml",
        ),
        FeedSource(
            "Breaking_News_World",
            "Breaking News",
            "https://feeds.breakingnews.ie/bnworld",
        ),
        FeedSource(
            "Breaking_News_Business",
            "Breaking News",
            "https://feeds.breakingnews.ie/bnbusiness",
        ),
        FeedSource(
            "Breaking_News_Discover",
            "Breaking News",
            "https://feeds.breakingnews.ie/bndiscover",
        ),
        FeedSource(
            "Irish_Examiner",
            "Irish Examiner",
            "https://www.irishexaminer.com/feed/35-top_news.xml",
        ),
        FeedSource("Gript", "Gript", "https://gript.ie/feed/"),
        FeedSource("The_Irish_Sun", "The Irish Sun", "https://www.thesun.ie/feed/"),
        FeedSource("Evoke", "Evoke", "https://evoke.ie/feed"),
    ]

    @classmethod
    def get_all_sources(cls) -> List[FeedSource]:
        """Get all feed sources"""
        return cls.SOURCES
