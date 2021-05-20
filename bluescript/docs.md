# Blue Script
### Author: Ryan Draskovics
### Date: 5/20/2021

##### Version: 0.4.2

## Back ground

Blue script is a basic programming language written in python for my end of year project. Blue Script has many features, some of which are functions, structs, arrays and a standard library. Blue Script will continue to be developed and more features will be released as time goes on.

### Basic syntax
Blue Script has a similar syntax to java script and python. 

##### Example:
```js
// create a variable named hello_world and print
let str hello_world = "hello world" 
print hello_world
```

Variables in Blue Script are made using the key word ___let___ and the the type, the types that are in Blue Script are, int (integers), float (floating point numbers), str (strings) and bool (booleans)

##### Example variables:

```js
let str a = "hello world"
let int b = 10
let float c = 5.6
let bool d  = false
```

The variable names can be anything **without** spaces in the name as the parser may run into issues with that. 



### How to use function?

Currently in Blue Script there isn't much to calling functions you create the function at an point in the code and you can call it anywhere. Blue Script has a,"create anywhere, call anywhere" modle with functions. 

```js
// create hello_world and returns nothing
func hello_world() -> null
{
    print "hello world"
}

call hello_wolrd()
```

The code above creates a function called "hello_world" and the calls it. the *func* keyword tells the parser that you are wishing to make a function. Functions in Blue Script are treated as their own "mini files", where using the keyword *call* will switch from reading from the main file and will move to the sub file which is that function scope.

### What if I want to return a value?

Well it's simple just return. 

```js
func hello_wolrd() -> str
{
    let str hello = "hello_world"
    return hello
}

func hello() -> str
{
    return "hello there"
}

func age() ->
{
    return 15
}
```

For all of the types in Blue Script you can have a return for it. You can even return structs. You can either return a variable or you could return the base value. 

### What if I want a custom type?

Well Blue Script has structs, said structs act as dictionaries where there is variable name and then a value, with this you can make your own types as structs can hold constant values. 

#### How to use structs

```c
struct myStruct
{
    int base = 0
    const int a = 10
}

// create a variable named
// varname with type myStruct
let myStruct varname

// print myStruct.a
print varname.a
```