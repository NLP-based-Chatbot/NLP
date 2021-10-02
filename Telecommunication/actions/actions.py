from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

ALLOWD_SERVICE_PROVIDERS = ["dialog", "mobitel", "hutch", "sltmobitel", "airtel", "slt"]

class ActionPackageDetails(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ValidateDataPackageForm(Action):

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
