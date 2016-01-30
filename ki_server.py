#!/usr/bin/python
import socket, sys
import time
import pickle
import binascii
import os
import array
import servermessage
import datetime
import csv
import datetime


#Functions
#-----------------------------------------------------------------------------------------------------------------------


def process_data(smRcv, data):
	#data = socket.recv(4096)
        leftCount   = data.__len__() 
        idx         = 0        
        while(leftCount) :
            leftCount, state, idx = smRcv.ProcessIncoming(data, idx)

            if( state == smRcv.INCOMINGSTATE.SERVERCOMS_HAVEMESSAGE): 
                ##print "Received good message!"       
                smRcv.parseMessage() 
		processed_data = smRcv.itemList
                smRcv.InitMessage()
	    else:
		processed_data = []  
  
	return processed_data

def send_message(string, socket):

	#create message
	sm = servermessage.ServerMessage()
	sm.MakeMessage(0x32, 0, string )
	
	#send the message
	socket.send( sm.WholeMessage )

	return 

def go_to_scene(scenename, socket):
	#create string
	string = "PUT" + chr(0x00) + "System" + chr(0x00) + "Storyboard" + chr(0x00) + "FocusedScene" + chr(0x00) + scenename + chr(0x00) + chr(0x00)
	send_message(string, socket)

	return 

def get_swipeCard_data():
	swipeCard_flag = 0 
	while (swipeCard_flag != 1):
			data = c.recv(4096)
			message  = process_data(smRcv, data)
			#print message
			if "Track2" in message:
				print message
				#print "cardswipe occured!!!" 
				track_2_data = message[4]
				swipeCard_flag = 1
	return track_2_data	

def get_odometerData():
	odometerData_flag = 0
	while (odometerData_flag != 1):
			data = c.recv(4096)
			message  = process_data(smRcv, data)
			#print message
			if "odometerData" in message:
				odometerData = message[5] 
				odometerData_flag = 1
	return odometerData


def get_driverID():
	driverID_flag = 0
	while (driverID_flag != 1):
			data = c.recv(4096)
			message  = process_data(smRcv, data)
			#print message
			if "driverID" in message:
				driverID = message[5] 
				driverID_flag = 1
	return driverID

def wait_for_cancel():
	filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable_flag.txt'
	wait = 0
	while (wait != 1):
			#data = c.recv(4096)
			#message  = process_data(smRcv, data)
			##print message
			if os.path.isfile(filepath): #or if message[1] == "d":
				#print "found disable_flag.txt"
				os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable_flag.txt')
				wait = 1
				charging_complete = 1
	return charging_complete



def start_cardreader(socket):
	#create string
	string = "PUT" + chr(0x00) + "System" + chr(0x00) + "Cardreader" + chr(0x00) + "StartCardreader" + chr(0x00) + chr(0x00)
	send_message(string, socket)
	return 

def determine_scene_procedure(track_2_data):
	scenario = 0
	field_5 = int(track_2_data[24])	
	field_9 = int(track_2_data[36])


	#decides which of the 12 scenarios it is...
	if field_5 == 0:
		if field_9 == 0:
			scenario = 1 

	if field_5 == 1:
		if field_9 == 0: 
			scenario = 2
		if field_9 == 2:
			scenario = 3
		if field_9 == 4:
			scenario = 4

	#returns scenarios (int value 1-4)
	return scenario

def execute_scenario(odometerData, driverID):
	#odometer
	if odometerData == 0:
		odometerData = ""
	else:
		go_to_scene("odometerData", c)
		odometerData = get_odometerData()
		
	#driverID
	if driverID == 0:
		driverID = ""
	else:
		go_to_scene("driverID", c)
		driverID = get_driverID()
	
	return  odometerData, driverID
	

def write_data_2_file(odometerData, driverID, track_2_data):
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/data_file.txt', 'w')		
	f.write(driverID + ",")
	f.write(odometerData + ",")
	f.write(track_2_data)
	f.close()
	return

