from app.services.auth.locations_provinces_service import list_provinces


def locations_provinces_action(region_id):
    return list_provinces(region_id)
