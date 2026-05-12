from app.services.auth.locations_cities_service import list_cities


def locations_cities_action(province_id):
    return list_cities(province_id)
