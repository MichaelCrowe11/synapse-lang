import unittest

from synapse_lang.ai_suggestions import CodeAnalyzer, SuggestionType


class TestAISuggestionsResearchDiscovery(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeAnalyzer()

    def test_research_discovery_pattern_is_suggested(self):
        line = "This research project improves discovery and communication."
        suggestions = self.analyzer._suggest_patterns(line, 0)

        self.assertTrue(
            any(s.title == "Apply research_discovery pattern" for s in suggestions)
        )

        research_suggestion = next(
            s for s in suggestions if "research" in s.keywords
        )
        self.assertEqual(research_suggestion.type, SuggestionType.PATTERN)

