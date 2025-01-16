import _G
import utils
import page_action as action
from datetime import datetime, timedelta
from errors import NeoError

class BaseJob:
    def __init__(self, job_name:str, url:str, new_page:bool=True,
                 priority:int=0, page=None, context=None, next_run=None,
                 enabled=True, close_delay=5000,
                 **kwargs):
        self.job_name = job_name
        self.url = url
        self.next_run = next_run if next_run else datetime.now()
        self.new_page = new_page
        self.page     = None
        self.context     = None
        self.priority    = priority
        self.enabled     = enabled
        self.close_delay = close_delay
        self.args = {}
        self.return_value = NeoError(0)
        for key, value in kwargs.items():
            self.args[key] = value
        self.signal = {}
        self.set_context(context)
        self.set_page(page)

    def run_now(self):
        self.next_run = datetime.now()

    def set_context(self, context):
        self.context = context

    def set_page(self, page):
        self.page = page

    def start(self):
        # this function will run concurrently in generator
        if self.new_page:
            self.set_page(self.context.new_page())
        yield from self.goto(self.url)
        _G.log_info("Executing job")
        yield from self.execute()
        yield from self.stop()

    def goto(self, url):
        _G.log_info("Waiting for page to load")
        self.page.goto(url, wait_until='commit')
        self.page.once("load", self.on_page_load)
        while not self.signal.get('load', False):
            self.page.evaluate('document.readyState')
            yield

    def on_page_load(self):
        _G.log_info("Page loaded")
        self.signal['load'] = True

    def execute(self):
        yield

    def stop(self):
        _G.log_info(f"Stopping job {self.job_name}, delay={self.close_delay}ms")
        yield from _G.rwait(self.close_delay / 1000.0)
        if self.new_page and self.page:
            self.page.close()

    def _wait_until_elements_found(self, selectors:list, timeout:int=10):
        '''
        Wait until all selectors are found.
        '''
        while timeout > 0:
            ret = []
            for selector in selectors:
                try:
                    ele = self.page.query_selector(selector)
                except Exception as e:
                    pass
                if not ele:
                    break
                ret.append(ele)
            else:
                return ret
            timeout -= 1
            yield from _G.rwait(1)
        return False

    def _wait_until_element_found(self, selectors:list, timeout:int=10):
        '''
        Wait until one of the selectors is found.
        '''
        while timeout > 0:
            for selector in selectors:
                try:
                    node = self.page.query_selector(selector)
                except Exception as e:
                    pass
                if node:
                    return node
            timeout -= 1
            yield from _G.rwait(1)
        return False

    def wait_until_elements_found(self, success_callback, fail_callback, selectors:list, timeout:int=10):
        while True:
            r = yield from self._wait_until_elements_found(selectors, timeout)
            if r == False:
                return fail_callback()
            elif r:
                return success_callback(r)

    def wait_until_element_found(self, success_callback, fail_callback, selectors:list, timeout:int=10):
        while True:
            r = yield from self._wait_until_element_found(selectors, timeout)
            if r == False:
                print("Element not found")
                return fail_callback()
            elif r:
                print("Element found")
                return success_callback(r)

    def click_element(self, selector:str, nth_element:int=None, **kwargs):
        node = None
        if nth_element != None:
            node = self.page.query_selector_all(selector)[nth_element]
        else:
            node = self.page.query_selector(selector)
        if node:
            action.click_node(self.page, node, **kwargs)
            return node
        return None

    def calc_next_run(self, shortcut:str='daily'):
        curt = utils.localt2nst(datetime.now())
        if shortcut == 'daily':
            tomorrow = datetime(curt.year, curt.month, curt.day, 0, 0, 0) + timedelta(days=1)
            self.next_run = utils.nst2localt(tomorrow)
        elif shortcut == 'monthly':
            next_month = curt.replace(day=1, hour=0, minute=0, second=0) + timedelta(days=31)
            next_month = next_month.replace(day=1)
            self.next_run = utils.nst2localt(next_month)
        return self.next_run

    def to_dict(self):
        return {
            'class': self.__class__.__name__,
            'job_name': self.job_name,
            'url': self.url,
            'next_run': self.next_run.timestamp(),
            'new_page': self.new_page,
            'priority': self.priority,
            'enabled': self.enabled,
            'close_delay': self.close_delay,
            'args': self.args
        }

    def load_data(self, data):
        data = {**self.to_dict(), **data}
        self.job_name = data['job_name']
        self.url = data['url']
        self.next_run = datetime.fromtimestamp(data['next_run'])
        self.new_page = data['new_page']
        self.priority = data['priority']
        self.close_delay = data['close_delay']
        self.enanbled = data['enabled']
        self.args = data['args']
        return self
