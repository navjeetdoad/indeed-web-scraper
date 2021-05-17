# imports our required modules
import requests
from bs4 import BeautifulSoup
import re
import math

# creates a Scrapper class in order to get our information from the indeed website
class Scraper:
    def __init__(self, job_name: str, location: str, radius: int):
        # takes in our parameters, which are the jobs name, its location, and the radius in which its located
        self.job_name = job_name
        self.location = location
        self.radius = radius
        self._url = ''

        # keeps track of what page of the website we are on and what page number it is
        self.page = None
        self.page_number = 0
        self.get_content()

        # keeps track of if we skip the offer or not
        self.is_skipped = ''
        # we then keep track of the offers that we have found from the website
        self.offers = {}
        # keeps track of the number of offers we've found so far
        self.number_of_offers = 0

        # create a beautiful soup object
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.result = None

        # call find_job_offers in order to create an array of our jobs
        self.__find_job_offers()

    # we create some basic getter/setter functions
    def get_url(self) -> str:
        return self._url

    def set_url(self, url: str) -> None:
        self._url = url

    # connect is used to take the url created from our parameters, and then tries to connect to the website
    def connect(self, url: str) -> object:
        try:
            self.set_url(url)
            connection = requests.get(self.get_url())
            return connection
        except requests.exceptions.RequestException as e:
            return e

    # the url is created from the indeed website by following the pattern created by the url, and thus
    # redirecting us to the correct website
    def get_content(self) -> None:
        self.page = self.connect(f'https://ca.indeed.com/jobs?q=\
{self.job_name}&l={self.location}&sort=date&radius={self.radius}\
&start={self.page_number}')
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.result = self.soup.find(id='resultsCol')

    # we set is_skipped by asking for input from the user
    def skip(self) -> None:
        self.is_skipped = input("Do you want to skip offers that are older than 30 days? (Input y for Yes, or n for No): ")

    def find_jobs_div(self) -> str:
        return self.result.find_all('div', class_='jobsearch-SerpJobCard')

    # a function used to add to our array of jobs by adding the name, location, date and link to the job
    def add_to_offers(self, title: str, company: str, location: str, date: str,
                      link: str) -> None:
        self.offers[title.text.strip()] = {
            'company': company.text.strip(),
            'location': location.text.strip(),
            'date': date.text.strip(),
            'link': "https://pl.indeed.com" + str(link)
        }

    # finds the number of pages that we will be going over
    def find_number_of_pages(self) -> int:
        pages = self.soup.find(id='searchCountPages')
        if not pages:
            return False
        text = pages.text.strip()

        number_of_pages = int(re.findall(r'\d+', text)[1])
        # divides the number by 15 and returns it since there are only 15 jobs on an indeed page
        return math.ceil(number_of_pages / 15)

    def update_pages(self, pages: int) -> list:
        pages_urls = []
        for i in range(pages):
            counter = i * 10
            pages_urls.append(counter)
        return pages_urls

    # checks if we have a location in our job or not
    def is_location_set(self, location: str, job: object) -> tuple:
        if not location:
            location = job.find('span', class_='location')
            if not location:
                return False, None
        return True, location

    def is_over30_skipped(self, date: str) -> bool:
        if self.is_skipped.lower() == 'y':
            if date.text.strip()[:3] == '30+':
                return True
        return False

    # if no offers are found, this function just prints out that none were found. otherwise, we add
    # the jobs to the array and we print that the user should check output.html
    def __find_job_offers(self) -> None:
        # calls skip to see if we should skip finding jobs or not
        self.skip()
        # gets the number of pages we've searched through
        pages = self.find_number_of_pages()
        if not pages:
            print('No offers found! Try to change your query.')
            return
        
        pages_updated = self.update_pages(pages)

        # loops through the page in the pages
        for page in pages_updated:
            self.page_number = page
            # gets the content from the website
            self.get_content()
            jobs = self.find_jobs_div()
            # then loops through the jobs
            for job in jobs:
                # gets the info from each job
                title = job.find('h2', class_='title')
                company = job.find('span', class_='company')
                location = job.find('div', class_='location')
                date = job.find('span', class_='date')
                link = job.find('a')['href']
                
                is_location, location = self.is_location_set(location, job)

                if not is_location or self.is_over30_skipped(date):
                    continue

                if None in (title, company, location, date, link):
                    print("Something went wrong, offer skipped...")
                    continue

                self.add_to_offers(title, company, location, date, link)
                self.number_of_offers += 1
        print("Done! Go check output.html")

    def __repr__(self) -> str:
        return f'Scraper object with {self.get_url()} URL'
