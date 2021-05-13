from UPL.Core import currentDir
import bs_types

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
        """  
        self.env = {
            "vars"      : {
                "global":{
                    "null" : ["null", bs_types.null]
                },
                "main" : {
                    
                }
            },   ## x : ["bs_int", 23456236]
            "lables"    : {},   
            "functions" : {}    ## funcName : {"args":[bs_types.null], "return":"null" ,"code": [code]}
        }

        self.included_files = []

    def set_scope(self, scope_name) -> None:
        if scope_name in self.env['vars'].keys():
            self.prev_scope.append(self.current_scope)
            self.current_scope = scope_name
        else:
            raise Exception(f"Scope '{scope_name}' does not exist")

    def scope_add(self, scope_name) -> None:
        self.env["vars"][scope_name] = {}

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

    def lable_add(self, lable_name, location):
        if lable_name in self.env["lables"].keys():
            return False ## we dont want this

        self.env["lables"][lable_name] = location

    def lable_get(self, lable_name):
        return self.env['lables'][lable_name] if lable_name in self.env['lables'].keys() else "NULL"

    def add_func(self, name, return_type, args, code):
        if name in self.env["functions"].keys():
            return False ## already exists
        
        self.env['functions'][name] = {"args":args, "return":return_type, "code":code}

        return True

    def type_guess(self, varValue):
        if '"' in varValue:
            return varValue

        elif varValue == 'false':
            return False

        elif varValue == 'true':
            return True

        elif '.' in varValue:
            return float(varValue)

        else:
            try:
                return int(varValue)
            
            ## return string if nothing else works
            except Exception:
                return f"\"{varValue}\""

    ## check if it's a recast or something
    def var_add(self, name, dtype, varValue, mutable=True):
        
        match dtype:
            case None:
                self.env["vars"][self.current_scope][name] = [dtype, None, mutable]
                return
                
            case "int":
                varValue = int(varValue)
                
            case "float":
                varValue = float(varValue)
            
            case "str":
                if varValue == None:
                    varValue = "null"
                elif '"' in varValue:
                    varValue = varValue.replace('\"','')
                else:
                    varValue = f'"{varValue}"'
            
            case "chr":
                varValue = chr(varValue[0])
            
            case "bool":
                if varValue == 'true':
                    varValue = 1
                else:
                    varValue = 0
            
            ## wildcard case
            case _:
                pass

        self.env["vars"][self.current_scope][name] = [dtype, varValue,mutable]

    def mem_get(self):
        out = {
            "Current Scope" : self.current_scope,
            "Memory"        : self.env
        }
        return out

    def var_get(self, name):
        """
            var_data[0] -> type
            var_data[1] -> data
                - if it's an array its a class object
            var_data[2] -> mutable
        """
        
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
            
        if name in self.env["vars"][self.current_scope].keys():
            var_data = self.env["vars"][self.current_scope][name]
            
            ## it exists
            if index != -1 and var_data[0] == 'array':
                
                ret_data = var_data[1].array_get(index)
                ret_val = None
                
                if type(ret_data) == str:
                    ret_data = f'"{ret_data}"'
                    ret_val = ["str", ret_data, True]
                
                elif type(ret_data) == int:
                    ret_val = ["int", ret_data, True]
                
                elif type(ret_data) == float:
                    ret_val = ["float", ret_data, True]
                
                elif type(ret_data) == bool:
                    ret_val = ["bool", ret_data, True]
                
                return ret_val
                
            if var_data[0] == 'array':
                return ["array", var_data[1].data, var_data[2]]
                        
            if var_data[0] == 'str' and index != -1:
                return ["str", var_data[1][index], var_data[2]]
                
            return var_data
        
        return False
        