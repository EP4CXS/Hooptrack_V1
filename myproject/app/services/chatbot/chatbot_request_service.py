from app.services.chatbot_service import ChatbotService


def chatbot_request_action_service(message, history=None, user=None):
    return ChatbotService.ask(message=message, history=history, user=user)
    