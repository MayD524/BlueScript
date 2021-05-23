import UPL

BS_TOCHAR = '->'

class BGUI:
    def __init__(self, MEMORY, builtin):
        self.MEMORY = MEMORY
        self.builtin = builtin    
    
    def gui_prompt(self, args):
        """
            Use:
            bprompt <title>, <prompt> -> <return>
        """
        
        ## split between title and prompt
        ## clean strings (just to make life easier later)
        gui_title, gui_data = args.split(',', 1)
        gui_title = gui_title.strip()
        
        title_var = self.MEMORY.var_get(gui_title.strip())
        
        prompt, output = gui_data.split(BS_TOCHAR, 1)
        
        ## doing this now to make life easier
        prompt = prompt.strip()
        output = output.strip()
        
        outvar = self.MEMORY.var_get(output)
        prompt_var = self.MEMORY.var_get(prompt)
        if outvar == False:
            raise Exception(f"Variable <{output}> does not exist.") 
        
        if title_var == False:
            title_var = self.MEMORY.type_guess(gui_title)
        else:
            ## set to data section of the variables memory
            title_var = title_var[1]
            
        if prompt_var == False:
            prompt_var = self.MEMORY.type_guess(prompt)
        else:
            prompt_var = prompt_var[1]
            
        tmp = UPL.gui.prompt(title=title_var, text=prompt_var)
        
        tmp = tmp if tmp != None else ""
        
        ## set the output to whatever we got from the prompt
        self.MEMORY.var_add(output, outvar[0], str(tmp), outvar[2], outvar[4])
    
def pluginMain(MEMORY, builtin):
    bgui_class = BGUI(MEMORY, builtin)
    
    ops = {
        "bprompt" : bgui_class.gui_prompt
    }
    
    return ops