from sentence_comparison import similarity_score

def check_atribute(classifcation_response, custom_dict, flag):
    response1 = classifcation_response["response1"]
    missing_key = ["firstName" , "lastName", "address", "phone", "city", "state", "postalCode", "country" ]
    missing_key_dict= {
         "firstName": "First Name",
         "lastName" : "Last Name",
         "phone" : "Phone number",
         "address":"Street Address",
         "city" :"City",
         "state" : "State",
         "postalCode" : "Postal code",
         "country" : "Country",
         

    }
    question_key = ""
    compulsory_attribute = ["address", "city", "state", "postalCode", "country" ]
    no_of_mis =0
    no_of_compulsory = 0
    for key, values in custom_dict.items():
        if values =="" and key in missing_key:
            question_key = question_key + " " + missing_key_dict[key] + ","
            no_of_mis +=1
    for key, values in custom_dict.items():
        if values =="" and key in compulsory_attribute:
            no_of_compulsory +=1
             
    print("custom_dict....................",custom_dict)
    if "updated" in  response1:  
        pass
    else:
        # if similarity_score(response1) > 0.8:
        #     pass
        if similarity_score(response1) > 0.8:
            pass
        
        elif custom_dict["firstName"] =="" and custom_dict["lastName"] =="":
            classifcation_response["response1"] = f"Provide the full name of {flag}"

        elif custom_dict["firstName"] !="" and custom_dict["lastName"] =="":
            classifcation_response["response1"] = f"Provide the last name of {flag}"
    
        elif custom_dict["firstName"] =="" and custom_dict["lastName"] !="":
            classifcation_response["response1"] = f"Provide the first name of {flag}"

        elif no_of_mis > 4 and no_of_compulsory > 4:
            classifcation_response["response1"] = f"Provide the complete address of {flag}"
        
        elif custom_dict["address"] =="":
            classifcation_response["response1"] = f"Provide the {flag} address"
        
        elif custom_dict["city"] =="":
            classifcation_response["response1"] = f"Provide the {flag} city"

        elif custom_dict["state"] =="":
            classifcation_response["response1"] = f"Provide the {flag} state"

        elif custom_dict["postalCode"] =="":
            classifcation_response["response1"] = f"Provide the {flag} postal code"

        elif custom_dict["country"] =="":
            classifcation_response["response1"] = f"Provide the {flag} country"
        
        elif custom_dict["phone"] =="":
            classifcation_response["response1"] = f"Provide the {flag} phone number"

        elif no_of_mis==0:
            pass    

        else :
            question_prompt = f"Provide {flag}'s" +  question_key[:-1] + "."
            print("question_prompt....................",question_prompt)
            classifcation_response["response1"] = question_prompt



# from sentence_comparison import similarity_score
# import re

# def extract_updated_sentences(text):
#     # Regular expression to match sentences with the word 'updated'
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split by sentences
#     updated_sentences = [sentence for sentence in sentences if 'updated' in sentence.lower()]
    
#     print("updated_sentences.............",updated_sentences)
#      # Filter sentences containing 'updated'
#     return updated_sentences





# def check_atribute(classifcation_response, custom_dict, flag):
#     response1 = classifcation_response["response1"]
#     missing_key = ["firstName" , "lastName", "address", "phone", "city", "state", "postalCode", "country" ]
#     missing_key_dict= {
#          "firstName": "First Name",
#          "lastName" : "Last Name",
#          "phone" : "Phone number",
#          "address":"Street Address",
#          "city" :"City",
#          "state" : "State",
#          "postalCode" : "Postal code",
#          "country" : "Country",
         

#     }
#     print("missing_key_dict.........",missing_key_dict)
#     # Extract sentences containing the word 'updated'
#     question_key = ""
#     compulsory_attribute = ["address", "city", "state", "postalCode", "country" ]
#     no_of_mis =0
#     no_of_compulsory = 0
#     for key, values in custom_dict.items():
#         if values =="" and key in missing_key:
#             question_key = question_key + " " + missing_key_dict[key] + ","
#             no_of_mis +=1
#     for key, values in custom_dict.items():
#         if values =="" and key in compulsory_attribute:
#             no_of_compulsory +=1
#     updated_sentences = extract_updated_sentences(response1)
#     if len(updated_sentences)>0:
#           text = " ".join(updated_sentences) + " "
#           text = re.sub(r'(\d)(?=\.)', r'\1 ', text)
         
#     else:
#           text="" 
#     print("custom_dict....................",custom_dict)
#     if similarity_score(response1) > 0.8:
#          pass
    
#     elif custom_dict["firstName"] =="" and custom_dict["lastName"] =="":
#          classifcation_response["response1"] = text + f"Provide the full name of {flag}"

#     elif custom_dict["firstName"] !="" and custom_dict["lastName"] =="":
#          classifcation_response["response1"] = text + f"Provide the last name of {flag}"
  
#     elif custom_dict["firstName"] =="" and custom_dict["lastName"] !="":
#          classifcation_response["response1"] = text + f"Provide the first name of {flag}"

#     elif no_of_mis > 4 and no_of_compulsory > 4:
#         classifcation_response["response1"] = text + " " + f"Provide the complete address of {flag}"

        
#     elif no_of_mis==0:
#             pass

#     else :
#         question_prompt = text + " " + f"Provide {flag}'s" +  question_key[:-1] + "."
#         print("question_prompt....................",question_prompt)
#         classifcation_response["response1"] = question_prompt