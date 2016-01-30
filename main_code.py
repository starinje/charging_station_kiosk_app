#!/usr/bin/python
import socket, sys
import time
import os.path
import serial
import datetime
import csv
import glob


#notes
#turned off the charging vehicle sequence. 
#commented out all of the changescene commands
#commented out charge_vehicle def

def change_scene(sceneName):
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/' + sceneName + '.txt', 'w')
	f.close()
	return

def parse_file(filepath):
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/data_file.txt', 'rb')
	reader = csv.reader(f, delimiter = ',')
	for item in reader:
		data_list = item
	#print data_list
	driver_id =  data_list[0]
	odometer_data =  data_list[1]
	track_2_data = data_list[2]

	os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/data_file.txt')
	
	
	

	#make sure driver_id, and odometer_data are correct lengths

	if len(driver_id) <= 6:
		length = len(driver_id)
		#create string of nul characters
		i = 1
		while i <= (6 - length):
			driver_id = driver_id + " "
			i = i + 1

	if len(driver_id) > 6:
		driver_id = "      "

	if len(odometer_data) <= 10:
		length = len(odometer_data)
		#create string of nul characters
		i = 1
		while i <= (10 - length):
			odometer_data = odometer_data + " "
			i = i + 1

	if len(odometer_data) > 10:
		odometer_data = "          "

	if len(track_2_data) != 37:
		track_2_data = "                   =                 "

	
	exp_month = track_2_data[22:24]
	exp_year = track_2_data[20:22]

	
	return driver_id, odometer_data, track_2_data, exp_year, exp_month

#returns date and time
def date_time():
	date_time = datetime.datetime.now()
	string = str(date_time)
	year = string[2:4]
	month = string[5:7]
	day = string[8:10]
	hour = string[11:13]
	minute = string[14:16]
	second = string[17:19]
	return year, month, day, hour, minute, second


def date_time_local():
	date_time = datetime.datetime.utcnow()
	string = str(date_time)
	year_local = string[2:4]
	month_local = string[5:7]
	day_local = string[8:10]
	hour_local = string[11:13]
	minute_local = string[14:16]
	second_local = string[17:19]
	return year_local, month_local, day_local, hour_local, minute_local, second_local


def calculate_audit_number():
	#needs to make a new number for each transaction

	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/working/audit_number.txt', 'r')
	audit_number = f.read()
	f.close()
	
	

	#create string and integer copies of the audit number
	audit_number_integer = int(audit_number)
	audit_number_string = str(audit_number)
	
	#convert string to correct length (6 characters)
	length = len(audit_number_string)
	if length <= 6:
		i = 1
		while i <= (6 - length):
			audit_number_string = "0" + audit_number_string 
			i = i + 1


	#increment audit number
	audit_number_integer = audit_number_integer + 1
	if audit_number_integer > 100000:
		audit_number_integer = 0


	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/working/audit_number.txt', 'w')
	f.write(str(audit_number_integer))
	f.close()

	audit_number = audit_number_string
	return audit_number


def create_800_xml():
	xml_file = open("/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/xml_templates/0800_xml_template.txt")
	xml_800_message = xml_file.read()

	year, month, day, hour, minute, second = date_time()

	#field 0 - Message Type ID
	x = xml_800_message.find('field id="0"')
	value = "0800"
	xml_800_message = xml_800_message[:x+20] + value + xml_800_message[x+20:]
	
	#field 7 - Message Type ID
	x = xml_800_message.find('field id="7"')
	value = month + day + hour + minute + second
	xml_800_message = xml_800_message[:x+20] + value + xml_800_message[x+20:]
	
	#field 11 - Message Type ID
	x = xml_800_message.find('field id="11"')
	value = "000001"
	xml_800_message = xml_800_message[:x+21] + value + xml_800_message[x+21:]
	
	#field 70 - Message Type ID
	x = xml_800_message.find('field id="70"')
	value = "301"
	xml_800_message = xml_800_message[:x+21] + value + xml_800_message[x+21:]

	#field 125 - Message Type ID
	x = xml_800_message.find('field id="125"')
	value = "4815EDF4........705D"
	xml_800_message = xml_800_message[:x+22] + value + xml_800_message[x+22:]
	
	return xml_800_message


