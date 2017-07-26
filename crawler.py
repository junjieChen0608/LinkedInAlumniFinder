"""
Please read me if you are a developer

You need to:
1, No doubt that you need to install Chrome Webdriver and Selenium in order to get the whole program running
2, change the Chrome Webdriver path to your own path in the setup_driver()
3, fill in dummy Linkedin account before the call of simulate_login()

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from sys import platform
import os
import random
from xlrd import open_workbook
from xlutils.copy import copy
import re


class LinkedinCrawler:
    def __init__(self, info_dict, file_path):
        # TODO change constructor signature to a dictionary and a file path string
        self.first_name = ""
        self.last_name = ""
        self.file_path = ""
        self.first_name_index = 11
        self.last_name_index = 12
        self.job_title_index = 24
        self.company_name_index = 25
        self.school1_index = 36
        self.school2_index = 40
        self.school3_index = 44
        self.start_row = 2
        self.end_row = 2
        self.read_book = None
        self.read_sheet = None
        self.write_book = None
        self.write_sheet = None
        if file_path == "":
            self.first_name = info_dict["firstName"].lower()
            self.last_name = info_dict["lastName"].lower()
        else:
            self.file_path = file_path
            print("Batch search with file: " + self.file_path)
        self.driver = None

    """
    randomly pause for few seconds, make it slow and steady
    """
    def random_pause(self):
        random.seed()
        to_pause = random.randint(1, 5)
        self.driver.implicitly_wait(to_pause)


    """
    web driver set up
    """
    def setup_driver(self, page):
        print("\nSetting up web driver...\n")
        chrome_path = ""
        if platform.startswith('linux'):
            chrome_path = os.path.abspath("drivers/chromedriver_linux64")
        elif platform.startswith('darwin'):
            chrome_path = os.path.abspath("drivers/chromedriver_mac64")
        elif platform.startswith('win32') or platform.startswith('cygwin'):
            chrome_path = os.path.abspath("drivers/chromedriver_win32.exe")
        else:
            raise ValueError('Operating System not supported!')
        self.driver = webdriver.Chrome(chrome_path)
        self.driver.get(page)


    """
    simulate login
    """
    def simulate_login(self, email, password):
        if email == "" or password == "":
            print("email and password cannot be empty.")
            raise RuntimeError

        # automated login process
        login_email = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-email"))
        )
        login_password = self.driver.find_element_by_class_name("login-password")
        sign_in_btn = self.driver.find_element_by_id("login-submit")

        # input credentials then log in
        print("Inputting credentials...\n")
        login_email.clear()
        login_email.send_keys(email)
        login_password.clear()
        login_password.send_keys(password)
        sign_in_btn.click()


    """
    start searching
    """
    def start_search(self, region="buffalo"):

        search_bar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//*[@class="ember-text-field ember-view"]"""))
        )

        search_bar.clear()
        search_bar.send_keys(self.first_name + " " + self.last_name + " " + region)
        search_bar.send_keys(Keys.RETURN)


    """
    wait result page to render
    """
    def wait_result(self):

        try:
            potential_divs = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, """//div[@class="search-result__info pt3 pb4 ph0"]"""))
            )
            return potential_divs
        except TimeoutException:
            print("No match!!")
            return []


    """
    populate the result set with coarse-grain filtered result
    for further evaluation, Linkedin occasionally returns irrelevant search results for unknown reason
    """
    def coarse_filter(self, potential_divs, result_set):

        for div in potential_divs:
            inner_anchor = div.find_element(By.TAG_NAME, "a")
            profile_link = inner_anchor.get_attribute("href")

            inner_h3 = inner_anchor.find_element(By.TAG_NAME, "h3")
            inner_h3_id = inner_h3.get_attribute("id")

            inner_span = inner_anchor.find_element(By.XPATH, "//*[@id=\"" + inner_h3_id + "\"]/span[1]/span")
            inner_span_text = inner_span.text.lower().replace(" ", "")
            if self.first_name in inner_span_text and self.last_name in inner_span_text:
                result_set.add(profile_link)
        print(str(len(result_set)) + " candidates survived from coarse-grain filter")


    """
    fine-grain filter that evaluates accuracy score of all candidate profile links
    """
    def fine_filter(self, potential_link_set, row=0):
        print("Checking " + str(len(potential_link_set)) + " potential profile links...\n")
        print("=" * 100)
        for link in potential_link_set:
            print("Clicked: " + link)
            self.driver.get(link)
            score = 0

            #verify job history
            score += self.verify_job(row)

            # verify education
            score += self.verify_degree(row)
            print("Accuracy score:", score)
            print("=" * 100)


    """
    verify job history, check if input job title matches the latest job tile in this profile link
    """
    def verify_job(self, row=0):
        local_score = 0
        print("verifying job...")
        job_list = None

        # try catch block for error checking, because some profile link have no job data
        try:
            job_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located( (By.XPATH,
                                                     """//a[@data-control-name="background_details_company"]"""))
            )
        except:
            print("No job data found!!\n")
            return local_score

        print(str(len(job_list)) + " job data found\n")
        # the top job information in this profile link
        latest_job_title = ""
        latest_company = ""
        latest_job_info = ""
        # current job information from input spreadsheet
        current_job_title = self.convert_str(self.read_sheet.cell(row, self.job_title_index).value)
        current_company = self.convert_str(self.read_sheet.cell(row, self.company_name_index).value)
        # iterate on all job history in this profile link
        for job in job_list:
            # get job title
            job_title = job.find_element(By.TAG_NAME, "h3").text

            # record the top job title as the latest job title
            if latest_job_title == "":
                latest_job_title += job_title

            #  get all other job info
            h4_tags = job.find_elements(By.TAG_NAME, "h4")
            # temp job info is used to compose job description
            temp_job_info = ""
            company_name = ""
            # iterate on all h4 tags in this job item, these h4 tags contain all info about this job title
            for h4 in h4_tags:
                h4_text = h4.text
                h4_text_sub = self.convert_str(h4_text)
                # the actual company name is after this phrase, so we slice the string to get it
                if "companyname" in h4_text_sub:
                    company_name = h4_text_sub[len("companyname"):]
                    if latest_company == "":
                        latest_company = h4_text[len("Company Name")+1:]
                temp_job_info += h4_text + "\n"

            # record job description for the latest job
            if latest_job_info == "":
                latest_job_info = temp_job_info

            #  check if current job is empty in the spreadsheet, if yes, just replace it with latest one and break the loop
            if current_job_title == "":
                current_job_title = latest_job_title
                current_company = latest_company
                print("empty job is currently on record, break loop since new job is found")
                print("current job: " + current_job_title + "\ncurrent company: " + current_company)
                break

            # check if job title matches
            position_sub = self.convert_str(job_title)
            if position_sub in current_job_title or current_job_title in position_sub:
                print("job title match!!")
                local_score += 1

            # check if company matches
            if current_company in company_name or company_name in current_company:
                print("company name match!!")
                local_score += 1

        print("latest job:\n" + latest_job_title + "\n" + latest_job_info)
        print("*" * 100)
        return local_score


    """
    verify education data of this link, i.e., school name, major, grad year
    """
    def verify_degree(self, row=0):
        local_socre = 0
        print("verifying degree...")
        education_list = None
        # error checking, for some profile link don't even have education info
        try:
            education_list = WebDriverWait(self.driver, 10).until(
                #  The reason why choose this xpath is <a> tags with this data-control-name wraps all the data we want
                EC.presence_of_all_elements_located((By.XPATH,
                                                     """//a[@data-control-name="background_details_school"]"""))
            )
        except TimeoutException:
            print("No education data found!!")
            return local_socre

        print(str(len(education_list)) + " education data found\n")

        #  There are 3 school columns in the input spreadsheet
        #   need to match each of them with current profile link
        for col in range(self.school1_index, self.school3_index+1, 4):
            if self.read_sheet.cell(row, col).value != "":
                # iterate on all education data in this profile link
                for education in education_list:
                    # find school name
                    school = education.find_element(By.TAG_NAME, "h3")
                    school_name = school.text
                    print(school_name)
                    # check school
                    if self.check_school(self.convert_str(school_name)) == 1:
                        print("school match!!")
                        local_socre += 1

                    # find major info
                    major_infos = education.find_elements(By.CLASS_NAME, "pv-entity__comma-item")
                    major_text = ""
                    for major_info in major_infos:
                        # print(major_info.text)
                        major_text += major_info.text
                    print(major_text)
                    # check major and degree
                    if self.check_degree(self.convert_str(major_text),
                                         self.convert_str(self.read_sheet.cell(row, col + 1).value)) == 1:
                        print("degree match!!")
                        local_socre += 1

                    if self.check_major(self.convert_str(self.read_sheet.cell(row, col+3).value),
                                        self.convert_str(major_text)) == 1:
                        print("major match!!")
                        local_socre += 1

                    # find graduation year
                    grad_years = education.find_elements(By.TAG_NAME, "time")
                    grad_year = ""
                    if len(grad_years) == 2:
                        grad_year = grad_years[1].text
                    elif len(grad_years) == 1:
                        grad_year = grad_years[0].text

                    print("graduation year: " + grad_year + "\n")
                    if self.check_gradyear(str(int(self.read_sheet.cell(row, col+2).value)), grad_year) == 1:
                        print("graduation year match!!")
                        local_socre += 1
        return local_socre


    """
    check school name with all possible synonyms
    """
    def check_school(self, input):
        if "universityatbuffalo" in input or "stateuniversityofnewyorkatbuffalo" in input:
            return 1


    """
    check if degree matches
    """
    def check_degree(self, base_text, compare_to):
        if ("bachelor" in base_text or "master" in base_text) and "science" in base_text:
            if "bs" in compare_to:
                return 1
            elif "ms" in compare_to:
                return 1
            else:
                return 0
        elif ("bachelor" in base_text or "master" in base_text) and "art" in base_text:
            if "ba" in compare_to:
                return 1
            elif "ma" in compare_to:
                return 1
            else:
                return 0
        else:
            return 1 if compare_to in base_text else 0

    """
    check major
    """
    def check_major(self, base_text, compare_to):
        return 1 if base_text in compare_to else 0


    """
    check graduation year
    """
    def check_gradyear(self, base_text, compare_to):
        return 1 if base_text == compare_to else 0

    """
    helper function to remove all non-alphabet characters in given string, and convert it to lower case
    """
    def convert_str(self, input):
        return re.sub("\W", "", input).lower()


    """
    crawl utility function for loop
    """
    def crawl_utl(self, row=0):
        print("Start searching " + self.first_name + " " + self.last_name + " ...\n")
        self.start_search()

        print("Waiting page to render...\n")
        potential_divs = self.wait_result()
        print(str(len(potential_divs)) + " potential candidate entering coarse-grain filter")
        if len(potential_divs) == 0:
            return

        """
        coarse grain filter
        """
        potential_link_set = set()
        self.coarse_filter(potential_divs, potential_link_set)

        """
        fine grain filter
        """
        self.fine_filter(potential_link_set, row)


    """
    main routine for UI invocation
    """
    def crawl_linkedin(self):

        page = "https://www.linkedin.com"
        print("crawling: " + page)
        self.setup_driver(page)

        print("Log-in landing page...\n")
        email = "371000549@qq.com"
        password = "1313123"
        self.simulate_login(email, password)

        # TODO batch search, output modified write book
        if(self.file_path != ""):
            #  construct read book and write book
            print("copying write book...\n")
            self.read_book = open_workbook(self.file_path)
            self.read_sheet = self.read_book.sheet_by_index(0)
            self.write_book = copy(self.read_book)
            self.write_sheet = self.write_book.get_sheet(0)
            for row in range(self.start_row-1, self.end_row, 1):
                self.first_name = self.read_sheet.cell(row, self.first_name_index).value.lower()
                self.last_name = self.read_sheet.cell(row, self.last_name_index).value.lower()
                self.crawl_utl(row)
        else:
            self.crawl_utl()

        # finally, close the web browser
        self.driver.close()
        print("Crawling complete")
