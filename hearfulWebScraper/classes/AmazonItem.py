
CSSSelectors = {
  #Product Selectors
  'product_title' : "#productTitle::text",
  'product_price' : "#priceblock_ourprice::text",
  'product_sale' : ".priceBlockSavingsString::text", 
  'product_rating_count' : "#acrCustomerReviewText::text",
  'review_page_link' : 'a[data-hook="see-all-reviews-link-foot"]::attr(href)',
}

XPathSelectors = {
  # Product Selectors
  'product_brand': '//div[@id="productOverview_feature_div"]/div/table/tr/td[2]/span/text()',
  'next_product_price': '//div[@id="olp_feature_div"]/div[last()]/span[1]/a/span[2]/text()',
  'product_description': '//div[@id="productDescription"]/p/text()',
  'product_specs': '//div[@id="featurebullets_feature_div"]//li[not(@id)]/span/text()',
  'review_rating': '//span[@class="reviewCountTextLinkedHistogram noUnderline"]/@title',
}

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

  def addReview(self, review):
    self._reviews.append(review)

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

  # Selector Functions
  @staticmethod
  def scrapeProductName(response):
    return str.strip(response.css(CSSSelectors['product_title']).get())
  
  @staticmethod
  def scrapeProductBrand(response):
    return str.strip(response.css(CSSSelectors['product_title']).get())

  @staticmethod
  def scrapeProductPrice(response):
    
    # See if it's there initially
    productPrice = response.css(CSSSelectors['product_price']).get()

    # If we don't find it using css, try xpath
    if productPrice == None:
      productPrice = response.xpath(XPathSelectors['next_product_price']).get()

    # If we still can't find it, then just give a negative value
    if productPrice == None:
      productPrice = "$-1.0"
    
    return float(productPrice[1:])

  @staticmethod
  def scrapeProductSale(response):
    productSale = response.css(CSSSelectors['product_sale']).get()

    # If there is no product sale, return -1.0
    if productSale == None:
      return -1.0
    else:
      # Just pull the amount from the string we got
      cleaned = str.strip(productSale) 
      return float(cleaned[1:cleaned.index(" ")])

  @staticmethod
  def scrapeProductDescrptions(response):
    
    # If there's a description there, use it
    description = response.xpath(XPathSelectors['product_description']).get()
    if description != None:
      return [description]

    # Otherwise use the product_specs
    descriptions = response.xpath(XPathSelectors['product_specs']).getall() 
    def trim(string):
      return str.strip(string)
    return map(trim, descriptions)

  @staticmethod
  def scrapeProductRating(response):
    rating = response.xpath(XPathSelectors['review_rating']).get()
    return float(rating[0:rating.index(" ")])

  @staticmethod
  def scrapeProductReviewCount(response):
    return int(response.css(CSSSelectors['product_rating_count']).get().split(' ', 1)[0])
