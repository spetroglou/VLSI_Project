import datetime

current_datetime = datetime.datetime.now()
formatted_time = current_datetime.strftime("%a %d %b %Y, %H:%M:%S")

open_bracket = "{"

print(f"""* *******************************************************************************
* *                                                                             *
* *         My Library for the 2nd part of the semester project in ECE327       *
* * Designed according to the Cadence's NangateOpenCellLibrary_slow.txt Library *
* *                       Petroglou Spyridon 03185                              *
* *                                                                             *
* *******************************************************************************
*
* Temperature                         : 27C
* Voltage                             : 2.5V
*

library (NangateOpenCellLibrary) {open_bracket}

  /* Documentation Attributes */
  date                    		        : "{formatted_time}";
  revision                		        : "revision 1.0";
  comment                 		        : "Copyright (c) 2004-2011 Nangate Inc. All Rights Reserved.";

  /* General Attributes */
  technology                          (cmos);
  delay_model                         : table_lookup;

  /* Units Attributes */
  time_unit                           : "1ns";
  leakage_power_unit                  : "1nW";
  voltage_unit                        : "1V";
  current_unit                        : "1mA";
  pulling_resistance_unit             : "1kohm";
  capacitive_load_unit                  (1,ff);

  /* Threshold Definitions */
  slew_lower_threshold_pct_fall 	    : 30.00 ;
  slew_lower_threshold_pct_rise 	    : 30.00 ;
  slew_upper_threshold_pct_fall 	    : 70.00 ;
  slew_upper_threshold_pct_rise 	    : 70.00 ;
  input_threshold_pct_fall      	    : 50.00 ;
  input_threshold_pct_rise      	    : 50.00 ;
  output_threshold_pct_fall     	    : 50.00 ;
  output_threshold_pct_rise     	    : 50.00 ;""")