from setuptools import setup

setup(
    name="changedetection.io-amazon-price-scraper",
    author="dgtlmoon",
    url='https://changedetection.io',
    author_email="dgtlmoon@gmail.com",
    version="1.0.0",
    packages=["cdio_amazon_restock_price_scraper"],
    install_requires=["changedetection.io", "price-parser", "beautifulsoup4"],
    python_requires=">= 3.10",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='amazon price restock detection notification price change alerts amazon.de',
    entry_points={
        "changedetectionio": [
            "cdio_amazon_restock_price_scraper = cdio_amazon_restock_price_scraper.plugin:restock_price_scraper",
        ],
        "changedetectionio.restock_price_scraper": [
            "cdio_amazon_restock_price_scraper = cdio_amazon_restock_price_scraper.plugin:restock_price_scraper",
        ],
    },
)
