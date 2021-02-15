import scrapy

class QuotesSpider(scrapy.Spider):
  # Unique name for the spider
  name = "quotes"

  # URLs that are made right when the Spider is run
  start_urls = [
    # 'http://quotes.toscrape.com/page/2/',
    'http://quotes.toscrape.com/page/1/'
  ]

  # # Returns an itterable of scrapy requests
  # def start_requests(self):
  #   urls = [
  #     'http://quotes.toscrape.com/page/1/',
  #     'http://quotes.toscrape.com/page/2/',
  #   ]
  #   for url in urls:
  #     yield scrapy.Request(url=url, callback=self.parse)
  

  # parse:Handles the response for each request, response(TextResponse)
  
  # # Basic parsing
  # def parse(self, response):
  #   page = response.url.split("/")[-2]
  #   filename = 'output/quotes-%s.html' % page
  #   with open(filename, 'wb') as f:
  #     f.write(response.body)
  #   self.log('Saved file %s' % filename)

  # Parsing to JSON and then follow any additional links
  def parse(self, response):
    for quote in response.css('div.quote'):
      yield {
        'text': quote.css('span.text::text').get(),
        'author': quote.css('small.author::text').get(),
        'tags': quote.css('div.tags a.tag::text').getall(),
      }

    # If we have a next page to go to, then recursively pull the data from that page as well.
    next_page = response.css('li.next a::attr(href)').get()
    if next_page is not None:
      # next_page = response.urljoin(next_page)
      # yield scrapy.Request(next_page, callback=self.parse)
      yield response.follow(next_page, callback=self.parse)