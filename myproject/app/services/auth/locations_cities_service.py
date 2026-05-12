from .locations_regions_service import LOCATIONS


def list_cities(province_id):
    return LOCATIONS["cities"].get(int(province_id), [])
