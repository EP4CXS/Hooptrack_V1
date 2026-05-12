from app.services.chatbot.chatbot_request_service import chatbot_request_action_service


def chatbot_request_action_controller(message, history=None, user=None):
    return chatbot_request_action_service(message=message, history=history, user=user)
