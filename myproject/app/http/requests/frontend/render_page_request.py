from dataclasses import dataclass


@dataclass(frozen=True)
class RenderPageRequest:
    page_name: str
    entity_id: str | None

    @staticmethod
    def from_route_params(page_name="dashboard", entity_id=None):
        return RenderPageRequest(page_name=page_name, entity_id=entity_id)
