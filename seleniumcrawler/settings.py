# Scrapy settings for seleniumcrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'seleniumcrawler'

SPIDER_MODULES = ['seleniumcrawler.spiders']
NEWSPIDER_MODULE = 'seleniumcrawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'seleniumcrawler (+http://www.yourdomain.com)'
