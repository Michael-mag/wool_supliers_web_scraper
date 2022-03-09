import scrapy
from knitters_scraper.items import WoolItem
from dataclasses import dataclass
from typing import Any, Optional, Dict

SPECS_FILTERS = {
    "Marke": "brand",
    "Nadelstärke": "needle_size",
    "Zusammenstellung": "composition",
}

NAMES_AND_BRANDS = {
    "Natura XL": "DMC",
    "Safran": "Drops",
    "Baby Merino Mix": "Drops",
    "Alpacca Speciale": "Hahn",
    "Special double knit": "Stylecraft",
    "Special dk": "Stylecraft",
}

DELIVERY_INFO_PAGES = {
    "wollplatz.de": "https://www.wollplatz.de/versandkosten-und-lieferung",
}

BRAND_TAG_ELEMENT = 'itemprop="name">'
ACTUAL_PRICE_TAG_ELEMENT = '//div[@class="buy-price"]//span[@class="product-price-amount"]/text()'

@dataclass
class WoolSpecifications:
    brand: str
    composition: str
    needle_size: str

    @classmethod
    def get_filtered_wool_specifications_from_response(
        cls, response: Any
    ) -> "WoolSpecifications":
        table_rows = dict()
        specs = response.split("<tr>")[1:-1]

        for spec in specs:
            spec_split = spec.split("<td>")
            if len(spec_split) >= 2:
                spec_name = spec_split[1].split("</td>")[0]
            print(spec_name)
            if spec_name in SPECS_FILTERS.keys():
                spec_value_split = spec.split("<td>")
                if len(spec_value_split) > 2:
                    spec_value = spec_value_split[2].split("</td>")[0]
                    if spec_name == "Marke":
                        spec_value = spec_value.split(f"{BRAND_TAG_ELEMENT}")[1].split(
                            "</span>"
                        )[0]
                else:
                    spec_value = ""
                table_rows[SPECS_FILTERS[spec_name]] = spec_value
        return WoolSpecifications(**table_rows)


@dataclass
class DeliveryInfo:
    delivery_time: str
    delivery_price: Dict[str, str]
    site_name: str

    @classmethod
    def get_delivery_info_from_response(cls, site_name: str) -> "DeliveryInfo":
        pass


class ScrapWollplatzSpider(scrapy.Spider):
    name = "scrap_wollplatz"

    # add more allowed domains in this list
    # TODO: add more allowed domains from a config or settings file
    allowed_domains = ["wollplatz.de"]

    # TODO: add more start urls from a config or settings file
    # the following urls already have a filter applied from the website for the specified brands
    # NOTE: The brand Hahn was not found on the website, so it was removed from the list
    start_urls = [
        "https://www.wollplatz.de/wolle/dmc/dmc-natura-xl?sqr=dmc",
        "https://www.wollplatz.de/wolle/drops/drops-safran?sqr=safran",
        "https://www.wollplatz.de/wolle/drops/drops-baby-merino-mix?sqr=%20%20Baby%20Merino%20Mix",
        "https://www.wollplatz.de/wolle/stylecraft/stylecraft-special-dk"
    ]

    def parse(self, response: Any) -> WoolItem:

        # just extract all the wool_specs we need
        wool_specs_response = response.xpath(
            '//div[@id="pdetailTableSpecs"]//table'
        ).extract()
        wool_specifications = (
            WoolSpecifications.get_filtered_wool_specifications_from_response(
                wool_specs_response[0]
            )
        )

        # extract the name of the wool
        wool_name_response = response.xpath(
            '//h1[@id="pageheadertitle"]/text()'
        ).extract()[0]
        wool_name = self.get_wool_name(wool_name_response)

        if not wool_name:
            raise ValueError(
                f"No wool name found for {wool_name_response}.\n"
                "Please add the wool name and its respective brand to the NAMES_AND_BRANDS dictionary"
            )

        wool = WoolItem()

        # populate the wool item with the wool specifications
        wool["brand"] = wool_specifications.brand
        wool["name"] = wool_name

        # be sure to use the product-price-amount under buy price
        # if there is a discount, this would reflect here
        wool["price"] = response.xpath(ACTUAL_PRICE_TAG_ELEMENT).get()

        wool["needle_size"] = wool_specifications.needle_size
        wool["composition"] = wool_specifications.composition
        wool["delivery_time"] = DeliveryInfo.get_delivery_info_from_response(site_name=response.url.split(".")[1])

        return wool

    def get_wool_name(self, wool_name_response: str) -> Optional[str]:
        for name in NAMES_AND_BRANDS.keys():
            if name in wool_name_response:
                return name
        return None
