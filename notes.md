# Notes

## Instructions

1. List the sites on each line `site_list.txt`

## Problems & Solutions

- Had some issues with installing pip on my machine. Mostly because I was trying to use python2 to run python3. #Was able to install it all using a script file `get-pip.py` and that got it running. Also had to update the pathing to run pip since it wasn't installed in the proper directory (I'm using WSL so there are some issues there)
- It's `yield`, not `yeild`
- 

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