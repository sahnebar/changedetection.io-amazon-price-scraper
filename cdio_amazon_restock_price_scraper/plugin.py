import re
from typing import Dict, Optional
from pluggy import HookimplMarker
from bs4 import BeautifulSoup
from price_parser import Price

hookimpl_cdio = HookimplMarker("changedetectionio")
hookimpl_restock = HookimplMarker("changedetectionio.restock_price_scraper")

class restock_price_scraper(object):

    @staticmethod
    @hookimpl_cdio
    @hookimpl_restock
    def get_itemprop_availability_override(content: str, fetcher_name: str, fetcher_instance, url: str, llm_intent=None) -> Optional[Dict]:
        """
        Custom implementation of get_itemprop_availability for Amazon pages (amazon.de, amazon.com, amzn.eu, etc.).
        """
        url_lower = (url or '').lower()
        is_amazon = bool(re.search(r'https?://([^/]+\.)?(amazon\.[a-z\.]+|amzn\.[a-z]+)', url_lower)) or ('amazon.' in url_lower) or ('amzn.' in url_lower)

        if not is_amazon:
            return None

        soup = BeautifulSoup(content, 'html.parser')
        price = restock_price_scraper._extract_amazon_price(soup)

        if price is not None:
            return {
                'price': price,
                'availability': 'in stock',
                'currency': 'EUR' if ('amazon.de' in url_lower or '€' in content) else 'USD'
            }
        return None

    @staticmethod
    @hookimpl_cdio
    @hookimpl_restock
    def scrape_price_restock(watch, html_content: str, screenshot: bytes, update_obj: Dict) -> Dict:
        """
        Legacy hook implementation for changedetection.io.
        """
        url = (watch.get("url") or "").lower()
        is_amazon = bool(re.search(r"https?://([^/]+\.)?(amazon\.[a-z\.]+|amzn\.[a-z]+)", url)) or ("amazon." in url) or ("amzn." in url)

        if is_amazon:
            if not update_obj.get("restock", {}).get("price"):
                if "restock" not in update_obj or not isinstance(update_obj["restock"], dict):
                    update_obj["restock"] = {}

                soup = BeautifulSoup(html_content, "html.parser")
                extracted_price = restock_price_scraper._extract_amazon_price(soup)

                if extracted_price is not None:
                    update_obj["restock"]["price"] = float(extracted_price)
                    update_obj["restock"]["in_stock"] = True

        return update_obj

    @staticmethod
    def _extract_amazon_price(soup: BeautifulSoup) -> Optional[float]:
        """
        Extract price matching modern Amazon HTML structures (amazon.de, amazon.com, etc.).
        """
        selectors = [
            "#corePriceDisplay_desktop_feature_div span.a-offscreen",
            "#corePrice_desktop span.a-offscreen",
            "#corePrice_feature_div span.a-offscreen",
            ".apexPriceToPay span.a-offscreen",
            "span.a-price.aok-align-center span.a-offscreen",
            "span.a-price span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#price_inside_buybox",
            "#buyBoxAccordion span.a-price span.a-offscreen",
            ".sns-base-price span.a-offscreen"
        ]

        for selector in selectors:
            for elem in soup.select(selector):
                text = elem.text.strip()
                if text:
                    p = Price.fromstring(text)
                    if p and p.amount_float is not None:
                        return float(p.amount_float)

        price_container = soup.find("span", class_="a-price")
        if price_container:
            whole_elem = price_container.find("span", class_="a-price-whole")
            fraction_elem = price_container.find("span", class_="a-price-fraction")
            if whole_elem:
                whole_str = whole_elem.text.strip().rstrip(",.").replace(".", "").replace(",", "")
                fraction_str = fraction_elem.text.strip().rstrip(",.") if fraction_elem else "00"
                if whole_str and whole_str.isdigit():
                    try:
                        return float(f"{whole_str}.{fraction_str}")
                    except ValueError:
                        pass

        price_match = re.search(r"(\d{1,3}(?:\.\d{3})*|\d+)[,\.](\d{2})\s*€|€\s*(\d{1,3}(?:\.\d{3})*|\d+)[,\.](\d{2})", soup.text)
        if price_match:
            groups = [g for g in price_match.groups() if g is not None]
            if len(groups) >= 2:
                whole = groups[0].replace(".", "")
                frac = groups[1]
                try:
                    return float(f"{whole}.{frac}")
                except ValueError:
                    pass

        return None
