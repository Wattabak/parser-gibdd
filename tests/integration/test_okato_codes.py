import unittest

from lib.okato_codes import req_federal_okato_codes, parse_federal_okato, country_okato_codes


class TestOkatoCodes(unittest.TestCase):
    def test_federal_codes(self) -> None:
        response = req_federal_okato_codes()
        parsed = parse_federal_okato(response)
        print(parsed)

    def test_country_codes(self) -> None:
        countries = country_okato_codes()
        print(countries)
        self.assertIs(False)


if __name__ == "__main__":
    unittest.main()
