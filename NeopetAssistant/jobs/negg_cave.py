import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError

class NeggCaveJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("negg_cave", "https://www.neopets.com/shenkuu/neggcave/", **kwargs)

    def execute(self):
        yield from _G.rwait(2)
        html = self.page.evaluate("document.documentElement.outerHTML").replace('\\', '')
        yield from self.goto("https://thedailyneopets.com/articles/negg-solver/")
        script = f"document.getElementById('PageSourceBox').value = `{html}`"
        self.page.evaluate(script)
        yield from _G.rwait(1)
        for _ in range(3):
            self.page.query_selector('button[type=button]').click()
            yield from _G.rwait(1)
        answer = []
        for slot in self.page.query_selector_all('tr > td > img'):
            src = str(slot.get_property('src'))
            num = int(src.split('/')[-1].split('.')[0])
            answer.append(num)
        _G.logger.info(f"Answer: {answer}")
        yield from self.goto(self.url)
        yield from _G.rwait(2)
        self.scroll_to(0, 100)
        shape_base = '#mnc_parch_ui_symbol_{:d}'
        color_base = '#mnc_parch_ui_color_{:d}'
        negg_grid  = '#mnc_grid_cell_{:d}_{:d}'
        last_shape, last_color = -1,-1
        for idx, num in enumerate(answer):
            shape = num % 3
            if shape != last_shape:
                self.page.query_selector(shape_base.format(shape)).click()
                yield from _G.rwait(0.5)
            self.page.query_selector(negg_grid.format(idx // 3, idx % 3)).click()
            yield from _G.rwait(0.5)
            last_shape = shape
        self.page.query_selector(shape_base.format(last_shape)).click() # unselct
        yield from _G.rwait(1)
        for idx, num in enumerate(answer):
            color = num // 3
            if color != last_color:
                self.page.query_selector(color_base.format(color)).click()
                yield from _G.rwait(0.5)
            self.page.query_selector(negg_grid.format(idx // 3, idx % 3)).click()
            yield from _G.rwait(0.5)
            last_color = color
        yield from _G.rwait(1)
        self.click_element('#mnc_negg_submit_text')