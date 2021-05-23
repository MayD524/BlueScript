import os

## Constants
BS_TOCHAR = '->'

class osTools:
    def __init__(self, MEMORY, builtin):
        self.MEMORY = MEMORY
        self.builtin = builtin
        
        self.MEMORY.var_add("osTools_version", "str", "0.0.1", False, True)
    
    ## cwd <dir>
    def change_dir(self, directory):
        tmp = self.MEMORY.var_get(directory.strip())
        if tmp == False:
            directory = self.MEMORY.type_guess(directory)
        
        else:
            directory = tmp[1]

        os.chdir(directory)

    ## pwd <dir>
    def getCurrentDir(self, output):
        tmp = self.MEMORY.var_get(output.strip())
        
        if tmp == False:
            raise Exception(f"Unknown variable '{output}'")

        tmp[1] = os.getcwd()
        
        self.MEMORY.var_add(output, "str", tmp[1], tmp[2], tmp[4])

    ## list_dir <dir> -> <array>
    def list_dir(self, directory):
        directory, output = directory.split(BS_TOCHAR, 1)
        directory = directory.strip()
        output = output.strip()
        
        outVar = self.MEMORY.var_get(output)
        
        dir_data = []
        
        if outVar == False or outVar[0] != 'array':
            raise Exception(f"Variable '{output}' either does not exist or is not an array.")
         
        if directory == '"current"':
            dir_data = os.listdir()
            
        else:
            dirVar = self.MEMORY.var_get(directory)
            
            if dirVar == False:
                dirVar = self.MEMORY.type_guess(directory)
            else:
                dirVar = dirVar[1]
            
            ## remove " from strings.
            dirVar = dirVar.replace('"','') if '"' in dirVar else dirVar
            
            dir_data = os.listdir(dirVar)
        
        
        outVar[1] = outVar[1] + dir_data
        
        self.MEMORY.var_add(output, "array", outVar[1], outVar[2], outVar[4])  

def pluginMain(MEMORY, builtin):
    
    ostools = osTools(MEMORY, builtin)
    
    ops = {
        "cwd" : ostools.change_dir,
        "pwd" : ostools.getCurrentDir,
        "list_dir" : ostools.list_dir
    }
    
    return ops