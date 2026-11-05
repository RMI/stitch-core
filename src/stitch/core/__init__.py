from stitch.typings import hello as type_hello
from stitch.app import hello as app_hello
def hello() -> str:
    print(type_hello())
    print(app_hello())
    return "Hello from stitch-core!"
