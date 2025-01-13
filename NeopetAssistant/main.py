from _G import logger
from playwright.sync_api import sync_playwright
import os


def create_context(pw, id):
    logger.info(f"Creating browser context#{id}")
    args = []
    logger.info(f"Launching browser context#{id} with args: {args}")
    return pw.chromium.launch_persistent_context(
        "./profile_{:04d}".format(id),
        headless=False,
        args=args
    )

def main():
    pw = sync_playwright().start()
    context = create_context(pw, 1)

if __name__ == '__main__':
    main()