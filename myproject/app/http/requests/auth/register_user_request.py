from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserRequest:
    payload: dict

    @staticmethod
    def from_request_data(data):
        return RegisterUserRequest(payload=dict(data))
