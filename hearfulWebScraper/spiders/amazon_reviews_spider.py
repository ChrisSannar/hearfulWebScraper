import scrapy

CSSSelectors = {
  'product_title' : "#productTitle::text",
  'product_brand' : "#productOverview_feature_div", # tr:first-child td:last-child span",
  'review_count' : "#acrCustomerReviewText::text",
}

XPathSelectors = {
  'product_brand': '//div[@id="productOverview_feature_div"]'
}

headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

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
    for url in urls:
      yield scrapy.Request(url=url, headers=headers, callback=self.initialParse)
  
  # Parses the main site page
  def initialParse(self, response):
    productName = str.strip(response.css(CSSSelectors['product_title']).get())
    # productBrand = str.strip(response.css(CSSSelectors['product_brand']).get())
    reviewCount = int(response.css(CSSSelectors['review_count']).get().split(' ', 1)[0])
    

    print("-----------------------------------------------")
    print(response.xpath(XPathSelectors['product_brand']).get())
    print({
      reviewCount,
      # productBrand,
      productName,
    })
    print("-----------------------------------------------")

# A single amazon item we are reviewing
class AmazonItem:

  def __init__(self, name="", brand="", source="", price=0.0, rating=0.0, reviews=[]):
    self._name = name
    self._brand = brand
    self._source = source
    self._price = price
    self._rating = rating
    self._reviews = reviews

  # Follow Encapsulation
  def getName(self):
    return self._name

  def getBrand(self):
    return self._brand

  def getSource(self):
    return self._source

  def getPrice(self):
    return self._price

  def getRating(self):
    return self._rating