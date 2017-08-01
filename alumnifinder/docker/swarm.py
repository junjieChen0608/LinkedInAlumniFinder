import docker


class SwarmManager:
    """Controls the swarm of docker nodes"""

    def __init__(self, excel_file):
        self.excel = excel_file
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')  # linux

    def calc_number_of_workers(self) -> int:
        pass

    def create_workers(self, num):
        pass

    def split_up_tasks(self) -> list:
        pass

    def assign_tasks(self):
        pass