#create 0100 pre-authorization xml message
def create_0100_xml(audit_number, exp_year, exp_month, driver_id, odometer_data, track_2_data, po_reference_number, invoice_number):

	chain_code = "G5682"
	merchant_id = "011598110"
	message_type = "0100"
	processing_code = "003000" 
	preauthorization_amount = "000000000100"
	year, month, day, hour, minute, second = date_time()
	year_local, month_local, day_local, hour_local, minute_local, second_local = date_time_local()
	merchant_type = "5542"
	pos_entry_mode = "9010"
	pos_condition_code = "02"	
	institution_id_code = "1042000314"
	terminal_id = chain_code + "0000000001"
	card_acceptor_institution_id = merchant_id + "      " 
	address = "9339 APPOLDS RD        ROCKY RIDGE  MDUS"
	currency_code = "840"
	pos_geographic_data = "0000021778    "
	additional_pos_data = "312 0P00" + chain_code + "00000000001001000000000"
	terminal_sequence_number = "000003"
	terminal_sequence_number = audit_number
	fleet_product_data = "003"
	driver_number = "            " 
	vehicle_id = track_2_data[27:32] + "   "
	prompt_code = "  "
	restriction_code = "  "
	service_type = "0 "
	merchant_discount_amount = "00000000"
	participant_discount_amount = "00000000"
	sales_tax_amount_non_fuel = "000000000"
	gross_fuel_price = "000000000"
	gross_non_fuel_price = "000000100"
	net_non_fuel_price = "000000000" 
	company_name = "MRIT"
	merchant_name = "Merit Solar    "
	

	
	
	
	xml_file = open("/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/xml_templates/0100_xml_template.txt")
	xml_0100_message = xml_file.read()
	
	#field 0 - Message Type ID
	x = xml_0100_message.find('field id="0"')
	value = message_type
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]

	#field 3 - processing code
	x = xml_0100_message.find('field id="3"')
	value = processing_code
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]

	#field 4 - amount, transaction
	x = xml_0100_message.find('field id="4"')
	value = preauthorization_amount  
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]

	#field 7 - transmission date and time (MMDDHHMMSS) 
	x = xml_0100_message.find('field id="7"')
	value = month + day + hour + minute + second
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]

	#field 11 - sytems trace audit number
	x = xml_0100_message.find('field id="11"')
	value = audit_number
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 12 - local transaction time (hhmmss)
	x = xml_0100_message.find('field id="12"')
	value = hour_local + minute_local + second_local
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 13 - local transaction date (mmdd)
	x = xml_0100_message.find('field id="13"')
	value = month_local + day_local
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 14 - expiration date (yymm)
	x = xml_0100_message.find('field id="14"')
	value = exp_year + exp_month
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]
	
	#field 18 - merchant type
	x = xml_0100_message.find('field id="18"')
	value = merchant_type
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 22 - pos entry mode
	x = xml_0100_message.find('field id="22"')
	value = pos_entry_mode
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 25 - pos condition code
	x = xml_0100_message.find('field id="25"')
	value = pos_condition_code
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 32 - aquiring inst. id code
	x = xml_0100_message.find('field id="32"')
	value = institution_id_code     
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 35 - track 2 data
	x = xml_0100_message.find('field id="35"')
	value = track_2_data
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 37 - retrieval reference number
	x = xml_0100_message.find('field id="37"')
	value = year + day + "00" + audit_number
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 41 - terminal id
	x = xml_0100_message.find('field id="41"')
	value = terminal_id
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 42 - card acceptor institution id
	x = xml_0100_message.find('field id="42"')
	value = card_acceptor_institution_id
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 43 - street adress, city, state, country
	x = xml_0100_message.find('field id="43"')
	#need to concatonate street adress, city, state, country into a single string
	value = address
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 49 - currency code, transaction
	x = xml_0100_message.find('field id="49"')
	value = currency_code
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]
	
	
	#field 59 - national pos geographic data
	x = xml_0100_message.find('field id="59"')
	value = pos_geographic_data
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]

	#field 60 - additional pos data
	x = xml_0100_message.find('field id="60"')
	value = additional_pos_data
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]	

	#field 62
	#_______________________________________________________________________________________________________________________

	field_62_position = xml_0100_message.find('isomsg id="62"')

	#field 2 terminal sequence number
	x = xml_0100_message.find('field id="2"', field_62_position)
	value = terminal_sequence_number
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]

	#field 3 fleet product data
	x = xml_0100_message.find('field id="3"', field_62_position)
	value = fleet_product_data
	xml_0100_message = xml_0100_message[:x+20] + value + xml_0100_message[x+20:]	


	#field 40 fleet customer data
	x = xml_0100_message.find('field id="40"', field_62_position)
	value = driver_number + vehicle_id + odometer_data + driver_id + prompt_code + restriction_code + service_type + merchant_discount_amount + participant_discount_amount + sales_tax_amount_non_fuel + gross_fuel_price + gross_non_fuel_price + net_non_fuel_price + company_name + po_reference_number + invoice_number
	xml_0100_message = xml_0100_message[:x+21] + value + xml_0100_message[x+21:]


	#________________________________________________________________________________________________________________________

	#field 123 - merchant name
	x = xml_0100_message.find('field id="123"')
	value = merchant_name
	xml_0100_message = xml_0100_message[:x+22] + value + xml_0100_message[x+22:]


	return xml_0100_message


