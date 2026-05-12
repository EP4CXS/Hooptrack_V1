from django.test import SimpleTestCase
from rest_framework.serializers import ValidationError

from app.http.requests.chatbot_request import ChatbotRequest


class ChatbotRequestTests(SimpleTestCase):
    def test_from_request_data_accepts_message(self):
        dto = ChatbotRequest.from_request_data({"message": "hello"})
        self.assertEqual(dto.message, "hello")
        self.assertIsNone(dto.history)

    def test_from_request_data_rejects_blank_message(self):
        with self.assertRaises(ValidationError):
            ChatbotRequest.from_request_data({"message": "   "})

    def test_from_request_data_rejects_non_list_history(self):
        with self.assertRaises(ValidationError):
            ChatbotRequest.from_request_data({"message": "hello", "history": "bad"})
