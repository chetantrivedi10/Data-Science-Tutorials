__author__="Anurag"
from selenium import webdriver
from bs4 import BeautifulSoup
import time,datetime,re,random
# from urllib.parse import urlencode
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox import firefox_profile
from DataCollection.config import Monster_config
config = Monster_config()
import logging
from DataCollection.config import logfile,logformat
class job_link_scraping():
    def __init__(self):
        self.logger = logging.getLogger("Monster job links scraping")
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(filename=logfile)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(logformat)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def linksAutomation(self, database, keyword, location=None, browser="phantomjs"):

        if browser == "firefox":
            self.driver = webdriver.Firefox()
        elif browser == "chrome":
            self.driver = webdriver.Chrome(config["chromepath"])
        else:
            self.driver = webdriver.PhantomJS(config["phantomjspath"])

        self.driver.delete_all_cookies()
        self.baseurl = "http://www.monsterindia.com/"
        if location:
            self.searchurl = self.baseurl + keyword.strip().lower().replace(" ","-") + "-jobs-in-" + location.strip().lower()+".html"
        else:
            self.searchurl = self.baseurl + keyword.strip().lower().replace(" ","-") + "-jobs"+".html"

        self.logger.info("search url - %s",self.searchurl)

        self.driver.get(self.searchurl)
        pageCount = self.pagecount(self.driver.page_source)
        self.logger.info("total jobs found - %s",pageCount)
        for pagenumber in range(1, round(pageCount / 40)):
            pagination = self.driver.find_element_by_class_name("pagination.pull-right")
            pages = pagination.find_elements_by_tag_name("li")
            pages[pagenumber+1].find_element_by_tag_name("a").click()
            time.sleep(random.randint(5, 10))
            # print(pagenumber,pages)
            self.logger.info("current url - %s",self.driver.current_url)
            # trickurl = self.searchurl.replace(".html","")+"-"+str(pagenumber)+".html"
            # self.driver.get(trickurl)
            for job in self.linksScraper(self.driver.page_source):
                try:
                    self.logger.info("job link - %s",job)
                    self.logger.info("inserting job link in database - %s",database.insert(job))
                except Exception as e:
                    self.logger.fatal("exception in inserting job link  - %s", e)
                    pass

        self.driver.close()

    def pagecount(self, page):
        Soup = BeautifulSoup(page, "lxml")
        try:
            jobs = int(Soup.find(config["job_count"]["name"], config["job_count"]["attrs"]).text.split("of")[-1].split()[0])
            return jobs
        except Exception as e:
            self.logger.fatal("exception in find jobs count - %s",e)
            return "Error"

    def linksScraper(self,page):
        Soup = BeautifulSoup(page,"lxml")
        descriptionArray = []
        # postedday = [i.text for i in Soup.find_all("time",{"class":"share_links jobDate cls_job_date_format"})]

        for indx,jobs in enumerate(Soup.find_all(config["job_section"]["name"], config["job_section"]["attrs"])):
            descriptionurl = ""
            descriptionId = ""
            descriptionTitle = ""
            employerName = ""
            exprequired = ""
            location = ""
            skillsRequired = ""
            summary = ""
            salary = ""
            recruiter = ""
            postedDay = ""
            morejobs = ""

            ####################### Title ###############################
            try:
                descriptionTitle = jobs.find(config["job_title"]["name"], config["job_title"]["attrs"]).text.strip()
            except Exception as e:
                self.logger.exception("exception in job title  - %s",e)
                pass

            ####################### Description Url #####################
            try:
                descriptionurl = jobs.find(config["job_url"]["name"], config["job_url"]["attrs"])["href"].strip()
            except Exception as e:
                self.logger.exception("exception in job url - %s",e)
                pass

            # ####################### Description ID ######################
            try:
                descriptionId = re.findall("(\d+?.html\?)",jobs.find(config["job_url"]["name"], config["job_url"]["attrs"])["href"].strip())[0].split(".")[0]
            except Exception as e:
                self.logger.exception("exception in job id - %s",e)
                pass

            ####################### Job Summary #########################
            try:
                summary = jobs.find(config["job_summary"]["name"], config["job_summary"]["attrs"]).text.strip()
            except Exception as e:
                self.logger.exception("exception in job summary - %s",e)
                pass

            ######################## Job Employer ########################
            try:
                employerName = jobs.find(config["job_employer"]["name"], config["job_employer"]["attrs"]).text.strip()
            except Exception as e:
                self.logger.exception("exception in employer name - %s",e)
                pass

            ####################### Job Employer Url ####################
            # try:
            #     morejobs = jobs.find("span",{"class":"hidden-xs"}).find("a",{"class":"dice-btn-link"})["href"].strip()
            # except Exception as e:
            #     print("exception in employer url ",e)
            #     pass
            ######################## Job Location #######################
            try:
                location = jobs.find(config["job_location"]["name"], config["job_location"]["attrs"]).text.strip()
            except Exception as e:
                self.logger.exception("exception in job location - %s",e)
                pass

            ####################### skills Required ######################
            try:
                skillsRequired = jobs.find(config["job_skills"]["name"], config["job_skills"]["attrs"]).text
            except Exception as e:
                self.logger.exception("exception in job skills - %s",e)
                pass

            ####################### experience Required #################
            try:
                exprequired = jobs.find(config["job_experience"]["name"], config["job_experience"]["attrs"]).text.strip()
            except Exception as e:
                self.logger.exception("Exception in experience required - %s",e)
                pass

            ####################### Job Posted Date #####################
            try:
                postedDay = jobs.find(config["job_posted"]["name"], config["job_posted"]["attrs"]).text.split(":")[-1].strip()
            except Exception as e:
                self.logger.exception("exception in job Posted Date - %s", e)
                pass

            # print("descriptiontitle ----------->",descriptionTitle)
            # print("descriptionId    ----------->",descriptionId)
            # print("descriptionurl   ----------->",descriptionurl)
            # print("descriptionlocation -------->",location)
            # print("descriptionemployer -------->",employerName)
            # print("descriptionemployerUrl ----->",morejobs)
            # print("descriptionPostedDate ------>",postedDay)
            # print("descriptionSummary --------->",summary)
            # print("descriptionSkills ---------->",skillsRequired)
            # print("descriptionExperience ------>",exprequired)
            # print("***************************************************************************************")
            descriptionDict = {}
            descriptionDict["_id"] = descriptionurl
            descriptionDict["jobDescriptionID"] = descriptionId
            descriptionDict["jobDescriptionURL"] = descriptionurl
            descriptionDict["jobTitle"] = descriptionTitle
            descriptionDict["jobLocation"] = location
            descriptionDict["jobSummary"] = summary
            descriptionDict["jobSalary"] = salary
            descriptionDict["jobPosted"] = postedDay
            descriptionDict["jobExperience"] = exprequired
            descriptionDict["jobSkills"] = skillsRequired
            descriptionDict["jobType"] = ""
            descriptionDict["employer"] = employerName
            descriptionDict["scrapTime"] = datetime.datetime.now()
            descriptionDict["postType"] = "general"
            descriptionDict["processFlag"] = "false"
            descriptionDict["source"] = "MonsterIndia"
            descriptionDict["moreJobsURL"] = ""
            descriptionDict["postedBy"] = recruiter
            descriptionArray.append(descriptionDict)

        return descriptionArray

