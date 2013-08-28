import time
from scrapy.item import Item, Field
from selenium import webdriver
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest
from scrapy import log
from time import strftime
from datetime import timedelta
from datetime import datetime
import datetime
from scrapy.selector import HtmlXPathSelector

class SeleniumCrawlerSpider(BaseSpider):
    name = "SeleniumCrawlerSpider"
    allowed_domains = ["directferries.com", "directferries.co.uk", "ssl.directferries.com"]
    
    def __init__(self, category=None, *args, **kwargs):
        self.driver = webdriver.Firefox()
        super(SeleniumCrawlerSpider, self).__init__(*args, **kwargs)
                
        LOG_FILE = "scrapy_%s_%s.log" % (self.name, "now")

        # remove the current log
        # log.log.removeObserver(log.log.theLogPublisher.observers[0])
        # re-create the default Twisted observer which Scrapy checks
        log.log.defaultObserver = log.log.DefaultObserver()
        # start the default observer so it can be stopped
        log.log.defaultObserver.start()
        # trick Scrapy into thinking logging has not started
        log.started = False
        # start the new log file observer
        log.start(LOG_FILE)
        # continue with the normal spider init

        #defining the trip "leg" code (Dublin - Liverpool [18] / Liverpool - Dublin [66])
        dcode="18"
        if category == "dublin":
            dcode="18"
        elif category == "liverpool":
            dcode="66"
        
        self.start_urls = ['https://ssl.directferries.com/ferry/secure/multi_price_detail.aspx?stdc=DF10&grid=0&rfid=%s&psgr=1&curr=1&retn=True' % dcode]

        self.log("Init finished")

    def parse_trip_items(self):
        self.log("starting to parse divs")
        
        items = []
        trip_divs = self.driver.find_elements_by_xpath("//div[@class='ticket']")

        self.log("found %d trips divs" % trip_divs.__len__())
        #each trip div has desribed two trip legs, we have to create 2 elements for each div
        for trip in trip_divs:
            #1st trip leg
            item = self.TripItem()
            item['route_name'] = (trip.find_elements_by_xpath(".//div[@class='ticket_header']"))[0].text
            item['origin_name'] = (trip.find_elements_by_xpath(".//div[@class='info1']//p[@class='porttxt']"))[0].text
            item['destination_name'] = (trip.find_elements_by_xpath(".//div[@class='info1']//p[@class='porttxt2']"))[0].text
            item['departure_time'] = (trip.find_elements_by_xpath(".//div[@class='info1']//p[not(@*)]"))[0].text.replace("Depart: ","") #p tag without any information
            item['arrival_time'] = (trip.find_elements_by_xpath(".//div[@class='info2']//p[not(@*)]"))[0].text.replace("Arrive: ","") #p tag without any information
            item['duration'] = (trip.find_elements_by_xpath(".//p[@class='dur1']"))[0].text
            item['price'] = (trip.find_elements_by_xpath(".//p[@class='pricetxt']"))[0].text
            items.append(item)
            
            #2nd trip leg
            item = self.TripItem()
            item['route_name'] = (trip.find_elements_by_xpath(".//div[@class='ticket_header']"))[0].text
            item['origin_name'] = (trip.find_elements_by_xpath(".//div[@class='info2']//p[@class='porttxt']"))[0].text
            item['destination_name'] = (trip.find_elements_by_xpath(".//div[@class='info2']//p[@class='porttxt2']"))[0].text
            item['departure_time'] = (trip.find_elements_by_xpath(".//div[@class='info1']//p[not(@*)]"))[1].text.replace("Depart: ","") #p tag without any information
            item['arrival_time'] = (trip.find_elements_by_xpath(".//div[@class='info2']//p[not(@*)]"))[1].text.replace("Arrive: ","") #p tag without any information
            item['duration'] = (trip.find_elements_by_xpath(".//p[@class='dur2']"))[0].text
            item['price'] = (trip.find_elements_by_xpath(".//p[@class='pricetxt']"))[0].text
            items.append(item)
                    
        return items

    
    def parse(self, response):
        self.driver.get(response.url)
        
        time.sleep(10)
        
        self.log("starting to fill form")
        
        #tomorrow
        departure_date = (datetime.date.today()+ timedelta(days=1)).strftime("%d %B %Y")
        #returning in 3 days
        return_date = (datetime.date.today()+ timedelta(days=4)).strftime("%d %B %Y")
        
        #departure date
        #smarty pants hack uh? removes the readonly to be able to fill the value, Maybe exists a right way to do it
        self.log("filling departure date")
        self.driver.execute_script("document.getElementById('cal_out').removeAttribute('class');")
        self.driver.execute_script("document.getElementById('cal_out').removeAttribute('readonly');")
        date1El = self.driver.find_element_by_id("cal_out")
        date1El.clear()
        date1El.send_keys(departure_date)
        
        #return date
        self.log("filling return date")
        date2El = self.driver.find_element_by_id("cal_ret")
        self.driver.execute_script("document.getElementById('cal_ret').removeAttribute('class');")
        self.driver.execute_script("document.getElementById('cal_ret').removeAttribute('readonly');")        
        date2El.clear()
        date2El.send_keys(return_date)
        
        #passenger age
        self.log("filling passenger age")
        passenger_age = self.driver.find_element_by_id("passengerAges_Age1_ddlAges")
        all_options = passenger_age.find_elements_by_tag_name("option")
        for option in all_options:
            print "Value is: %s" % option.get_attribute("value")
            if(option.get_attribute("value") == "18"):
                option.click()
        
        #no vehicle
        self.log("filling no vehicle option")
        noVeh = self.driver.find_element_by_id("vehicleDetails_radNoVehicle")
        noVeh.click()
        
        time.sleep(5)
        
        #departure hour
        self.log("filling departure hour")
        departureH = self.driver.find_element_by_id("ddOutTime")
        all_options = departureH.find_elements_by_tag_name("option")
        all_options[1].click()#first hour
        
        #return hour
        self.log("filling return hour")
        departureH = self.driver.find_element_by_id("ddRetTime")
        all_options = departureH.find_elements_by_tag_name("option")
        all_options[all_options.__len__()-1].click()#last hour
        
        
        self.log("getting the submit button")
        el = self.driver.find_element_by_id("butSubmit")
        if el:
            self.log("found submit button")
            el.click()

        time.sleep(20)
        
        #####################################
        #Time to parse the items and generate the JSON file 
        #####################################
        
        items = self.parse_trip_items()

        self.driver.close()
        
        return items
    
    
    class TripItem(Item):
        route_name = Field()
        origin_name = Field()
        destination_name = Field()
        departure_time = Field()
        arrival_time = Field()
        duration = Field()
        price = Field()
