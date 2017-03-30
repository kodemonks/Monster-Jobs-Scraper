# MonsterJobs Scraper


## Web Scraper to Scrape Monster Jobs for new job postings :

### Script Depenencies :
*  Python version - 2.7
*  BeautofulSoup
*  selenium         
*  phantomjs  
*  mysql-connector-python

## HOW TO USE -  

Script takes two input arguments - Search Keyword (i.e. - 'Java','Data Analyst') + Job post days (i.e. - 7 or 9)
i.e. -
*   Python MonsteJobsScraper 'Java' 7

## Module details : 

Script uses Python and phantomjs (headless browser) to scrape Jobs section from monster jobs.
If detail is new then Job Description is saved as Text file and an entry is done in MySQL for same.


## Other details :

* All Job Description will be saved in outputJobs folder and filename will be saved in MySQLDB.
* Logfile - ghostdriver.log (phantomjs driver logs)  +   MonsterJobs.log (Module logs).
* All Job Description will be saved in outputJobs folder and filename will be saved in MySQLDB.


## DB will be updated with following details - 
* Job Title
* Company Name
* Location
* registration date
* Output Job Desc. file-name.
