from sightcall_scraping.domain.models.url import Url
from sightcall_scraping.domain.sitemap_parser import SitemapParser


def test_sitemap_parser_returns_all_urls(sitemap_xml):
    parser = SitemapParser()
    urls = parser.parse(sitemap_xml)
    expected_urls = [
        Url("https://sightcall.com/blog/"),
        Url("https://sightcall.com/blog/telecom-embrace-api-fication-trend-new-revenue/"),
    ]
    assert urls == expected_urls


def test_sitemap_parser_returns_all_sitemap_urls_from_index(sitemap_index_xml):
    parser = SitemapParser()
    sitemap_urls = parser.parse(sitemap_index_xml)
    expected_sitemap_urls = [
        Url("https://sightcall.com/post-sitemap.xml"),
        Url("https://sightcall.com/page-sitemap.xml"),
    ]
    assert sitemap_urls == expected_sitemap_urls
