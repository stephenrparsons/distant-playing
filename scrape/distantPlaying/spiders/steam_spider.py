import scrapy

from distantPlaying.items import SteamItem
from distantPlaying.lib import clean_html

class SteamSpider(scrapy.Spider):
    name = "steam"
    allowed_domains = ["store.steampowered.com"]
    # start_urls = ["http://store.steampowered.com/search/#sort_by=Name_ASC&sort_order=ASC&page=%d"%(i) for i in range(1,636)]
    start_urls = ["http://store.steampowered.com/search/#sort_by=Name_ASC&sort_order=ASC&page=%d"%(i) for i in range(1,2)]

    def parse(self, response):
        for game in response.xpath('//a[contains(@class, "search_result_row")]/@href'):
            url = response.urljoin(game.extract())
            yield scrapy.Request(url, callback=self.parseGamePage)

    def parseGamePage(self, response):
        item = SteamItem()

        # title = scrapy.Field()
        # description = scrapy.Field()
        # shortDescription = scrapy.Field()
        # userReviews = scrapy.Field()
        # released = scrapy.Field()
        # tags = scrapy.Field()
        # price = scrapy.Field()
        # misc = scrapy.Field()
        # genre = scrapy.Field()
        # developedBy = scrapy.Field()
        # publishedBy = scrapy.Field()
        # windowsSysRequirements = scrapy.Field()

        item['body'] = response.body
        item['link'] = response.url
        # item['description'] = clean_html(response.body.split('<h2>Description</h2>')[1].split('<div class="sideBarLinks">')[0])
        # item['publishedBy'] = map(clean_html, response.xpath('//div[contains(text(), "Published by")]/following-sibling::div[1]/a/text()').extract())
        # item['developedBy'] = map(clean_html, response.xpath('//div[contains(text(), "Developed by")]/following-sibling::div[1]/a/text()').extract())
        # item['released'] = clean_html(response.xpath('//div[contains(text(), "Released")]/following-sibling::div[1]/a/text()').extract()[0])
        # item['platforms'] = map(clean_html, response.xpath('//div[contains(text(), "Platform")]/following-sibling::div[1]/a/text()').extract())
        # item['genre'] = map(clean_html, response.xpath('//div[contains(text(), "Genre")]/following-sibling::div[1]/a/text()').extract())
        # item['perspective'] = map(clean_html, response.xpath('//div[contains(text(), "Perspective")]/following-sibling::div[1]/a/text()').extract())
        # item['theme'] = map(clean_html, response.xpath('//div[contains(text(), "Theme")]/following-sibling::div[1]/a/text()').extract())
        # item['misc'] = map(clean_html, response.xpath('//div[contains(text(), "Misc")]/following-sibling::div[1]/a/text()').extract())
        # item['ratings'] = 
        item['title'] = response.xpath("//div[@class='apphub_AppName']/text()").extract()
        self.logger.info(str(item['title'])+item['link'])
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