#create 0220 pre-authorization xml message
def create_0220_xml(audit_number, exp_year, exp_month, auth_code, driver_id, odometer_data, track_2_data, total_charge_amount, charge_amount, po_reference_number, invoice_number, product_quantity, unit_price, unit_price_string, charge_amount_service_fee, product_quantity_service_fee, unit_price_string_service_fee ):

	chain_code = "G5682"
	merchant_id = "011598110"
	message_type = "0220"
	processing_code = "003000" 
	pan = track_2_data[0:19]
	preauthorization_amount = "000000000100"
	year, month, day, hour, minute, second = date_time()
	year_local, month_local, day_local, hour_local, minute_local, second_local = date_time_local()
	merchant_type = "5542"
	pos_entry_mode = "0210"
	pos_condition_code = "02"	
	institution_id_code = "1042000314"
	terminal_id = chain_code + "0000000001"
	card_acceptor_institution_id = merchant_id + "      " 
	address = "9339 APPOLDS RD        ROCKY RIDGE  MDUS"
	currency_code = "840"
	additional_amounts = "3057840C000000000100"
	pos_geographic_data = "0000021778    "
	additional_pos_data = "312 0400" + chain_code + "00000000001001000000000"
	terminal_sequence_number = "000003"
	terminal_sequence_number = audit_number
	fleet_product_data = "003"
	driver_number = "            " 
	vehicle_id = track_2_data[27:32] + "   "
	prompt_code = "  "
	restriction_code = "  "
	service_type = "0 "
	merchant_discount_amount = "00000000"
	participant_discount_amount = "00000000"
	sales_tax_amount_non_fuel = "000000000"
	gross_fuel_price = "00000" + charge_amount[8:12]
	gross_non_fuel_price = "000000000"
	net_non_fuel_price = "000000000" 
	product_type = "F" 
	product_code = "296   "
	unit_of_measure = "G"
	company_name = "MRIT"
	merchant_name = "Merit Solar    "

	#service fee
	product_type_service_fee = "N"
	product_code_service_fee = "255   "
	unit_of_measure_service_fee = "G"
	
	
	
	xml_file = open("/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/xml_templates/0220_xml_template.txt")
	xml_0220_message = xml_file.read()
	
	#field 0 - Message Type ID
	x = xml_0220_message.find('field id="0"')
	value = message_type
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 3 - processing code
	x = xml_0220_message.find('field id="3"')
	value = processing_code
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 2 - pan
	x = xml_0220_message.find('field id="2"')
	value = pan
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 4 - amount, transaction
	x = xml_0220_message.find('field id="4"')
	value = str(total_charge_amount)  
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 7 - transmission date and time (MMDDHHMMSS) 
	x = xml_0220_message.find('field id="7"')
	value = month + day + hour + minute + second
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 11 - sytems trace audit number
	x = xml_0220_message.find('field id="11"')
	value = audit_number
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 12 - local transaction time (hhmmss)
	x = xml_0220_message.find('field id="12"')
	value = hour_local + minute_local + second_local
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 13 - local transaction date (mmdd)
	x = xml_0220_message.find('field id="13"')
	value = month_local + day_local
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 14 - expiration date (yymm)
	x = xml_0220_message.find('field id="14"')
	value = exp_year + exp_month
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]
	
	#field 18 - merchant type
	x = xml_0220_message.find('field id="18"')
	value = merchant_type
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 22 - pos entry mode
	x = xml_0220_message.find('field id="22"')
	value = pos_entry_mode
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 25 - pos condition code
	x = xml_0220_message.find('field id="25"')
	value = pos_condition_code
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 32 - aquiring inst. id code
	x = xml_0220_message.find('field id="32"')
	value = institution_id_code
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 37 - retrieval reference number
	x = xml_0220_message.find('field id="37"')
	value = year + day + "00" + audit_number
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 38 - auth_code
	x = xml_0220_message.find('field id="38"')
	value = auth_code
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 41 - terminal id
	x = xml_0220_message.find('field id="41"')
	value = terminal_id
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 42 - card acceptor institution id
	x = xml_0220_message.find('field id="42"')
	value = card_acceptor_institution_id
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 43 - street adress, city, state, country
	x = xml_0220_message.find('field id="43"')
	#need to concatonate street adress, city, state, country into a single string
	value = address
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 49 - currency code, transaction
	x = xml_0220_message.find('field id="49"')
	value = currency_code
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]
	
	#field 54 - additional amounts
	x = xml_0220_message.find('field id="54"')
	value = additional_amounts
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 59 - national pos geographic data
	x = xml_0220_message.find('field id="59"')
	value = pos_geographic_data
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 60 - additional pos data
	x = xml_0220_message.find('field id="60"')
	value = additional_pos_data
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]	

	#field 62
	#_______________________________________________________________________________________________________________________

	field_62_position = xml_0220_message.find('isomsg id="62"')

	#field 2 terminal sequence number
	x = xml_0220_message.find('field id="2"', field_62_position)
	value = terminal_sequence_number
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]

	#field 3 fleet product data
	x = xml_0220_message.find('field id="3"', field_62_position)
	value = fleet_product_data
	xml_0220_message = xml_0220_message[:x+20] + value + xml_0220_message[x+20:]	


	#field 40 fleet customer data
	x = xml_0220_message.find('field id="40"', field_62_position)
	value = driver_number + vehicle_id + odometer_data + driver_id + prompt_code + restriction_code + service_type + merchant_discount_amount + participant_discount_amount + sales_tax_amount_non_fuel + gross_fuel_price + gross_non_fuel_price + net_non_fuel_price + company_name + po_reference_number + invoice_number 
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#field 41 fleet customer data
	x = xml_0220_message.find('field id="41"', field_62_position)
	value = str(charge_amount) + str(product_type) + str(product_code) + str(product_quantity) + unit_price_string + str(unit_of_measure) + str(charge_amount_service_fee) + str(product_type_service_fee) + str(product_code_service_fee) + str(product_quantity_service_fee) + unit_price_string_service_fee + str(unit_of_measure_service_fee)
	xml_0220_message = xml_0220_message[:x+21] + value + xml_0220_message[x+21:]

	#________________________________________________________________________________________________________________________

	#field 123 - merchant name
	x = xml_0220_message.find('field id="123"')
	value = merchant_name
	xml_0220_message = xml_0220_message[:x+22] + value + xml_0220_message[x+22:]


	return xml_0220_message