"""
def print_receipt(socket):

	year, month, day, hour, minute, second = date_time()
	merchant_id = "011598110"
	terminal_id = "G5682"
	date =  month +"/" + day + "/" + year
	time = hour +":" + minute + ":" + second
	account_number = "12345"
	approval_code = "000132"
	rate = "$0.12/KWH"
	rate_service_fee = "$0.20/KWH"
	exp_date = "06/14"
	quantity = "16.1"
	quantity_service_fee = "16.1"
	amount =  " 1.93"
	amount_service_fee =  " 3.22"
	total_amount = " 5.15"
	invoice_number = "1"

	
	os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/reciept_data.txt')

	print "merchant_id ", merchant_id 
	print "terminal_id ", terminal_id
	print "date ", date 
	print "time ", time 
	print "account_number ", account_number 
	print "invoice_number ",  invoice_number
	print "approval_code ", approval_code 
	print "rate", rate 
	print "rate_service_fee ", rate_service_fee 
	print "exp_date", exp_date
	print "quantity", quantity  
	print "quantity_service_fee", quantity_service_fee  
	print "amount", amount 
	print "amount_service_fee", amount_service_fee
	print "total amount", total_amount 
	
	
	text =  "*****************************************\n" + "              Merit Solar                 \n" + "            9339 Appolds Rd               \n" + "          Rocky Ridge MD 21778            \n" + "Card Acceptor ID Code:" + merchant_id + " \n" + "Card Acceptor Terminal ID:" + merchant_id + " \n" + "Acct# XXXXXXXXXXXXXXX" + account_number + "\n" + "Exp: " + exp_date + "\n" + date + "                         " + time + "\n" + "Retrievel Reference Number:" + invoice_number + "        \n" + "Approval Code:" + approval_code + "\n" + "Product              Qty           Amount\n" + "-----------------------------------------\n" + "EV Level2@" + rate + "  " + quantity + "             " + amount + "\n"+ "Service Fee@" + rate_service_fee + "  " + quantity_service_fee   + "             " + amount_service_fee   + "\n"+ "                                         \n" + "Total:                             " + total_amount + "\n" + "                                         \n" + "                                         \n" + "   Thank You for choosing Merit Solar    \n\r"
	
	#text = "hello world"
	print text
	
	string_0 = "GET" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "PrinterStatus" + chr(0x00) + chr(0x00)
	
	#send text
	string_1 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "PrintText" + chr(0x00) + text + chr(0x00) + chr(0x00)

	#linefeed
	string_2 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "LineFeed" + chr(0x00) + "15" + chr(0x00) + chr(0x00)

	#cut receipt paper
	string_3 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "CutPaper" + chr(0x00) + chr(0x00)

	send_message(string_0, socket)	
	data = c.recv(4096)
	message  = process_data(smRcv, data)
	print message
	send_message(string_1, socket)
        send_message(string_2, socket)
	send_message(string_3, socket)
		
	

	return

"""

def print_receipt(socket):
	print "printing receipt"

	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/receipt_data.txt', 'r')
	
	reader = csv.reader(f, delimiter = ',')		
	for item in reader:
		data_list = item

	merchant_id = data_list[0]
	terminal_id = data_list[1]
	date = data_list[2]
	time = data_list[3]
	account_number = data_list[4]
	invoice_number = data_list[5]
	approval_code = data_list[6]
	rate = data_list[7]
	rate_service_fee = data_list[8]
	exp_date = data_list[9]
	quantity = data_list[10]
	quantity_service_fee = data_list[11]
	amount = data_list[12]
	amount_service_fee = data_list[13]
	total_amount = data_list[14]



	os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/receipt_data.txt')

	print "merchant_id ", merchant_id 
	print "terminal_id ", terminal_id
	print "date ", date 
	print "time ", time 
	print "account_number ", account_number 
	print "invoice_number ",  invoice_number
	print "approval_code ", approval_code 
	print "rate", rate 
	print "rate_service_fee ", rate_service_fee 
	print "exp_date", exp_date
	print "quantity", quantity  
	print "quantity_service_fee", quantity_service_fee  
	print "amount", amount 
	print "amount_service_fee", amount_service_fee
	print "total amount", total_amount 
	
	text =  "*****************************************\n" + "                 ergGo                    \n" + "            9339 Appolds Rd               \n" + "          Rocky Ridge MD 21778            \n" + "Card Acceptor ID Code:" + merchant_id + " \n" + "Card Acceptor Terminal ID:" + merchant_id + " \n" + "Acct# XXXXXXXXXXXXXXX" + account_number + "\n" + "Exp: " + exp_date + "\n" + date + "                         " + time + "\n" + "Retrievel Reference Number:" + invoice_number + "        \n" + "Approval Code:" + approval_code + "\n" + "Product                Qty         Amount\n" + "-----------------------------------------\n" + "EV Level2@" + rate + "    " + quantity + "           " + amount + "\n"+ "Service Fee@" + rate_service_fee + "  " + quantity_service_fee   + "           " + amount_service_fee   + "\n"+ "                                         \n" + "Total:                               " + total_amount + "\n" + "                                         \n" + "                                         \n" + "       Thank You for choosing ergGo      \n\r"
	
	print text
	
	#send text
	string_1 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "PrintText" + chr(0x00) + text + chr(0x00) + chr(0x00)

	#linefeed
	#string_2 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "LineFeed" + chr(0x00) + "15" + chr(0x00) + chr(0x00)

	#cut receipt paper
	string_3 = "PUT" + chr(0x00) + "System" + chr(0x00) + "Printer" + chr(0x00) + "CutPaper" + chr(0x00) + chr(0x00)

	
	
	send_message(string_1, socket)
        #	send_message(string_2, socket)
	send_message(string_3, socket)
		
	

	return


