import requests
from lxml import html
import re
from enum import Enum


class EstateReadResult(Enum):
    OK = 1
    WRONG_PRICE = 2
    WRONG_LIVING_AREA = 3
    WRONG_LOCALITY = 4
    WEBSITE_FAULT = 5
    NO_ESTATES = 6
    NO_ESTATE_WEBSITE = 7
    NO_PRICE = 8


class Estate:
    def __init__(self):
        self.type = []
        self.title = []
        self.price = []
        self.living_area = []
        self.area = []
        self.land = []
        self.street = []
        self.location = []
        self.new = []


class WebsiteReader:
    def __init__(self):
        self.website_first_part = 'https://www.topreality.sk/vyhladavanie-nehnutelnosti'
        self.website_second_part = '.html?searchType=string&cat=&form=1&type%5B%5D='
        self.website_third_part = '&obec=c600-Banskobystrick%C3%BD+kraj%2Cc100-Bratislavsk%C3%BD+kraj%2Cc800-' \
                                  'Ko%C5%A1ick%C3%BD+kraj%2Cc400-Nitriansky+kraj%2Cc700-Pre%C5%A1ovsk%C3%BD+kraj' \
                                  '%2Cc300-Tren%C4%8Diansky+kraj%2Cc200-Trnavsk%C3%BD+kraj%2Cc500-%C5%BDilinsk%C3%' \
                                  'BD+kraj&distance=&q=&cena_od=0&cena_do=0&vymera_od=0&vymera_do=0&n_search=' \
                                  'search&page=estate&gpsPolygon='

        self.types = [
            ('garsonka', 101),
            ('dvojgarsonka', 108),
            ('jednoizbovy_byt', 102),
            ('dvojizbovy_byt', 103),
            ('trojizbovy_byt', 104),
            ('stvorizbovy_byt', 105),
            ('pataviacizbovy_byt', 106),
            ('mezonet', 109),
            ('apartman', 110),
            ('chata', 201),
            ('chalupa', 202),
            ('rodinny_dom', 204),
            ('rodinna_vila', 205),
            ('usadlost', 206),
            ('administrativny_priestor', 401),
            ('obchodny_priestor', 402),
            ('restauracny_priestor', 403),
            ('sportovy_priestor', 404),
            ('vyrobny_priestor', 406),
            ('slkadovy_priestor', 407),
            ('opravarensky_priestor', 408),
            ('chovny_priestor', 409),
            ('najomny_dom', 301),
            ('administrativny_objekt', 302),
            ('polyfunkcny_objekt', 303),
            ('obchodny_objekt', 304),
            ('restauracia', 305),
            ('hotel_penzion', 306),
            ('kupelny_objekt', 307),
            ('sportovy_objekt', 308),
            ('vyrobny_objekt', 310),
            ('skladovy_objekt', 311),
            ('prevadzkovy_areal', 312),
            ('polnohospodarsky_objekt', 313),
            ('opravarensky_objekt', 314),
            ('cerpacia_stanica', 315),
            ('garaz', 317),
            ('hromadna_garaz', 318),
            ('spevnene_plochy', 319),
            ('mala_elektraren', 320),
            ('sportovisko_zavodisko', 321),
            ('historicky_objekt', 322),
            ('rekreacny_pozemok', 801),
            ('pozemok_rodinny_dom', 802),
            ('pozemok_bytovy_dom', 803),
            ('komercna_zona', 806),
            ('priemyslena_zona', 807),
            ('zahrada', 809),
            ('sad', 810),
            ('luka_pasienok', 811),
            ('orna_poda', 812),
            ('chmelnica_vinica', 813),
            ('lesna_poda', 814),
            ('vodna_plocha', 815),
            ('hrobove_miesto', 817)
        ]

        self.estates = []
        self.estates_websites = []
        self.page_content = None

    def read_page_content(self, website):
        request = requests.get(website)
        if request.status_code != 200:
            return EstateReadResult.WEBSITE_FAULT
        self.page_content = html.fromstring(request.text)

    def read_estates_websites(self):
        del self.estates_websites[:]
        estates = self.page_content.xpath("//div[@class='estate' or @class='estate estateOdd']")
        if not estates:
            return EstateReadResult.NO_ESTATES
        for estate in estates:
            estate_website = estate.xpath(".//child::a[@title]/@href")
            if not estate_website:
                return EstateReadResult.NO_ESTATE_WEBSITE
            self.estates_websites.append(estate_website[0])

        return EstateReadResult.OK

    def read_estate_price(self, estate):
        estate_price = self.page_content.xpath("//meta[@itemprop = 'price']/@content")

        if len(estate_price) != 1:
            return EstateReadResult.WRONG_PRICE

        if estate_price[0] == '0.00':
            return EstateReadResult.NO_PRICE

        estate.price = estate_price[0]
        return EstateReadResult.OK

    def read_estate_title(self, estate):
        estate_title = self.page_content.xpath("//head//title/text()")

        if not estate_title or len(estate_title) > 1:
            estate.title = 'no_title'
            return

        estate.title = estate_title[0].split('::')[0].strip()

    def read_estate_location(self, estate):
        estate_location = self.page_content.xpath("//span[text() = 'Lokalita']/parent::*//child::a/text()")

        if len(estate_location) != 1:
            return EstateReadResult.WRONG_LOCALITY

        estate.location = estate_location[0]
        return EstateReadResult.OK

    def read_estate_street(self, estate):
        estate_street = self.page_content.xpath("//span[text() = 'Ulica']/parent::*//child::strong/text()")

        if len(estate_street) != 1:
            estate.street = 'no_street'
            return

        estate.street = estate_street[0]

    def read_estate_living_area(self, estate):
        estate_area = self.page_content.xpath("//span[translate(text(),'Úžá', 'Uza') = 'Uzitkova plocha']"
                                              "/parent::*//child::strong/text()")
        if len(estate_area) != 1:
            return EstateReadResult.WRONG_LIVING_AREA

        estate_area[0] = re.sub("[^0-9]", "", estate_area[0])
        estate.living_area = estate_area[0]
        return EstateReadResult.OK

    def read_estate_area(self, estate):
        estate_area = self.page_content.xpath("//span[translate(text(),'á', 'a') = 'Zastavana plocha']"
                                              "/parent::*//child::strong/text()")
        if len(estate_area) != 1:
            estate.area = 'no_area'
            return

        estate_area[0] = re.sub("[^0-9]", "", estate_area[0])
        estate.area = estate_area[0]

    def read_estate_land(self, estate):
        estate_land = self.page_content.xpath("//span[text() = 'pozemok']/parent::*//child::strong/text()")
        if len(estate_land) != 1:
            estate.land = 'no_land'
            return

        estate_land[0] = re.sub("[^0-9]", "", estate_land[0])
        estate.land = estate_land[0]

    def read_estate_new(self, estate):
        estate_new = self.page_content.xpath("//span[translate(text(), 'ľ', 'l') = 'Stav nehnutelnosti:']"
                                             "/parent::*//child::strong/text()")

        if len(estate_new) != 1:
            estate.new = 'old'
            return

        estate.new = 'new'

    def read_estate_from_website(self):
        estate = Estate()
        result = self.read_estate_price(estate)
        if result != EstateReadResult.OK:
            if result == EstateReadResult.NO_PRICE:
                return EstateReadResult.NO_PRICE
            else:
                return EstateReadResult.WRONG_PRICE

        self.read_estate_title(estate)
        self.read_estate_street(estate)
        result = self.read_estate_location(estate)
        if result != EstateReadResult.OK:
            return EstateReadResult.WRONG_LOCALITY

        result = self.read_estate_living_area(estate)
        if result != EstateReadResult.OK:
            return EstateReadResult.WRONG_LIVING_AREA

        self.read_estate_area(estate)
        self.read_estate_land(estate)
        self.read_estate_new(estate)

        self.estates.append(estate)
        return EstateReadResult.OK

    def read(self):
        for estate_type, estate_id in self.types:
            page_number = ''
            riser = 1
            while True:
                result = self.read_page_content(self.website_first_part + page_number +
                                                self.website_second_part + str(estate_id) + self.website_third_part)
                if result != EstateReadResult.OK:
                    return EstateReadResult.WEBSITE_FAULT

                riser = riser + 1
                page_number = '-' + str(riser)

                result = self.read_estates_websites()
                if result != EstateReadResult.OK:
                    if result == EstateReadResult.NO_ESTATE_WEBSITE:
                        return EstateReadResult.NO_ESTATE_WEBSITE
                    else:
                        break

                for estate_website in self.estates_websites:
                    result = self.read_page_content(estate_website)
                    if result != EstateReadResult.OK:
                        return EstateReadResult.WEBSITE_FAULT

                    result = self.read_estate_from_website()
                    if result == EstateReadResult.WRONG_PRICE or result == EstateReadResult.WRONG_LOCALITY\
                            or result == EstateReadResult.WRONG_LIVING_AREA:
                        return result

                    if result == EstateReadResult.NO_PRICE:
                        continue

                    self.estates[-1].type = estate_type

        return EstateReadResult.OK