class job_description_scraping():

    def __init__(self):
        self.logger = logging.getLogger("Monster Job Description Scraping")
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(filename=logfile)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(logformat)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def descriptionAutomation(self,database,browser = "phantomjs"):

        if browser=="firefox":
            self.driver = webdriver.Firefox()

        elif browser=="chrome":
            self.driver = webdriver.Chrome(config["chromepath"])

        else:
            self.driver = webdriver.PhantomJS(config["phantomjspath"])

        for joblink in database.find({"processFlag":"false"},
                                     {"_id":1}, no_cursor_timeout=True):

            self.jobDescUrl = joblink["_id"]
            self.logger.info("job description url - %s",self.jobDescUrl)
            self.driver.get(self.jobDescUrl)
            time.sleep(random.randint(5,20))
            ########## calling function to extract the data #############
            FullDesc = self.descriptionExtraction(page=self.driver.page_source)
            if FullDesc:
                try:
                    self.logger.info("updating job description - %s",
                    database.update({"_id":joblink["_id"]},{"$set":{"full_desc":str(FullDesc),
                                                                    "descriptionPage":self.driver.page_source,
                                                                    "processFlag":"true",
                                                                    "descTime":datetime.datetime.now()}}))
                except Exception as e:
                    self.logger.fatal("exception in updating job description - %s",e)
                    pass
        self.driver.close()

    def descriptionExtraction(self,page):
        Soup = BeautifulSoup(page,"lxml")
        try:
            Description = "\n <br> \n".join([str(X) for X in Soup.findAll(config["job_description"]["name"], config["job_description"]["attrs"])])
            skils = ", ".join([i.text for i in Soup.findAll(config["job_description_skills"]["name"], config["job_description_skills"]["attrs"])])
            output = Description+"\n <br> \n"+skils
            return output
        except Exception as e:
            self.logger.fatal("exception in finding job description - %s",e)
            return "Error"

if __name__ == '__main__':
    from pymongo import MongoClient
    db = MongoClient("localhost",27017)["jd-scraper"]["monsterindia.com"]
    # classcall = job_link_scraping().linksAutomation(db, keyword="java developer",browser="firefox")

    # page = open("/home/anurag/Desktop/monster_links.html","r").read()
    # classcall = job_link_scraping().linksScraper(page=page)

    # page = open("/home/anurag/Desktop/monster_description.html","r").read()

    classcall2 = job_description_scraping().descriptionAutomation(database=db,browser="firefox")
    # print("classcall",classcall)