from bs4 import BeautifulSoup
from selenium import webdriver
import MySQLdb as mysql
import time
import random
from MySqlDB import  MySqlDBFetcher
from optparse import OptionParser


#Global variables used in script
# Delay In Number Of Seconds To Use To Slow Down The Script
time_delay = 2
#Implicit wait if JS is still rendering the HTML DOM
implicit_wait_time = 6
#PhantomJS driver used globally across all functions
driver = None
recordsToScrape=30

dbDetailsList=[]
dbSingleJob=[]

jobDetailList=[]




#Custom header used for PhantomJS driver |
#It will make it hard to detect
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
           'Connection': 'keep-alive'
           }


# List of User Agent's, each time driver is being instantiated
# we randomly choose one user agent for scraping
#
uaList=[
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Ubuntu/10.10 Chromium/8.0.552.237 Chrome/8.0.552.237 Safari/534.10',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
'Mozilla/5.0 (compatible; Origyn Web Browser; AmigaOS 4.0; U; en) AppleWebKit/531.0+ (KHTML, like Gecko, Safari/531.0+)',
'Mozilla/5.0 (compatible; Origyn Web Browser; AmigaOS 4.1; ppc; U; en) AppleWebKit/530.0+ (KHTML, like Gecko, Safari/530.0+)'
]



#
#Function creates a new driver or returns an existing driver if any
#using custom header and User Agent
def getOrCreateDriver():
    global driver
    for key, value in headers.iteritems():
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
    webdriver.DesiredCapabilities.PHANTOMJS[
        'phantomjs.page.settings.userAgent'] = random.choice(uaList)
    driver = driver or webdriver.PhantomJS()
    print(driver.capabilities)
    driver.set_window_size(1120, 550)
    driver.implicitly_wait(implicit_wait_time)
    return driver





#
#  Function to create search URL for given
#  parameters as - Search Keyword + Date modified
#
def fetchUrl(keyword,days):
    keyword.replace(" ", "-")
    return "https://www.monster.ca/jobs/search/"+keyword+"_5?tm="+days

#
#Fetch absolute link
#
def getAbsoluteNextPageLink(keyword,relativeLink):
    keyword.replace(" ", "-")
    return "https://www.monster.ca/jobs/search/" + keyword + "_5"+relativeLink



#
#Function to save Job data to a text file with given name
#
def saveToTextFile(jobDescription,fileName):
    f = open(fileName, "w")
    f.write(jobDescription.encode('utf8') + '\n')
    f.close()




#
#Check DB for given details using MySQLDB class
#
#details for given Timestamp
#

def checkDbforDetails(title,company,location,timestamp):
    db = MySqlDBFetcher()
    sql = "SELECT * FROM jobs_raw where TITLE = "+title+" COMPANY = "+company+" LOCATION = "+location.replace('\n','').strip();
    cur = db.fetchDBdetailsforTimeStamp(sql)
    numrows = int(cur.rowcount)
    print('DB check done records - ' + numrows)
    if (numrows > 0):
        return True
    else:
        return False



#
# Scrape until recordsToScrape criteria is fulfilled
#
def searchForEnoughJobs(keyword,days):
    global driver,jobDetailList,recordsToScrape
    url=fetchUrl(keyword,days)
    print('Got url '+str(url))
    driver.get(url)
    print('Got the page!!')
    recordsScraped=0
    try:
        while recordsScraped<recordsToScrape:
#Creating Soup element as it will be faster to parse / Phantomjs has rendered complete DOM
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print('Started scraping homepage!!')

            jobList = soup.find_all("div", {"class": "js_result_details-left"})
            print('Got job list')

            for job in jobList:
                try:
                    singleJobDetail=[]
                    job_data = job.find_all('a')
                    title = job_data[0].span.text
                    company = job_data[1].span.text
                    location = job_data[2].span.text
                    link = job_data[0].get('href')

                    # titles.append(title)
                    # companies.append(company)
                    # locations.append(location)
                    # links.append(link)

                    timestamp=""
                    flag = checkDbforDetails(title,company,location,timestamp)
                    if(flag):
                        continue

                    singleJobDetail.append(link)
                    singleJobDetail.append(title)
                    singleJobDetail.append(company)
                    singleJobDetail.append(location)



#Check if given detail is in our List of data
                    jobDetailList.append(singleJobDetail)
                    recordsScraped = recordsScraped+1
                    print("Scraped - "+title)
                    print("records scraped "+str(recordsScraped))
                    # print(company)
                    # print(link)
                    # print (location)
                    print('----------------\n')

                except Exception as e:
                    print('There is an Exception here!! Moving to DB next page!!')
                    print(e)
                    pass

                    # Got all jobs in given page lets check DB if we got some duplicate
            if(recordsScraped < recordsToScrape):
                print("Scraped all lets goto next page")
                # Moving to Next page as Requirement not satisfied
                next_page_link = soup.find('a', href=True, text='Next')['href']
                absoluteLink=getAbsoluteNextPageLink(keyword,next_page_link)
                print('Got Next Page link - ' + str(absoluteLink))
                driver.get(absoluteLink)
                driver.save_screenshot('Next page link')

            #End of while loop

    except Exception as e:
        print(e)
        print('Error')
        pass
    print('Finished scraping')
    driver.save_screenshot('Done.png')






#
#  Function to fetch for Job Description
#  for Given number of link selected after DB check
#
def fetchJobData(completeDataSet):
    global driver

    for completeData in completeDataSet:
        driver.get(completeData[0])
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print('Started scraping Job posting!!')

        try:
            jobData =  soup.find("div", {"id": "JobDescription"})
            if jobData is None:
                print('Search A failed')
                jobData = soup.find("div", {"id": "CJT-leftpanel"})
                if jobData is None:
                    print('Search B Failed')
                    jobData = soup.find("td", {"class": "jobdesc"})
                    if jobData is None:
                        print('Search A & B & C')
                        jobData = soup.find("div", {"id": "CJT-jobdescp"})
                        if jobData is None:
                            print('All search failed for - '+str(completeData[0]))
            completeData.append(str(completeData[1])+".txt")
            saveToTextFile(jobData.text,str(completeData[1]))
            print('Saved to file - '+completeData[1])

        except Exception as e:
            print("Got an Exception - "+str(e))
    print('\n\n\n\n')






# Main function
if __name__ == "__main__":
    # Opens PhantomJS Web Driver with changed user agent

    driver  =getOrCreateDriver()
    print('Phantomjs started')

    #Searching for jobs in given page until number of Jobs required are fulfilled
    searchForEnoughJobs('java','7')
    print('Done scraping basic Job Data lets check DB and scrape deep!!')

    #Goto each job and fetch more details from that Job
    fetchJobData(jobDetailList)
    print("All scraping done total records scraped - "+len(jobDetailList))
    print("Closing Phantomjs Driver")
    driver.quit()