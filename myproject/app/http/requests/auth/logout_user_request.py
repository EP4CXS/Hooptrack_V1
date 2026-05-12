from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutUserRequest:
    payload: dict

    @staticmethod
    def from_request_data(data):
        return LogoutUserRequest(payload=dict(data))
