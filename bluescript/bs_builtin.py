import bs_variables
import bs_types
import UPL

## changs most calls to self.MEMORY.env to self.MEMORY.blue_memory_get() - ryan 03:19

class BS_BUILTIN:
    def __init__(self, MEMORY):
        self.MEMORY = MEMORY  ## memory ref
        self.VARM   = bs_variables.BS_VARS(self.MEMORY)

    def blue_varUpdate(self, args):
        #check = any(map(args.__contains__, bs_types.LOGIC_ARRAY))
        mode = 0
        if '=' in args:
            var, data = args.split('=',1)
            
            ## cleanup data
            var = var.rstrip()
            data = data.lstrip()

            check = any(map(args.__contains__, bs_types.MATH_ARRAY))  

            if not check:
                varname = var
                var = self.MEMORY.var_get(varname)

                if var == False:
                    raise Exception(f"'{varname}' does not exist")

                temp = self.MEMORY.var_get(data)

                if temp == False:
                    data = self.MEMORY.type_guess(data)
                else:
                    data = temp[1]


                self.MEMORY.var_add(varname, var[0], data)
                return

            if var in self.MEMORY.blue_memory_get('vars').keys(): ## exists
                varname = var
                var = self.MEMORY.var_get(varname)

                ## math stuff
                math_oper = next(substring for substring in bs_types.MATH_ARRAY if substring in data)
                item_1, item_2 = data.split(math_oper, 1)

                ## remove leading/trailing useless spaces
                item_1 = item_1.rstrip()
                item_2 = item_2.lstrip()

                temp1 = self.MEMORY.var_get(item_1)
                temp2 = self.MEMORY.var_get(item_2)

                if temp1 == False:
                    item_1 = self.MEMORY.type_guess(item_1)

                else:
                    item_1 = temp1[1]

                if temp2 == False:
                    item_2 = self.MEMORY.type_guess(item_2)
                
                else:
                    item_2 = temp2[1]

                if type(item_1) == str: item_1 = f'\"{item_1}\"'; mode = 1
                if type(item_2) == str: item_2 = f'\"{item_2}\"'; mode = 1

                eval_string = f"{item_1} {math_oper} {item_2}"

                if mode == 1:
                    self.MEMORY.var_add(varname, var[0], f"\"{eval(eval_string)}\"")
                    return

                self.MEMORY.var_add(varname, var[0], eval(eval_string))
                return

            raise Exception(f"Variable '{var}' does not exist")

        raise Exception("No value being set.")

    def blue_input(self, args):
        tmp = "" ## for output stuff
        prompt, output = args.split(bs_types.TO_CHAR, 1)

        prompt = prompt.rstrip()
        output = output.lstrip()

        temp = self.MEMORY.var_get(prompt)

        if temp == False:
            tmp = input(prompt)

        else:
            tmp = input(prompt[1])

        

        output_string = f"{output} = {tmp}"
        self.blue_varUpdate(output_string)
        

    def call_func(self, args):
        func_name, args = args.split("(", 1)
        args = args.replace(')', '') ## remove tailing

        args = args.replace(' ', '')
        args = UPL.Core.removeEmpty(args.split(','))

        if func_name in list(self.MEMORY.env["functions"].keys()):
            func_data = self.MEMORY.env['functions'][func_name]
            
            if len(args) != len(func_data['args']):
                raise Exception(f"'{func_name}' expected {len(func_data['args'])} but got {len(args)}")
            
            code = func_data['code']

            return ('func_code', code)

        raise Exception(f"{func_name} has not been defined")
            
    def blue_logicalIf(self, args):
        ## check if args contains a logic operator
        check = any(map(args.__contains__, bs_types.LOGIC_ARRAY))    

        if check == True:  
            ## get the logic operator 
            logic_operator = next(substring for substring in bs_types.LOGIC_ARRAY if substring in args)
            ## get items to check
            item_1, item_2 = args.split(logic_operator, 1)

            ## remove leading/trailing useless spaces
            item_1 = item_1.rstrip()
            item_2 = item_2.lstrip()

            temp1 = self.MEMORY.var_get(item_1)
            temp2 = self.MEMORY.var_get(item_2)

            if temp1 == False:
                item_1 = self.MEMORY.type_guess(item_1)

            else:
                item_1 = temp1[1]

            if temp2 == False:
                item_2 = self.MEMORY.type_guess(item_2)
            
            else:
                item_2 = temp2[1]

            eval_string = f"{item_1} {logic_operator} {item_2}"

            return ("LOGIC_OUT",eval(eval_string))

    def blue_goif(self, args):
        args, goto_loc = args.split(bs_types.TO_CHAR, 1)

        goto_data = self.MEMORY.lable_get(goto_loc.lstrip())

        if goto_data == "NULL":
            raise Exception(f"'{goto_loc}' does not exist")

        out = self.blue_logicalIf(args.rstrip()) ## send with removing trailing spaces

        if out[1] == False:
            return ("goto_out", False)
            

        return ("lable_location", goto_data)

    def blue_lable(self, args):
        self.MEMORY.lable_add(args, self.MEMORY.CurrentLine)

    def blue_goto(self, args):
        lable_data = self.MEMORY.lable_get(args)
        
        if lable_data == "NULL":
            raise Exception(f"Lable '{args}' does not exist")

        return ('lable_location',lable_data)

    def blue_vardec(self, args):
        dtype, args = args.split(' ', 1) ## get type and args

        if '=' in args:
            name, data = args.split('=', 1)
            name = name.rstrip() ## remove tailing spaces
            data = data.lstrip() ## remove leading spaces
            out = self.MEMORY.var_get(data)

            ## not var
            if out != False:
                self.MEMORY.var_add(name, dtype, out)
            
            ## var
            else:
                self.MEMORY.var_add(name, dtype, data)


        else:
            self.MEMORY.var_add(args, dtype, bs_types.null)

    def blue_print(self, args):
        if "\"" in args:
            ## print string
            print(args.replace("\"", ""))
            return
        
        out = self.MEMORY.var_get(args)

        if out == False:
            raise Exception(f"Variable '{args}' does not exist")
        
        print(out[1])


def include_file(filename):
    if not filename.endswith(".bs"):
        filename += ".bs"

    if UPL.Core.file_exists(filename):
        return UPL.Core.file_manager.read_file(filename)

    else:
        raise Exception(f"Cannot find file '{filename}'")