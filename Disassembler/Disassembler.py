'''
Camilla Lucero
CS 4200
Disassembler
'''
#Function that turns a string digit/character to a y86 register
def string_to_register(string):
    register = '%'

    if int(string) == 0:
        register += 'rax'
    
    elif int(string) == 1:
        register += 'rcx'
    
    elif int(string) == 2:
        register += 'rdx'
    
    elif int(string) == 3:
        register += 'rbx'
    
    elif int(string) == 4:
        register += 'rsp'
    
    elif int(string) == 5:
        register += 'rbp'
    
    elif int(string) == 6:
        register += 'rsi'
    
    elif int(string) == 7:
        register += 'rdi'
    
    elif string in '89ABCDE':
        register += 'r' + str(int(string,16))

    return register

#converts any immediate values into little endian
def hex_to_little_endian(hex):
    little_endian_hex = hex[::-1]
    return little_endian_hex

#---------------------------------------------------------
#Packages
import os

#This is the file path of the file you wish to decode. Change this! VVV
hex_file_path = 'C:\\Classes\\2023-2024\\CS 4200 - Comp. Arch\\CS 4200 Repo\\Disassembler\\decode.hex'


hex_file = '' #This will store a file object if filepath is valid
#if file path is valid, open it
print("Checking current directory for specified file: " + hex_file_path)
if os.path.isfile(hex_file_path):
    print("File found! Opening File...")
    hex_file = open(hex_file_path)

#if not, then prompt & quit
else:
    print("File was not found, please check your filepath and attempt again.")
    exit()

#read everything from the file - This probably isn't a good idea with bigger files, but decode.hex only has
#208 characters, so it is fine for our purposes
file_contents = hex_file.read()

#Close file
print("Closing File...")
hex_file.close()

#This nested dictionary stores all potenial combos within the y86 instruction set for easier printing
y86_instruction_set = {

    '0': {'0': 'halt'},

    '1': {'0': 'nop'},

    '2': {'0': 'rrmovq', #reg. to reg., requires register checks, 2 bytes max
          '1': 'cmovle',
          '2': 'cmovl',
          '3': 'cmove',
          '4': 'cmovne',
          '5': 'cmovege',
          '6': 'cmovg'}, 

    '3': {'0': 'irmovq'}, #imead. to reg, requires value & register check, max 10 bytes

    '4': {'0': 'rmmovq'}, #reg. to mem., requires register & mem address check, can be up to 10 bytes

    '5': {'0': 'mrmovq'}, #mem. to reg., requires register & mem address check, can be up to 10 bytes

    '6': {'0': 'addq',    #operations, 2 bytes max
          '1': 'subq',
          '2': 'andq',
          '3': 'xorq'},
    
    '7': {'0': 'jmp', #jumps, 7 bytes max
          '1': 'jle',
          '2': 'jl',
          '3': 'je',
          '4': 'jne',
          '5': 'jge',
          '6': 'jg'},
    
    '8': {'0': 'call'}, #call, 7bytes max

    '9': {'0': 'ret'}, #return

    'a': {'0': 'pushq'}, #Stack push, 2 bytes max

    'b': {'0': 'popq'}, # Stack pop, 2 bytes max

    'c': {'0': 'iaddq', #immediate value operations, 10 bytes max
          '1': 'isubq',
          '2': 'iandq',
          '3': 'ixorq'},
} #end of instruction set dictionary

print("\n\nStarting Disassemble... ")
print("---------------------------------------------------------------------------")

#Variable for string indexing
string_index = 0

while string_index < len(file_contents):
   
   instruction_string = '' #Variable used for printing

   #Grab first two instruction hex and iterate index to match
   instruction_bytes = file_contents[string_index] + file_contents[string_index+1]
   string_index += 2

   for instruction in y86_instruction_set:
       #Check what our intial instruction is,
       if instruction_bytes[0] == instruction: 
            
            #In the case of multi-functional instructions, get that
           if instruction_bytes[1] != 0:
               
               for instruction_type in y86_instruction_set[instruction]:
                   if instruction_bytes[1] == instruction_type:
        
                       instruction_string = y86_instruction_set[instruction][instruction_type]
                       break 
            
            #If our second hex is not zero, then we have a 'plain' instruction
           else:           
                #Set that into our instruction print
                instruction_string = y86_instruction_set[instruction]['0']
                break
    
    #Now that we have our instruction within our print tring, we can decide what else we need
    #from the next few hex values
    #If any instruction requiring a source and destination...
    #(register to register, operation, push, or pop)
   if instruction_bytes[0] in '26':
       
       #obtain our registers & convert them to readable text
       source = string_to_register(file_contents[string_index]) 
       destination = string_to_register(file_contents [string_index+1])
       string_index +=2 #dont forget to iterate index to match

       #Then concatinate to our instruction_string
       instruction_string = instruction_string + ' ' + source + ', ' + destination
    
    #If immediate to register move or immediate operation...
   elif instruction_bytes[0] in '3c':
       
       #Get our destination & the value we are putting in that register
        #There is a placeholder hex here, but we dont need it for our purposes. We skip it
        destination = string_to_register(file_contents[string_index+1])
        value = hex_to_little_endian(file_contents[(string_index+2):(string_index+2)+16]).lstrip('0')
        string_index += 18 #don't forget to iterate index to match

       #Then concatinate to our instruction_string
        instruction_string = instruction_string + ' $0x' + str(value) + ',' + destination
    
    #If register to memory move...
   elif instruction_bytes[0] == '4':
       
       #Get our source, destination, and address offset
       source = string_to_register(file_contents[string_index])
       destination = string_to_register(file_contents[string_index+1])
       address = file_contents[(string_index+2):(string_index+2)+16]
       string_index += 18 #don't forget to iterate index to match

        #Check if address is equal to 0, for formatting 
       if int(address,16) == 0x0:
           
           instruction_string = instruction_string + ' ' + source + ', (' + destination + ')'

       else:
           
           instruction_string = instruction_string + ' ' + source + ', 0x' + address + ' (' + destination + ')'

   #if memory to register move...
   elif instruction_bytes[0] == '5':
       
       #Get our source, destination, and address offset
       source = string_to_register(file_contents[string_index])
       destination = string_to_register(file_contents[string_index+1])
       address = file_contents[(string_index+2):(string_index+2)+16]
       string_index += 18 #don't forget to iterate index to match

        #Check if address is equal to 0, for formatting
       if int(address,16) == 0x0:
           
           instruction_string = instruction_string + ' (' + source + ') ,' + destination

       else:
           
           instruction_string = instruction_string + ' 0x' + address + ' (' + source + ') ,' + destination
    
   #if a call or jump instruction
   elif instruction_bytes[0] in '78':
       
       destination = file_contents[string_index:(string_index + 16)]
       string_index += 16

       instruction_string = instruction_string + ' 0x' + destination
    
    #if a push or pop...
   elif instruction_bytes[0] in 'ab':
        #obtain our registers & convert them to readable text
       destination = string_to_register(file_contents [string_index])
       #Another place holder hex, so we skip
       string_index +=2 #dont forget to iterate index to match

       #Then concatinate to our instruction_string
       instruction_string = instruction_string + ' ' + destination
       

    #Once we are done, print our instruction string
    #If our instruction string has a length of 0, an instruction wasn't paired and something went wrong
   if len(instruction_string) == 0:
       print("Something went wrong, no instruction found...")
    #Else, everything went successfully :)
   else:
       print(instruction_string)

print("---------------------------------------------------------------------------")
print("End of Disassemble")