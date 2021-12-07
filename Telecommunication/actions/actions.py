from typing import Any, Text, Dict, List
import requests
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import re
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

from rasa_sdk.events import (
  SlotSet,
  EventType
)

ALLOWD_TV_SERVICE_PROVIDERS = ["dialog", "peo"]
ALLOWD_SERVICE_PROVIDERS = ["dialog", "mobitel", "hutch", "airtel"]
PAYMENT_METHODS = ["prepaid", "postpaid"]
PACKAGE_TYPES = ["data card", "time based", "content based", "anytime", "unlimited"]
BASE_URL = "http://127.0.0.1:8000"

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

        results = requests.get(f"{BASE_URL}/telecom/packages/{service_provider}/{payment_method}/{package_type}").json()
        if(len(results)==0):
            dispatcher.utter_message(text = "Sorry, no entries found.")
        else:
            dispatcher.utter_message(json_message= {"packages":  results})

        return [SlotSet("service_provider", None), SlotSet("payment_method", None), SlotSet("package_type", None)]     

class ActionMakeComplaint(Action):

    def name(self) -> Text:
        return "make_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        title = tracker.get_slot('title')
        description = tracker.get_slot('description')
        fullname = tracker.get_slot('fullname')
        contactnum = tracker.get_slot('contactnum')
        email = tracker.get_slot('email')



        complaint_data = {
            "title" : title,
            "description" : description,
            "name" : fullname,
            "contact_no" : contactnum,
            "email" : email
        }

        results = requests.post(f"{BASE_URL}/telecom/complaint/", json=complaint_data)

        if results.ok:
            complaint = {"domain" : "telecom",
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
        dispatcher.utter_message(text=f"OK! you want details about {slot_value} plans.")
        return {"package_type": slot_value}


class ValidateComplaintForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_complaint_form"

    def validate_title(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if len(slot_value) < 5:
            dispatcher.utter_message(text=f"That's very short. Did you make a mistake?")
            return {"title": None}
        return {"title": slot_value}
    
    def validate_description(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if len(slot_value) < 10:
            dispatcher.utter_message(text=f"That's very short. Please explain little bit more")
            return {"description": None}
        return {"description": slot_value}
    
    def validate_fullname(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if len(slot_value) < 4:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled")
            return {"fullname": None}
        return {"fullname": slot_value}
    
    def validate_contactnum(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if not slot_value.isnumeric() or len(slot_value) < 10:
            dispatcher.utter_message(text=f"This is not a valid phone number")
            return {"contactnum": None}
        return {"contactnum": slot_value}
        
    def validate_email(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if not re.fullmatch(regex, slot_value):
            dispatcher.utter_message(text=f"This is not a valid email address")
            return {"email": None}
        return {"email": slot_value}

# Broadband details actions 
class ActionNewBroadbandConnection(Action):

    def name(self) -> Text:
        return "get_new_broadband_connection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/broadband/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

# Genaral details actions
class ActionNewConnection(Action):

    def name(self) -> Text:
        return "get_new_connection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        service_provider = tracker.get_slot('service_provider').lower()
        payment_method = tracker.get_slot('payment_method').lower()

        results = requests.get(f"{BASE_URL}/telecom/details/new_connection/{service_provider}/{payment_method}").json()

        if(results == None):
            dispatcher.utter_message(text = "Sorry, no entries found.")
        else:
            dispatcher.utter_message(text = results[0]['description'])
            if results[0]['url'] != "none":
                dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
 
        return [SlotSet("service_provider", None), SlotSet("payment_method", None)]     




class ValidateNewConnectionForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_new_connection_form"

    def validate_service_provider(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if slot_value.lower() not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text=f"We can only give details about Dialog, Mobitel, Hutch and Airtel.")
            return {"service_provider": None}
        dispatcher.utter_message(text=f"OK! you need a {slot_value} connection.")
        return {"service_provider": slot_value}
    
    def validate_payment_method(self, 
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        if slot_value.lower() not in PAYMENT_METHODS:
            dispatcher.utter_message(text=f"We can only give details about Prepaid and Postpaid plans")
            return {"payment_method": None}
        dispatcher.utter_message(text=f"OK! you prefer a {slot_value} plan.")
        return {"payment_method": slot_value}


class ActionChangePlan(Action):

    def name(self) -> Text:
        return "get_change_plan_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/change_plan/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

class ActionGetLoan(Action):

    def name(self) -> Text:
        return "get_loan_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/loan/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

class ActionCheckBalance(Action):

    def name(self) -> Text:
        return "get_check_balance_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/check_balance/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

class ActionSimLost(Action):

    def name(self) -> Text:
        return "get_sim_lost_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/sim_lost/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     


class ActionRechargeDetails(Action):

    def name(self) -> Text:
        return "get_recharge_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/recharge/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

class ActionSignalLostDetails(Action):

    def name(self) -> Text:
        return "get_signal_lost_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/signal_lost/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

class ActionCoverageDetails(Action):

    def name(self) -> Text:
        return "get_coverage_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('service_provider').lower()

        #simple validation
        if provider not in ALLOWD_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about service providers Dialog, Mobitel, Hutch and Airtel")
            return [SlotSet("service_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/coverage/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"See coverage map", "url": results[0]['url']}})
        return [SlotSet("service_provider", None)]     

# Television

class ActionTvConnectionDetails(Action):

    def name(self) -> Text:
        return "get_tv_connection_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('tv_provider').lower()

        #simple validation
        if provider not in ALLOWD_TV_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about Dialog TV and Peo TV")
            return [SlotSet("tv_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/tv/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = results[0]['description'])
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("tv_provider", None)]   

class ActionCheckTvBillDetails(Action):

    def name(self) -> Text:
        return "get_tv_check_bill_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('tv_provider').lower()

        #simple validation
        if provider not in ALLOWD_TV_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about Dialog TV and Peo TV")
            return [SlotSet("tv_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/tv_check_bill/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = f"{results[0]['description']}")
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("tv_provider", None)]   

class ActionTvPackageDetails(Action):

    def name(self) -> Text:
        return "get_tv_package_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        provider = tracker.get_slot('tv_provider').lower()

        #simple validation
        if provider not in ALLOWD_TV_SERVICE_PROVIDERS:
            dispatcher.utter_message(text = "Sorry, We can only provide details about Dialog TV and Peo TV")
            return [SlotSet("tv_provider", None)] 
        else:
            results = requests.get(f"{BASE_URL}/telecom/details/tv_packages/{provider}/none").json()
            if(results == None):
                dispatcher.utter_message(text = "Sorry, no entries found.")
            else:
                dispatcher.utter_message(text = f"{results[0]['description']}")
                if results[0]['url'] != "none":
                    dispatcher.utter_message(json_message={"button" : {"title":"More details", "url": results[0]['url']}})
        return [SlotSet("tv_provider", None)]   