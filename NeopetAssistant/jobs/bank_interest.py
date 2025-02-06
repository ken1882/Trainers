import _G
import utils
import re
from jobs.base_job import BaseJob
from datetime import datetime, timedelta
from errors import NeoError
import page_action as action

class BankInterestJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__("bank_interest", "https://www.neopets.com/bank.phtml", **kwargs)
        self.max_np_carry = 100000
        self.min_np_carry = 20000

    def execute(self):
        yield from _G.rwait(2)
        yield from self.collect()

    def collect(self):
        _G.logger.info("Collecting bank interest")
        self.click_element('#frmCollectInterest')
        yield from _G.rwait(5)

    def deposite_surplus(self):
        yield
        carry = action.get_available_np(self.page)
        if carry < self.max_np_carry:
            return
        action.scroll_to(self.page, 0, 500)
        yield from _G.rwait(1)
        amount = carry - self.min_np_carry
        balance = utils.str2int(self.page.query_selector('#txtCurrentBalance').text_content())
        _G.logger.info(f"Depositing {amount} NP")
        account_type = self.page.query_selector('#txtAccountType').text_content()
        next_grade_required_np = 0x7fffffff
        next_grade_delta = 0
        grade_level = 0
        for row in self.page.query_selector('#account_type').text_content().split('\n'):
            if '(min' not in row or 'NP)' not in row:
                continue
            r = re.search(r"\(min\s([0-9,]+)\sNP\)", row)
            if not r:
                continue
            type_name = row.split(' (min')[0]
            value = utils.str2int(r.group(1))
            if next_grade_required_np == 0:
                next_grade_required_np = value
                next_grade_delta = value - balance
                _G.log_info(f"Next grade required NP: {next_grade_required_np} (need {next_grade_delta} more)")
            if type_name == account_type:
                next_grade_required_np = 0
            grade_level += 1
        self.page.on("dialog", lambda dialog: dialog.accept())
        if balance + amount >= next_grade_required_np:
            self.page.quert_selector('#account_type').select_option(str(grade_level))
            yield from self.input_number('input[name=amount]', amount, 2)
        else:
            yield from self.input_number('input[name=amount]', amount)

