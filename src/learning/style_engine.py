"""
LearningStyleEngine - Phase 11

Converts user learning styles into structured instructional guidance for the AI Council.
Supports 5 learning styles: visual, conversational, step_by_step, exam_focused, research_oriented.

Each style defines teaching methods, content focus, output preferences, and elements to avoid.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class InvalidLearningStyleError(Exception):
    """
    Raised when an invalid or unsupported learning style is requested.
    
    Example:
        raise InvalidLearningStyleError("Unknown learning style: 'kinesthetic'")
    """
    pass


# ============================================================================
# LEARNING STYLE ENUM
# ============================================================================

class LearningStyleType(str, Enum):
    """Enumeration of supported learning styles."""
    VISUAL = "visual"
    CONVERSATIONAL = "conversational"
    STEP_BY_STEP = "step_by_step"
    EXAM_FOCUSED = "exam_focused"
    RESEARCH_ORIENTED = "research_oriented"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class LearningStyleProfile:
    """
    Data model representing a learning style profile.
    
    Attributes:
        style (str): Name of the learning style
        teaching_methods (List[str]): Recommended teaching methods for this style
        content_focus (List[str]): What aspects of content to emphasize
        output_preferences (List[str]): How to structure and present output
        avoid (List[str]): Elements to avoid when teaching this style
    
    Example:
        >>> profile = LearningStyleProfile(
        ...     style="visual",
        ...     teaching_methods=["diagrams", "flowcharts", "visual analogies"],
        ...     content_focus=["relationships", "processes", "visual representation"],
        ...     output_preferences=["structured sections", "visual explanations"],
        ...     avoid=["large text blocks", "purely verbal descriptions"]
        ... )
    """
    style: str
    teaching_methods: List[str]
    content_focus: List[str]
    output_preferences: List[str]
    avoid: List[str]

    def to_dict(self) -> Dict:
        """Convert profile to dictionary format.
        
        Returns:
            Dict: Profile as a dictionary
        """
        return {
            "style": self.style,
            "teaching_methods": self.teaching_methods,
            "content_focus": self.content_focus,
            "output_preferences": self.output_preferences,
            "avoid": self.avoid
        }


# ============================================================================
# LEARNING STYLE ENGINE
# ============================================================================

class LearningStyleEngine:
    """
    Engine for managing and retrieving learning style profiles.
    
    Converts learning style names into structured instructional guidance used by
    the AI Council. Provides profiles for 5 distinct learning styles, each with
    specific teaching methods, content focus, output preferences, and elements to avoid.
    
    Attributes:
        styles (Dict[str, LearningStyleProfile]): Dictionary of all learning style profiles
    
    Example:
        >>> engine = LearningStyleEngine()
        >>> profile = engine.get_style_profile("visual")
        >>> print(profile.teaching_methods)
        ['diagrams', 'flowcharts', 'visual analogies', 'concept mapping', 'infographics']
        
        >>> styles = engine.list_supported_styles()
        >>> print(styles)
        ['visual', 'conversational', 'step_by_step', 'exam_focused', 'research_oriented']
    """

    def __init__(self):
        """Initialize the LearningStyleEngine with all supported learning styles."""
        self.styles: Dict[str, LearningStyleProfile] = self._initialize_styles()

    def _initialize_styles(self) -> Dict[str, LearningStyleProfile]:
        """
        Initialize all supported learning styles with their profiles.
        
        Returns:
            Dict[str, LearningStyleProfile]: Dictionary mapping style names to profiles
        """
        return {
            LearningStyleType.VISUAL.value: self._create_visual_profile(),
            LearningStyleType.CONVERSATIONAL.value: self._create_conversational_profile(),
            LearningStyleType.STEP_BY_STEP.value: self._create_step_by_step_profile(),
            LearningStyleType.EXAM_FOCUSED.value: self._create_exam_focused_profile(),
            LearningStyleType.RESEARCH_ORIENTED.value: self._create_research_oriented_profile(),
        }

    @staticmethod
    def _create_visual_profile() -> LearningStyleProfile:
        """
        Create the Visual Learning Style profile.
        
        Visual learners prefer diagrams, charts, and visual representations.
        They benefit from spatial organization and visual relationships.
        
        Returns:
            LearningStyleProfile: Visual learning style profile
        """
        return LearningStyleProfile(
            style="visual",
            teaching_methods=[
                "diagrams",
                "flowcharts",
                "visual analogies",
                "concept mapping",
                "infographics",
                "color-coded information",
                "spatial organization"
            ],
            content_focus=[
                "relationships between concepts",
                "visual structures and hierarchies",
                "process flows and sequences",
                "comparative visualizations",
                "patterns and arrangements"
            ],
            output_preferences=[
                "structured sections with visual breaks",
                "descriptions of diagrams and charts",
                "visual explanations of abstract concepts",
                "before/after comparisons",
                "clearly organized hierarchies"
            ],
            avoid=[
                "large text blocks without breaks",
                "purely verbal descriptions",
                "dense paragraphs",
                "lack of structural organization"
            ]
        )

    @staticmethod
    def _create_conversational_profile() -> LearningStyleProfile:
        """
        Create the Conversational Learning Style profile.
        
        Conversational learners prefer dialogue, discussion, and explanations
        delivered as if in a conversation. They benefit from narrative flow.
        
        Returns:
            LearningStyleProfile: Conversational learning style profile
        """
        return LearningStyleProfile(
            style="conversational",
            teaching_methods=[
                "dialogue and discussion",
                "storytelling",
                "real-world examples through narrative",
                "question-and-answer format",
                "conversational tone",
                "social context and relevance",
                "relatable scenarios"
            ],
            content_focus=[
                "practical applications",
                "real-world context and relevance",
                "how concepts connect to human experience",
                "social and interpersonal dimensions",
                "motivational aspects"
            ],
            output_preferences=[
                "conversational tone and voice",
                "explanations as if talking to a friend",
                "narrative structure",
                "questions that invite reflection",
                "relatable examples and stories"
            ],
            avoid=[
                "overly formal or academic tone",
                "abstract concepts without context",
                "lack of human interest or relevance",
                "purely theoretical treatment"
            ]
        )

    @staticmethod
    def _create_step_by_step_profile() -> LearningStyleProfile:
        """
        Create the Step-by-Step Learning Style profile.
        
        Step-by-step learners prefer sequential, procedural instruction where
        each step logically follows the previous one. They value clear progression.
        
        Returns:
            LearningStyleProfile: Step-by-step learning style profile
        """
        return LearningStyleProfile(
            style="step_by_step",
            teaching_methods=[
                "numbered sequential steps",
                "procedures and algorithms",
                "explicit prerequisites",
                "gradual complexity increase",
                "checkpoint verification",
                "hands-on practice at each level",
                "clear dependencies between steps"
            ],
            content_focus=[
                "logical progression",
                "procedural accuracy",
                "prerequisite knowledge",
                "cause-and-effect relationships",
                "skill building in sequence"
            ],
            output_preferences=[
                "numbered or clearly sequenced steps",
                "explicit prerequisite statements",
                "checkpoint summaries",
                "practice exercises after key concepts",
                "verification methods for each step"
            ],
            avoid=[
                "jumping between topics",
                "assuming prior knowledge",
                "vague sequencing",
                "overwhelming multiple concepts at once"
            ]
        )

    @staticmethod
    def _create_exam_focused_profile() -> LearningStyleProfile:
        """
        Create the Exam-Focused Learning Style profile.
        
        Exam-focused learners are motivated by testing, assessment, and measurable
        outcomes. They benefit from practice questions and clear success criteria.
        
        Returns:
            LearningStyleProfile: Exam-focused learning style profile
        """
        return LearningStyleProfile(
            style="exam_focused",
            teaching_methods=[
                "practice questions and quizzes",
                "test-taking strategies",
                "high-yield key concepts",
                "common exam patterns",
                "frequent self-assessment",
                "answer explanations",
                "performance tracking"
            ],
            content_focus=[
                "testable knowledge",
                "frequently tested concepts",
                "common misconceptions and tricks",
                "exam-relevant applications",
                "performance metrics"
            ],
            output_preferences=[
                "clear learning objectives with assessment criteria",
                "practice questions with detailed explanations",
                "summary of key testable points",
                "common wrong answers explained",
                "performance feedback and scoring"
            ],
            avoid=[
                "tangential information not on exams",
                "unclear assessment criteria",
                "vague learning objectives",
                "lack of practice opportunities"
            ]
        )

    @staticmethod
    def _create_research_oriented_profile() -> LearningStyleProfile:
        """
        Create the Research-Oriented Learning Style profile.
        
        Research-oriented learners are driven by curiosity, depth, and understanding
        sources. They benefit from citations, connections to research, and deep dives.
        
        Returns:
            LearningStyleProfile: Research-oriented learning style profile
        """
        return LearningStyleProfile(
            style="research_oriented",
            teaching_methods=[
                "source citations and references",
                "research methodology explanations",
                "connection to academic literature",
                "exploration of alternative theories",
                "evidence-based reasoning",
                "open questions and research frontiers",
                "critical analysis frameworks"
            ],
            content_focus=[
                "evidence and supporting research",
                "theoretical foundations and debates",
                "research methods and validation",
                "current understanding and limitations",
                "unanswered questions and frontiers"
            ],
            output_preferences=[
                "citations and source references",
                "research basis for claims",
                "discussion of evidence quality",
                "multiple perspectives and debates",
                "suggestions for further exploration"
            ],
            avoid=[
                "unsupported claims",
                "oversimplification of complex topics",
                "lack of evidence or citations",
                "ignoring alternative viewpoints"
            ]
        )

    def get_style_profile(self, style_name: str) -> LearningStyleProfile:
        """
        Retrieve the learning style profile for a specific style.
        
        Args:
            style_name (str): Name of the learning style
                Valid values: 'visual', 'conversational', 'step_by_step', 'exam_focused', 'research_oriented'
        
        Returns:
            LearningStyleProfile: The requested learning style profile
        
        Raises:
            InvalidLearningStyleError: If the style_name is not supported
        
        Example:
            >>> engine = LearningStyleEngine()
            >>> profile = engine.get_style_profile("visual")
            >>> print(profile.style)
            'visual'
            
            >>> profile = engine.get_style_profile("invalid_style")
            # Raises InvalidLearningStyleError: Unknown learning style: 'invalid_style'
        """
        if style_name not in self.styles:
            supported = ", ".join(self.list_supported_styles())
            raise InvalidLearningStyleError(
                f"Unknown learning style: '{style_name}'. "
                f"Supported styles are: {supported}"
            )
        return self.styles[style_name]

    def list_supported_styles(self) -> List[str]:
        """
        List all supported learning styles.
        
        Returns:
            List[str]: List of supported learning style names
        
        Example:
            >>> engine = LearningStyleEngine()
            >>> styles = engine.list_supported_styles()
            >>> print(styles)
            ['visual', 'conversational', 'step_by_step', 'exam_focused', 'research_oriented']
        """
        return list(self.styles.keys())

    def is_valid_style(self, style_name: str) -> bool:
        """
        Check if a learning style is valid and supported.
        
        Args:
            style_name (str): Name of the learning style to validate
        
        Returns:
            bool: True if the style is supported, False otherwise
        
        Example:
            >>> engine = LearningStyleEngine()
            >>> engine.is_valid_style("visual")
            True
            >>> engine.is_valid_style("kinesthetic")
            False
        """
        return style_name in self.styles

    def get_all_profiles(self) -> Dict[str, LearningStyleProfile]:
        """
        Retrieve all learning style profiles.
        
        Returns:
            Dict[str, LearningStyleProfile]: Dictionary of all learning style profiles
        
        Example:
            >>> engine = LearningStyleEngine()
            >>> profiles = engine.get_all_profiles()
            >>> print(len(profiles))
            5
        """
        return self.styles.copy()

    def get_style_as_dict(self, style_name: str) -> Dict:
        """
        Retrieve a learning style profile as a dictionary.
        
        Useful for serialization or API responses.
        
        Args:
            style_name (str): Name of the learning style
        
        Returns:
            Dict: Learning style profile as dictionary
        
        Raises:
            InvalidLearningStyleError: If the style_name is not supported
        
        Example:
            >>> engine = LearningStyleEngine()
            >>> profile_dict = engine.get_style_as_dict("visual")
            >>> print(profile_dict["style"])
            'visual'
        """
        profile = self.get_style_profile(style_name)
        return profile.to_dict()


# ============================================================================
# SAMPLE USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Example: Basic usage of LearningStyleEngine."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    # Initialize engine
    engine = LearningStyleEngine()
    
    # List supported styles
    print("\nSupported Learning Styles:")
    print(engine.list_supported_styles())
    
    # Get a specific style profile
    visual_profile = engine.get_style_profile("visual")
    print(f"\n{visual_profile.style.upper()} Learning Style Profile:")
    print(f"  Teaching Methods: {visual_profile.teaching_methods}")
    print(f"  Content Focus: {visual_profile.content_focus}")
    print(f"  Output Preferences: {visual_profile.output_preferences}")
    print(f"  Avoid: {visual_profile.avoid}")


def example_error_handling():
    """Example: Error handling for invalid styles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Error Handling")
    print("=" * 70)
    
    engine = LearningStyleEngine()
    
    try:
        invalid_profile = engine.get_style_profile("kinesthetic")
    except InvalidLearningStyleError as e:
        print(f"\n✗ Error caught: {e}")


