from copy import deepcopy
import Input

class Act:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        self.kwargs = kwargs
        for k,v in kwargs.items():
            setattr(self, k, v)

    def perform(self):
        if self.kind == 'CLICK':
            self.do_click()

    def do_click(self):
        kwargs = deepcopy(self.kwargs)
        x, y = kwargs.pop('x') or 0, kwargs.pop('y') or 0
        if kwargs.pop('rclick'):
            Input.rclick(x, y, **kwargs)
        else:    
            Input.click(x, y, **kwargs)
