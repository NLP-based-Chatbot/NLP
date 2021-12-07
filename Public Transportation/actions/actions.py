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

# URL of the backend API
base_url = '127.0.0.1'

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

    slot_list = []
    location_depature = tracker.get_slot('location_departure')
    location_destination = tracker.get_slot('location_destination')
    travelling_mode = tracker.get_slot('travelling_mode')

    # slot check for nullity and making them null
    if location_depature:
      slot_list.append(SlotSet("location_departure", None)) 

    if location_destination:
      slot_list.append(SlotSet("location_destination", None)) 

    if travelling_mode:
      slot_list.append(SlotSet("available_bookings", None))   

    return slot_list  


class SlotResetSelection(Action):
  """Resets selection slots"""

  def name(self):
    return "action_reset_selection_slots"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    slot_list = []
    selection = tracker.get_slot('selection')
    seats = tracker.get_slot('seats')
    username = tracker.get_slot('username')

    # slot check for nullity and making them null
    if selection:
      slot_list.append(SlotSet("selection", None)) 

    if seats:
      slot_list.append(SlotSet("seats", None)) 

    if username:
      slot_list.append(SlotSet("username", None))   

    return slot_list  

class SlotsResetOffice(Action):
  """Resets office related slots"""

  def name(self):
    return "action_reset_office_slots"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    slot_list = []
    name = tracker.get_slot('office_name')
    address = tracker.get_slot('office_address')
    mode = tracker.get_slot('travelling_mode')

    # slot check for nullity and making them null
    if name:
      slot_list.append(SlotSet("office_name", None)) 

    if address:
      slot_list.append(SlotSet("office_address", None))  

    if mode:
      slot_list.append(SlotSet("travelling_mode", None))  

    return slot_list      

class SlotResetComplaint(Action):
  """Reset complaint slots"""

  def name(self):

    return "action_reset_complaint_slots"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:    

    slot_list = []
    # get current slot values
    title = tracker.get_slot('complaint_title')
    description = tracker.get_slot('complaint_description')
    vehical_number = tracker.get_slot('vehical_number')
    driver_id = tracker.get_slot('driver_id')
    conductor_id = tracker.get_slot('conductor_id')

    if title:
      slot_list.append(SlotSet("complaint_title", None))

    if description:
      slot_list.append(SlotSet("complaint_description", None)) 

    if vehical_number:
      slot_list.append(SlotSet("vehical_number", None))  

    if driver_id:
      slot_list.append(SlotSet("driver_id", None))

    if conductor_id:
      slot_list.append(SlotSet("condutor_id", None))    

    return slot_list            

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
      method = method.lower()

      results = requests.get(f"http://{base_url}:8000/transport/schedule/{method}/{departure}/{destination}").json()
      if not results:
        dispatcher.utter_message(text = f"There are currently no {method} schedules available from {departure} to {destination}")
      else:
        count = 0
        for result in results:
          count += 1
          dispatcher.utter_message(text = f"{count}. Vehical Number: {result['vehical_number']} -> Departure: {result['dep_time']} -> Arrival: {result['des_time']}")

class ActionBooking(Action):

  def name(self) -> Text:

    return "action_get_booking"

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
      method = method.lower()

      results = requests.get(f"http://{base_url}:8000/transport/schedule/{method}/{departure}/{destination}").json()
      if not results:
        dispatcher.utter_message(text = f"There are currently no {method} bookings availble from {departure} to {destination}")
      else:
        for result in results:
          if result['booking_available'] == True:
            dispatcher.utter_message(text = f"Trip ID: {result['trip_id']} -> Vehical Number: {result['vehical_number']} -> Departure: {result['dep_time']} -> Available Seats: {result['seats_available']}")

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

class MakeBooking(Action):
  """Make the booking"""

  def name(self):
    return "action_make_booking"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    trip_id = tracker.get_slot('selection')
    seats = tracker.get_slot('seats')
    username = tracker.get_slot('username')

    booking_data = {
      "trip_id": int(trip_id),
      "username": username,
      "seats": int(username)
    }

    results = requests.post(f"http://{base_url}:8000/transport/booking", json=booking_data)

    if results.ok:
      dispatcher.utter_message(text="You have succefully made the booking")
    else:
      dispatcher.utter_message(text="Something went wrong") 

    return [SlotSet("selection", None), SlotSet("seats", None), SlotSet("username", None)]   


class FindOffice(Action):
  """Find an office"""

  def name(self):
    return "action_find_office"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    name = tracker.get_slot('office_name')
    address = tracker.get_slot('office_address')
    mode = tracker.get_slot('travelling_mode')

    results = requests.get(f"http://{base_url}:8000/transport/office/{mode}/{name}/{address}").json()

    if not results :
      dispatcher.utter_message(text=f"Sorry, no entries found under {mode} {name} in {address}")
    else:
      for result in results:
         dispatcher.utter_message(text=f"Office Name: {mode} {name} - {address}")
         dispatcher.utter_message(text=f"Contact Number: {result['contact_number']}, Email: {result['email']}")

class AddComplaint(Action):
  """Add a complaint"""

  def name(self) -> Text:
    return "action_make_complaint"

  def run(
    self,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
  ) -> List[EventType]:

    title = tracker.get_slot('complaint_title')
    description = tracker.get_slot('complaint_description')
    vehical_number = tracker.get_slot('vehical_number')
    driver_id = tracker.get_slot('driver_id')
    conductor_id = tracker.get_slot('conductor_id')

    if driver_id == "0":
      driver_id = None

    if conductor_id == "0":
      conductor_id = None  

    complaint_data = {
      "type_id": 1,
      "title": title,
      "description": description,
      "vehical_number": vehical_number,
      "driver_id": driver_id,
      "conductor_id" : conductor_id
    }

    results = requests.post(f"http://{base_url}:8000/transport/complaint", json=complaint_data)

    if results.ok:
      complaint = {
        "domain": "transport",
        "type": "bus",
        "title": title,
        "description": description,
        "vehical_number": vehical_number,
        "driver_id": driver_id,
        "conductor_id" : conductor_id
      }
      dispatcher.utter_message(text = "You have succesfully made a complaint")
      dispatcher.utter_message(json_message = {"complaint":  complaint})  
    else:
      dispatcher.utter_message(text="Sorry, Complainet wasn't placed because of an error")


