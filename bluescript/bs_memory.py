import bs_builtin
import bs_types

class BS_MEMORY:
    def __init__(self,base_filename):
        self.baseFile    = base_filename
        self.CurrentLine = 0
        self.env = {
            "vars"      : {
                "null" : ["null", bs_types.null]
            },   ## x : ["bs_int", 23456236]
            "lables"    : {},   ## start: [34]
            "functions" : {}    ## funcName : {"args":[bs_types.null], "return":"null" ,"code": [code]}
        }

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
            return varValue.replace('"','') 

        elif varValue == 'false':
            return False

        elif varValue == 'true':
            return True

        elif '.' in varValue:
            return float(varValue)

        else:
            try:
                return int(varValue)
            except TypeError:
                return None
    
        

    ## check if it's a recast or something
    def var_add(self, name, dtype, varValue):
        
        if varValue == None:
            self.env["vars"][name] = [dtype, None]
            return
        
        if dtype == 'int':
            varValue = int(varValue)
        
        elif dtype == 'float':
            varValue = float(varValue)
        
        elif dtype == 'str':
            if '"' in varValue:
                varValue = varValue.replace('\"','')
            else:
                raise Exception('Illegal string')

        elif dtype == 'chr':
            varValue = chr(varValue[0])

        elif dtype == 'bool':
            if varValue == 'true':
                varValue = 1
            else:
                varValue = 0
        
        self.env["vars"][name] = [dtype, varValue]


    def var_get(self, name):
        if name in self.env["vars"].keys():
            ## it exists
            return self.env["vars"][name]

        return False
        