def example_validation():
    """Example: Validating learning styles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Style Validation")
    print("=" * 70)
    
    engine = LearningStyleEngine()
    
    test_styles = ["visual", "conversational", "kinesthetic", "step_by_step"]
    print("\nValidating styles:")
    for style in test_styles:
        is_valid = engine.is_valid_style(style)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {style}: {status}")


def example_all_profiles():
    """Example: Retrieving all profiles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: All Profiles")
    print("=" * 70)
    
    engine = LearningStyleEngine()
    
    all_profiles = engine.get_all_profiles()
    print(f"\nTotal learning styles available: {len(all_profiles)}")
    
    for style_name, profile in all_profiles.items():
        print(f"\n  {style_name.upper()}:")
        print(f"    Teaching Methods: {len(profile.teaching_methods)} methods")
        print(f"    Content Focus Areas: {len(profile.content_focus)} areas")


def example_serialization():
    """Example: Serializing profiles to dictionary format."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Serialization to Dictionary")
    print("=" * 70)
    
    engine = LearningStyleEngine()
    
    profile_dict = engine.get_style_as_dict("exam_focused")
    print("\nExam-Focused Profile as Dictionary:")
    for key, value in profile_dict.items():
        print(f"  {key}:")
        if isinstance(value, list):
            for item in value:
                print(f"    - {item}")
        else:
            print(f"    {value}")


def example_ai_council_integration():
    """Example: Integration with AI Council (pseudo-code context)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: AI Council Integration Context")
    print("=" * 70)
    
    engine = LearningStyleEngine()
    
    # Pseudo-example of how this would be used in the AI Council
    user_learning_style = "visual"
    topic = "Photosynthesis"
    
    print(f"\nScenario: User wants to learn '{topic}' with '{user_learning_style}' style")
    
    style_profile = engine.get_style_profile(user_learning_style)
    
    print(f"\nInstructional Guidance for AI Models:")
    print(f"  ✓ Use these teaching methods: {', '.join(style_profile.teaching_methods[:3])}")
    print(f"  ✓ Focus on: {', '.join(style_profile.content_focus[:2])}")
    print(f"  ✓ Structure output as: {', '.join(style_profile.output_preferences[:2])}")
    print(f"  ✗ Avoid: {', '.join(style_profile.avoid[:2])}")
    
    print(f"\nThis guidance would be passed to GPT, Claude, Gemini, and DeepSeek")
    print(f"to generate specialized educational content tailored to '{user_learning_style}' learners.")


if __name__ == "__main__":
    """Run all example demonstrations."""
    example_basic_usage()
    example_error_handling()
    example_validation()
    example_all_profiles()
    example_serialization()
    example_ai_council_integration()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
