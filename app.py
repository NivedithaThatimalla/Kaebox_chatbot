from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
# from openai import AsyncOpenAI
from openai import OpenAI 
import time
from fastapi.responses import StreamingResponse, JSONResponse
import json
from datetime import datetime
from uuid import uuid4

import copy
from test import get_flag_key, map_flag_key, flag_json, key_flag
from prompt import PROMPT_TEMPLATE, GUEST_PROMPT_TEMPLATE
from generate_json import  sender_prompt,pickup_prompt,receiver_prompt,package_information_prompt,package_dimensions_prompt,shipping_prompt,num_of_packages_prompt,terms_and_conditions_prompt
from external_apis import insurance_quote,getBeforePickupImage,uploadBeforePickupImage,sharedPayment
from utils import extract_options,extract_package_number, generate_collected_data,process_sentence,replace_encoded_values
from models import generate_gpt_response,get_details,get_vector_db_context
from json_templates import generate_sender_json,sender_json,package_details_json ,receiver_json,num_package_details_json
from collected_data import refined_consignment_details
# FastAPI app
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


app = FastAPI()

# from sentence_comparison import similarity_score
# from cross_check import check_atribute


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set OpenAI API Key
OPENAI_KEY = config.get('openai', 'api_key')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_KEY))
# openai.api_key = OPENAI_KEY``


conversation_context = {}
conversation_context_cache = {}
navigation_cache = {}

@app.get("/")
async def read_root():
    return JSONResponse({"response":"Welcome to Kaebox Chatbot!"})

