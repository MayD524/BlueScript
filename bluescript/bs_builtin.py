import bs_types
import UPL

## change most calls to self.MEMORY.env to self.MEMORY.blue_memory_get() - ryan 03:19
class BS_BUILTIN:
    def __init__(self, MEMORY):
        self.MEMORY = MEMORY  ## memory ref

    def blue_varUpdate(self, args):
        ## mode = 0 numbers
        ## mode = 1 string
        
        mutable = True ## can something be mutable?
        mode = 0
        
        if '=' in args:
            var, data = args.split('=',1)
            
            ## cleanup data
            var = var.rstrip()
            data = data.lstrip()

            ## check if we are adding anything
            check = any(map(args.__contains__, bs_types.MATH_ARRAY))  
            varname = var
            var = self.MEMORY.var_get(varname)
                
            if var == False:
                raise Exception(f"'{varname}' does not exist.")

            if var[2] == False:
                raise Exception(f"Cannot change unmutable value.")

            if not check:
                temp = self.MEMORY.var_get(data)

                if temp == False:
                    data = self.MEMORY.type_guess(data)
                else:
                    data = temp[1]

                self.MEMORY.var_add(varname, var[0], data, mutable)
                return

            ## clean up later
            
            if self.MEMORY.var_get(varname) != False: ## exists

                ## math stuff
                math_oper = next(substring for substring in bs_types.MATH_ARRAY if substring in data)
                item_1, item_2 = data.split(math_oper, 1)
                math_oper = "**" if math_oper == "^" else math_oper
                
                ## remove leading/trailing useless spaces
                item_1 = item_1.rstrip()
                item_2 = item_2.lstrip()

                ## get variable data
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

                ## if string make string
                if type(item_1) == str and '\"' not in item_1: item_1 = f'\"{item_1}\"'; mode = 1
                if type(item_2) == str and '\"' not in item_2: item_2 = f'\"{item_2}\"'; mode = 1

                eval_string = f"{item_1} {math_oper} {item_2}"

                ## string stuff
                if mode == 1:
                    self.MEMORY.var_add(varname, var[0], f"\"{eval(eval_string)}\"", mutable)
                    return
               
                self.MEMORY.var_add(varname, var[0], eval(eval_string), mutable)
                return
            
            raise Exception(f"Variable '{varname}' does not exist")

        raise Exception("No value being set.")

    def blue_input(self, args):
        tmp = "" ## for output stuff
        prompt, output = args.split(bs_types.TO_CHAR, 1)
        ## clean up prompt
        prompt = prompt.rstrip()
        if '"' in prompt: prompt = prompt.replace('"','')

        ## clean up output
        output = output.lstrip()

        temp = self.MEMORY.var_get(prompt)
        out = self.MEMORY.var_get(output)

        if out == False:
            pass

        if temp == False:
            tmp = input(prompt)

        else:
            tmp = input(temp[1])

        if out[0] == 'str':
            tmp = f"\"{tmp}\""

        output_string = f'{output} = {tmp}'

        self.blue_varUpdate(output_string)
        

    def call_func(self, args):
        output = None
        func_name, args = args.split("(", 1)
        args = args.replace(')', '') ## remove tailing
        args = args.replace(' ', '')
        
        if bs_types.TO_CHAR in args:
            args, output = args.split(bs_types.TO_CHAR, 1)
            
            if self.MEMORY.var_get(output) == False:
                raise Exception(f"Unknown var '{output}'")
            
            if ',' in args:
                func_args = args.split(',')
                needed_args = self.MEMORY.env["functions"][func_name]["args"]
                for x in range(len(needed_args)):
                    arg_get = self.MEMORY.var_get(func_args[x])
                        
                    if arg_get == False:
                        data = self.MEMORY.type_guess(func_args[x])
                        dtype = ""
                        if type(data) == str    : dtype = "str"
                        elif type(data) == int  : dtype = "int"
                        elif type(data) == float: dtype = "float"
                        elif type(data) == bool : dtype = "bool"
                        self.MEMORY.set_scope(func_name)
                        self.MEMORY.var_add(needed_args[x], dtype, data, True)

                    else:
                        self.MEMORY.set_scope(func_name)
                        self.MEMORY.var_add(needed_args[x], arg_get[0], arg_get[1], arg_get[2])

                    self.MEMORY.back_scope()
                    
        args = UPL.Core.removeEmpty(args.split(','))
        if func_name in list(self.MEMORY.env["functions"].keys()):
            func_data = self.MEMORY.env['functions'][func_name]
            
            needed_args = self.MEMORY.env["functions"][func_name]["args"]
            for x in range(len(needed_args)):
                arg_get = self.MEMORY.var_get(args[x])
                        
                if arg_get == False:
                    data = self.MEMORY.type_guess(args[x])
                    dtype = ""
                    if type(data) == str    : dtype = "str"
                    elif type(data) == int  : dtype = "int"
                    elif type(data) == float: dtype = "float"
                    elif type(data) == bool : dtype = "bool"
                    self.MEMORY.set_scope(func_name)
                    self.MEMORY.var_add(needed_args[x], dtype, data, True)

                else:
                    self.MEMORY.set_scope(func_name)
                    self.MEMORY.var_add(needed_args[x], arg_get[0], arg_get[1], arg_get[2])

                self.MEMORY.back_scope()
                    
                
            
            if len(args) != len(func_data['args']):
                raise Exception(f"'{func_name}' expected {len(func_data['args'])} but got {len(args)}")
            
            code = func_data['code']
            
            return ('func_code', code, output, func_name)

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
                if temp1[0] == 'str':
                    item_1 = f'"{temp1[1]}"'
                else:
                    item_1 = temp1[1]

            if temp2 == False:
                item_2 = self.MEMORY.type_guess(item_2)
            
            else:
                if temp2[0] == 'str':
                    item_2 = f'"{temp2[1]}"'
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
        mutable = True
        if 'const' in args:
            mutable = False
            args = args.split(' ', 1)[1]
            
        dtype, args = args.split(' ', 1) ## get type and args
        
        if '=' in args:
            name, data = args.split('=', 1)
            name = name.rstrip() ## remove tailing spaces
            data = data.lstrip() ## remove leading spaces
            out = self.MEMORY.var_get(data)

            ## not var
            if out != False:
                self.MEMORY.var_add(name, dtype, out, mutable)
            
            ## var
            else:
                self.MEMORY.var_add(name, dtype, data, mutable)

        else:
            self.MEMORY.var_add(args, dtype, bs_types.null, mutable)


    ## append to blue arrays
    def blue_append(self, args):
        data, varname = args.split(bs_types.TO_CHAR, 1)
        
        data = data.rstrip()
        varname = varname.lstrip()
        main_var = self.MEMORY.var_get(varname)
                
        if main_var == False:
            raise Exception(f"Variable '{main_var}' does not exist")

        if main_var[0] != 'array':
            raise TypeError(f"Cannot append to type '{main_var[0]}'")
        
        var_data = main_var[1]
        
        temp_var = self.MEMORY.var_get(data)
        
        if temp_var == False:
            data = self.MEMORY.type_guess(data)
        else:
            ## 2nd index of variables are data
            data = temp_var[1]
        
        if type(data) == str and '"' in data:
            data = data.replace('"','')
        var_data.append(data)    
        
        var_data = bs_types.BLUE_ARRAY(var_data, len(var_data))
        
        self.MEMORY.var_add(varname, "array", var_data)
        
    ## create blue array
    def blue_array(self, args):

        ## has '='
        if '=' in args:
            name, data = args.split('=')
            
            ## clean string
            name = name.rstrip()
            data = data.lstrip().replace('[','').replace(']','')

            if ',' in data:
                data = data.split(',')
            
            ## empty array for output
            data_array = []
            ## loop through args
            for arrData in data:
                ## clean up data
                arrData = arrData.lstrip().rstrip()
                test = self.MEMORY.var_get(arrData)
                
                ## if we dont have var get corret type
                if test == False:
                    arrData = self.MEMORY.type_guess(arrData)
                    
                    ## check if string if so remove \"
                    if type(arrData) == str and '"' in arrData:
                        arrData = arrData.replace('"','')

                else:
                    arrData = test[1]
                    
                data_array.append(arrData)
                
            var_data = bs_types.BLUE_ARRAY(data_array, len(data_array))
            self.MEMORY.var_add(name, "array", var_data)

    def blue_dict(self, args):
        pass

    def blue_print(self, args):
        if "\"" in args:
            ## print string
            print(args.replace("\"", ""))
            return
        
        out = self.MEMORY.var_get(args)

        if out == False:
            raise Exception(f"Variable '{args}' does not exist")
        
        if type(out[1]) == bs_types.BLUE_ARRAY:
            print(out[1].data)
            return
        
        if type(out[1]) == str and '\"' in out[1]:
            print(out[1].replace('"',''))
        
        print(out[1])


def include_file(filename, current_file):
    if not filename.endswith(".bs"):
        filename += ".bs"

    if filename == current_file:
        raise Exception("Cannot include self")

    if UPL.Core.file_exists(filename):
        return UPL.Core.file_manager.clean_read(filename)

    else:
        raise Exception(f"Cannot find file '{filename}'")