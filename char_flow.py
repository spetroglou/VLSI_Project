################### IMPORT LIBRARIES ###################
import json
import sys
import numpy as np

################### DEFINE CONSTANTS ###################
N1 = 4                               #NUM OF CIRCUITS
N2 = 4                               #NUM OF TIMING ARCS INSIDE A timing() FIELD
N3 = 7                               #NUM OF LUT INDEXES IN TIMING ARCS
N4 = 3                               #NUM OF LUT INDEXES IN CONSTRAINT ARCS

###################### FUNCTIONS #######################

#This function is used to open a file in reading mode with the json.load command
#It takes as an argument the filepath and it returns the name of data that were read, or 0 if something goes wrong
def read_file(filepath):
    try:
        with open(filepath, 'r') as file_name:
            data_name = json.load(file_name)
            return data_name
    except FileNotFoundError:
        print(f"The file wasn't read.")
    except Exception as e:
        print(f"An error occurred: {e}")    
    return 0

#This function is used to open a file in append mode
#It takes as an argument the text that is going to be appended
def append_file(append_data):
    try:
        with open(lib_filepath, "a") as lib_file:
            lib_file.write(append_data)
    except FileNotFoundError:
        print(f"No data to be appended.")
    except Exception as e:
        print(f"An error occurred: {e}")


#Initialize useful filepaths, it will make my life way easier
lib_filepath = 'my_library.lib'
json_filepath = 'my_config.json'
header_filepath = 'library_header.py'
lut_init_filepath = 'lut_templates.txt'

#A small cheat
open_bracket = "{"

#Firstly, I need to write the Library Header in my library.
#The informal header is placed into library_header.txt file and I need to write it into my library
#I also need to change the date using python commands
try:
    #Open the library header script for reading
    with open(header_filepath, "r") as header_file:
        header_data = header_file.read()

    #Open the .lib file for writing
    #Unfortunately I couldn't avoid syscalls, it's the most practical way to print the actual date and time in the header
    with open(lib_filepath, "w") as lib_file:
        sys.stdout = lib_file
        exec(header_data)
    
    sys.stdout = sys.__stdout__

    print(f"Data from library header have successfully written to my library")
