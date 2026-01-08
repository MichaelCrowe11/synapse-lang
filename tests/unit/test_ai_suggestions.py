import unittest

from synapse_lang.ai_suggestions import CodeAnalyzer, SuggestionType


class TestAISuggestionsResearchDiscovery(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()

    def test_research_discovery_pattern_is_suggested(self):
        line = "This research project improves discovery and communication."
        suggestions = self.analyzer._suggest_patterns(line, 0)

        pattern_suggestions = [
            s for s in suggestions if s.title == "Apply research_discovery pattern"
        ]
        self.assertTrue(pattern_suggestions)

        expected_keywords = {
            "research",
            "discovery",
            "insight",
            "publication",
            "communication",
            "dissemination",
        }
        self.assertTrue(
            any(
                keyword in expected_keywords
                for suggestion in pattern_suggestions
                for keyword in suggestion.keywords
            )
        )
        self.assertTrue(
            all(suggestion.type == SuggestionType.PATTERN for suggestion in pattern_suggestions)
        )
