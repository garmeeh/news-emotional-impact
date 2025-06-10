from dataclasses import dataclass
from typing import List


@dataclass
class CategoryTag:
    name: str
    guidelines: List[str]

    def to_text(self) -> str:
        """Convert a single tag to text format."""
        guidelines_text = "\n   - " + "\n   - ".join(self.guidelines)
        return f"{self.name}{guidelines_text}"


class CategoryTags:
    """Class containing all category tags. Remember to add new tags to the list if database is updated."""

    CATEGORY_TAGS: List[CategoryTag] = [
        CategoryTag(
            "Cost of Living",
            [
                "Tag articles about rising prices, inflation, household expenses, and daily economic pressures facing average citizens."
            ],
        ),
        CategoryTag(
            "Housing Crisis",
            [
                "Use for stories about housing affordability, rent increases, mortgage issues, property shortages, or housing market challenges."
            ],
        ),
        CategoryTag(
            "Taxation Policy",
            [
                "For coverage of tax reforms, rates, disputes, or significant changes to personal/corporate taxation systems."
            ],
        ),
        CategoryTag(
            "Public Spending & Budgets",
            [
                "Tag articles about government spending, national budgets, deficit discussions, or public fund allocation."
            ],
        ),
        CategoryTag(
            "Elections & Campaigns",
            [
                "Use for election news, political campaigns, voting, polling data, and electoral process stories."
            ],
        ),
        CategoryTag(
            "Diplomacy & International Relations",
            [
                "For diplomatic meetings, international agreements, foreign policy, or relations between nations."
            ],
        ),
        CategoryTag(
            "Social Justice & Equality",
            [
                "Tag stories about civil rights, discrimination, protests, or discussions of race, gender, and LGBTQ+ issues."
            ],
        ),
        CategoryTag(
            "Immigration & Refugees",
            [
                "For articles about migration policies, border issues, asylum seekers, or immigration reform debates."
            ],
        ),
        CategoryTag(
            "Education Policy",
            [
                "Use for school reforms, educational funding, curriculum changes, or academic institution policies."
            ],
        ),
        CategoryTag(
            "Business & Corporate News",
            [
                "Tag stories about major companies, corporate strategies, business performance, or industry trends."
            ],
        ),
        CategoryTag(
            "Banking & Financial Services",
            [
                "For banking regulations, interest rates, lending practices, or financial institution developments."
            ],
        ),
        CategoryTag(
            "Startups & Entrepreneurship",
            [
                "Use for new ventures, funding rounds, startup ecosystem news, or entrepreneur profiles."
            ],
        ),
        CategoryTag(
            "Financial Markets & Investments",
            [
                "Tag market trends, stock performance, investment analysis, or trading patterns."
            ],
        ),
        CategoryTag(
            "Digital Economy & Cryptocurrencies",
            [
                "For cryptocurrency news, digital payments, online marketplaces, or virtual economic trends."
            ],
        ),
        CategoryTag(
            "Trade & Exports",
            [
                "Use for international trade, tariffs, trade agreements, or export/import developments."
            ],
        ),
        CategoryTag(
            "Tourism & Travel",
            [
                "Tag stories about tourism industry, travel trends, hospitality sector, or destination development."
            ],
        ),
        CategoryTag(
            "Artificial Intelligence & Automation",
            [
                "For AI developments, machine learning breakthroughs, or automation impact stories."
            ],
        ),
        CategoryTag(
            "Cybersecurity & Data Privacy",
            [
                "Use for data breaches, cyber attacks, privacy regulations, or digital security issues."
            ],
        ),
        CategoryTag(
            "Digital Privacy & Ethics",
            [
                "Tag ethical concerns about technology, digital rights, algorithmic bias, or tech regulation debates."
            ],
        ),
        CategoryTag(
            "Technology & Gadgets",
            [
                "For consumer technology, device launches, tech reviews, or hardware innovations."
            ],
        ),
        CategoryTag(
            "Space Exploration",
            [
                "Use for space missions, astronomical discoveries, aerospace industry, or space technology."
            ],
        ),
        CategoryTag(
            "Scientific Research & Discovery",
            [
                "Tag breakthrough studies, research findings, or scientific innovations not covered by other categories."
            ],
        ),
        CategoryTag(
            "Climate Change",
            [
                "For global warming news, climate policy, environmental impact, or climate science updates."
            ],
        ),
        CategoryTag(
            "Sustainability & Green Tech",
            [
                "Use for renewable energy, sustainable practices, green innovations, or environmental technology."
            ],
        ),
        CategoryTag(
            "Natural Disasters",
            [
                "Tag natural catastrophes, weather events, geological phenomena, or disaster response efforts."
            ],
        ),
        CategoryTag(
            "Pollution & Waste",
            [
                "For environmental contamination, waste management, recycling initiatives, or pollution control."
            ],
        ),
        CategoryTag(
            "Conservation & Wildlife",
            [
                "Use for wildlife protection, biodiversity, habitat preservation, or species conservation."
            ],
        ),
        CategoryTag(
            "Public Health & Outbreaks",
            [
                "Tag disease outbreaks, health emergencies, public health measures, or epidemic/pandemic news."
            ],
        ),
        CategoryTag(
            "Mental Health",
            [
                "For mental wellness coverage, psychological health services, or mental health awareness."
            ],
        ),
        CategoryTag(
            "Nutrition & Fitness",
            [
                "Use for diet trends, exercise science, wellness programs, or sports medicine."
            ],
        ),
        CategoryTag(
            "Healthcare Policy",
            [
                "Tag healthcare legislation, medical insurance, hospital policies, or healthcare system changes."
            ],
        ),
        CategoryTag(
            "Celebrity Gossip",
            [
                "For entertainment industry gossip, celebrity news, or public figure personal stories."
            ],
        ),
        CategoryTag(
            "Reality Shows",
            [
                "Use for reality TV news, show updates, contestant stories, or format changes."
            ],
        ),
        CategoryTag(
            "Arts & Culture",
            ["Tag fine arts, cultural events, museum news, or artistic achievements."],
        ),
        CategoryTag(
            "Awards & Festivals",
            [
                "For major awards ceremonies, cultural festivals, or industry recognition events."
            ],
        ),
        CategoryTag(
            "Major Leagues & Tournaments",
            [
                "Use for professional sports leagues, major competitions, or tournament coverage."
            ],
        ),
        CategoryTag(
            "Athlete Scandals & Contract News",
            [
                "Tag sports controversies, player transfers, contract negotiations, or athlete misconduct."
            ],
        ),
        CategoryTag(
            "Labor Action & Disputes",
            ["For strikes, labor protests, union activities, or workplace disputes."],
        ),
        CategoryTag(
            "Employment & Job Market",
            [
                "Use for job trends, unemployment data, workforce development, or labor market analysis."
            ],
        ),
        CategoryTag(
            "Consumer Rights & Product Recalls",
            [
                "Tag consumer protection, product safety issues, recalls, or consumer advocacy."
            ],
        ),
        CategoryTag(
            "Inventions & Patents",
            [
                "Use for new inventions, patent disputes, or innovative technological developments."
            ],
        ),
        CategoryTag(
            "Transportation",
            [
                "Tag transportation systems, vehicle innovations, transit policies, or mobility trends."
            ],
        ),
        CategoryTag(
            "Infrastructure & Development",
            [
                "For infrastructure projects, urban development, construction, or facility improvements."
            ],
        ),
        CategoryTag(
            "Agriculture & Farming",
            [
                "Use for agricultural news, farming practices, food production, or rural development."
            ],
        ),
        CategoryTag(
            "Food & Dining",
            [
                "Tag restaurant industry, culinary trends, food culture, or dining experiences."
            ],
        ),
        CategoryTag(
            "Family & Relationships",
            [
                "For family dynamics, relationship trends, parenting, or domestic life stories."
            ],
        ),
        CategoryTag(
            "Personal Finance & Money-Saving",
            [
                "Use for financial advice, savings strategies, personal investment, or money management."
            ],
        ),
        CategoryTag(
            "Personal Development & Self-Help",
            [
                "Tag self-improvement, career development, life coaching, or personal growth."
            ],
        ),
        CategoryTag(
            "Fashion & Trends",
            [
                "For fashion industry news, style trends, designer coverage, or clothing retail."
            ],
        ),
        CategoryTag(
            "Demographics & Population",
            [
                "Use for population trends, demographic shifts, census data, or societal changes."
            ],
        ),
        CategoryTag(
            "Urban Development & Housing",
            [
                "Tag urban planning, city development, housing projects, or community planning."
            ],
        ),
        CategoryTag(
            "Religion & Spirituality",
            [
                "For religious events, spiritual practices, faith communities, or religious conflicts."
            ],
        ),
        CategoryTag(
            "Political Scandals & Corruption",
            [
                "Tag political misconduct, corruption investigations, or government accountability stories."
            ],
        ),
        CategoryTag(
            "Legal & Justice System",
            [
                "For legal reforms, justice system news, court procedures, or judicial appointments."
            ],
        ),
        CategoryTag(
            "Organized Crime & Gangs",
            [
                "Use for criminal network activities, gang-related news, or organized crime investigations."
            ],
        ),
        CategoryTag(
            "Court Cases & Trials",
            [
                "Tag significant legal proceedings, high-profile trials, or important court decisions."
            ],
        ),
        CategoryTag(
            "Terrorism & Extremism",
            [
                "For terrorist activities, extremist groups, counter-terrorism, or radicalization stories."
            ],
        ),
        CategoryTag(
            "Energy Crisis",
            [
                "Use for energy supply issues, power shortages, fuel prices, or energy security concerns."
            ],
        ),
        CategoryTag(
            "Weapons & Military Tech",
            [
                "Tag defense technology, military equipment, arms development, or weapons systems."
            ],
        ),
        CategoryTag(
            "Esports",
            [
                "For competitive gaming, esports tournaments, gaming teams, or industry developments."
            ],
        ),
        CategoryTag(
            "Product Reviews & Comparisons",
            [
                "Tag articles reviewing consumer products, comparison guides, or 'best of' product lists."
            ],
        ),
        CategoryTag(
            "Shopping Guides & Deals",
            [
                "Tag articles about shopping sales, discount alerts, or buying guides for specific products."
            ],
        ),
        CategoryTag(
            "Sponsored Content & Promotions",
            [
                "For clearly marked sponsored articles, advertorial content, or promotional features."
            ],
        ),
        CategoryTag(
            "Product Launches",
            [
                "Use for new product announcements, launch events, or upcoming release coverage."
            ],
        ),
        CategoryTag(
            "Subscription Services",
            [
                "Tag reviews or news about streaming services, subscription boxes, or membership programs."
            ],
        ),
        CategoryTag(
            "Home & Garden Products",
            [
                "For reviews of household items, garden equipment, or home improvement products."
            ],
        ),
        CategoryTag(
            "Beauty & Cosmetics Reviews",
            [
                "Use for makeup reviews, skincare product evaluations, or beauty tool assessments."
            ],
        ),
        CategoryTag(
            "Gaming Hardware & Software",
            ["Tag reviews of gaming consoles, PC components, or video game releases."],
        ),
        CategoryTag(
            "Lifestyle Products",
            [
                "For reviews of wellness products, fitness gear, or lifestyle accessories."
            ],
        ),
        CategoryTag(
            "Affiliate Content",
            [
                "Use for articles containing multiple affiliate links or primarily focused on driving purchases."
            ],
        ),
        CategoryTag(
            "Tech Reviews",
            [
                "For detailed reviews of smartphones, laptops, tablets, or other consumer electronics."
            ],
        ),
        CategoryTag(
            "Automotive Reviews",
            [
                "Use for car reviews, vehicle comparisons, or automotive product evaluations."
            ],
        ),
    ]

    @classmethod
    def to_text_list(cls) -> str:
        """Output all category tags as a numbered text list."""
        text_items = []
        for i, tag in enumerate(cls.CATEGORY_TAGS, 1):
            text_items.append(f"{i}. {tag.to_text()}\n")
        return "\n".join(text_items)