def disable_charging_station():   
	f = open('/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/disable.txt', 'w')
	f.close()
	return

def wait_for_disable():
	print "waiting for data"
	data = c.recv(4096)
	print "got data"
	message  = process_data(smRcv, data)	
	print message
	if "Keydown" in message:
				print "found word"
				disable_charging_station()
	return

#Main
#-----------------------------------------------------------------------------------------------------------------------

#define scenes
swipeCard = "swipeCard"
driverID = "driverID"
odometerData = "odometerData"
authorizing = "authorizing"
authorizationDenied = "authorizationDenied"
insertConnector = "insertConnector"
chargingVehicle = "chargingVehicle"
collectReceipt = "collectReceipt"



#open up socket
port = 18244
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "192.168.10.2"
s.bind(( host, port))

# Create a servermessage for receiving 
smRcv = servermessage.ServerMessage()

s.listen(5)
print "opening socket"
c,addr = s.accept()
print "got connection from", addr

#go_to_scene("loading", c)
i = 0
while i < 10:
	time.sleep(1)
	i = i + 1
	print i

data = c.recv(4096)
message  = process_data(smRcv, data)
print message

print "starting card reader"
#start card reader
start_cardreader(c)
print "starting card reader"

data = c.recv(4096)
message  = process_data(smRcv, data)
print message



while 1:
	
	go_to_scene("swipeCard", c)

	#wait for cardswipe
	track_2_data = get_swipeCard_data()
	if len(track_2_data) != 37:
		print "non-wex card was entered"
		go_to_scene("authorizationDenied", c)
		time.sleep(5)
	else:
		print "found a wex card"
		print "track_2_data", track_2_data


		#determine which scene scenario based on track 2 data
		scenario = determine_scene_procedure(track_2_data)
		print "scenario", scenario

		#displays appropriate scene sequence for each scenario and returns 2 data_fields: odometerData, driverID
	
		if scenario == 0:
			print "WEX card not supported"
			go_to_scene("authorizationDenied", c)
			time.sleep(5)
			
		else:
			if scenario == 1:
				odometerData, driverID = execute_scenario(0,0)
		
			elif scenario == 2:
				odometerData, driverID = execute_scenario(1,1)

			elif scenario == 3:
				odometerData, driverID = execute_scenario(1,0)
	
			elif scenario == 4:
				odometerData, driverID = execute_scenario(0,1)
	
		
			
	

			#by here we will have odometer_data and driver_id
			#write to data_file.txt and wait for scenarios below...
			write_data_2_file(odometerData, driverID, track_2_data)
	
	
			#continues to loop through the following scenarios
			process_complete = 0
			while (process_complete != 1):
				#change scene to authorizing scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/authorizing.txt'
				if os.path.isfile(filepath):
					go_to_scene("authorizing", c)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/authorizing.txt')
			

				#change scene to authorizationDenied scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/authorizationDenied.txt'
				if os.path.isfile(filepath):
					go_to_scene("authorizationDenied", c)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/authorizationDenied.txt')
			
				#change scene to insertConnector scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/insertConnector.txt'
				if os.path.isfile(filepath):
					go_to_scene("insertConnector", c)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/insertConnector.txt')
			
				#change scene to chargingVehicle scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/chargingVehicle.txt'
				if os.path.isfile(filepath):
					go_to_scene("chargingVehicle", c)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/chargingVehicle.txt')
					
				#change scene to collectReceipt scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/collectReceipt.txt'
				if os.path.isfile(filepath):
					go_to_scene("collectReceipt", c)
					print_receipt(c)
					time.sleep(10)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/collectReceipt.txt')
					process_complete = 1

				#change scene to swipecard scene
				filepath = '/home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/swipeCard.txt'
				if os.path.isfile(filepath):
					go_to_scene("swipeCard", c)
					os.system('rm /home/evcharger/Desktop/EV_Charging_Station_Software/Python_Scripts/KI_J1772_com_files/swipeCard.txt')
					process_complete = 1


			
