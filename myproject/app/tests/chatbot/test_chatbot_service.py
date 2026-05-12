from django.test import SimpleTestCase, override_settings
from unittest.mock import MagicMock, patch

from app.services.chatbot_service import ChatbotService
from app.services.groq_completion import groq_is_configured


def _mock_authenticated_user():
    user = MagicMock()
    user.is_authenticated = True
    user.profile = MagicMock(municipality="Testville")
    return user


class ChatbotServiceTests(SimpleTestCase):
    @override_settings(GROQ_API_KEY="")
    def test_uses_fallback_when_groq_not_configured(self):
        data = ChatbotService.ask("How do I create a team?")
        self.assertIn("reply", data)
        self.assertEqual(data.get("model"), "fallback-rules")

    @override_settings(GROQ_API_KEY="test-api-key")
    def test_groq_is_configured_helper(self):
        self.assertTrue(groq_is_configured())

    @override_settings(GROQ_API_KEY="")
    def test_groq_is_configured_false_when_empty(self):
        self.assertFalse(groq_is_configured())

    @override_settings(GROQ_API_KEY="test-api-key")
    @patch("app.services.chatbot_service.groq_chat_completion")
    def test_ask_uses_groq_when_key_set(self, mock_groq):
        mock_groq.return_value = {"content": "Groq assistant reply.", "model": "openai/gpt-oss-20b"}
        data = ChatbotService.ask("Explain the predictions page briefly.")
        self.assertEqual(data.get("reply"), "Groq assistant reply.")
        self.assertEqual(data.get("model"), "openai/gpt-oss-20b")
        mock_groq.assert_called_once()

    @patch('app.models.basketball.models.Player.objects.filter')
    def test_player_count_query(self, mock_filter):
        mock_qs = MagicMock()
        mock_qs.count.return_value = 5
        mock_filter.return_value = mock_qs
        user = _mock_authenticated_user()
        data = ChatbotService.ask("How many players are registered?", user=user)
        self.assertIn("reply", data)
        self.assertEqual(data.get("model"), "db-player-count")
        self.assertIn("5 player", data.get("reply"))

    @patch('app.models.basketball.models.Player.objects.filter')
    def test_player_count_query_variations(self, mock_filter):
        mock_qs = MagicMock()
        mock_qs.count.return_value = 3
        mock_filter.return_value = mock_qs
        user = _mock_authenticated_user()
        test_queries = [
            "player count",
            "total players",
            "number of players",
            "players registered",
            "registered players",
        ]
        for query in test_queries:
            with self.subTest(query=query):
                data = ChatbotService.ask(query, user=user)
                self.assertEqual(data.get("model"), "db-player-count")
                self.assertIn("3 player", data.get("reply"))

    def test_player_count_requires_auth(self):
        data = ChatbotService.ask("How many players are registered?", user=None)
        self.assertEqual(data.get("model"), "db-player-count-auth-required")
        self.assertIn("Sign in", data.get("reply", ""))
