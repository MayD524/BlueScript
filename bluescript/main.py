"""
    version : 0.4.2
    author  : Ryan Draskovics
    started : 5/6/2021
    This file is the main file
"""
import bs_errorHandler## Handles all of the errors (for error handler rewrite (replace raise))
import bs_osControler ## commands related to the os (cwd, cd, etc)
import bs_filehandler ## file reading
import bs_builtin     ## builting funcs
import bs_memory      ## global memory
import bs_types       ## generic stuff (keywords, etc)
import pprint         ## for pretty printing
import UPL            ## why do I always use this?
import sys

"""
    <Note for later>
    How can I do nested if?
    How can I do logic chains?

    <Notes>
    fixed string comparing

    FIX LOCALIZATION

    <STUFF I HAVE FINISHED/TODO>
    vars    - done -> 5/6/2021 - 23:27
    funcs   - done -> 5/6/2021 - 23:27
    print   - done -> 5/6/2021 - 23:27
    include - done -> 5/7/2021 - 00:14
    lables  - done -> 5/7/2021 - 16:14
    goto    - done -> 5/7/2021 - 16:14
    goif    - done -> 5/8/2021 - 02:38
    logic   - done -> 5/8/2021 - 03:05
    set     - done -> 5/8/2021 - 13:54 
    math    - done -> 5/8/2021 - 13:54 
    IO      - done -> 5/9/2021 - 14:02
    func_ret- done -> 5/10/2021- 12:32
    arrays  - done -> 5/11/2021- 11:08
    rework  - done -> 5/11/2021- 11:08
    lables
    funcargs- done -> 5/12/2021- 14:02
    files   - done -> 5/13/2021- 21:58
    size    - done -> 5/13/2021- 22:27
    sleep   - done -> 5/16/2021- 14:19
    free    - done -> 5/17/2021- 10:19
    nested  - done -> 5/17/2021- 23:31
    globals - done -> 5/18/2021- 10:53
    typeof  - done -> 5/18/2021- 13:45
    structs - done -> 5/19/2021- 14:06
    sockets - working on
    ostools - working on
    docs    - needa start - 1
    stdlib  - needa start - 2
    web?    - needa start - 5
    dicts   - needa start - 2
    errors  - needa start - 4
    bugfix  - working on - (this is a joke :>)
    better  - working on
    errirs
    rework  - working on
    types
    
    figure out some way to stop includes from going forever
""" 

