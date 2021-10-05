from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction,FormValidationAction

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

POSTURL = "http://" + CBOTBACKEND + QUERYURL

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
            buttons.append({"title":row["fields"]["spec_name"],"payload":"/inform{\"entry_id\": \""+str(row["pk"])+"\"}"})

        dispatcher.utter_button_message("Select the specialization you want", buttons)

        return []

class DoctorList(Action):

    def name(self) -> Text:
        return "act_list_doctors"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spec_id = tracker.get_slot("entry_id")
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

        response_doctor = requests.post(POSTURL,json={"function":"docbyhash","data":{"docthash":docthash}})
        doctor = response_doctor.json()[0]

        response_patient = requests.post(POSTURL,json={"function":"newpatient","data":{"username":username}})
        patient = response_patient.json()[0]

        doct_id = doctor["pk"]
        cust_id = patient["pk"]

        response = requests.post(POSTURL,json={"function":"newappoint","data":{"doct_id":doct_id , "cust_id":cust_id,"date":date,"time":time}})

        return []

class PreprocessAppointmentData(Action):

    def name(self) -> Text:
        return "act_set_appoint_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        date = tracker.get_slot("date")

        if date==None:
            reldate = tracker.get_slot("relative_date")
            if reldate=="today":
                date = str(datetime.date.today())
            elif reldate=="tomorrow":
                date = str(datetime.date.today()+datetime.timedelta(days=1))

        # response = requests.post(POSTURL,json={"function":"docbyhash","data":{"docthash":docthash}})
        # doctor = response.json()[0]


        return [SlotSet("date",date)]
                

    

    