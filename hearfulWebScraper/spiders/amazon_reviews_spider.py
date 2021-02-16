import scrapy
import random
import time
from datetime import datetime

# The list of our selectors for Amazon 
CSSSelectors = {
  'product_title' : "#productTitle::text",
  'product_price' : "#priceblock_ourprice::text",
  'product_sale' : ".priceBlockSavingsString::text", 
  'review_count' : "#acrCustomerReviewText::text",
  'review_page_link' : 'a[data-hook="see-all-reviews-link-foot"]::attr(href)',
  'review_list' : '#cm_cr-review_list'
}

XPathSelectors = {
  'product_brand': '//div[@id="productOverview_feature_div"]/div/table/tr/td[2]/span/text()',
  'next_product_price': '//div[@id="olp_feature_div"]/div[last()]/span[1]/a/span[2]/text()',
  'description': '//div[@id="productDescription"]/p/text()',
  'specs': '//div[@id="featurebullets_feature_div"]//li[not(@id)]/span/text()',
  'reviews': '//div[@id="cm_cr-review_list"]/div[@data-hook="review"]',
  'rating': '//span[@class="reviewCountTextLinkedHistogram noUnderline"]/@title',
  'review_next_page': '//div[@id="cm_cr-pagination_bar"]//li[last()]/a/@href',
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

    # ***
    # temp_url = "https://www.amazon.com/GoPro-Fusion-Waterproof-Digital-Spherical/product-reviews/B0792MJLNM/ref=cm_cr_getr_d_paging_btm_next_19?ie=UTF8&reviewerType=all_reviews&pageNumber=19"
    # headers = random.choice(headers_list)
    # item = AmazonItem("Thing", "Branders", "amazon", 10.0, 5.0, ["wurd"], 4.1)
    # yield scrapy.Request(url=temp_url, headers=headers, callback=self.parseReviews, cb_kwargs={'product': item})
    # ***
    
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

    # Organize those values into an AmazonItem
    product = AmazonItem(productName, productBrand, "amazon", productPrice, productSale, productDescrptions, productRating)
    
    # Wait a minute to make sure we don't get rate limited
    time.sleep(random.uniform(1.1, 1.6))

    # Once we have the product information set up, go ahead and pull the reviews
    review_page = response.css(CSSSelectors['review_page_link']).get()    
    if review_page is not None:
      yield response.follow(review_page, callback=self.parseReviews, cb_kwargs={'product': product})

  # Parses the reviews
  def parseReviews(self, response, product):

    # Get our list of reviews
    review_list = response.xpath(XPathSelectors['reviews'])
    for review in review_list:

      # Extract out the items of interest
      amazon_review_id = review.css('div::attr(id)').get()
      review_title = review.css('a[data-hook="review-title"] > span::text').get()
      if review_title is None:
        review_title = review.css('span[data-hook="review-title"] > span:first-child::text').get()

      # double check if we have a review rating
      review_rating_text = review.css('i[data-hook="review-star-rating"] > span::text').get()
      review_rating = 0.0
      if review_rating_text is not None:
        review_rating = float(review_rating_text[0:review_rating_text.index(" ")])
    
      # The "review-date" has both date and country information
      review_date_raw = review.css('span[data-hook="review-date"]::text').get()
      review_country = str.strip(review_date_raw[(review_date_raw.index("in ") + 3):(review_date_raw.index("on "))])
      review_date = datetime.strptime(review_date_raw[review_date_raw.index("on "):][3:], '%B %d, %Y')

      # For the review text, xpath keeps splitting by the <br> tags so we gotta try a work around
      review_text = "" 
      for line in review.xpath('//div[@id="' + amazon_review_id + '"]//span[@data-hook="review-body"]/span/text()').getall():
        review_text = review_text + line

      # When we're done, organize into an object and print
      review_obj = AmazonReview(amazon_review_id, review_title, review_rating, review_country, review_text, review_date)
      yield review_obj.toDict()
    
    # once we're done looping through the reviews, then time to get the next page
    next_page = response.xpath(XPathSelectors['review_next_page']).get()
    if next_page is not None:
      yield response.follow(next_page, callback=self.parseReviews, cb_kwargs={'product': product})


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
    
    # If there's a description there, use it
    description = response.xpath(XPathSelectors['description']).get()
    if description != None:
      return [description]

    # Otherwise use the specs
    descriptions = response.xpath(XPathSelectors['specs']).getall() 
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

  def toDict(self):
    return {
      'name': self._name,
      'brand': self._brand,
      'source': self._source,
      'price': self._price,
      'sale': self._sale,
      'rating': self._rating,
    }
  
  def __str__(self):
    return "{name} ({brand}) - ${price} (${sale}) {rating}/5 ".format(name=self._name, brand=self._brand, price=self._price, sale=self._sale, rating=self._rating)

# A review for a given AmazonItem
class AmazonReview:

  def __init__(self, id="", title="", rating=0.0, country="", text="", date=None):
    self._id=id
    self._title=title
    self._rating=rating
    self._country=country
    self._text=text
    self._date=date

  def getAmazonId(self):
    return self._id

  def getTitle(self):
    return self._title

  def getRating(self):
    return self._rating

  def getText(self):
    return self._text

  def getDate(self):
    return self._date
  
  def getCountry(self):
    return self._country

  def toDict(self):
    return {
      'id': self._id,
      'title': self._title,
      'rating': self._rating,
      'country': self._country,
      'text': self._text,
      'date': self._date,
    }

  def __str__(self):
    return "{id}: {title} <{country}> ({rating}) {date} - {text}".format(id=self._id, title=self._title, country=self._country, rating=self._rating, date=self._date, text=self._text)
