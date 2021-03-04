import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from serafimfinans.items import Article


class SerafimfinansSpider(scrapy.Spider):
    name = 'serafimfinans'
    start_urls = ['https://serafimfinans.se/nyheter/']

    def parse(self, response):
        links = response.xpath('//article/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="page-numbers gen-pagination gen-pagination-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h5/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="et_pb_section et_pb_section_1 gen-news-single-section et_section_regular"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
