# Amazon Reviews Web Scraper

A web scraper that uses spiders to crawl Amazon product pages and retrieve information such as product and reviews data.

## Installation

1. Install the required libraries if not already installed:
    - scrapy - `pip install scrapy`
    - pymongo - `pip install pymongo`
2. Set the following environment variables in the `hearfulWebScraper/settings.py`:
    - MONGODB_URI
    - MONGODB_DB
    - MONGODB_REVIEWS_COLLECTION
    - MONGODB_PRODUCTS_COLLECTION
    - *NOTE: If you don't have a Mongodb instance set up, follow [MongoDB Installation](###-MongoDB-Installation) to set up an instance*
3. List the sites you wish to scrape in `hearfulWebScraper/settings.py` under the `AMAZON_PRODUCT_URLS` list
4. Run the bot using scrapy command line: `scrapy crawl amazon_reviews`

### MongoDB Installation

The following technologes are required with admin access for this installation: `docker` and `docker-compose` 

1. Pull latest image - `docker pull mongo:latest`
2. Change the `user`, `pwd`, and `db` in the `mongo-init.js` file to match the values in `hearfulWebScraper/settings.py`.
3. Change the environment variables in `docker-compose.yml` file to match those in `mongo-init.js`.
4. *Optional* - In `docker-compose.yml`, change the `mongo-volume` to a different location.
    * NOTE: if you don't change this address, it'll create the `mongo-volume` in that same folder.
5. `docker-compose up -d` - Runs the docker container in the background.
6. Access container with `docker exec -it <container-name> bash`.
7. Start the mongo shell in bash - `mongo -u <username>` and enter your `<password>`.
8. Run the code in `init-mongo.js` in the shell.
9. Create your database and add a temporary collection to it - `use <db-name>`, `db.createCollection("<temp-name>")`.
10. Run the test-db.py file to test your connection (be sure to install necessary libraries [pymongo] and change the mongodb variables accordingly).