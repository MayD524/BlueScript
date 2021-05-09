import bs_builtin   ## builting funcs
import bs_memory    ## global memory
import bs_types     ## generic stuff (keywords, etc)
import UPL          ## why do I always use this?

"""
    <Note for later>
    How can I do nested if?
    How can I do logic chains?

    <STUFF I HAVE FINISHED/TODO>
    vars    - done -> 5/6/2021 - 23:27
    funcs   - done -> 5/6/2021 - 23:27
    print   - done -> 5/6/2021 - 23:27
    include - done -> 5/7/2021 - 00:14
    lables  - done -> 5/7/2021 - 16:14
    goto    - done -> 5/7/2021 - 16:14
    goif    - done -> 5/8/2021 - 02:38
    logic   - done -> 5/8/2021 - 03:05 -> review later / add nested
    set     - done -> 5/8/2021 - 13:54 
    nested  - needa start
    math    - done -> 5/8/2021 - 13:54 
    docs    - needa start
    stdlib  - needa start
    files   - needa start
    IO      - working on
    web?    - needa start
    array   - needa start
    dicts   - needa start
    errors  - needa start
"""

## Main class (everything happens here)
class BS_MAIN:
    def __init__(self, file_data, file_name):
        ## Generic bluescript stuff
        self.MEMORY     = bs_memory.BS_MEMORY(file_name)
        self.builtin    = bs_builtin.BS_BUILTIN(self.MEMORY)
        
        ## file data stuff
        self.file_data  = file_data     ## data in file
        self.file_name  = file_name     ## base file

        ## file reading stuff
        self.expected   = ''            ## What we are waiting for
        self.file_index = 0             ## for runtime
        self.parsed     = []            ## for runtime
        
        ## logic stuff
        self.in_logic   = False         ## are we in a logic block?
        self.read_logic = False         ## are we reading logic blocks?

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
            "endif"  : "here just for ease of life" ## remove later (in docs)
        }

    def blue_end_logic(self):
        if self.in_logic == True:
            self.in_logic = False

        if self.read_logic == True:
            self.read_logic = True

    def run_line(self, line):

        ## odd cases where we return early ie opcode only and logical stuff
        if self.in_logic == True and self.read_logic == False:
            return

        if line == "endif":
            self.blue_end_logic()
            return

        ## normal operations
        oper, args = line.split(' ', 1)

        out = UPL.Core.switch(self.opCodes, oper)
            
        if out == False:
            raise Exception(f"unknown token on line '{line}'")
                
        data_out = out(args)

        if data_out == None:
            return

        if data_out[0] == 'func_code':
            self.run_func(data_out[1])

        elif data_out[0] == 'lable_location':
            self.file_index = data_out[1]
            self.MEMORY.CurrentLine = self.file_index

        elif data_out[0] == "LOGIC_OUT":
            if data_out[1] == True:
                self.read_logic = True

            self.in_logic = True

    def run_func(self, func_code):
        func_index = 0
        while(func_code[func_index] != "exit_func"):
            line = func_code[func_index]
            
            if 'return' in line:
                return

            self.run_line(line)
            func_index += 1

    def runTime(self):
        self.file_index = 0
        self.parsed.append('EOF') ## why didn't this copy over?

        while (self.parsed[self.file_index] != "EOF"):
            line = self.parsed[self.file_index]
            self.run_line(line)
            self.file_index += 1
            self.MEMORY.CurrentLine = self.file_index

    def preRead(self):

        func_read = False
        current_func = ""
        expected = None ## change if expecting new
        temp = {} ## for storing function code

        while (self.file_data[self.file_index] != "EOF"):
            line = self.file_data[self.file_index].split(bs_types.COMMENT_CHAR,1)[0].strip() ## remove comments from line and remove newline            

            if line == '':## get rid of empty strings
                self.file_index += 1
                continue 
            
            ## do later
            if line.startswith('include'):
                filename = line.split(' ', 1)[1]
                code = bs_builtin.include_file(filename)
                self.file_data.remove("EOF")
                temp_data = self.file_data + code
                self.file_data = temp_data
                self.file_data.append("EOF")
                self.file_index += 1
                continue
                
            ## function stuff
            if expected == '{' and line == '{':
                expected = '}' ## expect to close
                self.file_index += 1
                continue ## we dont need to be here anymore
            
            ## not looking for func anymore
            if expected == '}' and line == '}':

                temp[current_func]['code'].append('exit_func')
                self.MEMORY.add_func(current_func, temp[current_func]['return'], temp[current_func]['args'], temp[current_func]['code'])
                func_read = False
                current_func = None
                expected = None
                temp = {}
                self.file_index += 1
                continue

            if func_read == True:
                temp[current_func]["code"].append(line)
                self.file_index += 1
                continue


            if line.startswith('func'):
                args = line.split(' ', 1)[1]

                ## read func
                expected = '{'
                func_name, func_args = args.split('(', 1)
                func_args = func_args.replace(')', '').replace(' ', '')

                if func_args == '':
                    func_args = []

                if ',' in func_args:
                    func_args = func_args.split(',')

                temp[func_name] = {"args":func_args,"return":None ,"code": []}

                current_func = func_name
                func_read = True

            else:
                self.parsed.append(line)

            self.file_index += 1

if __name__ == "__main__":
    BS_FILE = "test.bs"
    file_data = UPL.Core.file_manager.read_file(BS_FILE) ## read file
    file_data.append("EOF") ## append EOF string
    main = BS_MAIN(file_data, BS_FILE)

    main.preRead()
    main.runTime()