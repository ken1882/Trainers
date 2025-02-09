import _G, utils
import page_action as action
from random import randint
from datetime import datetime, timedelta
from playwright._impl._errors import TimeoutError

class BasePage():
    def __init__(self, page=None, url='about:blank', context=None):
        self.signal = {}
        self.context = context
        self.url  = url
        self.max_load_time = 10
        self.assume_loaded_time = datetime.now()
        self.set_page(page)

    def set_context(self, context):
        self.context = context

    def set_page(self, page):
        self.page = page
        if page == None:
            return
        self.page.on("framenavigated", self.on_navigation)
        self.page.on("load", self.on_page_load)

    def on_navigation(self, frame):
        # print(frame == self.page.main_frame, self.page.main_frame, frame)
        if frame != self.page.main_frame:
            return
        _G.log_info("Page navigated")
        self.signal.update({'loading': True, 'load': False})

    def goto(self, url=None, depth=0):
        if not url:
            url = self.url
        _G.log_info(f"Goto {url}, Waiting for page to load")
        while True:
            try:
                self.page.goto(url, wait_until='commit')
                break
            except TimeoutError as e:
                _G.log_error(f"Page timeout, retrying {depth}")
                depth += 1
                if depth > 3:
                    raise e
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

    def drag_to(self, locator_a, locator_b, steps=5, random_x=(-10, 10), random_y=(-10, 10)):
        self.do('drag_to', self.page, locator_a, locator_b, steps, random_x, random_y)

    def run_js(self, script_name):
        return self.do('eval_js', self.page, script_name)

    def wait_until_page_load(self):
        self.assume_loaded_time = datetime.now() + timedelta(seconds=self.max_load_time) // 2
        while not self.signal.get('loading', False):
            if datetime.now() > self.assume_loaded_time:
                _G.log_warning("Page load timeout, assume loading started")
                break
            yield
        self.assume_loaded_time = datetime.now() + timedelta(seconds=self.max_load_time)
        min_load_time = datetime.now() + timedelta(seconds=2)
        curt = datetime.now()
        while curt < min_load_time or not self.signal.get('load', False):
            curt = datetime.now()
            try:
                self.page.evaluate('document.readyState')
            except Exception:
                pass
            if curt> self.assume_loaded_time:
                _G.log_warning("Page load timeout, assume main content loaded")
                break
            yield

    def has_content(self, content:str, ignore_case=True):
        while True:
            try:
                if ignore_case:
                    return content.lower() in self.page.content().lower()
                return content in self.page.content()
            except Exception:
                return

    def on_page_load(self, _):
        _G.log_info("Page loaded")
        self.signal.update({'loading': False, 'load': True})

    def _wait_until_elements_found(self, selectors:list, timeout:int=10):
        '''
        Wait until all selectors are found.
        '''
        while timeout > 0:
            ret = []
            ele = None
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
            node = None
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

    def click_element(self, selector:str='', nth_element:int=None, node=None, **kwargs):
        if not node:
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
            if not bb: # element not visiable
                return
            x = 0
            y = y + bb['y'] - 100
        self.do('scroll_to', self.page, x, y)
        return (x, y)

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
