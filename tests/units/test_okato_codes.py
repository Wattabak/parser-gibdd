import unittest

from src.api.gibdd.okato import request_all_federal_okato
from src.api import all_okato_codes
from src.api import parse_federal_okato


class TestOkatoCodes(unittest.TestCase):
    def test_federal_codes(self) -> None:
        response = request_all_federal_okato()
        parsed = parse_federal_okato(response)
        print(parsed)

    def test_country_codes(self) -> None:
        countries = all_okato_codes()
        print(countries)


if __name__ == "__main__":
    unittest.main()
