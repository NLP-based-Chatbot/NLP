# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
  SlotSet,
  EventType
)

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

#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
