from alumnifinder.excel import parser


class Client:
    """Used to handle client arguments before handing off data to other classes for processing.

    Args:
        degree (str): type of degree.
        degree_year (int): year degree earned.
        excel_file (str): path to excel file.
        first_name (str): first name.
        last_name (str): last name.
        major (str): major of degree.
        linkedin_area (str): LinkedIn area from alumni.
        school_dept (str): department of major.
        work_city (str): city where alumni works.
        work_company (str): company alumni works for.
        work_state (str): state alumni works in.
        work_title (str): alumni's work title.
        work_zipcode (int): zipcode where alumni works.
    """

    def __init__(self, degree=None, degree_year=None, excel_file=None, first_name=None, last_name=None,
                 major=None, linkedin_area=None, school_dept=None, work_city=None, work_company=None, work_state=None,
                 work_title=None, work_zipcode=None):
        """Initializes Client class with optional parameters."""
        super(Client, self).__init__()

        self.degree = degree
        self.degree_year = degree_year
        self.excel_file = excel_file
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.region = linkedin_area
        self.school_dept = school_dept
        self.work_city = work_city
        self.work_company = work_company
        self.work_state = work_state
        self.work_title = work_title
        self.work_zipcode = work_zipcode

        # TODO: finish error/type checking
        if linkedin_area:
            pass
        elif excel_file:
            excel = parser.get(excel_file)
        else:
            raise ValueError("All arguments are empty.")
