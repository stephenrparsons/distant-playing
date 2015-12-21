import scrapy, re

from scrapy import log

from distantPlaying.items import MobyItem

def clean_html(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text).replace(u'\xa0', u' ')

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
        # item['developedBy'] = 
        # item['released'] = 
        # item['platforms'] = 
        # item['genre'] = 
        # item['perspective'] = 
        # item['theme'] = 
        # item['misc'] = 
        item['title'] = response.xpath("//h1/a/text()").extract()[0]
        log.msg(item['title']+ \
                '\n'+item['description']+
                '\n'+item['publishedBy']+
                '\n', level=log.INFO)
        yield item
