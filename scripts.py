import runpy

def run():
    m = runpy.run_path('./ddpy')
    m['app']()
