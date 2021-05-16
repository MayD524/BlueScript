from typing import Match
import bs_types
import UPL

def blue_fileHandler(args, MEMORY):
    filename, file_args = args.split(',',1)
    filename = filename.rstrip()
    file_args= file_args.lstrip()  
    
    mode, outVar = file_args.split(bs_types.TO_CHAR, 1)
    mode = mode.rstrip()
    outVar = outVar.lstrip()
    
    ## get vars
    filename_var = MEMORY.var_get(filename) 
    mode_var = MEMORY.var_get(mode) 
    outVar_var = MEMORY.var_get(outVar)
    
    if outVar_var == False:
        raise Exception(f"Variable '{outVar}' does not exist in current scope")

    if mode_var == False and '\"' in mode:
        mode_var = mode.replace('"', '')
    
    else:
        mode_var = mode_var[1]

    if filename_var == False and '\"' in filename:
        filename_var = filename.replace('"','')

    elif filename_var != False:
        filename_var = filename_var[1]
        
    ## if we are here something went very very very wrong
    else:
        raise Exception(f"Variable '{filename}' does not exist or is wrong type. Either declair '{filename}' or add quotes")
        
    match mode_var:
        case "r":
            FileData = UPL.Core.file_manager.read_file(filename_var)
            if outVar_var[0] == "str":
                outVar_var[1] = "".join(FileData)
                
            elif outVar_var[0] == 'array':
                outVar_var[1] += FileData
                
            MEMORY.var_add(outVar_var[0], outVar_var[1], outVar_var[2])
                  
        case "w":
            data = "".join(outVar_var[1])
            with open(filename_var, "w+") as writer:
                writer.write(data)