from django.shortcuts import render

from app.controllers.frontend.render_page_controller import render_page_action_controller
from app.http.requests.frontend.render_page_request import RenderPageRequest


def page_view(request, page_name="dashboard", entity_id=None):
    dto = RenderPageRequest.from_route_params(page_name=page_name, entity_id=entity_id)
    context = render_page_action_controller(page_name=dto.page_name, entity_id=dto.entity_id)
    return render(
        request,
        "app/index.html",
        context,
    )