@app.post("/converse")
async def converse(request: Request):
    start_time = time.time()

    # Get user_id from headers and use it for individual session
    user_id = request.headers.get('Userid')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")


    global conversation_context,sender_json, isSubmit, package_details_json, package_number,receiver_number,flag_json, key_flag, total,parcelShipping
    if 'receiver_number' not in globals():
        receiver_number = "none"
    isSubmit = False
    insurance_data = {}
    auth_token = request.headers.get('Authorization')

     # Initialize user's session context and consignment details
    if auth_token not in conversation_context_cache:
        conversation_context_cache[auth_token] = {}

    conversation_context = conversation_context_cache[auth_token]
    
    body = await request.json()
    user_message = body.get('message', '')
    user_details = body.get('user', '')
    consignment_update = body.get('consignment_update','')

    consignment_details = body.get('consignment', '')
    
    consignment_details["sendingUserId"] = user_id

    if "isSubmit" not in consignment_details:
        consignment_details["isSubmit"] = False

    if "package_number" not in consignment_details:
        consignment_details["package_number"] = None
    
    latest_consignment_details = copy.copy(consignment_details)
    collected_data, empty_fields = generate_collected_data(consignment_details)
    Updated_collected_data=refined_consignment_details(consignment_details)
    print("before Updated_collected_data",Updated_collected_data)
    
    Updated_collected_data = json.loads(Updated_collected_data)
    Updated_collected_data=replace_encoded_values(Updated_collected_data)
    print("empty fields", empty_fields)
    print("Updated_collected_data",Updated_collected_data)
    start_time = time.time()
    context = await get_vector_db_context(user_message)
    print("context...", context)
    print(f"context time:{time.time()-start_time:.4f}seconds")

    if user_message.lower()=="i want to send" and (isinstance(user_details, dict) or user_details):
        sender_json = generate_sender_json(user_details)
        # print("sender_json..............",sender_json)
        consignment_details["sender"] = sender_json
        consignment_details["pickup"] = sender_json
        if "id" in latest_consignment_details["sender"]:
            sender_id = latest_consignment_details["sender"]["id"]
            consignment_details['sender']["id"] = sender_id
        else:
            pass
        
        if "id" in latest_consignment_details["pickup"]:
            pickup_id = latest_consignment_details["pickup"]["id"]
            consignment_details['pickup']["id"] = pickup_id
        else:
            pass
        
        sender_details_str = json.dumps(sender_json, indent=4)
        # print("sender_details_str........................",sender_details_str)
        # prompt = PROMPT_TEMPLATE.replace("{sender_details}",sender_details_str).replace("{collected_data}", json.dumps(collected_data))
        prompt = PROMPT_TEMPLATE.replace("{sender_details}",sender_details_str).replace("{collected_data}", json.dumps(Updated_collected_data))

        if 'conversation' not in conversation_context:
            conversation_context['conversation'] = [{"role": "system", "content": prompt}]
            print("initial prompt..........",conversation_context['conversation'])
            if len(conversation_context['conversation'])==1:
                conversation_context['conversation'].append({"role": "system", "content": "conversation starts now.."})
        conversation_context['conversation'].append({"role": "user", "content": user_message})
        initial_response = await generate_gpt_response(conversation_context['conversation'])
        # if "(yes/no)".lower() in initial_response.lower():
        #     initial_response_1=initial_response
        #     initial_response_1=initial_response_1.replace("(yes/no)","")
        conversation_context['conversation'].append({"role": "assistant", "content": initial_response})
        
        clean_response,labels,options = extract_options(initial_response)
        if "pickup address" in initial_response.lower() and " same as" in initial_response.lower():
            isSubmit = True
        
        return JSONResponse({"conversation": consignment_details, "response": clean_response, "submit_flag": isSubmit,"options":options,"navigation":None})
    elif user_message.lower()=="i want to send" and user_details is None:
        # prompt = GUEST_PROMPT_TEMPLATE.replace("{context}", context).replace("{collected_data}", json.dumps(collected_data))
        prompt = GUEST_PROMPT_TEMPLATE.replace("{context}", context).replace("{collected_data}", json.dumps(Updated_collected_data))
        conversation_context['conversation'] = [{"role": "system", "content": prompt}]
        if len(conversation_context['conversation'])==1:
            conversation_context['conversation'].append({"role": "system", "content": "conversation starts now.."})
        initial_response = await generate_gpt_response(conversation_context['conversation'])
        conversation_context['conversation'].append({"role": "user", "content": user_message})
        conversation_context['conversation'].append({"role": "assistant", "content": initial_response})
        
        clean_response,labels,options = extract_options(initial_response)
        if "pickup address" in initial_response.lower() and "same as" in initial_response.lower():
            isSubmit = True
        return JSONResponse({"conversation": consignment_details, "response": clean_response, "submit_flag": isSubmit,"options":options,"navigation":None})
    else:
        # import pdb;pdb.set_trace()
        # Prepare conversation context
        if isinstance(user_details, dict) or user_details:
            sender_json = generate_sender_json(user_details)
            if consignment_details["isSenderSameAsPickup"]:
                consignment_details["sender"] = sender_json
                consignment_details["pickup"] = sender_json
            else:
                consignment_details["sender"] = sender_json
            if "id" in latest_consignment_details["sender"]:
                sender_id = latest_consignment_details["sender"]["id"]
                consignment_details['sender']["id"] = sender_id
            else:
                pass
            
            if "id" in latest_consignment_details["pickup"]:
                pickup_id = latest_consignment_details["pickup"]["id"]
                consignment_details['pickup']["id"] = pickup_id
            else:
                pass
            sender_details_str = json.dumps(sender_json, indent=4)
            template = PROMPT_TEMPLATE
            
        else:
            sender_details_str = None
            template = GUEST_PROMPT_TEMPLATE
            
        if 'conversation' not in conversation_context:
            conversation_context['conversation'] = [{"role": "system", "content": template}]
        # print(f"sender json time:{time.time()-start_time:.4f}seconds")

        conversation_context['conversation'].append({"role": "user", "content": user_message})
        
        if len(consignment_details["shipments"])>0:
            
            total = consignment_details["shipments"][0]["totalPackages"]
        else:
            total = 1
        
        parcelShipping="null"

        if sender_details_str:
            print("Entered into Authenticated Mode : -----")
            if len(conversation_context['conversation'])==2:
                Initial_conversation = "True"
            # conversation_context['conversation'].append({"role": "system", "content": "conversation starts now.."})
                prompt_with_context = template.replace("{context}", context).replace("{sender_details}", sender_details_str).replace("{collected_data}", json.dumps(Updated_collected_data)).replace("{emptyfields}", json.dumps(empty_fields)).replace("{total}", str(total)).replace("{parcelShipping}", parcelShipping).replace("{Initial_conversation}", Initial_conversation)
            else: 
                Initial_conversation = "False"
                prompt_with_context = template.replace("{context}", context).replace("{sender_details}", sender_details_str).replace("{collected_data}", json.dumps(Updated_collected_data)).replace("{emptyfields}", json.dumps(empty_fields)).replace("{total}", str(total)).replace("{parcelShipping}", parcelShipping).replace("{Initial_conversation}", Initial_conversation)
        
        else:
            if len(conversation_context['conversation'])==2:
                print("Entered into GUEST Mode : ------")
                sender_details_str = ""
                Initial_conversation = "True"
                prompt_with_context = template.replace("{context}", context).replace("{collected_data}", json.dumps(Updated_collected_data)).replace("{emptyfields}", json.dumps(empty_fields)).replace("{total}", str(total)).replace("{parcelShipping}", parcelShipping).replace("{Initial_conversation}", Initial_conversation)
            else:
                print("Entered into GUEST Mode : ------")
                sender_details_str = ""
                Initial_conversation = "False"
                prompt_with_context = template.replace("{context}", context).replace("{collected_data}", json.dumps(Updated_collected_data)).replace("{emptyfields}", json.dumps(empty_fields)).replace("{total}", str(total)).replace("{parcelShipping}", parcelShipping).replace("{Initial_conversation}", Initial_conversation)
    
    
        # print("prompt_with_context................",prompt_with_context)
        conversation_context['conversation'][0]["content"] = prompt_with_context
        # response_message = generate_gpt_response(conversation_context['conversation'])
        
        strtime = time.time()
        conversation_context['conversation'][0]["content"] = prompt_with_context
        conv_history=copy.deepcopy(conversation_context['conversation'])
        del conv_history[0]
 
        # Construct the GPT payload
        gpt_payload = [conversation_context['conversation'][0]] + conv_history[-20:]
        print("...........payload",gpt_payload)
        response_message = await generate_gpt_response(gpt_payload)

        # response_message = process_sentence(response_message)

        print("gpt response message.......",response_message)
        # print("gpt time in generating question response:---",time.time()-strtime)
        response_message = response_message.replace('```json','').replace('```','')
        # print(".......................................",conversation_context)

        classification_conversation = [conversation_context['conversation'][-2:]]

        print("classification_conversation.................get details",classification_conversation)
        strtime = time.time()
        classifcation_response = await get_details(response_message,classification_conversation)
        # print("classifcation_response..........................",classifcation_response)
        print("gpt time in generating question response:---",time.time()-strtime)
        classifcation_response = classifcation_response.replace('```json','').replace('```','')
        try:
            classifcation_response = json.loads(classifcation_response)
        except:
            classifcation_response = await get_details(response_message,classification_conversation)
            classifcation_response = classifcation_response.replace('```json','').replace('```','')
            classifcation_response = json.loads(classifcation_response)
        

        # if "residential" in conversation_context['conversation'][-2]["content"].lower() and "address" in conversation_context['conversation'][-2]["content"].lower() and "recipient" in conversation_context['conversation'][-2]["content"].lower() and ("yes" in conversation_context['conversation'][-1]["content"].lower() or "no" in conversation_context['conversation'][-1]["content"].lower()):
        #     classifcation_response['response1'] = "How many packages are you planning to ship?"
        #     response_message="How many packages are you planning to ship?"
        if "go to the".lower() in response_message.lower() and "section" in response_message.lower():
            classifcation_response['response1'] = response_message.replace("[","").replace("(","")
            response_message=response_message.replace("[","")
        
        conversation_context['conversation'].append({"role": "assistant", "content": classifcation_response['response1']})
        user_assistant_only = [msg for msg in conversation_context['conversation'] if msg['role'] in ['user', 'assistant']]

        #response1 , response2, reponse3
        package_number = extract_package_number(response_message)
        print("response and package number",response_message,package_number)
        if package_number is not None:
            package_number=package_number
        else:
            package_number=0
        strtime = time.time()
        try:
            if len(consignment_details["shipments"])>0 and "Confirmed" not in consignment_details["shipments"][0]["packages"][int(package_number)-1]:
                consignment_details["shipments"][0]["packages"][int(package_number)-1]["Confirmed"] = False
        except:
            pass
        
        for key in classifcation_response['response2']:

            if key.lower() == "sender_details":
                receiver_number="none"
                print("sender details triggered")
                updated_sender_data=consignment_details["sender"]
                sender_details = await sender_prompt(conversation_context["conversation"][-4:],updated_sender_data)
                sender_details = sender_details.replace('```json','').replace('```','')
                
                try:
                    sender_details = json.loads(sender_details)
                except:
                    sender_details = await sender_prompt(conversation_context["conversation"][-4:],updated_sender_data)
                    sender_details = sender_details.replace('```json','').replace('```','')
                    sender_details = json.loads(sender_details)
                
            
                if "id" in latest_consignment_details["sender"]:
                    sender_id = latest_consignment_details["sender"]["id"]
                    consignment_details['sender'] = sender_details
                    consignment_details['sender']["id"] = sender_id
                else:
                    consignment_details['sender'] = sender_details

                if consignment_details["isSenderSameAsPickup"]:
                    if "id" in latest_consignment_details["pickup"]:
                        pickup_id = latest_consignment_details["pickup"]["id"]
                        consignment_details["pickup"] = sender_details
                        consignment_details['pickup']["id"] = pickup_id
                    else:
                        consignment_details["pickup"] = sender_details
                
                

            elif key.lower() == "pickup_details":
                
                print("consignment_details in pickup...............",consignment_details)
                receiver_number="none"
                print("Pickup address update triggered")
                pick_up_json_template = consignment_details['pickup']
                
                print(pick_up_json_template)
                boolean_var = consignment_details["isSenderSameAsPickup"]
                # var = {"isSenderSameAsPickup":boolean_var}
                pick_up_json_template["isSenderSameAsPickup"] = boolean_var
                
                pickup_details = await pickup_prompt(conversation_context['conversation'][-4:], pick_up_json_template) 
                pickup_details = pickup_details.replace('```json','').replace('```','')
                # pickup_details = pickup_details.replace('```json','').replace('```','')
                
                try:
                    pickup_details = json.loads(pickup_details)
                except:
                    pickup_details = await pickup_prompt(conversation_context['conversation'][-4:], pick_up_json_template )      
                    pickup_details = pickup_details.replace('```json','').replace('```','')
                    pickup_details = json.loads(pickup_details)

                print("pickupdetails package section ------------------ >",pickup_details)

                if "pickup" in pickup_details:
                    if "id" in latest_consignment_details["pickup"] and "id" in latest_consignment_details["sender"]:
                        pickup_id = latest_consignment_details["pickup"]["id"]
                        sender_id_pickp = latest_consignment_details["sender"]["id"]
                        # check_atribute(classifcation_response, pickup_details["pickup"], "pickup")
                        consignment_details['pickup'] = pickup_details['pickup']
                        consignment_details['pickup']["id"] = pickup_id
                        consignment_details['sender']["id"] = sender_id_pickp
                    else:                        
                        consignment_details['pickup'] = pickup_details['pickup']
                else:
                    #check_atribute(classifcation_response, pickup_details, "pickup")
                    consignment_details['pickup'] = pickup_details
                    if "id" in latest_consignment_details["sender"]:
                        sender_id_pickp = latest_consignment_details["sender"]["id"]
                        consignment_details['sender']["id"] = sender_id_pickp
                    else:
                        pass
                        
                
                
                consignment_details["isSenderSameAsPickup"] = pickup_details["isSenderSameAsPickup"]
                
                # if consignment_details["isSenderSameAsPickup"]:
                #     consignment_details["sender"] = consignment_details['pickup']


            elif key.lower() == "recipient_details":
                try:
                    receiver_number=1
                    print("Recipient details update triggered")
                    if len(consignment_details["shipments"])>0:
                        receiver_json_template = consignment_details["shipments"][0].get("receiver",{})
                    else:
                        receiver_json_template = receiver_json
                    recipient_details = await receiver_prompt(conversation_context["conversation"][-4:], receiver_json_template)
                    recipient_details = recipient_details.replace('```json','').replace('```','')
                    try:
                        recipient_details = json.loads(recipient_details)
                    except:
                        recipient_details = await receiver_prompt(conversation_context["conversation"][-4:], receiver_json_template)
                        recipient_details = recipient_details.replace('```json','').replace('```','')
                        recipient_details = json.loads(recipient_details)
                    print("recipient_details.....",recipient_details)

                    # No need to convert package_details_json to a string; it's already a valid JSON object.
                    try:
                        receiver_data = {
                            "receiver":  recipient_details["receiver"],
                            "packages": [package_details_json],  # Packages should be a list of dictionaries
                            "totalPackages": 0
                        }
                    except:
                        receiver_data = {
                        "receiver":  recipient_details,
                        "packages": [package_details_json],  # Packages should be a list of dictionaries
                        "totalPackages": 0
                    }

                    if len(consignment_details["shipments"]) == 0:
                        consignment_details["shipments"].append(receiver_data)
                    else:
                        consignment_details["shipments"][0]["receiver"].update( recipient_details["receiver"])
                    
                    # check_atribute(classifcation_response,  recipient_details["receiver"] , "recipient")

                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]

            elif key.lower() == "number_of_packages":
                # import pdb; pdb.set_trace()
                try:
                    if len(consignment_details["shipments"])==0:
                        try:
                            try:
                                receiver_data = {
                                    "receiver":  recipient_details["receiver"],
                                    "packages": [package_details_json],  # Packages should be a list of dictionaries
                                    "totalPackages": 0
                                }
                            except:
                                receiver_data = {
                                "receiver":  recipient_details,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                        except:
                            receiver_data = {
                                "receiver":  receiver_json,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                    else:
                        pass
                        
                    # no_of_package_json = {"totalPackages":consignment_details["shipments"][0]["totalPackages"]}
                    # no_of_package_json = json.dumps(no_of_package_json)
                    # print("conversation_context[conversation][-2:].......",conversation_context["conversation"][-3:-1],conversation_context["conversation"][-2:])
                    try:
                        total_shipment_json_value = consignment_details["shipments"][0]["totalPackages"] 
                        total_shipment_json = {"totalPackages":total_shipment_json_value}
                        package_details = await num_of_packages_prompt(conversation_context["conversation"][-3:-1],total_shipment_json)
                        print("total_package_details....",package_details)
                        if not isinstance(package_details,dict):
                            package_details = package_details.replace('```json','').replace('```','')      
                        package_details = json.loads(package_details)
                        print("123333333333333",package_details)
                        
                        if len(consignment_details["shipments"])>0:
                            previous_packages = latest_consignment_details["shipments"][0]["totalPackages"]
                            consignment_details["shipments"][0]["totalPackages"] = package_details["totalPackages"]
                            new_packages = consignment_details["shipments"][0]["totalPackages"]
                            diff=abs(int(previous_packages)-int(new_packages))

                            print("count diff...................",diff)

                            if previous_packages>new_packages:
                                consignment_details["shipments"][0]["packages"]=consignment_details["shipments"][0]["packages"][:(int(new_packages))]
                            elif previous_packages<new_packages:
                                if isinstance(package_details_json,list):
                                    updated_json = diff*num_package_details_json
                                else:
                                    updated_json = diff*[num_package_details_json]
                                consignment_details["shipments"][0]["packages"].extend(updated_json)
                                consignment_details["shipments"][0]["packages"]=consignment_details["shipments"][0]["packages"][:(int(new_packages))]
                            else:
                                pass

                        else:
                            response_message = "Please provide the Recipient's details."
                    except:
                        pass
                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]


            elif key.lower() == "package_information":
                try:
                    if len(consignment_details["shipments"])==0:
                        try:
                            try:
                                receiver_data = {
                                    "receiver":  recipient_details["receiver"],
                                    "packages": [package_details_json],  # Packages should be a list of dictionaries
                                    "totalPackages": 0
                                }
                            except:
                                receiver_data = {
                                "receiver":  recipient_details,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            
                            consignment_details["shipments"].append(receiver_data)
                        except:
                            receiver_data = {
                                "receiver":  receiver_json,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                    else:
                        pass
                    receiver_number=1
                    strtime = time.time()
                    print("package details update triggered...............................................")
                
                    print("package_number..................",package_number)
                    package_information_json = {"serviceTypes": consignment_details["shipments"][0]["packages"][int(package_number)-1]["serviceTypes"],"type":consignment_details["shipments"][0]["packages"][int(package_number)-1]["type"]}
                    package_details = await package_information_prompt(conversation_context["conversation"][-10:-1],package_information_json)
                    # print("package_details...................",package_details)
                    package_details = package_details.replace('```json','').replace('```','')      
                    package_details = json.loads(package_details)
                    # Assuming the "packages" key in the provided JSON wraps the list, extract it:
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["serviceTypes"] = package_details["serviceTypes"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["type"] = package_details["type"]
                
                
                    print("gpt time in tagging packages:---",time.time()-strtime)
                
                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]

            elif key.lower() == 'package_dimensions':
                # import pdb; pdb.set_trace()
                try:
                    if len(consignment_details["shipments"])==0:
                        try:
                            try:
                                receiver_data = {
                                    "receiver":  recipient_details["receiver"],
                                    "packages": [package_details_json],  # Packages should be a list of dictionaries
                                    "totalPackages": 0
                                }
                            except:
                                receiver_data = {
                                "receiver":  recipient_details,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            } 
                            consignment_details["shipments"].append(receiver_data)
                        except:
                            receiver_data = {
                                "receiver":  receiver_json,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                    else:
                        pass
                    receiver_number=1
                    strtime = time.time()
                    print("package dimensions details update triggered...............................................")
                    # import pdb; pdb.set_trace()
                    print("package_number..................",package_number)
                    package_dimensions_json = {"length": consignment_details["shipments"][0]["packages"][int(package_number)-1]["length"],"width":consignment_details["shipments"][0]["packages"][int(package_number)-1]["width"],"height":consignment_details["shipments"][0]["packages"][int(package_number)-1]["height"],"weightOunces":consignment_details["shipments"][0]["packages"][int(package_number)-1]["weightOunces"]}
                    package_details = await package_dimensions_prompt(conversation_context["conversation"][-10:-1],package_dimensions_json)
                    print("package_details...................",package_details)
                    package_details = package_details.replace('```json','').replace('```','')      
                    package_details = json.loads(package_details)
                    # Assuming the "packages" key in the provided JSON wraps the list, extract it:
                    
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["length"] = package_details["length"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["width"] = package_details["width"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["height"] = package_details["height"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["weightOunces"] = package_details["weightOunces"]
                    
                
                    print("gpt time in tagging packages:---",time.time()-strtime)

                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]

            elif key.lower() == "shipping":
                try:
                    if len(consignment_details["shipments"])==0:
                        try:
                            try:
                                receiver_data = {
                                    "receiver":  recipient_details["receiver"],
                                    "packages": [package_details_json],  # Packages should be a list of dictionaries
                                    "totalPackages": 0
                                }
                            # except UnboundLocalError:
                            #     recipient_details = {}
                            #     receiver_data = {
                                
                            # }
                            except:
                                receiver_data = {
                                "receiver":  recipient_details,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            

                            consignment_details["shipments"].append(receiver_data)
                        except:
                            receiver_data = {
                                "receiver":  receiver_json,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                    else:
                        pass
                    receiver_number=1
                    strtime = time.time()
               
                    print("package details update triggered...............................................")
                    print("package_number..................",package_number)
                    
                    shipping_json = {"indications": consignment_details["shipments"][0]["packages"][int(package_number)-1]["indications"],"deliveryInstructions":consignment_details["shipments"][0]["packages"][int(package_number)-1]["deliveryInstructions"],"insuredValue":consignment_details["shipments"][0]["packages"][int(package_number)-1]["insuredValue"]}
                    package_details = await shipping_prompt(conversation_context["conversation"][-10:-1],shipping_json)
                    print("package_details...................",package_details)
                    package_details = package_details.replace('```json','').replace('```','')       
                    package_details = json.loads(package_details)
                    # Assuming the "packages" key in the provided JSON wraps the list, extract it:
                    package_number=classifcation_response['response3']["package"]
                    # import pdb; pdb.set_trace()
                    if package_number=="none":
                        package_number=1
                    
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["indications"] = package_details["indications"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["deliveryInstructions"] = package_details["deliveryInstructions"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["insuredValue"] = package_details["insuredValue"]
                    consignment_details["shipments"][0]["packages"][int(package_number)-1]["isInsuranceEnabled"]=package_details["isInsuranceEnabled"]
                
                    if len(consignment_details["shipments"])!=0:
                        insurance_data = insurance_quote(auth_token,consignment_details,package_number)
                    try:
                        if len(consignment_details["shipments"])!=0:
                            parcelShipping=consignment_details["shipments"][0]["packages"][int(package_number)-1]["parcelShipping"]
                            if parcelShipping=="null":
                                parcelShipping=parcelShipping
                            else:
                                parcelShipping="confirmed"
                             
                    except KeyError:
                        final_cleaned_response = classifcation_response["response1"]
                        
                
                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]
            
                print("gpt time in tagging packages:---",time.time()-strtime)

            elif key.lower() == "checkout":
                try:
                    if len(consignment_details["shipments"])==0:
                        try:
                            try:
                                receiver_data = {
                                    "receiver":  recipient_details["receiver"],
                                    "packages": [package_details_json],  # Packages should be a list of dictionaries
                                    "totalPackages": 0
                                }
                            except:
                                receiver_data = {
                                "receiver":  recipient_details,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            
                            consignment_details["shipments"].append(receiver_data)
                        except:
                            receiver_data = {
                                "receiver":  receiver_json,
                                "packages": [package_details_json],  # Packages should be a list of dictionaries
                                "totalPackages": 0
                            }
                            consignment_details["shipments"].append(receiver_data)
                    else:
                        pass
                    receiver_number=1
                    strtime = time.time()
                    print("package details update triggered...............................................")
                    try:
                        if "program terms and conditions" in conversation_context["conversation"][-3]["content"].lower():
                            message=conversation_context["conversation"][-3]["content"]
                        else:
                            message="Default"
                        package_number_tandc = extract_package_number(message)
                        confirmed_json = {"Confirmed":consignment_details["shipments"][0]["packages"][int(package_number_tandc)-1]["Confirmed"]}
                        
                        print("checkout package_number..................",package_number_tandc)
                        # checkout_json = {"termsandConditions": consignment_details["termsandConditions"]}
                        package_details = await terms_and_conditions_prompt(conversation_context["conversation"][-5:-1])
                        # import pdb; pdb.set_trace()
                        print("package_details...................",package_details)
                        package_details = package_details.replace('```json','').replace('```','')    
                        package_details = json.loads(package_details)
                        # Assuming the "packages" key in the provided JSON wraps the list, extract it:
                        print("confirmed flag",consignment_details["shipments"][0]["packages"][int(package_number_tandc)-1]["Confirmed"])
                        consignment_details["shipments"][0]["packages"][int(package_number_tandc)-1]["Confirmed"] = package_details["Confirmed"]
                    except:
                        pass

                except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]
            
                print("gpt time in tagging packages:---",time.time()-strtime)
            
           
            # Insurance API Calling Snippet #
            # Insurance API Calling Snippet #
            try:
                if insurance_data and isinstance(insurance_data, dict):
                    if "insurance_details" in insurance_data and isinstance(insurance_data["insurance_details"], dict):
                        print("package number in Insurance if conditions:----",package_number)
                        consignment_details["shipments"][0]["packages"][int(package_number)-1]["insuredValue"] = insurance_data["insurance_details"].get("insuredValue", 0)
                        consignment_details["shipments"][0]["packages"][int(package_number)-1]["insuranceQuoteId"] = insurance_data["insurance_details"].get("insuranceQuoteId", "")
                        consignment_details["shipments"][0]["packages"][int(package_number)-1]["insuranceCost"] = insurance_data["insurance_details"].get("insuranceCost", 0)
                    else:
                        print("Invalid format: 'insurance_details' is missing or not a dictionary")
                else:
                    print("Invalid insurance_data format or insurance_data is empty")
            except Exception as e:
                    print("exception Error at shipping section:",e)
                    final_cleaned_response = classifcation_response["response1"]
        
        try:
            if len(consignment_details["shipments"])>0:
                if (consignment_details["shipments"][0]["packages"][0]["insuredValue"]) >0:
                    if consignment_details.get("consignmentSharedPayment","") is not None:
                        if isinstance(consignment_details.get("consignmentSharedPayment",""),list):
                            consignment_id = consignment_details.get("id")
                            shared_phone_num = consignment_details.get("consignmentSharedPayment")[0].get("sharedUserPhoneNumber")
                            sharedamount = consignment_details.get("consignmentSharedPayment")[0].get("paymentAmountForOtherUser")
                            shared_data = sharedPayment(auth_token,consignment_id,shared_phone_num,sharedamount)
                            if shared_data is not None:
                                data = shared_data.get("consignmentSharedPayment","")
                                consignment_details["consignmentSharedPayment"]=data
                            else:
                                consignment_details = consignment_details

                        elif isinstance(consignment_details.get("consignmentSharedPayment",""),dict):
                            consignment_id = consignment_details.get("id")
                            shared_phone_num = consignment_details.get("consignmentSharedPayment").get("sharedUserPhoneNumber")
                            sharedamount = consignment_details.get("consignmentSharedPayment").get("paymentAmountForOtherUser")
                            shared_data = sharedPayment(auth_token,consignment_id,shared_phone_num,sharedamount)
                            if shared_data is not None:
                                data = shared_data.get("consignmentSharedPayment","")
                                consignment_details["consignmentSharedPayment"]=data
                            else:
                                consignment_details = consignment_details
                        else:
                            pass
            else:
                pass
        except Exception as e:
            print(e)
            final_cleaned_response = classifcation_response["response1"]
       

        # print("classifciation response for response1--->",classifcation_response['response1'])
        if isinstance(classifcation_response['response1'],dict):
            cleaned_response = json.loads(classifcation_response['response1']) 
        else:
            cleaned_response = classifcation_response['response1']
        
        # cleaned_response = json.loads(classifcation_response['response1']) if isinstance(classifcation_response, dict) else classifcation_response
        if isinstance(cleaned_response,dict):
            final_response = cleaned_response.get("response1", cleaned_response)
        else:
            final_response = cleaned_response

        # Extract options and navigation data
        # clean_response,options = extract_options(final_response)
        clean_response,labels,options = extract_options(final_response)
        print("clean_response,labels,options...",clean_response,labels,options)
        # print("line number 13111111111111",conversation_context["conversation"])
       
        if "updated to" in conversation_context["conversation"][-2]['content'].lower() or "updated to" in conversation_context["conversation"][-2]['content'].lower() or " want to submit" in conversation_context["conversation"][-2]['content'].lower():
            isSubmit = True            
        
        elif "pickup address" in conversation_context["conversation"][-3]['content'].lower() and  "same as" in conversation_context["conversation"][-3]['content'].lower():
            print("entered............")
            isSubmit = True
            consignment_update= True
        elif "residential address" in conversation_context["conversation"][-2]['content'].lower() and "pickup" in conversation_context["conversation"][-2]['content'].lower() or "residential address" in conversation_context["conversation"][-3]['content'].lower() and "pickup" in conversation_context["conversation"][-3]['content'].lower():
            
            isSubmit = True

        elif "residential address" in conversation_context["conversation"][-3]['content'].lower() :

            isSubmit = True
 
        elif "residential address" in conversation_context["conversation"][-2]['content'].lower() and "recipient" in conversation_context["conversation"][-2]['content'].lower() or  "residential address" in conversation_context["conversation"][-3]['content'].lower() and "recipient" in conversation_context["conversation"][-3]['content'].lower():
            isSubmit = True
        
        elif "is the pickup address same as the sender's" in conversation_context["conversation"][-2]['content'].lower() or "is the pickup address same as the sender's" in conversation_context["conversation"][-3]['content'].lower():
            isSubmit = True

        elif "[Privacy Policy]".lower() in clean_response.lower() or "[Terms of Service]".lower() in clean_response.lower() :
            isSubmit = True
       
        elif "is the pickup address the same as the sender's" in conversation_context["conversation"][-2]['content'].lower() or "is the pickup address the same as the sender's" in conversation_context["conversation"][-3]['content'].lower():
            isSubmit = True
        
        elif "residential address" in clean_response:
            isSubmit = True
        else:
            isSubmit = False



        ## Navigation Section ##
        previous_navigation_data = {"receiver": "none", "package": "none"}
        navigating_response = classifcation_response['response3']
        if not isinstance(navigating_response,dict):
            try:
                navigating_response = json.loads(navigating_response)
            except:
                navigating_response = navigation_cache
        # Check if previous data exists; if not, initialize it
        if 'navigation' not in navigation_cache:
            navigation_cache['navigation'] = previous_navigation_data
        # Update based on current response
        if package_number==0:
            package_number="none"
        else:
            package_number=package_number
        navigation_data = {
            "navigation": {
                "receiver": receiver_number,
                "package": package_number
            }
        }
       

        if "termsandConditions" not in consignment_details:
            consignment_details["termsandConditions"] = False
        else:
            consignment_details = consignment_details
        
        if "couponCode" not in consignment_details:
            consignment_details["couponCode"] = False
        else:
            consignment_details = consignment_details
        
        if "response1" in clean_response:
            data = json.loads(clean_response)
            final_cleaned_response = data.get("response1","")
        else:
            final_cleaned_response = clean_response
        
        if "[login]" in final_cleaned_response or "[sign up]" in final_cleaned_response:
            final_cleaned_response = """Please <span style=\"color: blue; text-decoration: underline;\"><a href=\"https://app-staging.kaebox.com/login\">login</a></span> or <span style=\"color: blue; text-decoration: underline;\"><a href=\"https://app-staging.kaebox.com/signup\">Sign Up</a></span> to complete the checkout process. If you have any questions, I'm here to assist."""
        
        elif "[Privacy Policy]" in final_cleaned_response or "[Terms of Service]" in final_cleaned_response:
            final_cleaned_response = f"""For package{package_number}, by proceeding, you acknowledge that you have read and agreed to the Program Terms and Conditions. Shipping protection is provided by UPS Capital Insurance Agency, Inc. I have read and accept the <span style=\"color: blue; text-decoration: underline;\"><a href=\"https://www.kaebox.com/privacy\">Privacy Policy</a></span> and <span style=\"color: blue; text-decoration: underline;\"><a href=\"https://www.kaebox.com/privacy-1\">Terms of Service</a></span>"""
            # isSubmit = True

        else:
            pass

        print("isSubmit",isSubmit)
        # print("conversation_context.............",conversation_context['conversation'])
        return JSONResponse({"conversation": consignment_details, "response": final_cleaned_response, "submit_flag": isSubmit,"options":options,"navigation":navigation_data, "consignment_update":consignment_update})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)