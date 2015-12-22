import scrapy

from scrapy import log

from distantPlaying.items import MobyItem
from distantPlaying.lib import clean_html

class MobySpider(scrapy.Spider):
    name = "moby"
    allowed_domains = ["mobygames.com"]
    start_urls = [
        "http://www.mobygames.com/browse/games/list-games/",
    ]

    def parse(self, response):
        for game in response.xpath("//table/tbody/tr/td[1]/a/@href"):
            url = response.urljoin(game.extract())
            yield scrapy.Request(url, callback=self.parseGamePage)
        for nextPage in response.xpath("//td[@class='mobHeaderNav']/a[contains(., 'Next')]/@href"):
            url = response.urljoin(nextPage.extract())
            yield scrapy.Request(url, callback=self.parse)

    def parseGamePage(self, response):
        item = MobyItem()
        item['body'] = response.body
        item['link'] = response.url
        item['description'] = clean_html(response.body.split('<h2>Description</h2>')[1].split('<div class="sideBarLinks">')[0])
        item['publishedBy'] = clean_html(response.xpath('//div[contains(text(), "Published by")]/following-sibling::div[1]/a/text()').extract()[0]).split(',')
        item['developedBy'] = clean_html(response.xpath('//div[contains(text(), "Developed by")]/following-sibling::div[1]/a/text()').extract()[0]).split(',')
        item['released'] = clean_html(response.xpath('//div[contains(text(), "Released")]/following-sibling::div[1]/a/text()').extract()[0]).split(',')
        item['platforms'] = clean_html(response.xpath('//div[contains(text(), "Platforms")]/following-sibling::div[1]/a/text()').extract()[0]).split(',')
        # item['genre'] = 
        # item['perspective'] = 
        # item['theme'] = 
        # item['misc'] = 
        item['title'] = response.xpath("//h1/a/text()").extract()[0]
        log.msg(item['title']+ \
                '\n'+item['description']+
                '\n'+item['publishedBy']+
                '\n'+item['developedBy']+
                '\n'+item['released']+
                '\n'+item['platforms']+
                '\n', level=log.INFO)
        yield item
