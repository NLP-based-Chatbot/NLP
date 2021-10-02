from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormAction,FormValidationAction

import json
import requests
import environ


env = environ.Env()

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

        specs = json.loads()

        buttons = []

        for row in specs:
            buttons.append({"title":row.spec_name,"payload":"/inform{\"entry_id\": \""+str(row.spec_id)+"\"}"})

        dispatcher.utter_message("Select the specialization you want", buttons)

        return []

class DoctorList(Action):

    def name(self) -> Text:
        return "act_list_doctors"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        spec_id = tracker.get_slot("entry_id")

        doctors = []

        if spec_id != "" or spec_id != None:
            # select doctors has no specialization
            pass
        else:
            # select doctors with specific specialization
            pass

        buttons = []

        for row in doctors:
            buttons.append({"title": "Dr."+row.first_name+" "+row.last_name,"payload":"/"+str(row.docthash)})

        dispatcher.utter_message("List of Doctors", buttons)

        return []

class TimeRange(Action):

    def name(self) -> Text:
        return "act_show_timerange"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        docthash = tracker.get_slot("docthash")

        selecteddoctor = None

        if docthash!= "" or docthash!=None:
            pass
        else:
            #fetch info about the doctor who is selected
            pass

        timefrom = selecteddoctor.time_from
        timeto= selecteddoctor.time_to

        dispatcher.utter_message("Dr."+selecteddoctor.first_name+" "+selecteddoctor.last_name+"\
             is available from "+timefrom+" to"+timeto+" . provide a easy time for you to meet the doctor")

        return []

class PlaceAppointment(FormAction):

    def name(self) -> Text:
        return "form_place_appointment"



    