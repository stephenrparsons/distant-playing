import scrapy

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
        item['publishedBy'] = map(clean_html, response.xpath('//div[contains(text(), "Published by")]/following-sibling::div[1]/a/text()').extract())
        item['developedBy'] = map(clean_html, response.xpath('//div[contains(text(), "Developed by")]/following-sibling::div[1]/a/text()').extract())
        item['released'] = clean_html(response.xpath('//div[contains(text(), "Released")]/following-sibling::div[1]/a/text()').extract()[0])
        item['platforms'] = map(clean_html, response.xpath('//div[contains(text(), "Platform")]/following-sibling::div[1]/a/text()').extract())
        item['genre'] = map(clean_html, response.xpath('//div[contains(text(), "Genre")]/following-sibling::div[1]/a/text()').extract())
        item['perspective'] = map(clean_html, response.xpath('//div[contains(text(), "Perspective")]/following-sibling::div[1]/a/text()').extract())
        item['theme'] = map(clean_html, response.xpath('//div[contains(text(), "Theme")]/following-sibling::div[1]/a/text()').extract())
        item['misc'] = map(clean_html, response.xpath('//div[contains(text(), "Misc")]/following-sibling::div[1]/a/text()').extract())
        # item['ratings'] = 
        item['title'] = response.xpath("//h1/a/text()").extract()[0]
        # self.logger.info('\nTitle: '+item['title']+
        #         '\nDescription: '+item['description']+
        #         '\nPublished by: '+unicode(item['publishedBy'])+
        #         '\nDeveloped by: '+unicode(item['developedBy'])+
        #         '\nReleased: '+item['released']+
        #         '\nPlatforms: '+unicode(item['platforms'])+
        #         '\nGenre: '+unicode(item['genre'])+
        #         '\nPerspective: '+unicode(item['perspective'])+
        #         '\nTheme: '+unicode(item['theme'])+
        #         '\nMisc: '+unicode(item['misc'])+
        #         '\n')
        yield item
