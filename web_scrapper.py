import re
from time import time
import mysql.connector
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "rps123",
    database = "linkedin"
)

mycursor = mydb.cursor()

start_time = time()
url = "https://www.linkedin.com/jobs/search/?f_TPR=r2592000&geoId=102713980&location=India"
no_of_jobs = 25

driver = webdriver.Chrome("C:\driver\chromedriver.exe")
driver.get(url)
sleep(3)
action = ActionChains(driver)

i = 2
while i <= (no_of_jobs/25):
    driver.find_element_by_xpath('/html/body/main/div/section/button').click()
    i = i + 1
    sleep(5)

pageSource = driver.page_source
lxml_soup = BeautifulSoup(pageSource, 'lxml')

# searching for all job containers
job_container = lxml_soup.find('ul', class_ = 'jobs-search__results-list')

print('You are scraping information about {} jobs.'.format(len(job_container)))

job_id = []

for job in job_container:

    job_ids = job.find('a', href=True)['href']
    job_ids = re.findall(r'(?!-)([0-9]*)(?=\?)', job_ids)[0]
    job_id.append(job_ids)

    job_titles = job.find("span", class_="screen-reader-text").text
    company_names = job.select_one('img')['alt']
    job_locations = job.find("span", class_="job-result-card__location").text
    post_dates = job.select_one('time')['datetime']
    job_desc = "N/A"

    sql = "INSERT INTO link_jobs (job_ids, post_title, company_name, job_location, post_date, job_desc) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (job_ids, job_titles, company_names, job_locations, post_dates, job_desc)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


for x in range(1, len(job_id) + 1):
    # clicking on different job containers to view information about the job
    job_xpath = '/html/body/main/div/section/ul/li[{}]/img'.format(x)
    driver.find_element_by_xpath(job_xpath).click()
    sleep(3)

    jobdesc_xpath = '/html/body/main/section/div[2]/section[2]/div'
    job_descs = driver.find_element_by_xpath(jobdesc_xpath).text

    item = job_id[x-1]

    sql = "UPDATE link_jobs SET job_desc = %s WHERE job_ids = %s"
    val = (job_descs, item)
    mycursor.execute(sql, val)
    mydb.commit()









