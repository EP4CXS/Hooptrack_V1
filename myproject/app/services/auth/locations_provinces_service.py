from .locations_regions_service import LOCATIONS


def list_provinces(region_id):
    return LOCATIONS["provinces"].get(int(region_id), [])