except FileNotFoundError:
    print(f"The library header was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

#Now it's time to write the lut instantiations in the .lib file
#The content of this part is located into lut_templates.txt
try:    
    #Open the lut template text for reading
    with open(lut_init_filepath, "r") as lut_init:
        read_lut_init = lut_init.read()

    #And write it into the .lib file. I also need to extend the file, not to overwrite
    with open(lib_filepath, "a") as lib_file:
        lib_file.write(read_lut_init)

    print(f"Data from Lut template have successfully written to my library")
except FileNotFoundError:
    print(f"The lut init was not found.")
except Exception as e:
    print(f"An error occurred: {e}")


#Now it's time to write the results from my config file into my library
#I have to make 3 cells, so the number of iterrations N1 will be 3
try:
    #Firstly, I need open the config file in reading mode
    #The data of this file will be stored into a variable named config_data
    with open(json_filepath, "r") as config_file:
        config_data = json.load(config_file)

        #Time for the iterrations
        for i in range(N1):
            #Every time that I want to write something in my lib file
            #I will open it in append mode using the append_file function
            name_value = config_data['models'][i]['name']
            lib_content = f'\n    cell("{name_value}") {open_bracket}\n'
            append_file(lib_content)

            #The only useful information that I need to include in cell rules is the ff group
            #It describes the functionality of sequential circuits
            #So I need to track all sequential circuits and extract all the useful information about it

            if config_data['models'][i]['type'] == 'sequential':
                #Retrieve useful information from the config file
                Q = config_data['models'][i]['ff_group'][0]['next_state_output']
                nQ = config_data['models'][i]['ff_group'][0]['not_next_state_output']
                D = config_data['models'][i]['ff_group'][0]['data_input']
                Clk = config_data['models'][i]['ff_group'][0]['clock_input']

                #Prepare the appending text
                lib_content = f'\n        ff ("{Q}","{nQ}") {open_bracket}\n          next_state: "{D}"\n          clocked_on: "{Clk}"'
                #And append the text
                append_file(lib_content)

                #Now, if the ff is asynchronous, I need to retrieve more information. This is described in the first index of the ff_group array
                if config_data['models'][i]['ff_group'][0]['ff_type'] == 'asynchronous':
                    Preset = config_data['models'][i]['ff_group'][0]['preset_input']
                    Clear = config_data['models'][i]['ff_group'][0]['clear_input']

                    #And transfer these data into my library
                    lib_content = f'\n          preset: "{Preset}"\n          clear: "{Clear}'
                    append_file(lib_content)

                append_file("\n        }")

            #The cell doesn't need to include any more information, time to implement the pin rules
            #So I need to create as many pin() fields as the pins that I have
            #First I will create the pin rules for input pins
            for j in range(np.size(config_data['models'][i]['input_pins'])):
                input_pin_value = config_data['models'][i]['input_pins'][j]
                lib_content = f'\n        pin("{input_pin_value}") {open_bracket}\n'
                append_file(lib_content)

            #Now, inside the input pin fields, we have the direction of the pin (obviously here is input pins)
            #Also, we have the capacitance of the pin and the constraint arcs if we have sequential circuit

                #Direction
                append_file("\n            direction: input;")

                #Capacitance
                append_file("\n            capacitance: 15.4;")
                
                #Timing field (only for constraint arcs)
                #Only sequential circuits have constraint arcs, so firstly, I need to check if my circuit is sequential
                if config_data['models'][i]['type'] == 'sequential':
                    for k in range(np.size(config_data['models'][i]['constraint_arcs'])):
                        #Also, all the types of constraint arcs that I need to characterise start either from data input
                        #or from asychronous set/reset inputs and end up in the clock input
                        #So, all input pins have constraint arc field, apart from clock input
                        if input_pin_value != Clk:
                            lib_content = f'\n\n            timing() {open_bracket}\n'
                            append_file(lib_content)

                            #I need to include and some useful information such as the pin that is related with the
                            #arc, and the type of the arc, if it's setup, hold, recovery or removal
                            related_pin_data = config_data['models'][i]['constraint_arcs'][k]['to_pin']
                            lib_content = f'\n                "related_pin": {related_pin_data};'
                            append_file(lib_content)

                            timing_type_data = config_data['models'][i]['constraint_arcs'][k]['constraint_type']
                            lib_content = f'\n                "timing_type: {timing_type_data}";'
                            append_file(lib_content)

                            #And now, it's time to print the array of the constraint arc
                            constraint_arc_array = ['rise_constraint', 'fall_constraint']
                            for arc_name in constraint_arc_array:
                                #The first thing that I need to do is to find the file that contains the delays
                                constraint_arc_filepath = config_data['models'][i]['constraint_arcs'][k][arc_name]

                                #And I will read this file using read_file function
                                constraint_arc_data = read_file(constraint_arc_filepath)

                                #Also, the information about the template is included inside my config file
                                lut_template_name = config_data['models'][i]['constraint_arcs'][k]['lut_template']

                                #Write the header of the arc in my library
                                lib_content = f'\n\n                {arc_name} ({lut_template_name}) {open_bracket}'
                                append_file(lib_content)

                                #Now it's time to load and then to print the indexes into my library
                                #The two params are constrained pin transition and related pin trnsition
                                con = []
                                for l in range(N4):
                                    index_value = constraint_arc_data['measurements'][l]['constrained_pin_transition']
                                    con.append(index_value)

                                lib_content = f'\n                      index_1 ("{con[0]}, {con[1]}, {con[2]}");'
                                append_file(lib_content)

                                #And related pin transition
                                rel = []
                                for l in range(N4):
                                    index_value = constraint_arc_data['measurements'][0]['related_pin_transition'][l]['related_pin_transition']
                                    rel.append(index_value)

                                lib_content = f'\n                      index_2 ("{rel[0]}, {rel[1]}, {rel[2]}");'
                                append_file(lib_content)

                                #And finally, I am ready to fill in the lut in my library with the delay values
                                for l in range(N4):
                                    for m in range(N4):
                                        index_value = constraint_arc_data['measurements'][l]['related_pin_transition'][m]['value']

                                        #In my config, I write the data of every column first and then from every row
                                        #So I need to save the data in this, a little bit weird,  way, to print them properly later 
                                        val[m][l] = index_value

                                    #And it's time to print this 2x2 array
                                lib_content = f"""
                        values ("{val[0][0]}, {val[0][1]}, {val[0][2]}", /
                                "{val[1][0]}, {val[1][1]}, {val[1][2]}", /
                                "{val[2][0]}, {val[2][1]}, {val[2][2]}");"""
                                
                                append_file(lib_content)
                                append_file("\n                }")

                            append_file("\n            }")
                
                append_file("\n        }")                   

            #And then for the output pins
            for j in range(np.size(config_data['models'][i]['output_pins'])):
                output_pin_value = config_data['models'][i]['output_pins'][j]
                lib_content = f'\n        pin("{output_pin_value}") {open_bracket}\n\n'
                append_file(lib_content)  

                #Here we have the direction of the pin (output pin), the function of the circuit
                #And all the circuit's timing arcs inside a field named timing()

                #Direction
                append_file("            direction: output;")

                #Function
                #If the circuit is combinational, the information exists in the function field of the config file
                #Else, you need to retrieve this information from the ff group
                if config_data['models'][i]['type'] == 'sequential':
                    #Q output has a different function that nQ output
                    #We assume that in the config file, in output_pins field, the first variable stands for normal exit Q
                    #And the second one for the complementary output not Q (nQ)
                    if config_data['models'][i]['output_pins'][j] == config_data['models'][i]['output_pins'][0]:
                        function_value = config_data['models'][i]['ff_group'][0]['next_state_output']
                    elif config_data['models'][i]['output_pins'][j] == config_data['models'][i]['output_pins'][1]:
                        function_value = config_data['models'][i]['ff_group'][0]['not_next_state_output']
                    else:
                        print("Error, this output pin doesn't exit")
                else:
                    function_value = config_data['models'][i]['function']

                lib_content = f'\n            function: {function_value};'
                append_file(lib_content)

                #Timing field
                #I need a new loop that tracks all timing arcs and prints them

                for k in range(np.size(config_data['models'][i]['timing_arcs'])):
                    #I need to confirm that the timing arc will be written inside the correct output pin
                    #That's only for gates with multiple output pins such as flip flops
                    if output_pin_value == config_data['models'][i]['timing_arcs'][k]['to_pin']:
                        lib_content = f'\n\n            timing() {open_bracket}\n'
                        append_file(lib_content)

                        #Inside the timing field, I need to include some parameters such as related pin and timing sence
                        #Related pin is the input pin that is changed while timing sence is the unateness of the pin
                        #The information of both of them exist inside my config file
                        related_pin_data = config_data['models'][i]['timing_arcs'][k]['from_pin']
                        lib_content = f'\n                "related_pin": {related_pin_data};'
                        append_file(lib_content)

                        unateness_data = config_data['models'][i]['timing_arcs'][k]['unateness']
                        lib_content = f'\n                "timing_sence": {unateness_data};'
                        append_file(lib_content)

                        #And now it's time to print the LUT inside my library
                        #So, I create an array with the name of my timing arcs and I will loop inside this array
                        timing_arc_array = ['cell_rise', 'cell_fall', 'rise_transition', 'fall_transition']

                        for arc_name in timing_arc_array:
                            #Retrieve the filepath from my config file
                            timing_arc_filepath = config_data['models'][i]['timing_arcs'][k][arc_name]
                        
                            #And now read the corresponding file using the read_file function
                            timing_arc_data = read_file(timing_arc_filepath)

                            #Also, in my config file exists the lut template that it is used to characterise the arcs
                            lut_template_name = config_data['models'][i]['timing_arcs'][k]['lut_template']

                            #Write the header of the arc in my library
                            lib_content = f'\n\n                {arc_name} ({lut_template_name}) {open_bracket}'
                            append_file(lib_content)

                            #I need to create an array in which I will save the input slew values 
                            #that I will retrieve from my LUTs
                            slew = []
                            for l in range(N3):
                                index_value = timing_arc_data['measurements'][l]['input_slew']
                                slew.append(index_value)

                            #Write the indexes in my library
                            lib_content = f'\n                    index_1 ("{slew[0]}, {slew[1]}, {slew[2]}, {slew[3]}, {slew[4]}, {slew[5]}, {slew[6]}");'
                            append_file(lib_content)

                            #And now I need to retrieve the output load values in a similar way
                            load = []
                            for l in range(N3):
                                index_value = timing_arc_data['measurements'][0]['output_load'][l]['output_load']
                                load.append(index_value)

                            #And I need to write the indexes for the output load this time
                            lib_content = f'\n                    index_2 ("{load[0]}, {load[1]}, {load[2]}, {load[3]}, {load[4]}, {load[5]}, {load[6]}");'
                            append_file(lib_content)

                            #And, finally, it's time to print the delay values inside my library
                            #The array is 2x2, so I need a nested for loop 

                            #Initialize this array
                            val = np.zeros((7, 7))

                            for l in range(N3):
                                for m in range(N3):
                                    index_value = timing_arc_data['measurements'][l]['output_load'][m]['value']

                                    #In my config, I write the data of every column first and then from every row
                                    #So I need to save the data in this, a little bit weird,  way, to print them properly later 
                                    val[m][l] = index_value

                            #And it's time to print this 2x2 array
                            lib_content = f"""
                    values ("{val[0][0]}, {val[0][1]}, {val[0][2]}, {val[0][3]}, {val[0][4]}, {val[0][5]}, {val[0][6]}", /
                            "{val[1][0]}, {val[1][1]}, {val[1][2]}, {val[1][3]}, {val[1][4]}, {val[1][5]}, {val[1][6]}", /
                            "{val[2][0]}, {val[2][1]}, {val[2][2]}, {val[2][3]}, {val[2][4]}, {val[2][5]}, {val[2][6]}", /
                            "{val[3][0]}, {val[3][1]}, {val[3][2]}, {val[3][3]}, {val[3][4]}, {val[3][5]}, {val[3][6]}", /
                            "{val[4][0]}, {val[4][1]}, {val[4][2]}, {val[4][3]}, {val[4][4]}, {val[4][5]}, {val[4][6]}", /
                            "{val[5][0]}, {val[5][1]}, {val[5][2]}, {val[5][3]}, {val[5][4]}, {val[5][5]}, {val[5][6]}", /
                            "{val[6][0]}, {val[6][1]}, {val[6][2]}, {val[6][3]}, {val[6][4]}, {val[6][5]}, {val[6][6]}");"""
                            
                            append_file(lib_content)

                            append_file("\n                }")

                        append_file("\n            }")
                
                append_file("\n        }")

            append_file("\n    }")

except FileNotFoundError:
    print(f"The lut init was not found.")
except Exception as e:
    print(f"An error occurred: {e}")   

#I have opened a bracket in the library and in the end of my library I need to close it
with open(lib_filepath, "a") as close_bracket:
    close_bracket.write('\n}')
