import _G
import utils
import page_action as action
from datetime import datetime, timedelta
from errors import NeoError
from models.mixins.base_page import BasePage
from jobs.priority_table import PriorityTable
class BaseJob(BasePage):
    def __init__(self, job_name:str, url:str, new_page:bool=True,
                 priority:int=None, page=None, context=None, next_run=None,
                 enabled=True, close_delay=5000, profile_name='',
                 **kwargs):
        super().__init__(page, url, context)
        self.job_name = job_name
        self.url = url
        self.next_run = next_run if next_run else datetime.now()
        self.new_page = new_page
        self.page     = None
        self.context  = None
        self.priority = priority
        self.enabled  = enabled
        self.close_delay  = close_delay
        self.profile_name = profile_name
        self.return_value = NeoError(0)
        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value
        self.load_args()
        self.set_context(context)
        self.set_page(page)

    def load_args(self):
        pass

    @property
    def priority(self):
        if self._priority is None:
            return PriorityTable.get(self.job_name, 0)
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value

    def run_now(self):
        self.next_run = datetime.now()

    def start(self):
        # this function will run concurrently in generator
        if self.new_page:
            self.set_page(self.context.new_page())
        yield from self.goto()
        if self.check_maintenance():
            _G.log_info(f"Job {self.job_name} detected maintenance, run after a hour")
            self.next_run = datetime.now() + timedelta(hours=1)
            return self.next_run
        _G.log_info("Executing job")
        yield from self.execute()
        yield from self.stop()

    def execute(self):
        yield

    def check_maintenance(self):
        if self.has_content('maintenance') and self.has_content('this site'):
            return True
        return False

    def stop(self):
        _G.log_info(f"Stopping job {self.job_name}, delay={self.close_delay}ms")
        yield from _G.rwait(self.close_delay / 1000.0)
        if self.new_page and self.page:
            self.page.close()

    def calc_next_run(self, shortcut:str='daily'):
        curt = utils.localt2nst(datetime.now())
        if shortcut == 'now':
            self.next_run = curt
        elif shortcut == 'daily':
            tomorrow = datetime(curt.year, curt.month, curt.day, 0, 0, 0) + timedelta(days=1)
            self.next_run = utils.nst2localt(tomorrow)
        elif shortcut == 'monthly':
            nm = curt.month + 1 if curt.month < 12 else 1
            next_month = curt.replace(month=nm, day=1, hour=0, minute=0, second=0)
            next_month = next_month + timedelta(hours=2)
            self.next_run = utils.nst2localt(next_month)
        return self.next_run

    def to_dict(self):
        return {
            'class': self.__class__.__name__,
            'job_name': self.job_name,
            'url': self.url,
            'next_run': self.next_run.timestamp(),
            'new_page': self.new_page,
            'priority': self._priority,
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
        self.enabled = data['enabled']
        self.args = data['args']
        self.load_args()
        return self
