from django.test import SimpleTestCase

from app.services.auth.locations_cities_service import list_cities
from app.services.auth.locations_provinces_service import list_provinces
from app.services.auth.locations_regions_service import list_regions


class LocationsServicesTests(SimpleTestCase):
    def test_list_regions_has_expected_seed_data(self):
        rows = list_regions()
        self.assertGreaterEqual(len(rows), 3)

    def test_list_provinces_for_known_region(self):
        rows = list_provinces(1)
        self.assertGreater(len(rows), 0)

    def test_list_cities_for_known_province(self):
        rows = list_cities(11)
        self.assertGreater(len(rows), 0)
