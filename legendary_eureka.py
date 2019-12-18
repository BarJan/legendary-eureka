#!/usr/bin/env python3

import re
import requests
import urllib.request

from linkedin import linkedin
from bs4 import BeautifulSoup


class Resource:
    def __init__(self, name):
        self.name = name

    def get_jobs(self):
        return None


class Linkedin(Resource):
    def __init__(self):
        Resource.__init__(self, 'linkedin')

    def scrap(self, jobsURL):
        try:
            # parsing jobs URL with
            page = urllib.request.urlopen(jobsURL)
            soup = BeautifulSoup(page, 'html.parser')
            if soup is not None:
                return soup
            else:
                return None
        except NameError:
            print('Error while scraping information from LinkedIn')

    def get_jobs(self, url):
        soup = self.scrap(url)
        jobs = self.extractJobs(soup)
        return jobs

    def extractJobs(self, soup):
        if soup is not None:
            jobTitleRegex = re.compile('^result-card__full-card-link')
            jobsList = soup.find_all('a', attrs={'class': jobTitleRegex})
            companyTitleRegex = re.compile('COMPANY-*')
            companysList = soup.find_all('label', attrs={'for': companyTitleRegex})
            linksList = []
            for link in jobsList:
                linksList.append(link.get('href'))
            finalList = []
            for job, company, link in zip(jobsList, companysList, linksList):
                finalList.append(
                    'Job Title: ' + str(job.getText()) + ',Comapny: ' + str(company.getText()) + ', Link:' + link)
            # Converting final list into dict
            finalDict = {i: finalList[i] for i in range(0, len(finalList))}
            return finalDict
        else:
            return None


class Indeed(Resource):
    def __init__(self):
        Resource.__init__(self, 'indeed')

    # TODO
    def get_jobs(self):
        pass


class Glassdoor(Resource):
    JOB_TYPES = ['fulltime', 'parttime', 'contract', 'internship', 'temporary', 'apprenticeship', 'entrylevel']

    def __init__(self):
        Resource.__init__(self, 'glassdoor')

        
    def get_jobs(self, job_title: str, job_location: str = None, job_type: str = None):
        """
        using part of code from: https://gist.github.com/scrapehero/352286d0f9dee87990cd45c3f979e7cb
        :param job_title: for example: 'python developer'.
        :param job_type: (optional) as in JOB_TYPES class variable.
        :param job_location: (optional, default = Israel) for search in specific Israel location, like: 'Tel Aviv'.
        """
        if job_type is None:
            job_type = ''

        elif job_type.lower().strip() not in self.JOB_TYPES:
            print(f'Job type {job_type} not found, searching for any job type instead.\n'
                  f'acceptable job types are: {" / ".join(self.JOB_TYPES)}')
            job_type = ''

        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
        }

        job_listing_url = 'https://www.glassdoor.com/Job/jobs.htm'

        print('Fetching location details')
        if job_location and job_location.lower().strip() != 'israel':  # searching jobs in specific location

            # Getting location id for search location
            location_headers = {
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                              ' Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
            }
            data = {
                'term': 'Israel',
                'maxLocationsToReturn': 9999  # true max is 1605
            }

            # TODO: wrap requests.post with try / except.
            location_url = 'https://www.glassdoor.co.in/findPopularLocationAjax.htm?'
            location_response = requests.post(location_url, headers=location_headers, data=data).json()

            # TODO: consider loading all cities and matching loc_id from json file
            #  and skip this part and next if also (?)
            for city_dict in location_response:
                if city_dict['countryName'] == 'Israel':
                    city_name = ' '.join(city_dict['label'].split()[:-1])
                    if city_name.lower() == job_location.lower().strip():
                        job_location = city_dict['label']
                        break

            if job_location in [dictionary['label'] for dictionary in location_response]:
                location_response = [dictionary for dictionary in location_response
                                     if job_location == dictionary['label']]

                loc_id = location_response[0]['locationId']
                loc_label = location_response[0]['label']

                # Form data to get job results
                loc_t = 'C'
                loc_id = loc_id
                print(f'Fetching jobs for location: {loc_label}')

            else:
                # TODO: add note in print message to look in help command that will show available cities
                #  (from data/json file) for search.
                print(f'Job location "{job_location}" not found')
                return False

        else:  # searching jobs in all Israel
            print('Fetching jobs for location: Israel')
            job_location = 'Israel'
            loc_t = 'N'
            loc_id = 119

        data = {
            'clickSource': 'searchBtn',
            'sc.keyword': job_title,
            'locT': loc_t,
            'locId': loc_id,
            'jobType': job_type
        }

        # TODO: wrap requests.post with try / except.
        response = requests.post(job_listing_url, headers=headers, data=data)
        soup = BeautifulSoup(response.content, 'html.parser')

        job_listings = {}
        for a in soup.find_all('a', href=True):

            # filtering job links that not containing job title (clickable image/company name/location links)
            if a['href'].startswith('/partner/') and \
                    (a.string is not None) and \
                    (a.string != 'JobInfo'):

                link = a['href']
                full_link = 'https://www.glassdoor.com' + link
                job_id = int(link.split('jobListingId=')[1])

                # avoid possible duplicates by comparing details
                if (job_location in job_listings) and (job_id not in job_listings[job_location]):
                    job_listings[job_location].update({job_id: [a.string, full_link]})

                elif (job_location in job_listings) and (a.string not in job_listings[job_location][job_id]):
                    job_listings[job_location][job_id].append(a.string)

                else:
                    job_listings[job_location] = {job_id: [a.string, full_link]}

        # return dictionary with search results: {job_location: {job_id: [job_title, job_link]}}
        return job_listings
