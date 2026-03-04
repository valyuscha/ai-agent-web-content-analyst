"""
Analysis configuration value objects.
Immutable configuration for analysis runs.
"""
from dataclasses import dataclass
from enum import Enum


class AnalysisMode(str, Enum):
    """Analysis mode determines extraction strategy"""
    GENERAL = "General summary"
    STUDY_NOTES = "Study notes"
    PRODUCT_MARKETING = "Product/marketing analysis"
    TECHNICAL = "Technical tutorial extraction"
    
    def get_plan(self) -> str:
        """Get extraction plan for this mode"""
        plans = {
            self.STUDY_NOTES: "Extract key concepts, definitions, examples, and learning objectives",
            self.PRODUCT_MARKETING: "Extract value propositions, target audience, pricing, competitive advantages, and market positioning",
            self.TECHNICAL: "Extract setup steps, code examples, prerequisites, troubleshooting tips, and best practices",
            self.GENERAL: "Extract main ideas, supporting arguments, conclusions, and practical implications"
        }
        return plans.get(self, plans[self.GENERAL])


class Tone(str, Enum):
    """Output tone for generated content"""
    FORMAL = "formal"
    FRIENDLY = "friendly"
    
    def get_instructions(self) -> str:
        """Get tone-specific writing instructions"""
        if self == self.FORMAL:
            return "Write in a professional, business-appropriate style. Use markdown formatting: **bold** for emphasis, bullet points with -, numbered lists, and clear structure."
        else:
            return "Write for someone who has NEVER done content analysis before. Explain everything simply. Use everyday language. No technical terms. Make it clear and easy to understand!"


class Language(str, Enum):
    """Output language for generated content"""
    ENGLISH = "English"
    POLISH = "Polish"
    UKRAINIAN = "Ukrainian"
    RUSSIAN = "Russian"


@dataclass(frozen=True)
class AnalysisConfig:
    """Immutable analysis configuration"""
    mode: AnalysisMode
    tone: Tone
    language: Language
    
    @classmethod
    def create(cls, mode: str, tone: str, language: str) -> "AnalysisConfig":
        """Factory method with validation"""
        return cls(
            mode=AnalysisMode(mode),
            tone=Tone(tone),
            language=Language(language)
        )
    
    def get_extraction_plan(self) -> str:
        """Get extraction plan for current mode"""
        return self.mode.get_plan()
    
    def get_tone_instructions(self) -> str:
        """Get tone instructions for current tone"""
        return self.tone.get_instructions()
