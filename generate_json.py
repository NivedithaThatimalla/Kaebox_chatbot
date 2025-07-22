
import requests
import openai
import json
import time,aiohttp

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

OPENAI_KEY = config.get('openai', 'api_key')


def gpt_model(prompt,maxtokens):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [{
                "role": "user",
                "content": prompt}],
                "max_tokens": maxtokens
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()
    import json
    from datetime import datetime

    # Create a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    completion_tokens = response_json['usage']['completion_tokens']
    prompt_tokens = response_json['usage']['prompt_tokens']

    # Prepare the new entry
    new_entry = {
        "gpt4o_input_tokens": prompt_tokens,
        "gpt4o_output_tokens": completion_tokens
    }

    # Initialize or load existing data
    try:
        with open("tokens.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Add the new entry under the current timestamp
    data[timestamp] = new_entry

    # Write updated data back to the file
    with open("tokens.json", "w") as file:
        json.dump(data, file, indent=4)
    # print("response_json tokens......", response_json)
    if 'choices' in response_json:
        response_content = response_json['choices'][0]['message']['content']
    else:
        print("response_json..",response_json)
        response_content = "Unexpected response format from OpenAI API"

    return response_content

async def sender_prompt(data, jstring):

   prompt = f"""You are a highly accurate address parser tasked with extracting and validating address information from user input. Follow these instructions strictly:
   ### Current Data
   - JSON: {jstring}
   - User Input: {data}

   ### Instructions:
   - Before map to respective field in {jstring} thoroughly check which section it refers only tag that data releted to "sender"
   - Analyze the provided input and match values to their corresponding keys in the JSON.
   - Update only the sender section of the JSON. Do not modify unrelated sections (e.g., pickup or recipient).
   - Always return a valid JSON object with updated values, preserving existing values for fields not updated.
   - Avoid assumptions. If any field is invalid or not provided, retain the existing value in the JSON.
   - Strictly avoid adding extra words, comments, or unnecessary details to the JSON object.

   ### Validation Rules:
   **Name (firstName, lastName):**
   - Split full names into firstName and lastName.
   - Remove titles (e.g., Mr., Dr.) and handle suffixes (e.g., Jr., Sr.).

   **Address:**
   - Standardize street suffixes (e.g., Street→St., Avenue→Ave.).
   - Validate length: max 100 characters for address, 50 for address2.
   - Handle PO Boxes, unit numbers, and suites.

   **Location (city, state, postalCode, country):**
   - Validate city based on state and country.
   - Convert state names to 2-letter codes.
   - Convert country names to ISO-2 codes (e.g., United States→US , Inida->IN..etc).
   - Validate postal code format according to the country. Strictly do not tag the postal code if it is not valid to that Country.

   **Contact (phone):**
   - Ensure only digits, allowing international formats with country codes.
   - Remove formatting characters (e.g., spaces, hyphens).
   - Validate the phone number which is belongs to that given country or not and accept if given phone numbers related to given Country in {jstring} and map to phone number.Strictly tag 10 digits only. 

   **Flags:**
   - Set `isMilitaryBox` to true if all conditions are met:
      - City is APO, DPO, or FPO.
      - State is AA, AE, or AP.
      - ZIP matches military patterns:
         - AA: 340xx
         - AE: 090xx-099xx
         - AP: 962xx-966xx
   Otherwise, set `isMilitaryBox` to false.
   - Validate `isResidential` as true/false based on user-provided data.

   ### Output Rules:
   - Always return a valid JSON object.
   - Do not add explanations or comments.
   - Ensure only the sender section is updated and other sections remain unchanged.

   ### Expected JSON Structure:
   {{
      "name": "",
      "firstName": "",
      "lastName": "",
      "company": "",
      "phone": "",
      "address": "",
      "address2": "",
      "city": "",
      "state": "",
      "postalCode": "",
      "country": "",
      "isResidential": false,
      "isMilitaryBox": false,
      "latitude": 0.0,
      "longitude": 0.0,
      "isDeleted": false,
      "isInternational": false,
      "fullAddress": ""
   }}

   ### Processing Steps:
   1. Extract relevant sender details from the user input.
   2. Validate each extracted field according to the rules.
   3. Update the corresponding fields in the JSON.
   4. Preserve existing values for fields not updated.
   5. Return the updated JSON object with only the sender section modified.

   Extract and validate the relevant data from the provided user input: {data}.
   """

   sender_data = gpt_model(prompt, maxtokens=300)

  
   return sender_data


# async def pickup_prompt(data,jstring):
#     start_time = time.time()
#     prompt = f"""You are tasked with extracting relevant keys from the provided pickup data in {data} and {jstring} and updating the corresponding fields missing fields in the mentioned JSON {jstring}. if you don't find any details to tag just return input json.
#                  Note: Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging irrelevant or extraneous information such as pronouns, conjunctions, and prepositions. Always focus on contextually relevant details.
#                     Extract relevant details from general paragraphs or casual sentences provided by the user. Understand the intent and fetches only the required data accurately, regardless of how the input is phrased.
#                     Address Validation:
#                     Validate the address components (e.g., city, state, postal code) before tagging them.
#                     Ensure that cities, states, and countries are correctly identified and mapped to their appropriate fields.
#                     Do not assign details incorrectly (e.g., assigning a city name to the postal code field).
#                     Extract the first name and last name accurately from the data provided, and assign each to their respective fields.
#                     Ensure phone numbers and postal codes are not confused:
#                         Phone Number: Should be a 10-digit number.
#                         Postal Code: Should be 5 to 6 characters or digits in length.
#                     If the user provides the country name in full (e.g., "United States") or in short form (e.g., "USA"), please convert it to the two-letter country code (e.g., "US") and tag it to the country field.
#                     Update the "isResidential" flag based on user response.
#                     Always maintain contextual accuracy when extracting and mapping address details.
#                     - Ensure that the data is accurately mapped to the 'pickup details' key in the JSON.
#                     - The name field should be generated by concatenating the firstName and lastName from the provided data.
#                     - Always cross check the information that tagged in pickup details below json {jstring} and ask for remaining empty fields.
#                     - If a person's name is found in the provided user message, intelligently tag it to the appropriate key: either "firstName" or "lastName"
#                     - consider user question also while updating the json whether user wants to update to which section.
#                     - Never tag sender and recipient section details to this section. If irrelevant details found Just return input json.
#                       < example while bot seeking sender's details but user wants to update his recipient details , it should allow and it should be tagged to recipient details not to sender's details>
#                     - Set "isMilitaryBox": "true" if:
#                             City: APO, DPO, or FPO (not actual destination or MPO).
#                             State: AA, AE, or AP (not actual destination).
#                             ZIP Code:
#                             AA: starts with 340
#                             AE: starts with 090-099
#                             AP: starts with 962-966
#                         Otherwise, set "isMilitaryBox": "false".

#                     The updated JSON file should be returned as a valid JSON object with no additional text or comments. Do not provide any explanations—just return the extracted JSON only.

#                     The output must strictly follow the format below:

                

#                     {{
#                     "pickup" : {{
#                         "name": "",
#                         "firstName": "",
#                         "lastName": "",
#                         "company": "",
#                         "phone": "",
#                         "address": "",
#                         "address2": "",
#                         "city": "",
#                         "state": "",
#                         "postalCode": "",
#                         "country": "",
#                         "isResidential": "false",
#                         "isMilitaryBox": "false",
#                         "latitude": 0.0,
#                         "longitude": 0.0,
#                         "isDeleted": "false",
#                         "isInternational": "false",
#                         "fullAddress": ""
#                     }},
#                     "isSenderSameAsPickup": false,
#                     "isSubmit":false
        
#                     }}

#                     #Additional instructions
#                     Note: convert True/False into small letters as true/false if exists.
#                     Note: if pickup address same as sender's address copy same senders address to pickup address and make the value of "isSenderSameAsPickup" as true.
#                     Note : if all pickup details are collected in {jstring} make "isSubmit" option as "true".
#                     Note: if pickup address not same as sender's address  address make "isSenderSameAsPickup" as false and return above empty json template as it is.
#                     Important Note: Never change "isSenderSameAsPickup" value unless user mentioned to change it in the conversation.
#                     Note: return valid json output ,without adding extra information or comments. Boolean values and null should be returned without any inverted commas.
#                     ** Note ** :  Strictly do not add any comments or extra information to Json file. Just return valid json after tagging the values.         
#                     [SCRATCHPAD]   
#                     Output Assembly:
#                     - Verify JSON format
#                     - Return result    
#                     """
#     pickup_data = gpt_model(prompt,maxtokens=300)
#     end_time = time.time()
#     print(f"generate_pickup_json took {end_time - start_time:.4f} seconds")
#     return pickup_data

# async def pickup_prompt(data,jstring):
#     start_time = time.time()
#     prompt = f"""You are tasked with extracting relevant keys from the provided pickup data in {data} and {jstring} and updating the corresponding fields missing fields in the mentioned JSON {jstring}. if you don't find any details to tag just return input json.
#                  Note: Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging irrelevant or extraneous information such as pronouns, conjunctions, and prepositions. Always focus on contextually relevant details.
#                     Extract relevant details from general paragraphs or casual sentences provided by the user. Understand the intent and fetches only the required data accurately, regardless of how the input is phrased.
#                     Address Validation:
#                     Validate the address components (e.g., city, state, postal code) before tagging them.
#                     Ensure that cities, states, and countries are correctly identified and mapped to their appropriate fields.
#                     Do not assign details incorrectly (e.g., assigning a city name to the postal code field).
#                     Extract the first name and last name accurately from the data provided, and assign each to their respective fields.
#                     Ensure phone numbers and postal codes are not confused:
#                         Phone Number: Should be a 10-digit number.
#                         Postal Code: Should be 5 to 6 characters or digits in length.
#                     If the user provides the country name in full (e.g., "United States") or in short form (e.g., "USA"), please convert it to the two-letter country code (e.g., "US") and tag it to the country field.
#                     Update the "isResidential" flag based on user response.
#                     Always maintain contextual accuracy when extracting and mapping address details.
#                     - Ensure that the data is accurately mapped to the 'pickup details' key in the JSON.
#                     - The name field should be generated by concatenating the firstName and lastName from the provided data.
#                     - Always cross check the information that tagged in pickup details below json {jstring} and ask for remaining empty fields.
#                     - If a person's name is found in the provided user message, intelligently tag it to the appropriate key: either "firstName" or "lastName"
#                     - consider user question also while updating the json whether user wants to update to which section.
#                     - Never tag sender and recipient section details to this section. If irrelevant details found Just return input json.
#                       < example while bot seeking sender's details but user wants to update his recipient details , it should allow and it should be tagged to recipient details not to sender's details>
#                     - Set "isMilitaryBox": "true" if:
#                             City: APO, DPO, or FPO (not actual destination or MPO).
#                             State: AA, AE, or AP (not actual destination).
#                             ZIP Code:
#                             AA: starts with 340
#                             AE: starts with 090-099
#                             AP: starts with 962-966
#                         Otherwise, set "isMilitaryBox": "false".

#                     The updated JSON file should be returned as a valid JSON object with no additional text or comments. Do not provide any explanations—just return the extracted JSON only.

#                     The output must strictly follow the format below:

                

#                     {{
#                     "pickup" : {{
#                         "name": "",
#                         "firstName": "",
#                         "lastName": "",
#                         "company": "",
#                         "phone": "",
#                         "address": "",
#                         "address2": "",
#                         "city": "",
#                         "state": "",
#                         "postalCode": "",
#                         "country": "",
#                         "isResidential": "false",
#                         "isMilitaryBox": "false",
#                         "latitude": 0.0,
#                         "longitude": 0.0,
#                         "isDeleted": "false",
#                         "isInternational": "false",
#                         "fullAddress": ""
#                     }},
#                     "isSenderSameAsPickup": false,
#                     "isSubmit":false
        
#                     }}

#                     #Additional instructions
#                     Note: convert True/False into small letters as true/false if exists.
#                     Note: if pickup address same as sender's address copy same senders address to pickup address and make the value of "isSenderSameAsPickup" as true.
#                     Note : if all pickup details are collected in {jstring} make "isSubmit" option as "true".
#                     Note: if pickup address not same as sender's address  address make "isSenderSameAsPickup" as false and return above empty json template as it is.
#                     Important Note: Never change "isSenderSameAsPickup" value unless user mentioned to change it in the conversation.
#                     Note: return valid json output ,without adding extra information or comments. Boolean values and null should be returned without any inverted commas.
#                     ** Note ** :  Strictly do not add any comments or extra information to Json file. Just return valid json after tagging the values.         
#                     [SCRATCHPAD]   
#                     Output Assembly:
#                     - Verify JSON format
#                     - Return result    
#                     """
#     pickup_data = gpt_model(prompt,maxtokens=300)
#     end_time = time.time()
#     print(f"generate_pickup_json took {end_time - start_time:.4f} seconds")
#     return pickup_data

async def pickup_prompt(data,jstring):
    start_time = time.time()
    prompt = f"""You are an address parser that extracts and validates pickup location information. Follow these instructions precisely:

The current json is {jstring}

### Input Processing Rules
- Extract relevant details from any format (natural language, structured text, or partial information)
- Return unchanged input JSON if no valid details found. Do not miss previous data.
- Only update fields where new information is provided
- Whenever user wants to update fields, tag updated values. Tag fields with the values provided by the user without adding extra words like "updated" or "tagged." Only the specified fields should reflect the new values exactly as given.
- Tag values exactly as provided without adding extra words
- Never invent or assume missing information
- Map names intelligently to firstName or lastName fields
- Never mix sender/recipient details with pickup details
- Consider user's intended section for updates
- Always cross check tagged information in pickup details and ask for remaining empty fields
- Always return valid JSON without comments

### Core Field Processing Rules

[FIRSTNAME_LASTNAME]
- Process full names into separate fields
- Generate name field by concatenating firstName + " " + lastName

[ADDRESS]
- Validate all address components
- Handle unit numbers and suites
- Map fields to correct categories (city, state, postal code)
- Convert country names to ISO-2 codes (e.g., United States→US , Inida->IN..etc).
- Maintain contextual accuracy in address mapping
- Validate postal code format according to the country. Strictly do not tag the postal code if it is not valid to that Country.


[CONTACT]
- Phone: Must be 10-digit number
- Postal Code: Must be 5-6 characters
- Remove formatting characters
- Validate the phone number which is belongs to that given country or not and accept if given phone numbers related to given Country in {jstring} and map to phone number.Strictly tag 10 digits only. 


### Special Conditions

[MILITARY_CHECK]
Set isMilitaryBox="true" if ALL match:
- City: APO, DPO, or FPO (not actual destination or MPO)
- State: AA, AE, or AP (not actual destination)
- ZIP patterns:
  AA: 340xx
  AE: 090xx-099xx
  AP: 962xx-966xx
Otherwise: "false"

[FLAGS]
- isResidential: Based on user response
- isSenderSameAsPickup: 
  * If Yes Set to true and copy sender's complete address to pickup when addresses match
  * If No Set to false and return empty template when addresses don't match
  * Never change this value unless user explicitly mentions by the user
- isSubmit: Set to true when all pickup details are complete
- isInternational: Based on country code
- Convert all boolean values to lowercase true/false

### Processing Steps
1. Read input text and existing JSON
2. Extract all relevant pickup fields
3. Validate each field
4. Set appropriate flags
5. Check sender/pickup address relationship:
   * If Is pickup address same as senders address -> "Yes": Copy sender address to pickup, set isSenderSameAsPickup=true
   * If Is pickup address same as senders address -> "No": Return empty template, set isSenderSameAsPickup=false
6. Return complete JSON

### Expected Output Format
{{
    "pickup": {{
        "name": "",
        "firstName": "",
        "lastName": "",
        "company": "",
        "phone": "",
        "address": "",
        "address2": "",
        "city": "",
        "state": "",
        "postalCode": "",
        "country": "",
        "isResidential": false,
        "isMilitaryBox": false,
        "latitude": 0.0,
        "longitude": 0.0,
        "isDeleted": false,
        "isInternational": false,
        "fullAddress": ""
    }},
    "isSenderSameAsPickup": false,
    "isSubmit": false
}}

[SCRATCHPAD]
1. Input Analysis:
- Identify pickup location information
- Check existing JSON values
- Understand user's intent for updates

2. Field Extraction:
- Names: <extracted> → <standardized>
- Address: <extracted> → <standardized>
- Location: <extracted> → <standardized>
- Contact: <extracted> → <standardized>

3. Validation:
- Verify address components
- Check military address conditions
- Validate formats
- Ensure correct field mapping

4. Flag Settings:
- Verify isSenderSameAsPickup conditions
- Calculate isSubmit status
- Set isInternational based on country
- Set other boolean flags

5. Output Assembly:
- Combine all processed fields
- Verify JSON format
- Return result without comments or extra information

### System Response Format
Return ONLY the JSON object with processed fields. No explanations or comments.
Extract the relevant data from the following chat history:
{data}"""
    pickup_data = gpt_model(prompt,maxtokens=300)
    end_time = time.time()
    print(f"generate_pickup_json took {end_time - start_time:.4f} seconds")
    return pickup_data

async def receiver_prompt(data, jstring):
    start_time = time.time()
    prompt = f"""
                You are an address parser that extracts and validates address information from user input. Follow these instructions precisely:
 
        The current json is {jstring}
        ### Input Processing Rules
        - Extract relevant address details from any format (natural language, structured text, or partial information)
        - When uncertain, preserve existing values from the input JSON
        - Return unchanged input JSON if no valid details found. Do not miss previous data.
        - Only update fields where new information is provided. 
        - Whenever user wants to update fields, tag updated values. Tag fields with the values provided by the user without adding extra words like "updated" or "tagged." Only the specified fields should reflect the new values exactly as given.
        - Never invent or assume missing information
        - If a person's name is found in the provided user message, intelligently tag it to the appropriate key: either "firstName" or "lastName"
        - Never tag sender and pickup section details to this section. If irrelevant details found Just return input json. 
        - Note : if all recipient's details are collected in {jstring} make "isSubmit" option as "true".
        - Always return valid json
        - ** Note ** :  Strictly do not add any comments or extra information to Json file. Just return valid json after tagging the values.
        
        ### Core Field Processing Rules
        
        [FIRSTNAME_LASTNAME]
        - Split full names, removing titles (Mr., Dr., etc.)
        - Handle suffixes (Jr., Sr., III) correctly
        - Set name = firstName + " " + lastName
        
        [ADDRESS]
        - Standardize street suffixes (Street→St., Avenue→Ave.)
        - Handle PO Boxes, unit numbers, and suites
        - Maximum 100 characters for address
        - Maximum 50 characters for address2
        
        [LOCATION]
        - City: Verify against state/country context
        - State: Convert full names to 2-letter codes
        - Convert country names to ISO-2 codes (e.g., United States→US , Inida->IN..etc).
        - Postal code: Validate format per country
        - Validate postal code format according to the country. Strictly do not tag the postal code if it is not valid to that Country.

        
        [CONTACT]
        - Phone: Standardize to numbers only
        - Allow international formats with country codes
        - Remove all formatting characters
        - Validate the phone number which is belongs to that given country or not and accept if given phone numbers related to given Country in {jstring} and map to phone number.Strictly tag 10 digits only. 

        ### Special Conditions
        
        [MILITARY_CHECK]
        Set isMilitaryBox="true" if ALL match:
        - City is APO, DPO, or FPO
        - State is AA, AE, or AP
        - ZIP matches patterns:
        AA: 340xx
        AE: 090xx-099xx
        AP: 962xx-966xx
        Otherwise, set to "false"
        
        [FLAGS]
        - isResidential: true/false(based on user response)
        - All boolean values as lowercase "true"/"false"
        
        ### Processing Steps
        1. Read input text and existing JSON
        2. Extract all relevant fields using rules above
        3. Validate each field
        4. Set appropriate flags
        5. Return complete JSON
        
        ### Expected Output Format
        ```json
        {{
            "receiver" : {{
                "name": "",
                "firstName": "",
                "lastName": "",
                "company": "",
                "phone": "",
                "address": "",
                "address2": "",
                "city": "",
                "state": "",
                "postalCode": "",
                "country": "",
                "isResidential": "false",
                "isMilitaryBox": "false",
                "latitude": 0.0,
                "longitude": 0.0,
                "isDeleted": "false",
                "isInternational": "false",
                "fullAddress": ""
            }},
            "isSubmit":false
        }}
        ```
        
        [SCRATCHPAD]
        Use this section to work step by step:
        1. Input Analysis:
        - Identify relevant information of recipient.
        - Note any existing JSON values
        
        2. Field Extraction:
        - Names: <extracted> → <standardized>
        - Address: <extracted> → <standardized>
        - Location: <extracted> → <standardized>
        - Contact: <extracted> → <standardized>
        
        3. Validation:
        - Check military address conditions
        - Verify location hierarchy
        - Validate formats
        
        4. Flag Settings:
        - Calculate isResidential
        - Calculate isInternational
        - Verify isMilitaryBox
        
        5. Output Assembly:
        - Combine all processed fields
        - Verify JSON format
        - Return result
        
        ### System Response Format
        Return ONLY the JSON object with the processed fields. Do not add explanations or comments.
        Extract the relevant data from the following chat history:
        {data}"""
                        
    recipient_data = gpt_model(prompt, maxtokens=500)
    end_time = time.time()
    print(f"receiver_prompt took {end_time - start_time:.4f} seconds")
    return recipient_data


# async def num_of_packages_prompt(data, json):
#     prompt = f"""
#                     You are tasked with extracting relevant keys from the provided package data in {data} and updating the corresponding fields in the JSON file below json. 
                   
#                         {json}
           
#                     i)  **totalPackages** : updated the `totalPackages` key based on the how many packages he wants to ship.
#                                             i) Add Packages:
#                                                 Handle cases where the user requests adding one or more packages, or specifies a particular number of packages to be added to the total.

#                                             ii) Remove Packages:
#                                                 Adjust the total number of packages when the user requests removing a specific number of packages from the total.
                    
#                     Note: If the user is not referring to the total_number and is instead discussing another section, do not update total_packages. Return the input JSON {json} as it is.
#                     Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    
#                     """
#     package_data = gpt_model(prompt,maxtokens=500)
#     return package_data

async def num_of_packages_prompt(data, json):
    prompt = f"""
                    Given a user message {data} and a JSON template {json}, update the totalPackages field according to these rules:

                    1.If the user's message indicates the number of packages they want to send
                    - replace the existing totalPackages value with the new number specified

                    2. If the user message indicates adding packages:
                    - Extract the number of packages to add
                    - Add this to the existing totalPackages value

                    3. If the user message indicates removing packages:
                    - Extract the number of packages to remove  
                    - Subtract this from the existing totalPackages value

                    4. If the user message doesn't mention package quantities:
                    - Return the original JSON unchanged

                    Rules:
                    - Only modify totalPackages field
                    - Maximum value for the "totalPackages" should be '8'
                    - Output must be valid JSON
                    - Return only the JSON with no additional text
                    - Boolean values should be without quotes
                    - Numbers should be without quotes
                    - null should be without quotes
                    - Strings should have quotes

                    Example inputs/outputs:
                    Input: "I want to add two packages"
                    {{
                    "totalPackages": 3
                    }}
                    Output:
                    {{
                    "totalPackages": 5
                    }}

                    Input: "What about the shipping date?"
                    {{
                    "totalPackages": 6
                    }}
                    Output:
                    {{
                    "totalPackages": 6
                    }}
                    """
    package_data = gpt_model(prompt,maxtokens=500)
    return package_data

async def terms_and_conditions_prompt(data):
    start_time = time.time()
    prompt = f"""
                    You are tasked with extracting relevant keys from the provided package data in {data} and updating the corresponding fields in the JSON file below json. 
                   
                        {{
                             "Confirmed":false
                              
                        }}
           
                    i)  **termsandConditions** : updated the `Confirmed` key to true when user acknowledged "yes" for termsandConditions.
                    Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    
                    """
    package_data = gpt_model(prompt,maxtokens=500)
    end_time = time.time()
    print(f"generate_package_json took {end_time - start_time:.4f} seconds")
    return package_data

async def package_information_prompt(data, json):
    start_time = time.time()
    prompt = f"""
                    You are tasked with extracting relevant keys from the provided package data in {data} and {json} and updating the corresponding fields in the JSON file below json. 
                    **Note:** Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging any irrelevant or extraneous information. 
                    ##Additional Instructions:
                    - Whenever user wants to update fields tag updated values.
                    - Never miss any value
                    - Always return valid json

                 Below is the output format:         
                {{
                    "type": 0,
                    "serviceTypes": [],    
                }}
                              

                    
                    - Update the Service Type and Package Type for a specific package. 
                    
                    i) **Service type for Package **: Ask the user to select at least one and up to three service types from:
                        - Pick-up & drop off (encode as 4)
                        - Packaging (encode as 1)
                        - Postage label (encode as 2)
                    For each selected service type, add the corresponding encoded value to the `serviceType` list for **Package ** in json. After tagging, verify by confirming: "You selected `selected service types` for Package . Proceed?"
                    
                    ii) **Package type for Package **: Ask the user to select one package type for the package:
                        - Box (encode as 3)
                        - Envelope (encode as 1)
                        - Letter (encode as 2)
                    Store the selected package type's encoded value in the `type` key for **Package ** in json. After tagging, confirm by saying: "You selected `selected package type` for Package . Proceed?"   
                    Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    """
    package_data = gpt_model(prompt,maxtokens=500)
    end_time = time.time()
    print(f"generate_package_json took {end_time - start_time:.4f} seconds")
    return package_data

async def package_dimensions_prompt(data, json):
    start_time = time.time()
    prompt = f"""
                    You are tasked with extracting relevant keys from the provided package data in {data} and {json} and updating the corresponding fields in the JSON file below json. 
                    **Note:** Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging any irrelevant or extraneous information.
                    **Note:**: If the user provides dimensions in the format length, width, and height (e.g., 3ft, 4ft 5inches, 6ft  or 3', 4'5", 6' ), convert them into inches and tag each value accurately to its respective field. Specifically: 

                    Ensure that the data provided by the user is tagged correctly, maintaining the accuracy of the associations between the dimensions and their respective fields."
                    *Note*: Convert all provided dimensions into inches, regardless of the units specified by the user. Update the respective keys in the {json} with the converted values.
                    Note: Convert user provided dimension into inches and tag to their respective fields.
                    --**weightOunces** : Update the "weightOunces" key with the package's weight. Convert the user's provided weight value into ounces, and assign it to "weightOunces". Do not tag any of "length", "width","height" values to weight. Do not hallucinate.
                    ##Additional Instructions:
                    - Whenever user wants to update fields tag updated values.
                    - Never miss any value
                    - Always return valid json
                {json} 
                    Store the selected package type's encoded value in the `type` key for **Package ** in json. After tagging, confirm by saying: "You selected `selected package type` for Package . Proceed?"   
                    Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    """
    package_data = gpt_model(prompt,maxtokens=500)
    end_time = time.time()
    print(f"generate_package_json took {end_time - start_time:.4f} seconds")
    return package_data

async def package_weight_prompt(data, json):
    start_time = time.time()
    prompt = f"""
                    You are tasked with extracting relevant keys from the provided package data in {data} and {json} and updating the corresponding fields in the JSON file below json. 
                    **Note:** Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging any irrelevant or extraneous information.
                    --For weight convert user input to ounces and store in `weightOunces` key. Do not hallucinate.
                    ##Additional Instructions:
                    - Whenever user wants to update fields tag updated values.
                    - Never miss any value 
                {{ 
                    "weightOunces": 0
                }} 
                    Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    """
    package_data = gpt_model(prompt,maxtokens=500)
    end_time = time.time()
    print(f"generate_package_json took {end_time - start_time:.4f} seconds")
    return package_data


async def shipping_prompt(data, json):
    start_time = time.time()
    prompt = f"""
                    You are tasked with extracting relevant keys and values from the provided package data in {data} and updated json {json} and update the corresponding fields in the JSON file below json.
                    If any value is updated in the {json} tag that updated value to the below json and return the final json.
                    **Note:** Leverage user input intelligently to accurately tag only the relevant values to their respective keys. Avoid tagging any irrelevant or extraneous information. For example, if a user provides input like "99999 my house is on Gandipet Road," only tag "99999" as the postal code and disregard the rest of the sentence. Always focus on contextually relevant details.
                     --**weightOunces** : Update the "weightOunces" key with the package's weight. Convert the user's provided weight value into ounces, and assign it to "weightOunces". Do not tag any of "length", "width","height" values to weight. Do not hallucinate.
                     ##Additional Instructions:
                    - Whenever user wants to update fields tag updated values.
                    - Never miss any value
                    - Always return valid json
                          
                {{
                    
                    "indications": [
                        0
                    ],
                    "deliveryInstructions": 0,
                    "insuredValue":0,
                    "isInsuranceEnabled":true
                    
                }}
            
                    i) **deliveryInstructions for Package **: Ask the user to select delivery insructions for the package:
                            If service type is "Pick-up & drop-off" or "Packaging" then `deliveryInsructions` will be:
                                i. None (default) (encode as 0)
                                ii.Leave at Door (only for local) (encode as 3)
                                iii.Ask for PIN at drop off (Only for local) (encode as 4)

                            If service type is "Postage label", then `deliveryInsructions` will be:
                                i. None(default) (encode as 0)
                                ii. No signature. (encode as 1)
                                iii Signature required. (encode as 2)
                        For each selected `deliveryInsructions`, add the corresponding encoded value to the ``deliveryInsructions`` list for **Package ** in json. After tagging, verify by confirming: "You selected `selected `deliveryInsructions`` for Package . Proceed?"
                    ii) **'Indications' for Package **: Ask the user to select 'Indications' for the package:
                            i. None (encode as 0)
                            ii. Fragile Items (encode as 1)
                            iii. Liquids (encode as 2)
                        For each selected `Indications`, add the corresponding encoded value to the ``Indications`` list for **Package ** in json. After tagging, verify by confirming: "You selected `selected `Indications`` for Package . Proceed?"
                    iii) **Insured value**: Update the insured coverage value to the key "insuredValue". Convert the value to dollar and tag it.
                    Note: If the user enters 0 for the 'insuredValue,' set 'isInsuranceEnabled' to false.
                    Return the updated, valid JSON object with no additional text or comments. Strictly do not provide additional comments or explanation just provide the extracted json only. Boolean values and null should be returned without any inverted commas.                
                    """
    package_data = gpt_model(prompt,maxtokens=600)
    end_time = time.time()
    print(f"generate_package_json took {end_time - start_time:.4f} seconds")
    return package_data




async def generate_json(data, jstring):
    start_time = time.time()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": f"""
                You are tasked with updating a JSON object {jstring} using values extracted from a conversation between a bot and a user, represented by {data}. 
                The conversation contains information about sender, pickup, and recipient details. Your goal is to accurately assign these values to the corresponding keys in the JSON object.
                Note: check the address carefully and then tag it to respective keys. Do not confuse between cities, states and countries.

                **Instructions:**

                Note: You should mention 'true' or 'false' value in lowercase in the json. please maintain all 'true' and 'false' are in lower case in {jstring}

                1. Analyze the conversation to determine whether the information pertains to sender, pickup, or recipient details.
                2. Map the extracted values to the appropriate keys in the JSON structure:
                    - Assign sender details to sende r-related keys.
                    - Assign pickup details to the corresponding pickup-related keys.
                    - Assign recipient details to recipient-related keys within the `shipments` list.
                    - Tag name with the concatenation of firstName and lastName to 'name' key in the {jstring}
                3. Only fill in pickup details if the user indicates that "sender details are the same as pickup details," or if the user provides the pickup details manually. Use 'true' or 'false' in lowercase for boolean values in the JSON.
                    
                    - Update the key "isSenderSameAsPickup" "false" if the pickup address is not the same as sender's address accordingly
                    - If pickup address is the same as sender's, set "isSenderSameAsPickup": true, otherwise false.
                    - If "isSenderSameAsPickup" is "true" then update the sender's address in pickup address.
                    - If "isSenderSameAsPickup" is "false" then clear the pickup address details and update the manual user entered details.

                4. When the bot initiates the conversation by asking for recipient details, immediately the following structure should be updated within the shipments key. Ensure that recipient-related information is properly nested within shipments only after the user has provided details. Otherwise, no updates should be made to the shipments key.
                    when user selected number of shipments then `"packages": []` only multiplied not `reciever` key.
                    suppose if user selected 2 shipments then all keys in `packages:[]` will be doubled. and "totalPackages" will be 2. But `reciever` will be 1 for that.
                

                    - Update the Service Type and Package Type for a specific package. For example, if the bot requests details for Package 1, update only Package 1. If it requests details for Package 2, update only Package 2. Do not update both packages simultaneously.
                    
                    i) **Service type for Package **: Ask the user to select at least one and up to three service types from:
                        - Pick-up & drop off (encode as 4)
                        - Packaging (encode as 1)
                        - Postage label (encode as 2)
                    For each selected service type, add the corresponding encoded value to the `serviceType` list for **Package ** in {jstring}. After tagging, verify by confirming: "You selected `selected service types` for Package . Proceed?"
                    
                    ii) **Package type for Package **: Ask the user to select one package type for the package:
                        - Box (encode as 3)
                        - Envelope (encode as 1)
                        - Letter (encode as 2)
                    Store the selected package type's encoded value in the `type` key for **Package ** in {jstring}. After tagging, confirm by saying: "You selected `selected package type` for Package . Proceed?"       
                
                    {{
                        "receiver": {{
                            "address": "",
                            "address2": "",
                            "city": "",
                            "company": "",
                            "country": "",
                            "firstName": "",
                            "isMilitaryBox": false,
                            "isResidential": false,
                            "lastName": "",
                            "name": "",
                            "phone": "",
                            "postalCode": "",
                            "state": "",
                            "isInternational": false
                        }},
                        "packages": [
                            {{
                            "externalTrackingNumber": "",
                            "insuredValue": 0,
                            "insuranceQuoteId": null,
                            "type": 3,
                            "weightOunces": 0,
                            "unitOfDimension": 1,
                            "unitOfWeight": 3,
                            "length": 0,
                            "width": 0,
                            "height": 0,
                            "bagSizeId": 0,
                            "useOfKaeboxBags": true,
                            "serviceTypes": [],
                            "shippingLabelUrl": "",
                            "deliveryType": 1,
                            "beforePickupImageId": null,
                            "packageNumber": null,
                            "indications": [0],
                            "parcelShipping": null,
                            "deliveryInstructions": 0,
                            "deliveryPin": null,
                            "customsDeclaration": null,
                            "printYourOwnLabel": true
                            }}
                        ],
                        "totalPackages": 1,
                        "totalCost": 0
                            
                    }}

                5. Ensure that the `shipments` key is populated for each recipient-related conversation, 
                6. Ensure that the `totalPackages` value matches the number of packages inside the `shipments` list.
                7. Split full names into first and last names where applicable.
                Return the final JSON object with the correct structure and values, without additional explanations.
                Note: return valid json without having any comments or exta information
            """
        }
    ],
    "max_tokens": 1400
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
            response_json = await response.json()

    if 'choices' in response_json:
        response_content = response_json['choices'][0]['message']['content']
    else:
        response_content = "Unexpected response format from OpenAI API"

    end_time = time.time()
    print(f"generate_json took {end_time - start_time:.4f} seconds")
    return response_content