def calculate_charge_amount(power_consumed, unit_price):
	charge_amount = str(int(power_consumed)*unit_price)
	#print charge_amount
	decimal_place = charge_amount.find(".")
	
	#if there is no decimal place
	if decimal_place == -1:
		charge_amount = charge_amount + "00"
		
	#if there is only one digit after decimal place
	if ((len(charge_amount) - 1) - decimal_place) == 1:
		charge_amount = charge_amount + "0"

	#if there are two digits after decimal place
	if ((len(charge_amount) - 1) - decimal_place) == 2:
		charge_amount = charge_amount + "00"

	#if there are more then two digits after the decimal place
	if ((len(charge_amount) - 1) - decimal_place) > 2:
		charge_amount = charge_amount[0:decimal_place+3]
	
	#remove decimal place
	charge_amount = charge_amount.replace('.', '')

	#make value 12 digits long...
	if len(charge_amount) <= 12:
		length = len(charge_amount)
		#create string of nul characters
		i = 1
		while i <= (12 - length):
			charge_amount =  "0" + charge_amount
			i = i + 1
	return(charge_amount)


def calculate_charge_amount_service_fee(power_consumed, unit_price):
	charge_amount = str(int(power_consumed)*unit_price)
	
	decimal_place = charge_amount.find(".")
	
	#if there is no decimal place
	if decimal_place == -1:
		charge_amount = charge_amount + "00"
		
	#if there is only one digit after decimal place
	if ((len(charge_amount) - 1) - decimal_place) == 1:
		charge_amount = charge_amount + "0"

	#if there are two digits after decimal place
	if ((len(charge_amount) - 1) - decimal_place) == 2:
		charge_amount = charge_amount + "00"

	#if there are more then two digits after the decimal place
	if ((len(charge_amount) - 1) - decimal_place) > 2:
		charge_amount = charge_amount[0:decimal_place+3]
	
	#remove decimal place
	charge_amount = charge_amount.replace('.', '')

	#make value 12 digits long...
	if len(charge_amount) <= 12:
		length = len(charge_amount)
		#create string of nul characters
		i = 1
		while i <= (12 - length):
			charge_amount =  "0" + charge_amount
			i = i + 1
	charge_amount_service_fee = charge_amount
	return(charge_amount_service_fee)

