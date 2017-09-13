from unittest import TestCase
from TopRealityReader import WebsiteReader, EstateReadResult
from lxml import html
from unittest.mock import patch


class WebsiteReaderMock:
    def __init__(self):
        self.page_content = []

    def read_page_content(self, website):
        with open(website, "r", encoding='UTF8') as file:
            page = file.read()

        self.page_content = html.fromstring(page)
        return EstateReadResult.OK


class TestEstate(TestCase):
    def test_read_estates_websites(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateWebsite.html', "r") as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estates_websites(), EstateReadResult.OK)
        self.assertEqual(reader.estates_websites, ['estate_1', 'estate_2'])

    def test_read_estate_from_website_all_props(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateAllProps.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.OK)
        self.assertEqual(len(reader.estates), 1)
        self.assertEqual(reader.estates[0].title, 'Henka_Dom')
        self.assertEqual(reader.estates[0].price, '199.00')
        self.assertEqual(reader.estates[0].street, 'S N P')
        self.assertEqual(reader.estates[0].location, 'Detva')
        self.assertEqual(reader.estates[0].living_area, '10')
        self.assertEqual(reader.estates[0].area, '11')
        self.assertEqual(reader.estates[0].land, '12')
        self.assertEqual(reader.estates[0].new, 'new')

    def test_read_estate_from_website_necessary_props(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateNecessaryProps.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.OK)
        self.assertEqual(len(reader.estates), 1)
        self.assertEqual(reader.estates[0].title, 'no_title')
        self.assertEqual(reader.estates[0].price, '199.00')
        self.assertEqual(reader.estates[0].street, 'no_street')
        self.assertEqual(reader.estates[0].location, 'Detva')
        self.assertEqual(reader.estates[0].living_area, '10')
        self.assertEqual(reader.estates[0].area, 'no_area')
        self.assertEqual(reader.estates[0].land, 'no_land')
        self.assertEqual(reader.estates[0].new, 'old')

    def test_read_estate_from_website_wrong_price(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateWrongPrice.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.WRONG_PRICE)
        self.assertEqual(len(reader.estates), 0)

    def test_read_estate_from_website_no_price(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateWrongPriceDohodou.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.NO_PRICE)
        self.assertEqual(len(reader.estates), 0)

    def test_read_estate_from_website_wrong_location(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateWrongLocation.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.WRONG_LOCALITY)
        self.assertEqual(len(reader.estates), 0)

    def test_read_estate_from_website_wrong_living_area(self):
        reader = WebsiteReader()
        with open(r'./UnitTests/TestSites/readEstateWrongLivingArea.html', "r", encoding='UTF8') as file:
            page = file.read()

        reader.page_content = html.fromstring(page)
        self.assertEqual(reader.read_estate_from_website(), EstateReadResult.WRONG_LIVING_AREA)
        self.assertEqual(len(reader.estates), 0)

    @patch('TopRealityReader.WebsiteReader.read_page_content', new=WebsiteReaderMock.read_page_content)
    def test_read(self):
        reader = WebsiteReader()
        reader.website_first_part = './UnitTests/TestSites/read'
        reader.website_second_part = 'estate'
        reader.website_third_part = '.html'
        reader.types = [("dom", 1), ("byt", 2)]

        self.assertEqual(reader.read(), EstateReadResult.OK)
        self.assertEqual(len(reader.estates), 2)