## Main class (everything happens here)
class BS_MAIN:
    def __init__(self, file_data, file_name):
        ## Generic bluescript stuff
        self.MEMORY       = bs_memory.BS_MEMORY(file_name)
        self.ErrorHandler = bs_errorHandler.BLUE_ERROR_HANDLER(self.MEMORY)
        self.builtin      = bs_builtin.BS_BUILTIN(self.MEMORY, self.ErrorHandler) 
        ## file data stuff
        self.file_data  = file_data     ## data in file
        self.file_name  = file_name     ## base file

        ## file reading stuff
        self.expected   = ''            ## What we are waiting for
        self.file_index = 0             ## for runtime
        self.parsed     = []            ## for runtime
        
        ## logic stuff
        self.nested_index = 0
        self.read_nested  = []
        ## operations
        self.opCodes    = {
            "exit"   : "EOF",
            "let"    : self.builtin.blue_vardec,
            "set"    : self.builtin.blue_varUpdate,
            "print"  : self.builtin.blue_print,
            "call"   : self.builtin.call_func,
            "lable"  : self.builtin.blue_lable,
            "goto"   : self.builtin.blue_goto,
            "goif"   : self.builtin.blue_goif,
            "if"     : self.builtin.blue_logicalIf,
            "input"  : self.builtin.blue_input,
            "array"  : self.builtin.blue_array,
            "append" : self.builtin.blue_append,
            "mem"    : self.print_mem,
            "sizeof" : self.builtin.blue_sizeof,
            "open"   : bs_filehandler.blue_fileHandler,
            "free"   : self.builtin.blue_mem_free,
            "sleep"  : self.builtin.blue_sleep,
            "type"   : self.builtin.blue_typeof,
            "struct" : "",
            "endif"  : "here just for ease of life" ## remove later (in docs)
        }

    ## here for debugging
    def print_mem(self, *args):
        pprint.pprint(self.MEMORY.mem_get())

    def run_line(self, line, mode):
        if line == "endif":
            del self.read_nested[-1]
            return
        
        ## odd cases where we return early ie opcode only and logical stuff
        ## added '"if" not in line' so that nested logic wont crash
        if self.read_nested != [] and self.read_nested[-1] == False:
            if "if" in line:
                self.nested_index += 1
                self.read_nested.append(False)
            return

        if line == "exit":
            exit()

        ## normal operations
        oper, args = line.split(' ', 1)

        out = UPL.Core.switch(self.opCodes, oper)
        
        if out == False:
            raise Exception(f"unknown token on line '{line}'")
        
        if oper == "open":
            data_out = out(args, self.MEMORY)
        
        else:        
            data_out = out(args)

        if data_out == None:
            return ("NULL","NULL")
        
        match data_out[0]:
            case 'func_code':
                self.run_func(data_out[3], data_out[1], data_out[2])
                
            case 'LOGIC_OUT':
                if data_out[1] == True:
                    self.read_nested.append(True)
                else:
                    self.read_nested.append(False)
                    
                self.nested_index += 1
                
            case 'lable_location': 
                if mode == 0:
                    self.file_index = data_out[1]
                    self.MEMORY.CurrentLine = self.file_index
                    
                elif mode == 1:
                    return data_out
                
            case _:
                pass
                
        ## return empty tuple for ease of life
        return ("NULL","NULL")

    ## run functions
    def run_func(self, func_name, func_code, output):
        func_index = 0
        check = False
        
        if output != None:
            check = self.MEMORY.var_get(output)
            
        self.MEMORY.set_scope(func_name)
        ## read func code
        while(func_code[func_index] != "exit_func"):
            line = func_code[func_index]
            
            ## return Data
            if 'return' in line:
                ## check for is not empty and for index
                if self.read_nested != [] and self.read_nested[-1] == False:
                    func_index += 1
                    self.MEMORY.CurrentLine = func_index
                    continue
                
                if check != False:
                    outdata = line.split(" ", 1)[1]
                    outdata = outdata.lstrip()
                    tmp = self.MEMORY.var_get(outdata)

                    self.MEMORY.back_scope()
                    if tmp == False:
                        update_string = f"{output} = {outdata}"
                        self.builtin.blue_varUpdate(update_string)
                        return

                    ## set var with data
                    self.MEMORY.var_add(output, tmp[0], tmp[1], tmp[2])
                    return
                self.MEMORY.back_scope()
                return
            
            ## this should fix lables in funcs
            data_out = self.run_line(line, 1)
            
            if data_out != None and data_out[0] == 'lable_location':
                func_index = data_out[1]
                continue

            func_index += 1
            self.MEMORY.CurrentLine = func_index

    def runTime(self):
        self.file_index = 0
        self.parsed.append('EOF') ## why didn't this copy over?

        while (self.parsed[self.file_index] != "EOF"):
            line = self.parsed[self.file_index]

            if line == "exit":
                return

            self.run_line(line, 0)
            self.file_index += 1
            self.MEMORY.CurrentLine = self.file_index

    def preRead(self):
        ## structs
        struct_read = False
        struct_temp = []
        struct_name = ""
        
        ## functions
        func_read = False
        current_func = ""
        temp = {} ## for storing function code

        expected = None ## change if expecting new

        while (self.file_data[self.file_index] != "EOF"):
            line = self.file_data[self.file_index].split(bs_types.COMMENT_CHAR,1)[0].rstrip().lstrip() ## remove comments from line and remove newline

            if line == '':## get rid of empty strings
                self.file_index += 1
                continue

            ## do later
            if line.startswith('include'):
                filename = line.split(' ', 1)[1]
                if filename not in self.MEMORY.included_files:
                    code = bs_builtin.include_file(filename, self.file_name)
                    self.file_data.remove("EOF")
                    temp_data = self.file_data + code
                    self.file_data = temp_data
                    self.file_data.append("EOF")
                    self.MEMORY.included_files.append(filename)
                self.file_index += 1
                continue
                
            ## function stuff
            if expected == '{' and line == '{':
                expected = '}' ## expect to close
                self.file_index += 1
                continue ## we dont need to be here anymore
            
            ## not looking for func anymore
            if expected == '}' and line == '}':
                if func_read == True:
                    temp[current_func]['code'].append('exit_func')
                    self.MEMORY.add_func(current_func, temp[current_func]['return'], temp[current_func]['args'], temp[current_func]['code'])
                    func_read = False
                    current_func = None
                    expected = None
                    temp = {}
                    self.file_index += 1
                if struct_read == True:
                    self.MEMORY.add_struct(struct_name, struct_temp)
                    struct_temp = []
                    struct_read = False
                    expected = None
                    self.file_index += 1
                continue

            if func_read == True:
                temp[current_func]["code"].append(line)
                self.file_index += 1
                continue
            
            elif struct_read == True:
                struct_temp.append(line)
                self.file_index += 1
                continue


            if line.startswith('func'):
                args = line.split(' ', 1)[1]

                ## read func
                expected = '{'
                func_name, func_args = args.split('(', 1)
                func_args = func_args.replace(')', '').replace(' ', '')

                func_args, returnType = func_args.split(bs_types.TO_CHAR, 1)

                if func_args == '':
                    func_args = []

                if ',' in func_args:
                    func_args = func_args.split(',')

                if type(func_args) != list: func_args = [func_args]
                
                temp[func_name] = {"args":func_args,"return":returnType ,"code": []}

                current_func = func_name
                func_read = True
                
                self.MEMORY.scope_add(func_name)
                self.file_index += 1
                continue

            elif line.startswith('struct'):
                if func_read == True:
                    raise Exception("Cannot declair a struct in a function.")
                struct_read = True
                args = line.split(' ', 1)[1]
                expected = '{'
                struct_name = args.lstrip().rstrip()
                self.file_index += 1
                continue
                
            else:
                self.parsed.append(line)

            self.file_index += 1


## for calling outside if not __main__
def run_Script(filename):
    file_data = UPL.Core.file_manager.clean_read(filename) ## read file
    file_data.append("EOF") ## append EOF string
    main = BS_MAIN(file_data, filename)

    main.preRead()
    main.runTime()

## if we are just running bluescript
if __name__ == "__main__":
    BS_FILE = "test.bs"
    file_data = UPL.Core.file_manager.clean_read(BS_FILE) ## read file
    file_data.append("EOF") ## append EOF string
    main = BS_MAIN(file_data, BS_FILE)

    main.preRead()
    main.runTime()