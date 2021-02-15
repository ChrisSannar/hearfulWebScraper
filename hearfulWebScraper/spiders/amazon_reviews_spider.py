import scrapy

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
      yield scrapy.Request(url=url, callback=self.initialParse)
  
  # Parses the main site page
  def initialParse(self, response):
    for rating in response.css('#acrCustomerReviewText::text'):
      print(rating)
    