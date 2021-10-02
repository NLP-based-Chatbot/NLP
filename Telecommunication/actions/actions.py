from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

ALLOWD_SERVICE_PROVIDERS = ["dialog", "mobitel", "hutch", "sltmobitel", "airtel", "slt"]
PAYMENT_METHODS = ["prepaid", "postpaid"]
PACKAGE_TYPES = ["data card", "time based", "content based", "anytime", "unlimited"]

class ActionPackageDetails(Action):

    def name(self) -> Text:
        return "get_package_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

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
            dispatcher.utter_message(text=f"We can only give details about Data card, time based, content based, anytime and unlimited plans.")
            return {"package_type": None}
        dispatcher.utter_message(text=f"OK! you want details about{slot_value} plans.")
        return {"package_type": slot_value}
