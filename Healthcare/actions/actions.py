from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,EventType
from rasa_sdk.forms import FormAction,FormValidationAction
from rasa_sdk.types import DomainDict

import json
import requests
import environ
import datetime

from pathlib import Path
import os


env = environ.Env()
environ.Env.read_env()

CBOTBACKEND = env('CBOTBACKEND')
QUERYURL = env('QUERYURL')
REPORTURL = env('REPORTURL')

POSTURL = "http://" + CBOTBACKEND + QUERYURL
REPORTURL = "http://" + CBOTBACKEND + REPORTURL

class SetIntent(Action):

    def name(self) -> Text:
        return "act_set_intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return []
        
class SpecList(Action):

    def name(self) -> Text:
        return "act_list_specilizations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        response = requests.post(POSTURL,json={"function":"speclist","data":{}})
        specs = response.json()

        buttons = []

        for row in specs:
            buttons.append({"title":row["fields"]["spec_name"],"payload":"/inform{\"spec_id\": \""+str(row["pk"])+"\"}"})

        dispatcher.utter_button_message("Select the specialization you want", buttons)

        return []

class DoctorList(Action):

    def name(self) -> Text:
        return "act_list_doctors"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spec_id = tracker.get_slot("spec_id")
        doctor_list = []

        if spec_id != "" and spec_id != None:
            response = requests.post(POSTURL,json={"function":"doctlist","data":{"spec_id":int(spec_id)}})
            doctor_list = response.json()
        else:
            response = requests.post(POSTURL,json={"function":"doctlist","data":{}})
            doctor_list = response.json()

        buttons = []

        for row in doctor_list:
            buttons.append({"title": "Dr."+row["fields"]["first_name"]+" "\
                +row["fields"]["last_name"],"payload":"/inform_docthash{\"docthash\":\""+str(row["fields"]["docthash"])+"\"}"})

        if len(buttons)==0:
            dispatcher.utter_message("No doctors are found with the provided specialization")
            return []

        dispatcher.utter_button_message("List of Doctors", buttons)

        return []

class TimeRange(Action):

    def name(self) -> Text:
        return "act_show_timerange"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        docthash = tracker.get_slot("docthash")

        selecteddoctor = None

        if docthash != "" and docthash != None:
            response = requests.post(POSTURL,json={"function":"docbyhash","data":{"docthash":docthash}})
            selecteddoctor = response.json()[0]
            response = requests.post(POSTURL,json={"function":"docavlbl","data":{"docthash":docthash}})
            doctors_time = response.json()[0]
        else:
            dispatcher.utter_message("Doctor's name is not provided")
            return []
            
        first_name = selecteddoctor["fields"]["first_name"]
        last_name = selecteddoctor["fields"]["last_name"]
        timefrom = doctors_time["fields"]["time_from"]
        timeto = doctors_time["fields"]["time_to"]

        dispatcher.utter_message("Dr. "+ first_name +" "+ last_name + " is available from " + timefrom + " to " + timeto)

        return []

class PlaceAppointment(Action):

    def name(self) -> Text:
        return "act_place_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot("date")
        time = tracker.get_slot("time")
        docthash = tracker.get_slot("docthash")
        username = tracker.get_slot("person_name")
        userhash = tracker.get_slot("userhash")

        response_doctor = requests.post(POSTURL,json={"function":"docbyhash","data":{"docthash":docthash}})
        doctor = response_doctor.json()[0]

        if userhash:
            response_patient = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
            patient = response_patient.json()[0]
        else:
            response_patient = requests.post(POSTURL,json={"function":"newpatient","data":{"username":username}})
            patient = response_patient.json()[0]

        doct_id = doctor["pk"]
        cust_id = patient["pk"]

        response = requests.post(POSTURL,json={"function":"newappoint","data":{"doct_id":doct_id , "cust_id":cust_id,"date":date,"time":time}})
        
        dispatcher.utter_message(text="Appointment was placed successfully")

        return [SlotSet("appointment_option",None),
        SlotSet("date",None),
        SlotSet("relativedate",None),
        SlotSet("time",None),
        SlotSet("docthash",None)]

