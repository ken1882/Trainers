from _G import wait
from datetime import datetime

class BaseJob:
    def __init__(self, job_name:str, url:str, new_page:bool=True, **kwargs):
        self.job_name = job_name
        self.url = url
        self.next_run = datetime(1970, 1, 1)
        self.new_page = new_page
        self.page = None
        self.context = None
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
        self.signal = {}

    def restart(self):
        self.next_run = datetime.now()

    def set_context(self, context):
        self.context = context

    def start(self):
        if self.new_page:
            self.page = self.context.new_page()
        self.page.goto(self.url)
        self.page.on("load", self.on_page_load)
        while not self.signal.get('load', False):
            wait(0.1)
        self.execute()
        self.stop()

    def on_page_load(self):
        self.signal['load'] = True

    def execute(self):
        pass

    def stop(self):
        if self.new_page and self.page:
            self.page.close()

    def wait_until_elements_found(self, selectors:list, timeout:int=10):
        '''
        Wait until all selectors are found.
        '''
        while timeout > 0:
            for selector in selectors:
                if not self.page.query_selector(selector):
                    break
            else:
                break
            timeout -= 1
            wait(1)
        return timeout > 0

    def wait_until_element_found(self, selectors:list, timeout:int=10):
        '''
        Wait until one of the selectors is found.
        '''
        while timeout > 0:
            for selector in selectors:
                node = self.page.query_selector(selector)
                if node:
                    return node
            timeout -= 1
            wait(1)
        return None

    def click_element(self, selector:str, nth_element:int=0):
        node = self.page.query_selector(selector)
        if node:
            node.click()
            return True
        return False
