from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.events import (
  SlotSet,
  EventType
)

ALLOWD_SERVICE_PROVIDERS = ["dialog", "mobitel", "hutch", "sltmobitel", "airtel", "slt"]
PAYMENT_METHODS = ["prepaid", "postpaid"]
PACKAGE_TYPES = ["data-card", "time-based", "content-based", "anytime", "unlimited"]

class ActionPackageDetails(Action):

    def name(self) -> Text:
        return "get_package_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        service_provider = tracker.get_slot('service_provider')
        payment_method = tracker.get_slot('payment_method')
        package_type = tracker.get_slot('package_type')

        service_provider = service_provider.lower()
        payment_method = payment_method.lower()
        package_type = package_type.lower()

        results = requests.get(f"http://127.0.0.1:8000/packages/{service_provider}/{payment_method}/{package_type}").json()
        if(results == None):
            dispatcher.utter_message(text = "Sorry, no entries found.")
        else:
            for result in results:
                dispatcher.utter_message(text = f"Package name: {result['package_name']} | Rs. {result['value']} | Description: {result['description']} | How to Activate: {result['activation_method']}")

        return [SlotSet("service_provider", None), SlotSet("payment_method", None), SlotSet("package_type", None)]     


class ValidateDataPackageForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_data_package_form"

    def validate_service_provider(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if slot_value.lower() not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text=f"We can only give details about Dialog, Mobitel, Hutch and Airtel.")
            return {"service_provider": None}
        dispatcher.utter_message(text=f"OK! your provider is {slot_value}.")
        return {"service_provider": slot_value}
    
    def validate_payment_method(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if slot_value.lower() not in PAYMENT_METHODS:
            dispatcher.utter_message(text=f"We can only give details about Prepaid and Postpaid plans")
            return {"payment_method": None}
        dispatcher.utter_message(text=f"OK! you want details about {slot_value} plans.")
        return {"payment_method": slot_value}
    
    def validate_package_type(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if slot_value.lower() not in PACKAGE_TYPES:
            dispatcher.utter_message(text=f"We can only give details about Data-card, time-based, content-based, anytime and unlimited plans.")
            return {"package_type": None}
        dispatcher.utter_message(text=f"OK! you want details about {slot_value} plans.")
        return {"package_type": slot_value}




class SlotResetTravel(Action):
  """Resets the slots related to transportation"""

  def name(self):

    return "action_reset_transport_slots"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    return [SlotSet("location_departure", None), SlotSet("location_destination", None), SlotSet("travelling_mode", None)]  

class ActionSchedule(Action):
  """Retrive transportation schedule"""

  def name(self):

    return "action_get_schedule"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:
    departure = tracker.get_slot('location_departure')
    destination = tracker.get_slot('location_destination')
    method = tracker.get_slot('travelling_mode')

    if destination and departure and method:
      departure = departure.lower()
      destination = destination.lower()

      results = requests.get(f"http://127.0.0.1:8000/transport/schedule/{method}/{departure}/{destination}").json()
      if(results == None):
        dispatcher.utter_message(text = "Sorry, no entries found.")
      else:
        for result in results:
           dispatcher.utter_message(text = f"Vehical Number: {result['vehical_number']} -> Departure: {result['dep_time']} -> Arrival: {result['des_time']}")

    return [SlotSet("location_departure", None), SlotSet("location_destination", None), SlotSet("travelling_mode", None)]     

class ActionTriggerResponseSelector(Action):
  """Retrival Action Finder"""

  def name(self) -> Text:

    return "action_trigger_response_selector"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:
    retrieval_intent = tracker.get_slot("retrieval_intent")
    if retrieval_intent:
      dispatcher.utter_message(template=f"utter_{retrieval_intent}")

    return [SlotSet("retrieval_intent", None)]  

