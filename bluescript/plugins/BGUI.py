import UPL

class BGUI:
    def __init__(self, MEMORY, builtin):
        self.MEMORY = MEMORY
        self.builtin = builtin
        
    def gui_prompt(self, prompt):
        print(UPL.gui.prompt(prompt))
    
    
def pluginMain(MEMORY, builtin):
    bgui_class = BGUI(MEMORY, builtin)
    
    ops = {
        "bprompt" : bgui_class.gui_prompt
    }
    
    return ops