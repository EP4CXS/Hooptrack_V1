from app.services.frontend.render_page_service import render_page_context_service


def render_page_action_controller(page_name="dashboard", entity_id=None):
    return render_page_context_service(page_name=page_name, entity_id=entity_id)
