import logging
import random
import re
from sys import platform
from time import sleep

from pandas import Series, DataFrame
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from src.alumnifinder.finder import drivers
from src.alumnifinder.utils import jsonreader as json

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
        input_data (panda's DataFrame): DataFrame object from Handler.
        output_data(panda's DataFrame): output DataFrame object
        kwargs (dict): dictionary of arguments that are passed in from the gui.
        - geolocation (str): target region
        - job_position (str): current alumni job position.

    Attributes:
        driver (Selenium WebDriver): used for web scraping.
        start_region (str): initial region for the start of the web search.
        row_first_name (str): first name of an alumni found in a particulate row
        row_last_name (str): last name of an alumni found in a particulate row
        row_index(int): row index that indicates which row is currently being modified
    """

    def __init__(self, input_data: DataFrame, output_data: DataFrame, **kwargs: dict):
        """Initializes Crawler class with optional arguments."""
        self.input_data = input_data
        self.output_data = output_data
        self.geolocation = kwargs['geolocation'] if 'geolocation' in kwargs else ""
        self.job_position = kwargs['job_position'] if 'job_position' in kwargs else ""
        self.row_index = 0
        self.row_counter = int(kwargs["start_row"]) if "start_row" in kwargs else 2
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
        log_phase = 'Setup'
        logger.debug('{}: Setting up web driver...'.format(log_phase))

        if platform.startswith('linux'):
            chrome_path = drivers.LINUX_DRIVER_PATH
        elif platform.startswith('darwin'):
            chrome_path = drivers.MAC_DRIVER_PATH
        elif platform.startswith('win32') or platform.startswith('cygwin'):
            chrome_path = drivers.WIN_DRIVER_PATH
        else:
            msg = '{}: Unsupported operating system found.'.format(log_phase)
            logger.exception(msg)
            raise OSError(msg)
        self.driver = webdriver.Chrome(chrome_path)  # sets member variable.
        logger.debug('{}: SUCCESS.'.format(log_phase))

    def random_pause(self) -> None:
        """Randomly pauses WebDriver.

        The purpose is to lower the chances of web scraping detection.
        """
        log_phase = 'Pause'
        to_pause = random.randint(2, 4)
        logger.debug('{}: Paused for '.format(log_phase) + str(to_pause) + 's')
        sleep(to_pause)

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
        log_phase = 'Login'
        logger.debug('{}: Attempting to login...'.format(log_phase))
        for account in json.get_credentials():
            logger.debug('{}: Finding web element(s)...'.format(log_phase))
            try:
                login_email = WebDriverWait(self.driver, 10).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, 'login-email'))
                )
                login_password = self.driver.find_element_by_class_name('login-password')
                sign_in_btn = self.driver.find_element_by_id('login-submit')
                logger.debug('{}: Inputting login credentials...'.format(log_phase))
                login_email.clear()
                login_email.send_keys(account.get('email'))
                login_password.clear()
                login_password.send_keys(account.get('password'))
                sign_in_btn.click()
            except NoSuchElementException:
                msg = '{}: Web element could not be found.'.format(log_phase)
                logger.exception(msg)
                raise NoSuchElementException(msg)

            if 'Log In or Sign Up' not in self.driver.title:
                logger.debug('{}: SUCCESS.'.format(log_phase))
                return
            else:
                logger.warning('{}: FAILED.'.format(log_phase))
                self.driver.get('https://www.linkedin.com')  # try-again with a different account
                self.driver.delete_all_cookies()

        msg = '{}: Could not login with any credentials.'.format(log_phase)  # All credentials failed
        logger.exception(msg)
        raise EOFError(msg)

    def start_search(self) -> None:
        """Inputs search parameters into search bar.

        Raises:
            NoSuchElementException: Web element could not be found, (most likely changed).
        """
        log_phase = 'Start-Search'
        logger.debug('{}: Finding search bar web element(s)...'.format(log_phase))

        # reload the LinkedIn home page to start search, this is meant to avoid reuse of previous search result
        self.driver.get("https://www.linkedin.com")
        self.random_pause()
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.XPATH, '//*[@class="ember-text-field ember-view"]'))
            )
        except NoSuchElementException:
            msg = '{}: Web element could not be found.'.format(log_phase)
            logger.exception(msg)
            raise NoSuchElementException(msg)
        logger.debug('{}: Inputting arguments into search bar...'.format(log_phase))
        search_bar.clear()
        logger.debug('{}: Searching ['.format(log_phase) + self.row_first_name + " " + self.row_last_name + ']')
        search_bar.send_keys(self.row_first_name + " " + self.row_last_name + " " + self.start_region)
        search_bar.send_keys(Keys.RETURN)

    def get_search_results(self) -> list:
        """WebDriver waits for search results and grabs web elements.

        Returns:
            list of "div"'s from search results.

        Raises:
            NoSuchElementException: Web element could not be found, (most likely changed).
        """
        log_phase = 'Search-Results'
        logger.debug('{}: Waiting for search results of '.format(log_phase) +
                     "[" + self.row_first_name + " " + self.row_last_name + "]")
        try:
            potential_divs = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_all_elements_located((
                    By.XPATH, '//div[@class="search-result__info pt3 pb4 ph0"]')))
            return potential_divs
        except NoSuchElementException:
            msg = '{}: Web element could not be found.'.format(log_phase)
            logger.exception(msg)
            return []
        except TimeoutException:
            logger.debug('{}: No match found.'.format(log_phase))
            return []

    def coarse_filter(self, potential_divs: list, result_set: set) -> None:
        """Populate the result set with coarse-grain filtered result for further evaluation.

        Linkedin occasionally returns irrelevant search results for unknown reason

        Args:
            potential_divs (list):
            result_set (set):
        """
        log_phase = 'Coarse-Filter'
        logger.debug('{}: Starting filter...'.format(log_phase))
        local_row_index = self.row_index
        for div in potential_divs:  # web-element
            logger.debug('{}: Finding web element(s)...'.format(log_phase))
            try:
                inner_anchor = div.find_element(By.TAG_NAME, "a")
                profile_link = inner_anchor.get_attribute("href")

                inner_h3 = inner_anchor.find_element(By.TAG_NAME, "h3")
                inner_h3_id = inner_h3.get_attribute("id")

                inner_span = inner_anchor.find_element(By.XPATH, "//h3[@id=\"" + inner_h3_id + "\"]/span[1]/span")
                inner_span_text = inner_span.text.lower().replace(" ", "")
                # logger.debug('{}: \nrow_first_name: {}\nrow_last_name: {}\ninner_span_text: {}'.format(
                #     log_phase, self.row_first_name, self.row_last_name, inner_span_text))
                if self.row_first_name in inner_span_text and self.row_last_name in inner_span_text:
                    # TODO 1, mark full name on this profile link to output's FULL_NAME_ON_LINKEDIN column
                    self.output_data.at[local_row_index, "FULL_NAME_ON_LINKEDIN"] = inner_span.text

                    # TODO 2, mark this profile link to output's PROFILE_LINK column
                    self.output_data.at[local_row_index,"PROFILE_LINK"] = profile_link
                    # TODO 3, increment the row index(local)
                    local_row_index+=1
                    result_set.add(profile_link)
            except NoSuchElementException:
                msg = '{}: Web element could not be found.'.format(log_phase)
                logger.exception(msg)
                raise NoSuchElementException(msg)
            except StaleElementReferenceException:
                msg = '{}: Web element lost.'.format(log_phase)
                logger.exception(msg)
                raise StaleElementReferenceException(msg)
        log_result = str(len(result_set))
        logger.debug('{}: \"{}\" candidates survived from coarse-grain filter.'.format(log_phase, log_result))

    def fine_filter(self, potential_link_set: set, row) -> None:
        """fine-grain filter that evaluates accuracy score of all candidate profile links"""
        log_phase = 'Fine-Filter'
        log_set_num = str(len(potential_link_set))
        logger.debug('{}: Checking \"{}\" candidates profile links...'.format(log_phase, log_set_num))
        logger.debug('=' * 100)
        for link in potential_link_set:
            logger.debug('{}: Clicked: {}'.format(log_phase, link))
            self.driver.get(link)
            score = 0
            score += self.verify_jobs(row)  # verify job history
            score += self.verify_degrees(row)  # verify education
            # TODO 8, for each iteration mark accuracy score to output's ACCURACY_SCORE column
            self.output_data.at[self.row_index,'ACCURACY_SCORE'] = score
            logger.debug('{}: Accuracy score: {}'.format(log_phase, score))
            logger.debug('=' * 100 + "\n")
            # TODO 9, increment row index(global)
            self.row_index+=1
        self.output_data.at[self.row_index, 'FIRST_NAME'] = ''
        self.row_index += 1

    def verify_jobs(self, row: Series) -> int:
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
                # TODO 5, mark latest job title to output's JOB_TITLE column
                self.output_data.at[self.row_index, 'JOB_TITLE'] = latest_job_title

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
                        # TODO 6, mark latest company to output's COMPANY_NAME column
                        self.output_data.at[self.row_index, 'COMPANY_NAME'] = latest_job_company
                temp_job_info += h4_text + "\n"

            # record job description for the latest job
            if not latest_job_info:
                latest_job_info = temp_job_info
                off_set = latest_job_info.find('Location') + len('Location') + 1
                # TODO 7, mark work location to output's COMPANY_LOCATION column
                self.output_data.at[self.row_index, 'COMPANY_LOCATION'] = latest_job_info[off_set:].replace("\n", "")

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

    def verify_degrees(self, row: Series) -> int:
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

    def check_school(self, str_input: str) -> bool:
        """Check school name with all possible synonyms"""
        if "universityatbuffalo" in str_input or "stateuniversityofnewyorkatbuffalo" in str_input:
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

    def convert_str(self, str_input: str) -> str:
        """helper function to remove all non-alphabet characters in given string, and convert it to lower case"""
        return re.sub("\W", "", str_input).lower()

    def crawl_util(self, row):
        """crawl utility function for loop"""
        log_phase = 'Crawl-Util'
        self.row_first_name = row["FIRST_NAME"].lower()
        self.row_last_name = row["LAST_NAME"].lower()
        self.start_search()
        potential_divs = self.get_search_results()
        log_div = str(len(potential_divs))
        if len(potential_divs) == 0:
            logger.debug("{}: No match for [".format(log_phase) + self.row_first_name + " " + self.row_last_name + "]")
            return
        potential_link_set = set()
        logger.debug("{}: \"{}\" potential div(s) entering coarse-grain filter".format(log_phase, log_div))
        self.coarse_filter(potential_divs, potential_link_set)  # coarse grain filter
        if len(potential_link_set) == 0:
            return
        # TODO 4, mark current search key words to the output's FIRST_NAME, LAST_NAME column
        self.output_data.at[self.row_index,"FIRST_NAME"] = row['FIRST_NAME']
        self.output_data.at[self.row_index, "LAST_NAME"] = row['LAST_NAME']
        self.output_data.at[self.row_index, "ROW_NUMBER_FROM_INPUT"] = self.row_counter
        self.fine_filter(potential_link_set, row)  # fine grain filter

    def crawl_linkedin(self):
        """main routine for UI invocation"""
        self.setup_driver()
        if self.driver:
            self.driver.get("https://www.linkedin.com")
            self.login()
            for index, row in self.input_data.iterrows():
                self.crawl_util(row)
                self.row_counter+=1
                self.random_pause()
            self.driver.close()
            logger.debug("Crawling complete")
