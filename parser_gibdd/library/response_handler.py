import abc

from requests import Response


class ResponseHandler(abc.ABC):
    """This is a parent class that handles the response data"""

    def __init__(self, response: Response):
        self.raw_response = response

    @abc.abstractmethod
    def parse(self):
        return self.raw_response.json()