class PreprocessAppointmentData(FormValidationAction):

    def name(self) -> Text:
        return "validate_place_appointment"

    async def validate_relativedate(self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:

        date = tracker.get_slot("date")
        reldate = tracker.get_slot("relativedate")

        if (date==None or date=="") and (reldate!=None and reldate!=""):
            if reldate=="today":
                date = str(datetime.date.today())
            elif reldate=="tomorrow":
                date = str(datetime.date.today()+datetime.timedelta(days=1))

            dispatcher.utter_message(text="Appointment is placed on "+reldate+" "+date)

        return [SlotSet("date",date)]

    async def validate_date_replace_slash(self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:

        date = tracker.get_slot("date")

        if "/" in date:
            date = date.split("/")
            date= "-".join(date)
            return [SlotSet("date",date)]
        elif "\\" in date:
            date = date.split("\\")
            date= "-".join(date)
            return [SlotSet("date",date)]

        return []
                    
class AskFor_DOCTHASH(Action):
    def name(self) -> Text:
        return "action_ask_docthash"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_ask_docthash")

        dispatcher.utter_message(text="You haven't selected a doctor")
        return []
    
class AskFor_DATE(Action):
    def name(self) -> Text:
        return "action_ask_date"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_ask_date")

        relativedate = tracker.get_slot("relativedate")
        
        if relativedate==None or relativedate=="":
            dispatcher.utter_message(text="Provide a date please [YYYY-MM-DD]")
        else:
            if reldate=="today":
                date = str(datetime.date.today())
            elif reldate=="tomorrow":
                date = str(datetime.date.today()+datetime.timedelta(days=1))
            return [SlotSet("date",date)]

        return []

class AskFor_TIME(Action):
    def name(self) -> Text:
        return "action_ask_time"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_ask_time")

        dispatcher.utter_message(text="Provide a comfortable  time for you [HH:mm]")
        return []

class AskFor_CLIENTPERSON(Action):
    def name(self) -> Text:
        return "action_ask_client_person"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_ask_client_person")

        client_person = tracker.get_slot("client_person")
        userhash = tracker.get_slot("userhash")

        if not(client_person or userhash):
            dispatcher.utter_message(text="It looks like you are a new client. Please tell your name to register as a new client. If you are already a client provide your user hash here")

        elif userhash:
            response = requests.post(POSTURL,json={"function":"clientdata", "data":{"userhash":userhash}})
            patients = response.json()
            client_person = patients[0]["fields"]["username"]
            return[SlotSet("client_person",client_person)]

        return []

class AskFor_USERHASH(Action):
    def name(self) -> Text:
        return "action_ask_userhash"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_ask_userhash")

        client_person = tracker.get_slot("client_person")
        userhash = tracker.get_slot("userhash")

        if not(client_person or userhash):
            dispatcher.utter_message(text="It looks like you are a new client. Please tell your name to register as a new client. If you are already a client provide your user hash here")
            return []
        elif client_person and not(userhash):
            dispatcher.utter_message(text="It looks like you are a new client. If you are already a client provide your user hash here")
            return []

        return []

class newPatient(Action):
    def name(self) -> Text:
        return "act_new_patient"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        client_person = tracker.get_slot("person_name")

        response = requests.post(POSTURL,json={"function":"newpatient","data":{"username":client_person}})
        print(response)
        patient = response.json()
        print(patient)

        try:
            if patient[0]["fields"]["query_success"]==0:
                dispatcher.utter_message("Couldn't add a new user")
        except KeyError:
            if patient[0]["fields"]["userhash"]:
                userhash = patient[0]["fields"]["userhash"]
                dispatcher.utter_message("Your userhash is "+patient[0]["fields"]["userhash"]+". Remember this userhash for access your data")
                return [SlotSet("userhash",userhash)]

class promptUserdata(Action):
    def name(self) -> Text:
        return "act_prompt_userdata"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        userhash = tracker.get_slot("userhash")
        
        response = requests.post(POSTURL,json={"function":"clientdata", "data":{"userhash":userhash}})
        patients = response.json()
        try:
            username = patients[0]["fields"]["username"]
            dispatcher.utter_message(text="Welcome "+username+". You can now access your appointments, reports and other reservations details")
            return [SlotSet("client_person",username)]
        except KeyError as e:
            print(e)
            dispatcher.utter_message(text="Sorry, No client was found with the given userhash. Please try again")
        return []



class checkAppointment(Action):
    def name(self) -> Text:
        return "act_check_appointment"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        userhash = tracker.get_slot("userhash")

        if userhash:
            client_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
            client = client_response.json()
            cust_id = client[0]["pk"]
            appointment_response = requests.post(POSTURL,json={"function":"listappoint","data":{"cust_id":cust_id}})
            appointments = appointment_response.json()

            buttons=[]

            for appoint in appointments:
                date = appoint["fields"]["date"]
                time = appoint["fields"]["time_slot"]
                doctor = appoint["fields"]["doctor_id"]
                buttons.append({"title":"appointment on "+date+" at "+time+"."  ,"payload":"/inform{\"appointment_id\":\""+str(appoint["pk"])+"\"}"})

            if len(buttons)==0:
                dispatcher.utter_message("No Appointment has been found")
                return []

            dispatcher.utter_button_message("Your Appointments", buttons)

        return []

class checkMedicaltest(Action):
    def name(self) -> Text:
        return "act_check_medtest"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        userhash = tracker.get_slot("userhash")

        if userhash:
            client_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
            client = client_response.json()
            cust_id = client[0]["pk"]
            medtest_response = requests.post(POSTURL,json={"function":"listmedtest","data":{"cust_id":cust_id}})
            medtests = medtest_response.json()

            #buttons=[]

            if len(medtests)==0:
                dispatcher.utter_message("No Medical tests are found")

            for mdt in medtests:
                date = mdt["fields"]["date"]
                time = mdt["fields"]["time_slot"]
                test_type = mdt["fields"]["test_type"]
                #buttons.append({"title":"appointment on "+date+" at "+time+"."  ,"payload":"/inform{\"appointment_id\":\""+str(appoint["pk"])+"\"}"})
                dispatcher.utter_message(text=test_type+" test on "+date+" at "+time+".")


            # if len(buttons)==0:
            #     dispatcher.utter_message("No Appointment has been found")
            #     return []

            # dispatcher.utter_button_message("Your Appointments", buttons)

        return []

class changeAppointment(Action):
    def name(self) -> Text:
        return "act_change_appointment"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        userhash = tracker.get_slot("userhash")
        appoint_id = tracker.get_slot("appointment_id")
        date = tracker.get_slot("date")
        time = tracker.get_slot("time")

        user_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
        user = user_response.json()

        change_response = requests.post(POSTURL,json={"function":"changeappoint","data":{"cust_id":user[0]["pk"],"appoint_id":appoint_id,"date":date,"time":time}})
        change_status = change_response.json()

        if change_status[0]["query_success"]=="1":
            dispatcher.utter_message(text="Appointment was changed successfully")
        elif change_status[0]["query_success"]=="0":
            dispatcher.utter_message(text="Couldn't change the appointment matched with provided data because of "+delete_status[0]["error"])
        
        return [SlotSet("appointment_option",None),
        SlotSet("appointment_id",None),
        SlotSet("date",None),
        SlotSet("time",None),]

class deleteAppointment(Action):
    def name(self) -> Text:
        return "act_delete_appointment"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        userhash = tracker.get_slot("userhash")
        appoint_id = tracker.get_slot("appointment_id")

        user_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
        user = user_response.json()

        delete_response = requests.post(POSTURL,json={"function":"deleteappoint","data":{"cust_id":user[0]["pk"],"appoint_id":appoint_id}})
        delete_status = delete_response.json()

        if delete_status[0]["query_success"]=="1":
            dispatcher.utter_message(text="Appointment was deleted successfully")
        elif delete_status[0]["query_success"]=="0":
            dispatcher.utter_message(text="Couldn't delete the appointment matched with provided data because of "+delete_status[0]["error"])
        
        return [SlotSet("appointment_option",None),
        SlotSet("appointment_id",None),]

class promptAppointmentOptions(Action):
    def name(self) -> Text:
        return "action_prompt_appointment_options"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        appoint_id = tracker.get_slot("appointment_id")

        if appoint_id:
            buttons = [{"title":"chanege appointment","payload":"/change_appiontment"},
            {"title":"cancel appointment","payload":"/delete_appointment"},
            {"title":"nothing","payload":"/nlu_fallback"}
            ]

            dispatcher.utter_button_message("What do you want to do with this appointment",buttons)

        else:
            dispatcher.utter_message(text="You havent selected an appointment yet. Select an appointment first")
        return []

class listReports(Action):
    def name(self) -> Text:
        return "act_list_reports"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed act_list_reports")

        userhash = tracker.get_slot("userhash")

        user_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
        user = user_response.json()
        cust_id = user[0]["pk"]

        reports_response = requests.post(POSTURL,json = {"function":"listreports","data":{"cust_id":cust_id}})
        reports_list = reports_response.json()

        if len(reports_list)==0:
            dispatcher.utter_message("No reports are found with your detailes")
            return []

        buttons = []

        for report in reports_list:
            buttons.append({"title":report["fields"]["report_name"],"payload":report["fields"]["reporthash"]})

        dispatcher.utter_button_message("here are your reports",buttons)

        return []

# class getreport(Action):
#     def name(self) -> Text:
#         return "action_download_report"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[EventType]:

#         print("executed action_download_report")

#         userhash = tracker.get_slot("userhash")
#         reporthash = tracker.get_slot("reporthash")

#         user_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
#         user = user_response.json()

#         cust_id = user[0]["pk"]

#         download_response = requests.post(POSTURL,json = {"function":"getreport","data":{"cust_id":cust_id,"reporthash":reporthash}})
#         download_report = download_response.json()

#         if len(download_report)>0:
#             dispatcher.utter_message(text="Here is your Report. Check Downloads",attachment=REPORTURL+download_report[0]["fields"]["report_filename"])
#         else:
#             dispatcher.utter_message(text="Couldn't find a report with given detailes.")
        
#         return [SlotSet("reporthash",None)]

class statReport(Action):
    def name(self) -> Text:
        return "action_status_report"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed action_status_report")

        userhash = tracker.get_slot("userhash")
        reporthash = tracker.get_slot("reporthash")

        user_response = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
        user = user_response.json()

        cust_id = user[0]["pk"]

        stat_response = requests.post(POSTURL,json = {"function":"getreport","data":{"cust_id":cust_id,"reporthash":reporthash}})
        stat_report = stat_response.json()

        if len(stat_report)>0:
            dispatcher.utter_message(text="You can get your report from "+ stat_report[0]["fields"]["available_on"] +" onwards. Ask for your report from the hospital. Thank you.")
        else:
            dispatcher.utter_message(text="Couldn't find a report with given detailes.")
        
        return [SlotSet("reporthash",None)]

class ActionMakeComplaint(Action):

    def name(self) -> Text:
        return "action_make_complain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        title = tracker.get_slot('cmpl_title')
        description = tracker.get_slot('cmpl_description')
        fullname = tracker.get_slot('cmpl_fullname')
        contactnum = tracker.get_slot('cmpl_contactnum')
        email = tracker.get_slot('cmpl_email')

        complaint_data = {
            "title" : title,
            "description" : description,
            "name" : fullname,
            "contact_no" : contactnum,
            "email" : email
        }

        results = requests.post(POSTURL, json={"function":"makecomplain","data":complaint_data})

        if results[0]["query_success"]=="1":
            complaint = {"domain" : "healthcare",
                         "fullname" : fullname,
                         "contactnum" : contactnum,
                         "email" : email,
                         "title" : title,
                         "description":description }
            dispatcher.utter_message(text = "You have succesfully made a complaint")
            dispatcher.utter_message(json_message= {"complaint":  complaint})    
        else:
            dispatcher.utter_message(text="Sorry, Complainet wasn't placed because of an error")

        return [SlotSet("title", None), SlotSet("description", None), SlotSet("fullname", None), SlotSet("contactnum", None), SlotSet("email", None)] 

class PlaceMedtest(Action):

    def name(self) -> Text:
        return "action_place_medtest"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot("date")
        time = tracker.get_slot("time")
        test_type = tracker.get_slot("test_type")
        username = tracker.get_slot("person_name")
        userhash = tracker.get_slot("userhash")

        if userhash:
            response_patient = requests.post(POSTURL,json={"function":"clientdata","data":{"userhash":userhash}})
            patient = response_patient.json()[0]
        else:
            response_patient = requests.post(POSTURL,json={"function":"newpatient","data":{"username":username}})
            patient = response_patient.json()[0]

        cust_id = patient["pk"]

        report_name= str(cust_id) + "-" + test_type + "-" + date
        available_on = str(datetime.datetime.strptime(date,"%Y-%m-%d").date()+datetime.timedelta(days=3))
 
        newreport_response = requests.post(POSTURL,json={"function":"newreport","data":{"cust_id":cust_id,"report_name":report_name,"available_on":available_on}})
        print(newreport_response.content)
        newreport = newreport_response.json()

        report_id = newreport[0]["pk"]

        response = requests.post(POSTURL,json={"function":"placemedtest","data":{"cust_id":cust_id,"date":date,"time":time,"test_type":test_type,"report_id":report_id}})
        response_status = response.json()

        if response_status[0]["query_success"]=="1":
            dispatcher.utter_message(text="Medical test was placed successfully")
        elif response_status[0]["query_success"]=="0":
            dispatcher.utter_message(text="Couldn't place Medical test with provided data because of "+response_status[0]["error"])

        return [
        SlotSet("date",None),
        SlotSet("relativedate",None),
        SlotSet("time",None),
        SlotSet("test_type",None),
        ]

class listTesttypes(Action):
    def name(self) -> Text:
        return "act_list_test_types"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        print("executed act_list_test_types")
        test_types = ["ecg","eeg","diabetic","prenancy","screening"]
        buttons =[]
        for tt in test_types:
            buttons.append({"title":tt,"payload":"/inform_testtype{\"test_type\":\""+tt+"\"}"})

        dispatcher.utter_button_message("Here are the available Medical tests",buttons)
        return []