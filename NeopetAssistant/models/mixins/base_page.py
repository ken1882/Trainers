import _G, utils
import page_action as action
from random import randint
from datetime import datetime, timedelta

class BasePage():
    def __init__(self, page=None, url='about:blank', context=None):
        self.signal = {}
        self.context = context
        self.page = page
        self.url  = url
        self.max_load_time = 10
        self.assume_loaded_time = datetime.now()

    def set_context(self, context):
        self.context = context

    def set_page(self, page):
        self.page = page

    def goto(self, url=None):
        if not url:
            url = self.url
        _G.log_info(f"Goto {url}, Waiting for page to load")
        self.page.goto(url, wait_until='commit')
        self.assume_loaded_time = datetime.now() + timedelta(seconds=self.max_load_time)
        yield from self.wait_until_page_load()

    def do(self, method, *args, **kwargs):
        '''
        Call a method in page_action, retry 3 times if failed
        '''
        for _ in range(3):
            try:
                return getattr(action, method)(*args, **kwargs)
            except Exception as e:
                _G.log_error(f"Error: {e}")
                _G.wait(0.5)
        return None

    def run_js(self, script_name):
        return self.do('eval_js', self.page, script_name)

    def wait_until_page_load(self):
        self.signal['load'] = False
        self.page.once("load", self.on_page_load)
        yield from _G.rwait(3)
        while not self.signal.get('load', False):
            try:
                self.page.evaluate('document.readyState')
            except Exception:
                pass
            if datetime.now() > self.assume_loaded_time:
                _G.log_warning("Page load timeout, assume main content loaded")
                break
            yield

    def on_page_load(self):
        _G.log_info("Page loaded")
        self.signal['load'] = True

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
            self.do('click_node', self.page, node, **kwargs)
            return node
        return None

    def scroll_to(self, x:int=0, y:int=0, node=None):
        if node:
            bb = node.bounding_box()
            x = 0
            y = y + bb['y'] - 100
        return self.do('scroll_to', self.page, x, y)

    def input_number(self, selector:str, number:int, nth_element:int=None):
        self.click_element(selector, nth_element)
        self.page.keyboard.press('Control+A')
        input_str = str(number)+'E'
        for i,digit in enumerate(input_str):
            if digit == 'E':
                break
            self.page.keyboard.press(digit)
            yield from _G.rwait(self.calc_numkey_interval(input_str[i], input_str[i+1]))

    def calc_numkey_interval(self, current, next):
        keys = '1234567890..........E'
        delta = abs(keys.index(current) - keys.index(next))
        ret = 0.2
        for _ in range(delta):
            ret += randint(10, 30) / 100.0
        return ret
