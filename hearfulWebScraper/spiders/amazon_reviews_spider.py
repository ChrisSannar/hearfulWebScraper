import scrapy
import random
import time

CSSSelectors = {
  'product_title' : "#productTitle::text",
  'product_price' : "#priceblock_ourprice::text",
  'product_sale' : ".priceBlockSavingsString::text", 
  'review_count' : "#acrCustomerReviewText::text",
}

XPathSelectors = {
  'product_brand': '//div[@id="productOverview_feature_div"]/div/table/tr/td[2]/span/text()',
  'next_product_price': '//div[@id="olp_feature_div"]/div[last()]/span[1]/a/span[2]/text()',
  'descriptions': '//div[@id="featurebullets_feature_div"]//li[not(@id)]/span/text()',
  'rating': '//span[@class="reviewCountTextLinkedHistogram noUnderline"]/@title'
}

headers_list = [
    # Firefox 77 Mac
     {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Chrome 83 Mac
    {
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    },
    # Chrome 83 Windows 
    {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

# Grab this list of sites to crawl
site_list_path = "./site_list.txt"
def get_sites():
  with open(site_list_path) as f:
    siteList = f.read()
    return siteList.splitlines()

class AmazonReviewsSpider(scrapy.Spider):
  name = "amazon_reviews"

  def start_requests(self):

    # Get the list of sites to crawl and parse the data for each
    urls = get_sites()
    headers = random.choice(headers_list)
    for url in urls:
      yield scrapy.Request(url=url, headers=headers, callback=self.initialParse)
  
  # Parses the main site page
  def initialParse(self, response):
    # Get each value we're after from the response
    productName = str.strip(response.css(CSSSelectors['product_title']).get())
    productBrand = str.strip(response.xpath(XPathSelectors['product_brand']).get())
    productPrice = self.scrapeProductPrice(response)
    productSale = self.scrapeProductSale(response)
    productDescrptions = self.scrapeProductDescrptions(response)
    productRating = self.scrapeProductRating(response)
    productReviewCount = int(response.css(CSSSelectors['review_count']).get().split(' ', 1)[0])

    product = AmazonItem(productName, productBrand, "amazon", productPrice, productSale, productDescrptions, productRating)
    
    print("-----------------------------------------------")
    print(product)
    print("-----------------------------------------------")

  # Pull the price from the response and returns it as a float
  def scrapeProductPrice(self, response):
    
    # See if it's there initially
    productPrice = response.css(CSSSelectors['product_price']).get()

    # If we don't find it using css, try xpath
    if productPrice == None:
      productPrice = response.xpath(XPathSelectors['next_product_price']).get()

    # If we still can't find it, then just give a negative value
    if productPrice == None:
      productPrice = "$-1.0"
    
    return float(productPrice[1:])

  # Pull the sale savings from the response and returns it as a float
  def scrapeProductSale(self, response):
    productSale = response.css(CSSSelectors['product_sale']).get()

    # If there is no product sale, return -1.0
    if productSale == None:
      return -1.0
    else:
      # Just pull the amount from the string we got
      cleaned = str.strip(productSale) 
      return float(cleaned[1:cleaned.index(" ")])
  
  # Pull the descriptions from the response and return a trimed version of them
  def scrapeProductDescrptions(self, response):
    descriptions = response.xpath(XPathSelectors['descriptions']).getall() 
    def trim(string):
      return str.strip(string)
    return map(trim, descriptions)

  # Pull the rating text from the response and return a float of the rating number
  def scrapeProductRating(self, response):
    rating = response.xpath(XPathSelectors['rating']).get()
    return float(rating[0:rating.index(" ")])


# A single amazon item we are reviewing
class AmazonItem:

  def __init__(self, name="", brand="", source="", price=0.0, sale=0.0, descriptions=[], rating=0.0, reviews=[]):
    self._name = name
    self._brand = brand
    self._source = source
    self._price = price
    self._sale = sale
    self._descriptions = descriptions
    self._rating = rating
    self._reviews = reviews

  # Encapsulation
  def getName(self):
    return self._name

  def getBrand(self):
    return self._brand

  def getSource(self):
    return self._source

  def getPrice(self):
    return self._price

  def getSalePrice(self):
    return self._sale

  def getDescriptions(self):
    return self._descriptions

  def getRating(self):
    return self._rating

  def getReviews(self):
    return self._reviews
  
  def __str__(self):
    return "{name} ({brand}) - ${price} (${sale}) {rating}/5 ".format(name=self._name, brand=self._brand, price=self._price, sale=self._sale, rating=self._rating)