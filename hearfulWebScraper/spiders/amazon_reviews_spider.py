import scrapy
import random
import time
from datetime import datetime

# Environment Variables
from scrapy.utils.project import get_project_settings

# MongoDB
import pymongo

# Our classes we're using
from hearfulWebScraper.classes.AmazonItem import AmazonItem
from hearfulWebScraper.classes.AmazonReview import AmazonReview

from hearfulWebScraper.util import *

# The list of our selectors for Amazon 
CSSSelectors = {
  #Product Selectors
  'product_title' : "#productTitle::text",
  'product_price' : "#priceblock_ourprice::text",
  'product_sale' : ".priceBlockSavingsString::text", 
  'product_rating_count' : "#acrCustomerReviewText::text",
  'review_page_link' : 'a[data-hook="see-all-reviews-link-foot"]::attr(href)',
  
  # Review Selectors
  'review_list' : '#cm_cr-review_list',
  'review_amazon_id' : 'div::attr(id)',
  'review_title': 'a[data-hook="review-title"] > span::text',
  'next_review_title': 'span[data-hook="review-title"] > span:first-child::text',
  'review_rating': 'i[data-hook="review-star-rating"] > span::text',
  'review_date': 'span[data-hook="review-date"]::text',
}

XPathSelectors = {
  # Product Selectors
  'product_brand': '//div[@id="productOverview_feature_div"]/div/table/tr/td[2]/span/text()',
  'next_product_price': '//div[@id="olp_feature_div"]/div[last()]/span[1]/a/span[2]/text()',
  'product_description': '//div[@id="productDescription"]/p/text()',
  'product_specs': '//div[@id="featurebullets_feature_div"]//li[not(@id)]/span/text()',
  
  # Review Selectors
  'reviews_all': '//div[@id="cm_cr-review_list"]/div[@data-hook="review"]',
  'review_rating': '//span[@class="reviewCountTextLinkedHistogram noUnderline"]/@title',
  'review_next_page': '//div[@id="cm_cr-pagination_bar"]//li[last()]/a/@href',
}

# A spider that scrape Amazon product information and reviews
class AmazonReviewsSpider(scrapy.Spider):
  name = "amazon_reviews"

  # Tie the MONGO client and db to the spider itself
  def __init__(self):
    self.settings = get_project_settings()
    self.client = pymongo.MongoClient(self.settings.get('MONGODB_URI'))
    self.db = self.client[self.settings.get('MONGODB_DB')]

  # The First request function
  def start_requests(self):
    
    # Get the list of sites to crawl and parse the data for each
    urls = self.settings.get('AMAZON_PRODUCT_URLS')
    self.headers = random.choice(headers_list)  # Random header to spoof amazon servers
    for url in urls:
      yield scrapy.Request(url=url, headers=self.headers, callback=self.initialParse)
  
  # Parses the main product page
  def initialParse(self, response):

    # Get each value we're after from the response
    productName = AmazonItem.scrapeProductName(response)
    productBrand = AmazonItem.scrapeProductBrand(response)
    productPrice = AmazonItem.scrapeProductPrice(response)
    productSale = AmazonItem.scrapeProductSale(response)
    productDescrptions = AmazonItem.scrapeProductDescrptions(response)
    productRating = AmazonItem.scrapeProductRating(response)
    productReviewCount = AmazonItem.scrapeProductReviewCount(response)

    # Organize those values into an AmazonItem
    product = AmazonItem(productName, productBrand, "Amazon", productPrice, productSale, productDescrptions, productRating)

    # The mongo_id of the product to be passed on into the reviews
    mongo_product_id = self.db[self.settings.get('MONGODB_PRODUCTS_COLLECTION')].insert_one(product.toDict()).inserted_id

    # Wait a minute to make sure we don't get rate limited
    time.sleep(random.uniform(0.9, 1.2))

    # Once we have the product information set up, go ahead and pull the reviews
    review_page = response.css(CSSSelectors['review_page_link']).get()    
    if review_page is not None:
      yield response.follow(review_page, callback=self.parseReviews, cb_kwargs={'product': product, 'product_id': mongo_product_id})

  # Parses the reviews
  def parseReviews(self, response, product, product_id):

    # Get our list of reviews
    review_list = response.xpath(XPathSelectors['reviews_all'])
    for review in review_list:

      # Extract out the items of interest
      review_amazon_id = review.css(CSSSelectors['review_amazon_id']).get()
      review_title = review.css(CSSSelectors['review_title']).get()
      if review_title is None:
        review_title = review.css(CSSSelectors['next_review_title']).get()

      # double check if we have a review rating
      review_rating_text = review.css(CSSSelectors['review_rating']).get()
      review_rating = 0.0
      if review_rating_text is not None:
        review_rating = float(review_rating_text[0:review_rating_text.index(" ")])

      # The "review-date" has both date and country information
      review_date_raw = review.css(CSSSelectors['review_date']).get()
      review_country = str.strip(review_date_raw[(review_date_raw.index("in ") + 3):(review_date_raw.index("on "))])
      review_date = datetime.strptime(review_date_raw[review_date_raw.index("on "):][3:], '%B %d, %Y')

      # For the review text, xpath keeps splitting by the <br> tags so we gotta try a work around
      review_text = "" 
      for line in review.xpath('//div[@id="' + review_amazon_id + '"]//span[@data-hook="review-body"]/span/text()').getall():
        review_text = review_text + line

      # When we're done, organize into an object, add it to our product, and return
      review_obj = AmazonReview(review_amazon_id, product_id, review_title, review_rating, review_country, review_text, review_date)
      product.addReview(review_obj)
      yield review_obj.toDict()
    
    # # once we're done looping through the reviews, then time to get the next page
    # next_page = response.xpath(XPathSelectors['review_next_page']).get()
    # if next_page is not None:
    #   time.sleep(random.uniform(0.6, 0.922))
    #   yield response.follow(next_page, callback=self.parseReviews, cb_kwargs={'product': product, 'product_id': product_id})


  # # Pull the price from the response and returns it as a float
  # def scrapeProductPrice(self, response):
    
  #   # See if it's there initially
  #   productPrice = response.css(CSSSelectors['product_price']).get()

  #   # If we don't find it using css, try xpath
  #   if productPrice == None:
  #     productPrice = response.xpath(XPathSelectors['next_product_price']).get()

  #   # If we still can't find it, then just give a negative value
  #   if productPrice == None:
  #     productPrice = "$-1.0"
    
  #   return float(productPrice[1:])

  # Pull the sale savings from the response and returns it as a float
  # def scrapeProductSale(self, response):
  #   productSale = response.css(CSSSelectors['product_sale']).get()

  #   # If there is no product sale, return -1.0
  #   if productSale == None:
  #     return -1.0
  #   else:
  #     # Just pull the amount from the string we got
  #     cleaned = str.strip(productSale) 
  #     return float(cleaned[1:cleaned.index(" ")])
  
  # Pull the descriptions from the response and return a trimed version of them
  # def scrapeProductDescrptions(self, response):
    
  #   # If there's a description there, use it
  #   description = response.xpath(XPathSelectors['product_description']).get()
  #   if description != None:
  #     return [description]

  #   # Otherwise use the product_specs
  #   descriptions = response.xpath(XPathSelectors['product_specs']).getall() 
  #   def trim(string):
  #     return str.strip(string)
  #   return map(trim, descriptions)

  # Pull the rating text from the response and return a float of the rating number
  # def scrapeProductRating(self, response):
  #   rating = response.xpath(XPathSelectors['review_rating']).get()
  #   return float(rating[0:rating.index(" ")])