def calculate_total_charge_amount(power_consumed, unit_price, unit_price_service_fee):
	total_charge_amount = str(int(power_consumed)*(unit_price + unit_price_service_fee))
	
	decimal_place = total_charge_amount.find(".")
	
	#if there is no decimal place
	if decimal_place == -1:
		total_charge_amount = total_charge_amount + "00"
		
	#if there is only one digit after decimal place
	if ((len(total_charge_amount) - 1) - decimal_place) == 1:
		total_charge_amount = total_charge_amount + "0"

	#if there are two digits after decimal place
	if ((len(total_charge_amount) - 1) - decimal_place) == 2:
		total_charge_amount = total_charge_amount + "00"

	#if there are more then two digits after the decimal place
	if ((len(total_charge_amount) - 1) - decimal_place) > 2:
		total_charge_amount = total_charge_amount[0:decimal_place+3]
	
	#remove decimal place
	total_charge_amount = total_charge_amount.replace('.', '')

	#make value 12 digits long...
	if len(total_charge_amount) <= 12:
		length = len(total_charge_amount)
		#create string of nul characters
		i = 1
		while i <= (12 - length):
			total_charge_amount =  "0" + total_charge_amount
			i = i + 1
	return(total_charge_amount)


#returns current electricity rate in 8 bytes (filled with zeros)
def electricity_rate():
	electricity_rate = .12
	electricity_rate_string = "00000120" #three decimal places
	return electricity_rate, electricity_rate_string

#returns current electricity rate in 8 bytes (filled with zeros)
def service_fee_rate():
	service_fee_rate = .20
	service_fee_rate_string = "00000200" #three decimal places
	return service_fee_rate, service_fee_rate_string

#returns 8 byte value of power consumed in KWH
def calculate_product_quantity(power_consumed):
	str_power_consumed = str(power_consumed)
	length = len(str_power_consumed)


	if length <= 5:
		i = 1
		while i <= (5 - length):
			str_power_consumed =  "0" + str_power_consumed
			i = i + 1
	

	str_power_consumed =  str_power_consumed + "000"
	product_quantity = str_power_consumed
	return product_quantity

#returns 8 byte value of minutes in minutes
def calculate_product_quantity_service_fee(power_consumed):
	str_power_consumed = str(power_consumed)
	length = len(str_power_consumed)


	if length <= 5:
		i = 1
		while i <= (5 - length):
			str_power_consumed =  "0" + str_power_consumed
			i = i + 1
	

	str_power_consumed =  str_power_consumed + "000"
	product_quantity_service_fee =  str_power_consumed
	return product_quantity_service_fee

def check_authorization(data):
	x = data.find('field id="39"')
	authorization_indicator = data[x+21:x+23] 
	if authorization_indicator == "00":
		auth_flag = 1
	else:
		auth_flag = 0
	return auth_flag

def get_auth_code(data):
	x = data.find('field id="38"')
	auth_code = data[x+21:x+27] 
	return auth_code	


def calculate_po_reference_number():
	po_reference_number = "              1" 
	return po_reference_number


def calculate_invoice_number():
	invoice_number = "         1"
	return invoice_number

def disable_charging_station():
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable.txt', 'w')
	f.close()
	return

