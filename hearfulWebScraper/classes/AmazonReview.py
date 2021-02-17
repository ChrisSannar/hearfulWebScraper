from datetime import datetime

CSSSelectors = {
  'review_amazon_id' : 'div::attr(id)',
  'review_title': 'a[data-hook="review-title"] > span::text',
  'next_review_title': 'span[data-hook="review-title"] > span:first-child::text',
  'review_rating': 'i[data-hook="review-star-rating"] > span::text',
  'review_date': 'span[data-hook="review-date"]::text',
}

XPathSelectors = {
  'reviews_all': '//div[@id="cm_cr-review_list"]/div[@data-hook="review"]',
  'review_rating': '//span[@class="reviewCountTextLinkedHistogram noUnderline"]/@title',
}

# A review for a given AmazonItem
class AmazonReview:
 
  def __init__(self, id="", product_id="", title="", rating=0.0, country="", text="", date=None):
    self._id=id
    self._product_id = product_id
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
      'product_id': self._product_id,
      'title': self._title,
      'rating': self._rating,
      'country': self._country,
      'text': self._text,
      'date': self._date,
    }

  def __str__(self):
    return "{id}: {title} <{country}> ({rating}) {date} - {text}".format(id=self._id, title=self._title, country=self._country, rating=self._rating, date=self._date, text=self._text)

  @staticmethod
  def scrapeReviewId(review):
    return review.css(CSSSelectors['review_amazon_id']).get();

  @staticmethod
  def scrapeReviewTitle(review):

    # For some reason, foreign reviews don't have titles linked in the proper way
    review_title = review.css(CSSSelectors['review_title']).get()
    if review_title is None:
      review_title = review.css(CSSSelectors['next_review_title']).get()
    return review_title

  @staticmethod
  def scrapeReviewRating(review):

    # Ratings are part of a bit of text so they need to be chopped out
    review_rating_text = review.css(CSSSelectors['review_rating']).get()
    review_rating = 0.0
    if review_rating_text is not None:
      review_rating = float(review_rating_text[0:review_rating_text.index(" ")])
    return review_rating

  @staticmethod
  def scrapeReviewCountry(review):
    review_date_raw = review.css(CSSSelectors['review_date']).get()
    return str.strip(review_date_raw[(review_date_raw.index("in ") + 3):(review_date_raw.index("on "))])
  
  @staticmethod
  def scrapeReviewDate(review):
    review_date_raw = review.css(CSSSelectors['review_date']).get()
    return datetime.strptime(review_date_raw[review_date_raw.index("on "):][3:], '%B %d, %Y')

  @staticmethod
  def scrapeReviewText(review, review_amazon_id):

    # text can be broken by <br> tags so we need to combine them together, also make them unique by review
    review_text = "" 
    for line in review.xpath('//div[@id="' + review_amazon_id + '"]//span[@data-hook="review-body"]/span/text()').getall():
      review_text = review_text + line
    return review_text

