import _G
import utils
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError


class TombolaJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("tombola", "https://www.neopets.com/island/tombola.phtml", **kwargs)
        self.args['played_today'] = False

    def execute(self):
        try:
            node = self.page.query_selector_all('input[type=submit]')[1]
            node.click()
            yield from _G.rwait(5)
            self.args['played_today'] = True
        except Exception as e:
            _G.log_warning(f"Error clicking on tombola: {e}")
            _G.log_warning("Probably not available yet, requeued for 1 hour")

    def calc_next_run(self):
        if self.args.get('played_today', False):
            return super().calc_next_run()
        else:
            self.next_run = datetime.now() + timedelta(hours=1)
            return self.next_run