def charge_vehicle():
	
	#open up connection to J1772 board
	ser = serial.Serial("/dev/ttyS1", 9600, parity = 'E', timeout = 0)
	print ser
	
	def j1772_write(command, connection):
		data = connection.write(command[0])
		ser.flush()
		##print command[0]
		data = connection.write(command[1])
		ser.flush()
		##print command[1]
		data = connection.write("\r")
		ser.flush()

	def j1772_read(connection):
		connection.flushInput()
		data = connection.readline()
		return data
		
	def j1772_read_wait(connection, command):
		flag = 0
		connection.flushInput()
		while flag != 1:	
			time.sleep(1)
			data = connection.readline()
			#print data
			if data.find(command) != -1:
				flag = 1
	
	print "enabling"
	ser.flush()
	ser.flushInput()
	j1772_write("en", ser)
	
	
	#poll status of vehicle and act accordingly
	complete_flag = 0
	ventilation_flag = 0
	fault_flag = 0
	disable_flag = 0
	connected_flag = 0
	power_flag = 0
	waiting_counter = 0
	connected_counter = 0

	while disable_flag != 1:	
		time.sleep(1)
		#ser.flushInput()
		#ser.flush()
		data = ser.readline()
		print data


		if data.find('Waiting') != -1:
			#if it is the first waiting found then switch kst-9000 scene to "insert connector"
			if waiting_counter < 1:
				#change scene to "insertConnector"
				change_scene("insertConnector")
				print "waiting for connection"

			#if the plug is disconnected before turning off charge
			if power_flag == 1:
				disable_charging_station()

			waiting_counter = waiting_counter + 1

		#if the status is "Connected"
		if data.find('Connected') != -1:
			connected_flag = 1
			#if the car finishes charging while the plug is still connected
			if power_flag == 1:
				#print "car is completely charged"
				disable_charging_station()
			
		#if the status is "Power On"
		if data.find('Power') != -1 and power_flag == 0:
			power_flag = 1
			#print "the car is charging"
			change_scene("chargingVehicle")

		#if the status is "Ventilation"
		if data.find('Ventilation') != -1:
			#print "ventilation requested"
			disable_charging_station()

		#if the status is "Fault"
		if data.find('Fault') != -1:
			#print "Fault Detected"
			disable_charging_station()

		
		
		#check file for flag to be written to disable charge
		if os.path.isfile('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable.txt'):
			print "found the disable flag"

			#remove the flag
			os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable.txt')	
	
			#disable the board
			disable_flag = 1
			j1772_write("di", ser)


	power_consumed = 16
	return power_consumed


#control power_meter
def power_meter(command):
	if command == 'start':
		state = 1
		command = 'X\r\n'
	if command == 'stop':
		state = 2
		command = 'Y\r\n' 
	if command == 'report':
		state = 3
		command = 'Z\r\n' 
	
	ser = serial.Serial(port="/dev/ttyS1", baudrate=9600, bytesize=8, parity = 'N', stopbits=1,timeout=5, xonxoff=0, rtscts=0)
	data = ser.write(command)	
	status = ser.readline()
	if state == 3:
		status = status[0:5]
		status = int(status)
		status = status/1000
			
	ser.close()
	return status


		


def receipt_data(exp_year, exp_month, track_2_data, invoice_number, rate, power_consumed, charge_amount, charge_amount_service_fee):
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/receipt_data.txt', 'w')	

	merchant_id = "011598110"
	terminal_id = "G5682"
	year, month, day, hour, minute, second = date_time()
	account_number = track_2_data[6:10]
	approval_code = "000132"
	rate = "$0.12/KWH"
	rate_service_fee = "$0.20/KWH"
	quantity = str(int(power_consumed))
	quantity_service_fee = str(int(power_consumed))
	amount =  charge_amount[8:10] + "." + charge_amount[10:12]
	amount_service_fee =  charge_amount_service_fee[8:10] + "." + charge_amount_service_fee[10:12]
	invoice_number = "1"

	#calculate total amount
	####
	dollar1 = amount[0:2]
	dollar2 = amount_service_fee[0:2]

	cents1 = amount[3:5]
	cents2 = amount_service_fee[3:5]

	int1 = int(dollar1)
	int2 = int(dollar2)
	int3 = int(cents1)
	int4 = int(cents2)

	total_dollars = int1 + int2
	total_cents = int3 + int4

	if total_cents > 99:
		total_cents = total_cents - 100
		total_dollars = total_dollars + 1
	
	if len(str(total_cents)) == 1:
		total_amount = str(total_dollars) + "." + "0" +str(total_cents)
	else:
		total_amount = str(total_dollars) + "." +str(total_cents)
	####



	f.write(merchant_id + ",")
	f.write(terminal_id + ",")
	f.write( month +"/" + day + "/" + year + ",")
	f.write( hour +":" + minute + ":" + second + ",")
	f.write(account_number + ",")
	f.write(invoice_number + ",")
	f.write(approval_code + ",")
	f.write(rate + ",")
	f.write(rate_service_fee + ",")
	f.write(exp_month + "/" + exp_year + ",")
	f.write(quantity + ",")
	f.write(quantity_service_fee + ",")
	f.write(amount + ",")
	f.write(amount_service_fee + ",")
	f.write(total_amount + ",")
	
	f.close()
	return



