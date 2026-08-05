# Amazon Price Scraper Plugin for changedetection.io

An enhanced **Restock & Price Detection** scraper plugin for [changedetection.io](https://changedetection.io). 

This plugin extracts prices and stock availability from Amazon product pages (including **amazon.de**, **amazon.com**, **amzn.eu**, **amazon.co.uk**, etc.) and feeds structured price data into the changedetection.io engine.

---

## Features & Improvements

- **Full Amazon.de & European Support**: Supports German/European price formats (`12,99 €`, `1.499,95 €`) as well as US formats (`$12.99`).
- **Modern Selector Cascade**: Extracts prices from current Amazon desktop/mobile DOM layouts:
  - `#corePriceDisplay_desktop_feature_div span.a-offscreen`
  - `#corePrice_desktop span.a-offscreen`
  - `#corePrice_feature_div span.a-offscreen`
  - `.apexPriceToPay span.a-offscreen`
  - `span.a-price.aok-align-center span.a-offscreen`
  - `span.a-price span.a-offscreen`
  - `#priceblock_ourprice`, `#priceblock_dealprice`, `#price_inside_buybox`
  - Structured `span.a-price-whole` & `span.a-price-fraction` parsing.
  - Regex fallback for localized currency formatting.
- **Pluggy Hook Compliance**:
  - Implements `get_itemprop_availability_override` (used by `changedetectionio.pluggy_interface`) returning `{ 'price': float, 'availability': 'in stock', 'currency': 'EUR'|'USD' }`.
  - Implements `scrape_price_restock` for legacy compatibility.
  - Decorator `@staticmethod` ensures smooth execution without `TypeError` missing `self` positional arguments.

---

## Plugin Architecture & Extension Guide

If you need to extend or update this scraper in the future:

### File Structure
- `cdio_amazon_restock_price_scraper/plugin.py`: Contains the `restock_price_scraper` class with `@staticmethod` hook implementations.
- `setup.py`: Entry points registered under both `changedetectionio` and `changedetectionio.restock_price_scraper`.

### How changedetection.io calls this plugin
When changedetection runs the `restock_diff` processor on an Amazon URL:
1. `get_itemprop_availability_from_plugin` in `pluggy_interface.py` triggers `plugin_manager.hook.get_itemprop_availability_override(...)`.
2. `restock_price_scraper.get_itemprop_availability_override` evaluates the URL and HTML content using `BeautifulSoup` and `price_parser.Price`.
3. The extracted price is returned as a float in the dictionary:
   ```python
   {
       'price': 19.99,
       'availability': 'in stock',
       'currency': 'EUR'
   }
   ```
4. Changedetection updates `update_obj['restock']` and triggers price alerts/notifications.

---

## Configuration & Usage in changedetection.io

1. **Fetch Method**: Set the Watch **Fetch Method** to **`Use Chrome / WebDriver`** (Amazon renders price elements dynamically with JS).
2. **Processor Mode**: Set the Watch **Processor** to **`Restock & Price`** and enable **`Follow price changes`**.
3. **Notification Templates**: Use variables such as:
   - `{{restock.price}}` - Current extracted price
   - `{{restock.in_stock}}` - Stock status (`True`/`False`)
   - `{{restock.original_price}}` - Previous price

---

## License

Apache-2.0
