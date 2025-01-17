import _G, utils
import page_action as action

class BasePage():
    def __init__(self, page=None, url='about:blank', context=None):
        self.signal = {}
        self.context = context
        self.page = page
        self.url  = url

    def set_context(self, context):
        self.context = context

    def set_page(self, page):
        self.page = page

    def goto(self, url=None):
        if not url:
            url = self.url
        _G.log_info(f"Goto {url}, Waiting for page to load")
        self.page.goto(url, wait_until='commit')
        yield from self.wait_until_page_load()

    def wait_until_page_load(self):
        yield from _G.rwait(1)
        self.signal['load'] = False
        self.page.once("load", self.on_page_load)
        while not self.signal.get('load', False):
            self.page.evaluate('document.readyState')
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
            action.click_node(self.page, node, **kwargs)
            return node
        return None

    def scroll_to(self, x:int=0, y:int=0, node=None):
        if node:
            bb = node.bounding_box()
            nx = 0
            ny = y + bb['y'] - 100
            return action.scroll_to(self.page, nx, ny)
        return action.scroll_to(self.page, x, y)
