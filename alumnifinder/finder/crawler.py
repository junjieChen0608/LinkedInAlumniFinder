import logging
import random
import re
from sys import platform

import pandas as pd
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from alumnifinder.finder import drivers
from alumnifinder.utils import jsonreader

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


class Crawler:
    """Searches LinkedIn for updates on alumni.

    Args:
        data (panda's DataFrame): dataframe object from Handler.
        kwargs (dict): dictionary of arguments that are passed in from the gui.
        - geolocation (str):
        - job_position (str): current alumni job position.

    Attributes:
        driver (Selenium WebDriver): used for web scraping.
        start_region (str): initial region for the start of the web search.
        row_first_name (str): first name of an alumni found in a particulate row
        row_last_name (str): last name of an alumni found in a particulate row
    """

    def __init__(self, data: pd.DataFrame, **kwargs: dict):
        """Initializes Crawler class with optional arguments."""
        self.data = data
        if 'geolocation' in kwargs:
            self.geolocation = kwargs['geolocation']
        if 'jobPosition' in kwargs:
            self.job_position = kwargs['jobPosition']

        self.driver = None
        self.start_region = 'Buffalo'
        self.row_first_name = ""
        self.row_last_name = ""

    def setup_driver(self) -> None:
        """Locates path of WebDriver Chrome executable and sets it to the driver.

        The Selenium WebDriver requires a browser executable in order to open a browser and use the web. We're using
        the Chrome WebDriver for this process and it requires that you have Google Chrome Web Browser pre-installed on
        your machine.

        Raises:
            OSError: Unsupported operating system found.
        """
        LOG_PHASE = 'Setup'
        logger.debug('{}: Setting up web driver...'.format(LOG_PHASE))

        if platform.startswith('linux'):
            chrome_path = drivers.LINUX_DRIVER_PATH
        elif platform.startswith('darwin'):
            chrome_path = drivers.MAC_DRIVER_PATH
        elif platform.startswith('win32') or platform.startswith('cygwin'):
            chrome_path = drivers.WIN_DRIVER_PATH
        else:
            msg = '{}: Unsupported operating system found.'.format(LOG_PHASE)
            logger.exception(msg)
            raise OSError(msg)
        self.driver = webdriver.Chrome(chrome_path)  # sets member variable.
        logger.debug('{}: SUCCESS.'.format(LOG_PHASE))

    def random_pause(self) -> None:
        """Randomly pauses WebDriver.

        The purpose is to lower the chances of web scraping detection.
        """
        # TODO fix random pause with time module
        LOG_PHASE = 'Pause'
        to_pause = random.randint(2, 4)
        # logger.debug('{}: Paused for '.format(LOG_PHASE) + str(to_pause) + 's')
        time.sleep(to_pause)

    def login(self) -> None:
        """WebDriver finds web elements for login and performs login actions.

        The Selenium WebDriver locates the necessary web elements required for the login process. Since LinkedIn can
        change their HTML attributes without notice, this method is prone to failure in the future. If the HTML has
        changed, a maintainer will have to reassign the necessary attributes for the login process. This can easily be
        done by going to the website and using Google Chrome's Web Developers Tools to find the necessary HTML elements.

        Raises:
            NoSuchElementException: Web element could not be found, (most likely changed).
            EOFError: All credentials in 'config/cred.json' failed to login. This could be due to a scraper account
            being blocked.
        """
        LOG_PHASE = 'Login'
        logger.debug('{}: Attempting to login...'.format(LOG_PHASE))
        for account in jsonreader.get_credentials():
            logger.debug('{}: Finding web element(s)...'.format(LOG_PHASE))
            try:
                login_email = WebDriverWait(self.driver, 10).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, 'login-email'))
                )
                login_password = self.driver.find_element_by_class_name('login-password')
                sign_in_btn = self.driver.find_element_by_id('login-submit')
                logger.debug('{}: Inputting login credentials...'.format(LOG_PHASE))
                login_email.clear()
                login_email.send_keys(account.get('email'))
                login_password.clear()
                login_password.send_keys(account.get('password'))
                sign_in_btn.click()
            except NoSuchElementException:
                msg = '{}: Web element could not be found.'.format(LOG_PHASE)
                logger.exception(msg)
                raise NoSuchElementException(msg)

            if 'Log In or Sign Up' not in self.driver.title:
                logger.debug('{}: SUCCESS.'.format(LOG_PHASE))
                return
            else:
                logger.warning('{}: FAILED.'.format(LOG_PHASE))
                self.driver.get('https://www.linkedin.com')  # try-again with a different account

        msg = '{}: Could not login with any credentials.'.format(LOG_PHASE)  # All credentials failed
        logger.exception(msg)
        raise EOFError(msg)

    def start_search(self) -> None:
        """Inputs search parameters into search bar.

        Raises:
            NoSuchElementException: Web element could not be found, (most likely changed).
        """
        LOG_PHASE = 'Start-Search'
        logger.debug('{}: Finding search bar web element(s)...'.format(LOG_PHASE))
        # reload the LinkedIn page to start search, this is meant to avoid reuse of previous search result
        self.driver.get("https://www.linkedin.com")
        self.random_pause()
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.XPATH, '//*[@class="ember-text-field ember-view"]'))
            )
        except NoSuchElementException:
            msg = '{}: Web element could not be found.'.format(LOG_PHASE)
            logger.exception(msg)
            raise NoSuchElementException(msg)
        logger.debug('{}: Inputting arguments into search bar...'.format(LOG_PHASE))
        search_bar.clear()
        logger.debug('{}: Searching ['.format(LOG_PHASE) + self.row_first_name + " " + self.row_last_name + ']')
        search_bar.send_keys(self.row_first_name + " " + self.row_last_name + " " + self.start_region)
        search_bar.send_keys(Keys.RETURN)

    def get_search_results(self) -> list:
        """WebDriver waits for search results and grabs web elements.

        Returns:
            list of "div"'s from search results.

        Raises:
            NoSuchElementException: Web element could not be found, (most likely changed).
        """
        LOG_PHASE = 'Search-Results'
        logger.debug('{}: Waiting for search results of '.format(LOG_PHASE) +
                     "[" + self.row_first_name + " " + self.row_last_name + "]")
        try:
            potential_divs = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_all_elements_located((
                    By.XPATH, '//div[@class="search-result__info pt3 pb4 ph0"]')))
            return potential_divs
        except NoSuchElementException:
            msg = '{}: Web element could not be found.'.format(LOG_PHASE)
            logger.exception(msg)
            return []
        except TimeoutException:
            logger.debug('{}: No match found.'.format(LOG_PHASE))
            return []

    def coarse_filter(self, potential_divs: list, result_set: set) -> None:
        """Populate the result set with coarse-grain filtered result for further evaluation.

        Linkedin occasionally returns irrelevant search results for unknown reason

        Args:
            potential_divs (list):
            result_set (set):
        """
        LOG_PHASE = 'Coarse-Filter'
        logger.debug('{}: Starting filter...'.format(LOG_PHASE))
        for div in potential_divs:  # web-element
            logger.debug('{}: Finding web element(s)...'.format(LOG_PHASE))
            inner_span_text = ""
            try:
                inner_anchor = div.find_element(By.TAG_NAME, "a")
                profile_link = inner_anchor.get_attribute("href")

                inner_h3 = inner_anchor.find_element(By.TAG_NAME, "h3")
                inner_h3_id = inner_h3.get_attribute("id")

                inner_span = inner_anchor.find_element(By.XPATH, "//h3[@id=\"" + inner_h3_id + "\"]/span[1]/span")
                inner_span_text = inner_span.text.lower().replace(" ", "")
                # logger.debug('{}: \nrow_first_name: {}\nrow_last_name: {}\ninner_span_text: {}'.format(
                #     LOG_PHASE, self.row_first_name, self.row_last_name, inner_span_text))
                if self.row_first_name in inner_span_text and self.row_last_name in inner_span_text:
                    result_set.add(profile_link)
            except NoSuchElementException:
                msg = '{}: Web element could not be found.'.format(LOG_PHASE)
                logger.exception(msg)
                raise NoSuchElementException(msg)
            except StaleElementReferenceException:
                msg = '{}: Web element lost.'.format(LOG_PHASE)
                logger.exception(msg)
                raise StaleElementReferenceException(msg)
        log_result = str(len(result_set))
        logger.debug('{}: \"{}\" candidates survived from coarse-grain filter.'.format(LOG_PHASE, log_result))

    def fine_filter(self, potential_link_set: set, row) -> None:
        """fine-grain filter that evaluates accuracy score of all candidate profile links"""
        LOG_PHASE = 'Fine-Filter'
        log_set_num = str(len(potential_link_set))
        logger.debug('{}: Checking \"{}\" candidates profile links...'.format(LOG_PHASE, log_set_num))
        logger.debug('=' * 100)
        for link in potential_link_set:
            logger.debug('{}: Clicked: {}'.format(LOG_PHASE, link))
            self.driver.get(link)
            score = 0
            score += self.verify_jobs(row)  # verify job history
            score += self.verify_degrees(row)  # verify education
            logger.debug('{}: Accuracy score: {}'.format(LOG_PHASE, score))
            logger.debug('=' * 100 + "\n")

    def verify_jobs(self, row: pd.Series) -> int:
        """verify job history, check if input job title matches the latest job tile in this profile link"""
        logger.debug('Verifying jobs...')
        local_score = 0

        # try catch block for error checking, because some profile link have no job data
        try:
            job_list = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_all_elements_located((
                    By.XPATH, '//a[@data-control-name="background_details_company"]')))
        except:
            logger.debug('No job data found.')
            return local_score

        logger.debug(str(len(job_list)) + ' job data found')
        # the top job information in this profile link
        latest_job_title = ""
        latest_job_company = ""
        latest_job_info = ""
        # current job information from input spreadsheet
        if type(row['WORK_TITLE']) is str and row['WORK_TITLE']:
            job_title_from_excel = self.convert_str(row['WORK_TITLE'])
        else:
            job_title_from_excel = ""

        if type(row['WORK_COMPANY_NAME1']) is str and row['WORK_COMPANY_NAME1']:
            job_company_from_excel = self.convert_str(row['WORK_COMPANY_NAME1'])
        else:
            job_company_from_excel = ""

        # iterate on all job history in this profile link
        for job in job_list:

            try:
                job_title = job.find_element(By.TAG_NAME, "h3").text  # get job title
                h4_tags = job.find_elements(By.TAG_NAME, "h4")  # get all other job info
            except NoSuchElementException:
                msg = 'Web element could not be found.'
                logger.exception(msg)
                raise NoSuchElementException(msg)

            # record the top job title as the latest job title
            if not latest_job_title:
                latest_job_title += job_title

            # temp job info is used to compose job description
            temp_job_info = ""
            company_name_sub = ""

            # iterate on all h4 tags in this job item, these h4 tags contain all info about this job title
            for h4 in h4_tags:
                h4_text = h4.text
                h4_text_sub = self.convert_str(h4_text)
                # the actual company name is after this phrase, so we slice the string to get it
                if "companyname" in h4_text_sub:
                    company_name_sub = h4_text_sub[len("companyname"):]
                    if not latest_job_company:
                        latest_job_company = h4_text[len("Company Name") + 1:]
                temp_job_info += h4_text + "\n"

            # record job description for the latest job
            if not latest_job_info:
                latest_job_info = temp_job_info

            # check if current job is empty in the spreadsheet, if yes, just replace it with latest job from LinkedIn
            # and break the loop
            if not job_title_from_excel:
                job_title_from_excel = latest_job_title
                job_company_from_excel = latest_job_company
                logger.debug('Empty job is currently on record, break loop since new job is found')
                logger.debug('Current job: ' + job_title_from_excel)
                logger.debug('Current company: ' + job_company_from_excel)
                break

            # check if job title matches
            job_title_sub = self.convert_str(job_title)
            if job_title_sub in job_title_from_excel or job_title_from_excel in job_title_sub:
                logger.debug('Job title match.')
                local_score += 1

            # check if company matches
            if job_company_from_excel in company_name_sub or company_name_sub in job_company_from_excel:
                logger.debug('Company name match.')
                local_score += 1

        logger.debug('latest job: ' + latest_job_title)
        logger.debug('latest job info: ' + latest_job_info)
        logger.debug('*' * 100)
        local_score += self.verify_jobs_helper(self.convert_str(latest_job_title), self.convert_str(latest_job_info))
        return local_score

    def verify_jobs_helper(self, job_title: str, job_info: str) -> int:
        """match search keywords with the latest job"""
        local_score = 0
        if self.job_position:
            target_job = self.convert_str(self.job_position)
            if job_title in target_job:
                local_score += 1
        if self.geolocation:
            target_location = self.convert_str(self.geolocation)
            if target_location in job_info:
                local_score += 1
        return local_score

    def verify_degrees(self, row: pd.Series) -> int:
        """verify education data of this link, i.e., school name, major, grad year"""
        logger.debug('Verifying degrees...')
        local_score = 0
        # error checking, for some profile link don't even have education info
        try:
            education_list = WebDriverWait(self.driver, 5).until(
                #  The reason why choose this xpath is <a> tags with this data-control-name wraps all the data we want
                expected_conditions.presence_of_all_elements_located((
                    By.XPATH, '//a[@data-control-name="background_details_school"]')))
        except TimeoutException:
            logger.debug('No education data found.')
            return local_score

        logger.debug(str(len(education_list)) + " education data found\n")
        schools = [row['SCHOOL1'], row['SCHOOL2'], row['SCHOOL3']]
        majors = [row['MAJOR1'], row['MAJOR2'], row['MAJOR3']]
        degrees = [row['DEGREE_CODE1'], row['DEGREE_CODE2'], row['DEGREE_CODE3']]
        grad_yrs = [row['DEGREE_YEAR1'], row['DEGREE_YEAR2'], row['DEGREE_YEAR3']]
        #  There are 3 school columns in the input spreadsheet
        #   need to match each of them with current profile link
        for school_col, major_col, degree_col, gradyrs_col in zip(schools, majors, degrees, grad_yrs):
            # check current school_col value is a non-empty string, not other type
            if type(school_col) is str and school_col:
                # iterate on all education data in this profile link
                for education in education_list:
                    # find school name
                    school = education.find_element(By.TAG_NAME, "h3")
                    school_name = school.text
                    # logger.debug(school_name)
                    # check school
                    if self.check_school(self.convert_str(school_name)):
                        logger.debug("school match.")
                        local_score += 1

                    # find major info
                    major_infos = education.find_elements(By.CLASS_NAME, "pv-entity__comma-item")
                    major_text = ""
                    for major_info in major_infos:
                        # logger.debug(major_info.text)
                        major_text += major_info.text
                    # logger.debug(major_text)
                    # check major and degree
                    if self.check_degree(self.convert_str(major_text), self.convert_str(degree_col)):
                        logger.debug("degree match.")
                        local_score += 1

                    if self.check_major(self.convert_str(major_text), self.convert_str(major_col)):
                        logger.debug("major match.")
                        local_score += 1

                    # find graduation year
                    grad_years = education.find_elements(By.TAG_NAME, "time")
                    grad_year = ""
                    if len(grad_years) == 2:
                        grad_year = grad_years[1].text
                    elif len(grad_years) == 1:
                        grad_year = grad_years[0].text

                    logger.debug("graduation year: " + grad_year)
                    if self.check_gradyear(grad_year, str(int(gradyrs_col))):
                        logger.debug("graduation year match.")
                        local_score += 1
        return local_score

    def check_school(self, input: str) -> bool:
        """Check school name with all possible synonyms"""
        # TODO: add more possible synonyms
        if "universityatbuffalo" in input or "stateuniversityofnewyorkatbuffalo" in input:
            return True
        else:
            return False

    def check_degree(self, text_from_web: str, text_from_sheet: str) -> bool:
        """check if degree matches"""
        if ("bachelor" in text_from_web or "master" in text_from_web) and "science" in text_from_web:
            if "bs" in text_from_sheet:
                return True
            elif "ms" in text_from_sheet:
                return True
            else:
                return False
        elif ("bachelor" in text_from_web or "master" in text_from_web) and "art" in text_from_web:
            if "ba" in text_from_sheet:
                return True
            elif "ma" in text_from_sheet:
                return True
            else:
                return False
        else:
            return text_from_sheet in text_from_web

    def check_major(self, text_from_web: str, text_from_sheet: str) -> bool:
        """check major"""
        return text_from_sheet in text_from_web

    def check_gradyear(self, text_from_web: str, text_from_sheet: str) -> bool:
        """check graduation year"""
        return text_from_web == text_from_sheet

    def convert_str(self, input: str) -> str:
        """helper function to remove all non-alphabet characters in given string, and convert it to lower case"""
        return re.sub("\W", "", input).lower()

    def crawl_util(self, row):
        """crawl utility function for loop"""
        LOG_PHASE = 'Crawl-Util'
        self.row_first_name = row["FIRST_NAME"].lower()
        self.row_last_name = row["LAST_NAME"].lower()
        self.start_search()
        potential_divs = self.get_search_results()
        log_div = str(len(potential_divs))
        if len(potential_divs) == 0:
            logger.debug("{}: No match for [".format(LOG_PHASE) + self.row_first_name + " " + self.row_last_name + "]...")
            return
        potential_link_set = set()
        logger.debug("{}: \"{}\" potential div(s) entering coarse-grain filter".format(LOG_PHASE, log_div))
        self.coarse_filter(potential_divs, potential_link_set)  # coarse grain filter
        if len(potential_link_set) == 0:
            return
        self.fine_filter(potential_link_set, row)  # fine grain filter

    def crawl_linkedin(self):
        """main routine for UI invocation"""
        self.setup_driver()
        if self.driver:
            self.driver.get("https://www.linkedin.com")
            self.login()
            for index, row in self.data.iterrows():
                self.crawl_util(row)
                self.random_pause()
            self.driver.close()
            logger.debug("Crawling complete")
