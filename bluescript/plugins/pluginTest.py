

## example plugin
"""
def pluginMain(MEMORY, builtin):
    return "hello world"
"""

class pluginTest:
    def __init__(self, MEMORY, builtin):
        self.MEMORY = MEMORY
        self.builtin = builtin

    def test(self, args):
        print(args)


def pluginMain(MEMORY, builtin):
    plugin = pluginTest(MEMORY, builtin)
    new_ops = {
        "test" : plugin.test
    }
    return new_ops