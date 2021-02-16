# Notes

## Instructions

1. List the amazon product pages on each line `site_list.txt`
  * Ex: "https://www.amazon.com/GoPro-Fusion-Waterproof-Digital-Spherical/dp/B0792MJLNM/ref=sr_1_3?crid=D3C7EDM435E7&keywords=gopro%2Bfusion&qid=1550442454&s=electronics&sprefix=GoPro%2BFu%2Celectronics%2C1332&sr=1-3&th=1"
2. Run the script with scrapy `scrapy crawl amazon_reviews -o <json-file-path>`

## Problems & Solutions

- Had some issues with installing pip on my machine. Mostly because I was trying to use python2 to run python3. #Was able to install it all using a script file `get-pip.py` and that got it running. Also had to update the pathing to run pip since it wasn't installed in the proper directory (I'm using WSL so there are some issues there)
- It's `yield`, not `yeild`
- Amazon temporarily allowed access to python bots, but eventually blocked us. That was fixed by setting a different user agent, however we'll have to changed it every now and then to prevent Amazon from figuring out we're using a bot
  * 'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"

## Web Structure

Useful Selectors
- Homepage:
  * `#acrCustomerReviewText` - <span> The total number of views: Ex. "773 ratings"
  * `a[data-hook="see-all-reviews-link-foot"]` - <a> the link to the page to see all reviews
- all_reviews
  * `cm_cr-review_list` - <div> The primary part of the page that contains all the reviews and the 
  * `#cm_cr-review_list > div[data-hook="review"]` - <div> retrieves all the divs that contain reviews

  
## Notes

- Commands:
  * `scrapy crawl <spider>` - Runs the following spider
  * `scrapy crawl <spider> -o <file>` - Sends the Output to the given file
  * `scrapy shell -s USER_AGENT='<agent>' '<url>'` - Sets the shell for the request
- Other
```
function getElementByXpath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}
```