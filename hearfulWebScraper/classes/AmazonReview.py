
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
