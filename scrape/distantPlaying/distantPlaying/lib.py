import scrapy, re

from scrapy import log

def clean_html(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text).replace(u'\xa0', u' ')

