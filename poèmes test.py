#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  print test.py
#  
#  Copyright 2025  <jauderaspbian@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import RPi.GPIO as GPIO
import time
import cups
import tempfile
import os

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# GPIO pin configuration
BUTTON_PIN = 17  # Button pin
LED_PIN = 27     # LED pin

# Set up GPIO pins
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button with pull-up resistor
GPIO.setup(LED_PIN, GPIO.OUT)  # LED pin as output

# Printer test page and cut function
def print_test_page_with_cut(printer_name):
    conn = cups.Connection()

    # Use a default file or check the existence of a test page
    test_page_path = "/usr/share/cups/data/testprint"  # Default test page
    if not os.path.exists(test_page_path):
        print(f"Error: Test page file {test_page_path} does not exist!")
        return

    try:
        # Create a temporary file to hold the test page
        with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
            # Copy the test page content into the temporary file
            with open(test_page_path, "rb") as test_file:
                temp_file.write(test_file.read())
            temp_file_path = temp_file.name

        # Send the test page to the printer
        job_id = conn.printFile(printer_name, temp_file_path, "Test Page with Cut", {})
        print(f"Test page sent to printer '{printer_name}' with job ID {job_id}")

   

        # Send the cut command to the printer (GS V command for cutting)
        cut_command = b"\x1d\x56\x01"  # GS V cut command for Epson printers
        cut_temp_file_path = "/tmp/cut_command.raw"
        with open(cut_temp_file_path, "wb") as cut_file:
            cut_file.write(cut_command)

        # Send the cut command to the printer
        job_id = conn.printFile(printer_name, cut_temp_file_path, "Cut Command", {})
        print(f"Cut command sent to printer '{printer_name}' with job ID {job_id}")

        # Clean up the temporary files
        os.remove(temp_file_path)
        os.remove(cut_temp_file_path)

    except Exception as e:
        print(f"Error printing or cutting: {e}")

# Main loop
try:
    # Initialize CUPS connection and get the default printer
    conn = cups.Connection()
    default_printer = conn.getDefault()
    if not default_printer:
        print("No default printer found. Ensure the printer is configured in CUPS.")
        exit(1)
    print(f"Using default printer: {default_printer}")

    print("Ready. Press the button to print a test page.")

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button pressed
            print("Impression en cours...")
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the LED
            
            # Print the test page and cut the paper
            print_test_page_with_cut(default_printer)
            
            # Cooldown after cutting
            time.sleep(3)  # Keep LED on for 3 seconds
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the LED
        else:
            print("En attente d'une action...")
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    GPIO.cleanup()  # Clean up GPIO on exit







