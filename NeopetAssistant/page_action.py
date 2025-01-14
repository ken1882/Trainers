
def scrollTo(page, x=0, y=0):
    page.evaluate(f"window.scrollTo({x}, {y})")
