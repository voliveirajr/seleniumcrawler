seleniumcrawler
===============

This is a Webcrawler based on Scrapy and Selenium frameworks

This spider crawls thru the directferries.com website in order to generate a json file with all tickets available for one 
of these directions Dublin-Liverpool / Liverpool-Dublin with departure tomorrow and returning in 3 days.

HOW TO EXECUTE:

Is required an environment with the following requirements installed:
-Python 2.7
-Scrapy 0.18
-Selenium web-drivers

To execute the crawler the following command should be executed from the project path

scrapy crawl crawlermate_selenium -a category=[dublin or liverpool] -o [filename] -t json

for an example, to generate tickets for dublin to liverpool on items.json file you should execute
scrapy crawl crawlermate_selenium -a category=dublin -o items.json -t json

References:

http://docs.seleniumhq.org/
http://http://scrapy.org/
