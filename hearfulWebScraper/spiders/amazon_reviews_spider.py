import scrapy

# Utility functions
import random
import time
from hearfulWebScraper.util import *

# Environment Variables
from scrapy.utils.project import get_project_settings

# MongoDB
import pymongo

# Our classes we're using
from hearfulWebScraper.classes.AmazonItem import AmazonItem
from hearfulWebScraper.classes.AmazonReview import AmazonReview


# The list of our selectors for Amazon 
CSSSelectors = {
  'review_page_link' : 'a[data-hook="see-all-reviews-link-foot"]::attr(href)',
}
XPathSelectors = {
  'reviews_all': '//div[@id="cm_cr-review_list"]/div[@data-hook="review"]',
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
      review_amazon_id = AmazonReview.scrapeReviewId(review)
      review_title = AmazonReview.scrapeReviewTitle(review)
      review_rating = AmazonReview.scrapeReviewRating(review)
      review_country = AmazonReview.scrapeReviewCountry(review)
      review_date = AmazonReview.scrapeReviewDate(review)
      review_text = AmazonReview.scrapeReviewText(review, review_amazon_id)

      # When we're done, organize into an object, add it to our product, and return
      review_obj = AmazonReview(review_amazon_id, product_id, review_title, review_rating, review_country, review_text, review_date)
      product.addReview(review_obj)
      yield review_obj.toDict()
    
    # once we're done looping through the reviews, then time to get the next page
    next_page = response.xpath(XPathSelectors['review_next_page']).get()
    if next_page is not None:
      time.sleep(random.uniform(0.6, 0.922))
      yield response.follow(next_page, callback=self.parseReviews, cb_kwargs={'product': product, 'product_id': product_id})
