from UPL.Core import currentDir
import bs_types
import os
## should lables be put in scopes?
class BS_MEMORY:
    def __init__(self,base_filename):
        self.baseFile      = base_filename
        self.CurrentLine   = 0
        self.current_scope = "main"
        ## array so we can back track
        self.prev_scope    = []  ## last index is most recent
        
        """
            new way to handle vars
            vars
                namespaces
                    local vars
            lables
                namespaces
                    lables
        """  
        self.env = {
            "vars"      : {
                "global":{
                    "null" : ["null", bs_types.null, False, 0, True],
                    "BS_VERSION" : ['str', "0.4.2", False, len("0.4.2"), True],
                    "os_name" : ["str", os.name, False, len(os.name), True]
                },
                "main" : {}
            },   ## x : ["bs_int", 23456236, 0]
            "lables"    : {"main":{}},   
            "functions" : {},    ## funcName : {"args":[bs_types.null], "return":"null" ,"code": [code]}
            "structs"   : {}
        }

        self.included_files = []

    def struct_check(self, name):
        if type(name) == list:
            return False
        if name not in self.env["structs"].keys():
            return False
        
        return True

    def add_struct(self, name, data):
        if self.struct_check(name):
            raise Exception(f"Struct {name} already exists")
        
        self.env['structs'][name] = data

    ## change current scope
    ## (runs when calling function)
    def set_scope(self, scope_name) -> None:
        if scope_name in self.env['vars'].keys():
            self.prev_scope.append(self.current_scope)
            self.current_scope = scope_name
        else:
            raise Exception(f"Scope '{scope_name}' does not exist")

    ## create a new scope
    ## (runs at func call)
    def scope_add(self, scope_name) -> None:
        self.env["vars"][scope_name] = {}
        self.env["lables"][scope_name] = {}

    ## go back a scope
    ## (runs on func return)
    def back_scope(self) -> None:
        ## get new scope
        self.current_scope = self.prev_scope[len(self.prev_scope)-1]
        
        ## remove last index
        self.prev_scope = self.prev_scope[:-1]
    
    def blue_memory_get(self,key):
        if key == "all":
            return self.env

        if key in self.env.keys():
            return self.env[key]

        raise Exception(f"Key '{key}' does not exist")

    ## creates lables during runtime
    def lable_add(self, lable_name, location):
        if lable_name in self.env["lables"].keys():
            return False ## we dont want this

        self.env["lables"][self.current_scope][lable_name] = location

    def lable_get(self, lable_name):
        ## fixed lables
        ## in funcs they redeclaired their lable
        if self.current_scope != "main":
            return self.env['lables'][self.current_scope][lable_name]+1 if lable_name in self.env['lables'][self.current_scope].keys() else "NULL"
        return self.env['lables'][self.current_scope][lable_name] if lable_name in self.env['lables'][self.current_scope].keys() else "NULL"
    
    def remove_func(self, name):
        del self.env['vars'][name]
        del self.env['functions'][name]
        del self.env['lables'][name]
    
    ## called during main.BS_MAIN.preRead()
    ## adds functions to the global scope
    def add_func(self, name, return_type, args, code):
        if name in self.env["functions"].keys():
            return False ## already exists
        
        self.env['functions'][name] = {"args":args, "return":return_type, "code":code}

        return True

    ## changing type of non-variable and of variables
    def type_guess(self, varValue):
        if '"' in varValue:
            return varValue

        elif varValue == 'false':
            return 0

        elif varValue == 'true':
            return 1

        elif '.' in varValue:
            try:
                return float(varValue)
            except Exception:
                return "struct"

        else:
            try:
                return int(varValue)
            
            ## return string if nothing else works
            except Exception:
                return f"\"{varValue}\""

    ## check if it's a recast or something
    ## Adds/edits variables in self.env check __init__()
    def var_add(self, name, dtype, varValue, mutable=True, is_global=False):
        ## what type are we dealing with?
        ## recast to correct type
        scope = self.current_scope
        
        if is_global != False:
            scope = "global"
            
        if name in self.env['vars'][scope].keys():
            temp = self.env['vars'][scope][name]
            if temp[2] == False:
                raise Exception(f"You cannot change the value of '{name}' as it is immutable.")

        match dtype:
            case None:
                self.env["vars"][scope][name] = [dtype, None, mutable, 0, is_global]
                return
                
            case "int":
                varValue = int(varValue)
                
            case "float":
                varValue = float(varValue)
            
            case "str":
                if varValue == None:
                    varValue = ""
                elif '"' in varValue:
                    varValue = varValue.replace('\"','')
                else:
                    varValue = f"{varValue}"
            
            case "chr":
                varValue = chr(ord(varValue[0]))
            
            case "bool":
                if varValue == 'true':
                    varValue = 1
                else:
                    varValue = 0
            
            ## wildcard case
            ## check for struct
            case _:
                    
                if self.struct_check(dtype):
                    self.env["vars"][scope][name] = ['struct', {}, mutable, 0, is_global]
                    temp = self.env["structs"][dtype]
                    var_data = None
                    for item in temp:
                        mutable = True
                        if "const" in item: 
                            item = item.replace('const ', '')
                            mutable = False
                            
                        vType, data = item.split(' ',1)
                        
                        if '=' in data:
                            var_name, var_data = data.split('=', 1)
                            var_name = var_name.rstrip()           
                            var_data = var_data.lstrip()
                            
                            var_data = eval(var_data)
                                           
                        else:
                            var_name = data.lstrip().rstrip() ## just clean up the string
                            
                            match vType:
                                case "int":
                                    var_data = 0
                                case "float":
                                    var_data = 0.0
                                case "str":
                                    var_data = ""
                                case "bool":
                                    var_data = True
                                case "array":
                                    var_data = []
                                case _:
                                    pass
                        
                        self.env["vars"][scope][name][1][var_name] = [vType, var_data, mutable, len(var_data) if type(var_data) == str or type(var_data) == list else len(str(var_data)), False]                 
                        
                    return
            
        ## for the size of what we are working with    
        var_size = 0
        if type(varValue) == str:
            var_size = len(varValue)
        elif type(varValue) == bs_types.BLUE_ARRAY:
            var_size = len(varValue.data)
        else:
            var_size = varValue
            
        ## vars are added here
        ## doesnt go to current scope as to check if we are global
        
        if '.' in name:
            tmp = self.type_guess(name)
            
            if tmp == 'struct':
                struct_name, var_name = name.split('.',1)
                
                if struct_name in self.env["vars"][scope].keys():
                    tmp = self.env["vars"][scope][struct_name]
                    if type(tmp) == list:
                        self.env["vars"][scope][struct_name][1][var_name][1] = varValue
                        return
                    self.env["vars"][scope][struct_name][var_name] = [dtype,varValue,mutable,var_size,is_global]
                    return
                
                else:
                    raise Exception(f"Struct '{struct_name}' does not exist in this context")
        
        self.env["vars"][scope][name] = [dtype,varValue,mutable,var_size,is_global]

    ## get mem stuff here
    def mem_get(self):
        out = {
            "Current Scope" : self.current_scope,
            "Memory"        : self.env
        }
        return out

    ## gets variables from self.env ^^ check __init__()
    def var_get(self, name):
        """
            var_data[0] -> type
            var_data[1] -> data
            var_data[2] -> mutable
            var_data[3] -> variable size
            var_data[4] -> is global
        """
        if '.' in name:
            tmp = self.type_guess(name)
            
            if tmp == "struct":
                struct_name, var_name = name.split('.',1)
                
                index = -1
                if '[' in var_name:
                    var_name, tmp_index = var_name.split('[', 1)
                    tmp_index = tmp_index.strip()[:-1]
                    if self.var_get(tmp_index) == False:
                        index = int(tmp_index)
                    else:
                        index = self.var_get(tmp_index)[1]
                
                ## dealing with structs     
                if struct_name in self.env["vars"][self.current_scope].keys():
                    tmp = self.env["vars"][self.current_scope][struct_name]
                    if index == -1:
                        if type(tmp) == list:
                            return tmp[1][var_name]
                        return tmp[var_name]
                    else:
                        return tmp[1][var_name][1][index]
                
                elif struct_name in self.env["vars"]["global"].keys():
                    return self.env["vars"]["global"][struct_name][var_name]
                
                else:
                    raise Exception(f"'{struct_name}' does not exist in current context.")
            
        index = -1
        ## we are dealing with an array (index of which)
        if '[' in name:
            name, index = name.split('[', 1)
            
            ## get index
            index = index.replace(']','')
            
            index_isVar = self.var_get(index)
            
            if index_isVar == False:
                try:
                    index = int(index)
                except:
                    raise Exception(f"'{index}' cannot be converted to int")

            elif index_isVar[0] == 'int':
                index = index_isVar[1]
            
            else:
                raise Exception(f"'{index}' is not an int.")
            
        if name in self.env["vars"][self.current_scope].keys() or name in self.env["vars"]["global"].keys():

            if name in self.env["vars"][self.current_scope].keys():
                var_data = self.env["vars"][self.current_scope][name]
            else:
                
                var_data = self.env["vars"]["global"][name]
            
            ## it exists
            if index != -1 and var_data[0] == 'array':
                
                ret_data = var_data[1][index]
                ret_val = None
                
                if type(ret_data) == str:
                    ret_data = f'"{ret_data}"'
                    ret_val = ["str", ret_data, True, len(ret_data), False]
                
                elif type(ret_data) == int:
                    ret_val = ["int", ret_data, True, ret_data, False]
                
                elif type(ret_data) == float:
                    ret_val = ["float", ret_data, True, ret_data, False]
                
                elif type(ret_data) == bool:
                    ret_val = ["bool", ret_data, True, 1, False]
                return ret_val
            
            ## return all of var_data   
            if type(var_data) == dict:
                return ["struct", var_data, True, len(var_data), False]
            
            if var_data[0] == 'array':
                if type(var_data[1]) == list:
                    return ["array", var_data[1], var_data[2], var_data[3], var_data[4]]
                return ["array", var_data[1].data, var_data[2], var_data[3], var_data[4]]
                        
            if var_data[0] == 'str' and index != -1:
                return ["str", var_data[1][index], var_data[2], var_data[3], var_data[4]]
        
            return var_data
        
        return False
        