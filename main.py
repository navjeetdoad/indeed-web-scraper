# imports our scraper and template modules
from scraper.scraper import Scraper
from scraper.template import Template

# function used to just facilitate our inputs
def start_scraping():
    # gets our parameters that we will use in the scraper class when we call it
    job_name = input('Enter job name: ')
    place = input('Enter place: ')
    radius = int(input('Enter radius: '))
    # call the scraper class
    scraper = Scraper(job_name, place, radius)
    # print the job url out
    print(f'URL: {scraper.page.url}, Place: {scraper.location}, Job name: \
{scraper.job_name}\n')
    # then we just call our template class
    template = Template(scraper.offers, scraper.number_of_offers)

# call start_scraping in our main function
if __name__ == '__main__':
    start_scraping()
