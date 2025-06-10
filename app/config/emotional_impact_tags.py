from dataclasses import dataclass
from typing import List


@dataclass
class EmotionalImpactTag:
    name: str
    guidelines: List[str]

    def to_text(self) -> str:
        """Convert a single tag to text format."""
        guidelines_text = "\n   - " + "\n   - ".join(self.guidelines)
        return f"{self.name}{guidelines_text}"


class EmotionalImpactTags:
    """Class containing all emotional impact tags. Remember to add new tags to the list if database is updated."""

    EMOTIONAL_IMPACT_TAGS: List[EmotionalImpactTag] = [
        EmotionalImpactTag(
            "Relief / Reassurance",
            [
                "Content that resolves prior anxieties",
                "Updates providing solutions or improvements to concerning situations",
            ],
        ),
        EmotionalImpactTag(
            "Anxiety / Fear",
            [
                "Content that elicits worry, dread, or fear about potential threats, uncertainties, or future harm",
                "Focuses on immediate or anticipated personal safety concerns",
            ],
        ),
        EmotionalImpactTag(
            "Anger / Outrage",
            [
                "Stories that provoke strong frustration, hostility, or a sense of injustice in readers",
                "Includes reactions to unfairness, corruption, or abuse of power",
            ],
        ),
        EmotionalImpactTag(
            "Moral Outrage / Ethical Conflict",
            [
                "Content that challenges fundamental moral values or presents ethical dilemmas",
                "Stories involving complex moral choices or violations of deeply held principles",
            ],
        ),
        EmotionalImpactTag(
            "Stress / Overwhelm",
            [
                "Articles that could induce feelings of pressure, mental overload, or an inability to cope",
                "Coverage of systemic issues, cascading crises, or compounding problems",
            ],
        ),
        EmotionalImpactTag(
            "Sadness / Grief",
            [
                "Coverage of tragedy, loss of life, personal misfortunes, or heartbreaking stories",
                "Content that evokes deep emotional pain or mourning",
            ],
        ),
        EmotionalImpactTag(
            "Triggering / Traumatic",
            [
                "Content involving violence, abuse, severe accidents, or graphic details",
                "Stories that might re-traumatize readers with past experiences",
            ],
        ),
        EmotionalImpactTag(
            "Hopelessness / Despair",
            [
                "News that suggests a lack of solutions or an overwhelming negative outlook",
                "Content that leaves readers feeling powerless or dejected",
            ],
        ),
        EmotionalImpactTag(
            "Frustration / Helplessness",
            [
                "Stories highlighting systemic barriers or obstacles to change",
                "Content where clear solutions exist but implementation seems impossible",
            ],
        ),
        EmotionalImpactTag(
            "Cynicism / Distrust",
            [
                "Articles that may erode faith in institutions or societal systems",
                "Coverage that reveals systemic failures or institutional betrayal",
            ],
        ),
        EmotionalImpactTag(
            "Nostalgia / Loss of Past",
            [
                'Content that evokes longing for "better times"',
                "Stories highlighting significant cultural or societal changes",
            ],
        ),
        EmotionalImpactTag(
            "Social Connection / Belonging",
            [
                "Articles affecting readers' sense of community or group identity",
                "Content that strengthens or challenges social bonds",
            ],
        ),
        EmotionalImpactTag(
            "Guilt / Shame",
            [
                "Stories framed in ways that could induce self-blame or moral conflict",
                "Content addressing social or cultural taboos",
            ],
        ),
        EmotionalImpactTag(
            "Confusion / Uncertainty",
            [
                "Articles creating ambiguity or presenting conflicting information",
                "Content that leaves readers mentally unsettled or questioning",
            ],
        ),
        EmotionalImpactTag(
            "Curiosity / Wonder",
            [
                "Stories that spark intellectual or emotional engagement",
                "Content presenting novel discoveries or fascinating insights",
            ],
        ),
        EmotionalImpactTag(
            "Uplifting / Inspiring",
            [
                "Pieces with a hopeful or encouraging angle",
                "Stories featuring personal triumphs or positive community actions",
            ],
        ),
        EmotionalImpactTag(
            "Compassion / Empathy",
            [
                "Stories focusing on altruism and supportive communities",
                "Content encouraging emotional connection with others",
            ],
        ),
        EmotionalImpactTag(
            "Empowerment / Motivation",
            [
                "Articles highlighting personal agency and success stories",
                "Content providing actionable strategies for improvement",
            ],
        ),
    ]

    @classmethod
    def to_text_list(cls) -> str:
        """Output all emotional impact tags as a numbered text list."""
        text_items = []
        for i, tag in enumerate(cls.EMOTIONAL_IMPACT_TAGS, 1):
            text_items.append(f"{i}. {tag.to_text()}\n")
        return "\n".join(text_items)
