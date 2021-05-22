import os

class osTools:
    def __init__(self, MEMORY, builtin):
        self.MEMORY = MEMORY
        self.builtin = builtin
        
        self.MEMORY.var_add("osTools_version", "str", "0.0.1", False, True)
    
    ## cwd <dir>
    def change_dir(self, directory):
        tmp = self.MEMORY.var_get(directory)
        if tmp == False:
            directory = self.MEMORY.type_guess(directory)
        
        else:
            directory = tmp[1]

        os.chdir(directory)

    ## pwd <dir>
    def getCurrentDir(self, output):
        tmp = self.MEMORY.var_get(output)
        
        if tmp == False:
            raise Exception(f"Unknown variable '{output}'")

        tmp[1] = os.getcwd()
        
        self.MEMORY.var_add(output, "str", tmp[1], tmp[2], tmp[4])

    ## list_dir <dir>
    def list_dir(self, directory):
        print(directory)

def pluginMain(MEMORY, builtin):
    
    ostools = osTools(MEMORY, builtin)
    
    ops = {
        "cwd" : ostools.change_dir,
        "pwd" : ostools.getCurrentDir,
        "list_dir" : ostools.list_dir
    }
    
    return ops