################################################################################################################################################################################
#main program loop----------------------------------------------------------------------------------------


#remove all txt files in /KI_J1772 directory
files = glob.glob('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/*')
for f in files:
	os.remove(f)	

while 1:

	#file that has been dumped from KST-9000 
	filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/data_file.txt'

	#open up file and extract driver id, track 2 data, and odometer data
	if os.path.isfile(filepath):
		print "found data file"

		
		#change scene to "authorizing"
		change_scene("authorizing")

	
		#create variables for ISO-8583 messages
		driver_id, odometer_data, track_2_data, exp_year, exp_month = parse_file(filepath)
		audit_number = calculate_audit_number()
		po_reference_number = calculate_po_reference_number()
		invoice_number = calculate_invoice_number()
		unit_price = electricity_rate()
	
		
		#create 0800 message
		xml_0800_message = create_800_xml()
		print "creating 0800 message"
		
		#create 0100 message
		xml_0100_message = create_0100_xml(audit_number, exp_year, exp_month, driver_id, odometer_data, track_2_data, po_reference_number, invoice_number)
		print "creating 0100 message" 

		
		#open socket and send 0100 message to ISO-Bridge
		host = "192.168.1.1"
		port = 8000
		print "opening socket to isobridge"
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host,port))
		
		#send 0800 message
		print "sending 0800 message"	
		sock.send(xml_0800_message)
		
		data = sock.recv(1024)	
		time.sleep(2)
		
		#send 0100 message
		print "sending 0100 message"	
		sock.send(xml_0100_message)
		
		
		#collect response
		data = sock.recv(1024)
		print data		
		

		#check for authorization
		print "checking authorization"
		auth_flag = check_authorization(data)		
		
		#if the transaction is authorized, then charge vehicle
		if auth_flag == 1:
			"authorized"
	
			#charge vehicle
			print "charging vehicle"
			power_consumed = charge_vehicle()

		
			
			#calculate power consumed data
			unit_price, unit_price_string = electricity_rate()
			charge_amount = calculate_charge_amount(power_consumed, unit_price)
			product_quantity = calculate_product_quantity(int(power_consumed))

			#calculate minutes charged data
			
			unit_price_service_fee, unit_price_string_service_fee = service_fee_rate()
			charge_amount_service_fee = calculate_charge_amount_service_fee(power_consumed, unit_price_service_fee)
			product_quantity_service_fee = calculate_product_quantity_service_fee(int(power_consumed))
		
			#create xml_220 message
			auth_code = get_auth_code(data)
			total_charge_amount = calculate_total_charge_amount(power_consumed, unit_price, unit_price_service_fee)
			print "creating 0220 message"
			xml_0220_message =create_0220_xml(audit_number, exp_year, exp_month, auth_code, driver_id, odometer_data, track_2_data, total_charge_amount, charge_amount, po_reference_number, invoice_number, product_quantity, unit_price, unit_price_string, charge_amount_service_fee, product_quantity_service_fee, unit_price_string_service_fee )

			
			#send 0220 message to ISO-Bridge
			print "sending 0220 message"
			sock.send(xml_0220_message)
			
			
			print "creating receipt data"
			receipt_data(exp_year, exp_month, track_2_data, invoice_number, unit_price, power_consumed, charge_amount, charge_amount_service_fee)
			change_scene("collectReceipt")

			
		#if not then display that transaction was denied
		else:
			#print "authorization denied"
			change_scene("authorizationDenied")
			time.sleep(5)
			change_scene("swipeCard")





		

	else:
		print "data_file.txt file not found"
		time.sleep(1)
        

