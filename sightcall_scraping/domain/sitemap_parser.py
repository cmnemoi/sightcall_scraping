from typing import List
from xml.etree import ElementTree as ET

from .models.url import Url


class SitemapParser:
    def parse(self, sitemap_xml: str) -> List[Url]:
        root = ET.fromstring(sitemap_xml)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        if root.tag.endswith("urlset"):
            locations = root.findall(".//ns:loc", namespace)
        elif root.tag.endswith("sitemapindex"):
            locations = root.findall(".//ns:loc", namespace)
        else:
            locations = []
        return [Url(location.text) for location in locations if location.text is not None]
