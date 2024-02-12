import scrapy
from scrapy import Spider

#  from scrapy.selector import Selector
from bs4 import BeautifulSoup

# To test one url at a time
urls_holder = [
    "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=0#reviews",
    "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=10#reviews",
    "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=20#reviews",
    "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=30#reviews",
    "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=40#reviews",
]


class YelpboltSpider(scrapy.Spider):
    name = "yelpbolt"
    start_urls = [
        "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=0#reviews",
        "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=10#reviews",
        "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=20#reviews",
        "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=30#reviews",
        "https://www.yelp.com/biz/upland-rheumatology-center-upland-2?osq=doctors&start=40#reviews",
    ]

    def parse(self, response):
        # Select each reviewer block
        reviewer_blocks = response.css(
            "div#reviews div.css-1qn0b6x ul.list__09f24__ynIEd li.css-1q2nwpv"
        )

        for reviewer_block in reviewer_blocks:
            # Extract the reviewer name
            name = reviewer_block.css(
                "div div.css-1vgj5dw div div.css-1u1p5a2 div::attr(aria-label)"
            ).get()
            ratings = []
            dates = []
            texts = []

            """
            There may be multiple reviews per customer. Because of the structure and the need
            to ignore business sutomer service responses, it's best to scrape the first listed
            review and then scrape additional reviews if they're not customer service responses.
            """
            # Extract the First Review
            # Rating
            rating = reviewer_block.css("div.css-14g69b3::attr(aria-label)").get()
            ratings.append(rating)
            # Date
            date = reviewer_block.css("span.css-chan6m::text").get()
            dates.append(date)
            # Text
            text = reviewer_block.css("span.raw__09f24__T4Ezm").xpath("string(.)").get()
            texts.append(text)

            """Scrape any Additional Reviews not from Customer Service"""
            additional_reviews = reviewer_block.css(
                "div.block-quote__09f24__qASfJ.css-kjl932"
            )
            # For each reviews, extract the relevant information
            for additional_review in additional_reviews:
                # First, check that it isn't a customer service response
                check = additional_review.css("p.css-chan6m::text").get()
                if check == "Business Customer Service":
                    continue
                # If it's not a customer service response, extract the review information
                # Rating
                rating = additional_review.css(
                    "div.css-14g69b3::attr(aria-label)"
                ).get()
                ratings.append(rating)
                # Date
                date = additional_review.css("span.css-chan6m::text").get()
                dates.append(date)
                # Text
                text = (
                    additional_review.css("span.raw__09f24__T4Ezm")
                    .xpath("string(.)")
                    .get()
                )
                texts.append(text)

            """Check Data Integrity and Yield"""
            # Ensure number of ratings, dates, and texts is the same
            assert len(ratings) == len(dates) == len(texts)

            # Yield the extracted data
            for i in range(len(ratings)):
                yield {
                    "reviewer": name,
                    "rating": ratings[i],
                    "date": dates[i],
                    "content": texts[i],
                }
