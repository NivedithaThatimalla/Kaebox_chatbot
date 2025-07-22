#Kiran code

# import re

# option_pattern = r'(?<!\d)\b\d{1,2}\.\s+(.*?)(?=\s*\b\d{1,2}\.\s|$)'
# yes_no_pattern = r'\b(yes/no)\b'
# # empty_parentheses_pattern = r'\(\s*\)'
# empty_parentheses_pattern = r'\[\s*\]|\(\s*\)'

# options = {}

# def extract_options(response):
#     labels = []
    
#     # Search for numeric options (e.g., "1. option")
#     options_match = re.findall(option_pattern, response, re.DOTALL)
    
#     # If options exist, add them to the list (trimming spaces)
#     if options_match:
#         labels.extend(option.strip() for option in options_match)
    
#     # Search for "yes/no" responses
#     yes_no_match = re.findall(yes_no_pattern, response, flags=re.IGNORECASE)

#     # If "yes" or "no" are found, add them to the options list
#     if yes_no_match:
#         labels.extend(["Yes", "No"])
    
#     # Remove the options from the original response text
#     cleaned_response = re.sub(option_pattern, '', response, flags=re.DOTALL).strip()
#     cleaned_response = re.sub(yes_no_pattern, '', cleaned_response, flags=re.IGNORECASE).strip()
#     cleaned_response = re.sub(empty_parentheses_pattern, '', cleaned_response).strip()  # Remove empty parentheses

#     # Determine the correct type
#     checkbox_keywords = ["Postage label", "Pick-up & drop-off", "Packaging", "Fragile Items", "Liquids"]
#     radio_keywords = ["Leave at the Door (local only)", "Ask for PIN at drop-off (local only)", "None"]
    
#     # Check if any checkbox-specific keywords are in the labels
#     if any(keyword in labels for keyword in checkbox_keywords):
#         type = "checkbox"
#     # Check if only radio-specific keywords are in the labels
#     elif all(keyword in radio_keywords for keyword in labels):
#         type = "radio"
#     # Default to radio if there are options but no specific type-determining keywords
#     else:
#         type = "radio" if labels else None

#     if """select from the \"Carrier option\" dropdown.""".lower() in response.lower():
#         labels = ["Continue"]
#     elif """ shipping protection is provided by ups capital insurance agency """.lower() in response.lower():
#         labels = ["Acknowledge"]
#     else:
#         pass

#     options["options"] = {"labels": labels, "type": type}

#     if '(Yes/No)' in labels:
#         labels.remove('(Yes/No)')
        
#     return cleaned_response, labels, options



# import re

# # Keywords to identify valid options
# valid_keywords = [
#     "pick-up & drop-off", "packaging", "postage label", "box", "envelope", "letter",
#     "none", "leave at the door (local only)", "ask for pin at drop-off (local only)",
#     "no signature", "signature required","Fragile Items","Liquids", "Continue", "Acknowledge"
# ]

# # Patterns for options and yes/no detection
# option_pattern = r'(?<!\d)\b\d{1,2}\.\s+(.*?)(?=\s*\b\d{1,2}\.\s|$)'
# yes_no_pattern = r'\b(yes/no)\b'
# empty_parentheses_pattern = r'\[\s*\]|\(\s*\)'

# options = {}

# def extract_options(response):
#     labels = []
    
#     # Preserve the original response for reference
#     original_response = response.strip()
    
#     # Search for numeric options (e.g., "1. option")
#     options_match = re.findall(option_pattern, response, re.DOTALL)
#     valid_option_lines = []
    
#     # Filter valid options: only include exact matches from the valid keywords list
#     if options_match:
#         for option in options_match:
#             # Clean and check if the option text matches exactly with valid keywords
#             option_cleaned = option.strip().lower()
#             if option_cleaned in (keyword.lower() for keyword in valid_keywords):
#                 labels.append(option.strip())
#                 valid_option_lines.append(option.strip())  # Keep track of valid options to remove later
    
#     # Remove the options from the response text
#     for valid_option in valid_option_lines:
#         pattern = re.escape(valid_option)
#         response = re.sub(rf'\d+\.\s*{pattern}', '', response, flags=re.IGNORECASE).strip()
    
#     # Search for "yes/no" responses
#     yes_no_match = re.findall(yes_no_pattern, response, flags=re.IGNORECASE)

#     # If "yes" or "no" are found, add them to the options list
#     if yes_no_match:
#         labels.extend(["Yes", "No"])
    
#     # Clean up empty parentheses
#     cleaned_response = re.sub(empty_parentheses_pattern, '', response).strip()

#     # If no valid options were found, return the original response
#     if not labels:
#         return original_response, [], {"options": None}

#     # Determine the correct type
#     checkbox_keywords = ["postage label", "pick-up & drop-off", "packaging"]
#     radio_keywords = [
#         "leave at the door (local only)", "ask for pin at drop-off (local only)",
#         "none", "no signature", "signature required"
#     ]
    
#     # Check if any checkbox-specific keywords are in the labels
#     if any(keyword.lower() in [label.lower() for label in labels] for keyword in checkbox_keywords):
#         type = "checkbox"
#     # Check if only radio-specific keywords are in the labels
#     elif all(label.lower() in [keyword.lower() for keyword in radio_keywords] for label in labels):
#         type = "radio"
#     # Default to radio if there are options but no specific type-determining keywords
#     else:
#         type = "radio"

#     options["options"] = {"labels": labels, "type": type}

#     return cleaned_response, labels, options


import re

# Keywords to identify valid options
valid_keywords = [
    "pick-up & drop-off", "packaging", "postage label", "box", "envelope", "letter",
    "none", "leave at the door (local only)", "ask for pin at drop-off (local only)",
    "no signature", "signature required", "Fragile Items", "Liquids","continue", "acknowledge"
]

# Patterns for options and yes/no detection
option_pattern = r'(?<!\d)\b\d{1,2}\.\s+(.*?)(?=\s*\b\d{1,2}\.\s|$)'
yes_no_pattern = r'\b(yes/no)\b'
empty_parentheses_pattern = r'\[\s*\]|\(\s*\)'

options = {}

def extract_options(response):
    labels = []
    
    # Preserve the original response for reference
    original_response = response.strip()
    
    # Search for numeric options (e.g., "1. option")
    options_match = re.findall(option_pattern, response, re.DOTALL)
    valid_option_lines = []
    
    # Filter valid options: only include exact matches from the valid keywords list
    if options_match:
        for option in options_match:
            # Clean and check if the option text matches exactly with valid keywords
            option_cleaned = option.strip().lower()
            if option_cleaned in (keyword.lower() for keyword in valid_keywords):
                labels.append(option.strip())
                valid_option_lines.append(option.strip())  # Keep track of valid options to remove later
    
    # # Special handling for "Continue" and "Acknowledge"
    # for keyword in ["continue", "acknowledge"]:
    #     if keyword in response.lower():
    #         labels.append(keyword.capitalize())
    #         response = re.sub(rf'1\.\s*{keyword}', '', response, flags=re.IGNORECASE).strip()

    # Remove the options from the response text
    for valid_option in valid_option_lines:
        pattern = re.escape(valid_option)
        response = re.sub(rf'\d+\.\s*{pattern}', '', response, flags=re.IGNORECASE).strip()
    
    # Search for "yes/no" responses
    yes_no_match = re.findall(yes_no_pattern, response, flags=re.IGNORECASE)

    # If "yes" or "no" are found, add them to the options list
    if yes_no_match:
        labels.extend(["Yes", "No"])
    cleaned_response = re.sub(yes_no_pattern, '', response).strip()
    # Clean up empty parentheses
    cleaned_response = re.sub(empty_parentheses_pattern, '', cleaned_response).strip()
    # cleaned_response = re.sub(yes_no_pattern, '', cleaned_response).strip()
    # If no valid options were found, return the original response
    if not labels:
        return original_response, [], {"options": None}

    # Determine the correct type
    checkbox_keywords = ["postage label", "pick-up & drop-off", "packaging","Fragile Items", "Liquids"]
    radio_keywords = [
        "leave at the door (local only)", "ask for pin at drop-off (local only)",
        "none", "no signature", "signature required"
    ]
    
    # Check if any checkbox-specific keywords are in the labels
    if any(keyword.lower() in [label.lower() for label in labels] for keyword in checkbox_keywords):
        type = "checkbox"
    # Check if only radio-specific keywords are in the labels
    elif all(label.lower() in [keyword.lower() for keyword in radio_keywords] for label in labels):
        type = "radio"
    # Default to radio if there are options but no specific type-determining keywords
    else:
        type = "radio"

    options["options"] = {"labels": labels, "type": type}
    if "(yes/no)" in cleaned_response:
        cleaned_response.replace("(yes/no)","")
    return cleaned_response, labels, options













# import re

# # Patterns
# option_pattern = r'(?<!\d)\b\d{1,2}\.\s+(.*?)(?=\s*\b\d{1,2}\.\s|$)'
# yes_no_pattern = r'\b(yes/no)\b'
# empty_parentheses_pattern = r'\(\s*\)'

# # Keywords for filtering
# checkbox_keywords = ["Postage label", "Pick-up & drop-off", "Packaging", "Fragile Items", "Liquids"]
# radio_keywords = ["Leave at the Door (local only)", "Ask for PIN at drop-off (local only)", "None"]
# package_type = ["Box","Envelope","Letter"]
# # instructions_indiations = ["None","Leave at the Door (local only)","Ask for PIN at drop-off (local only)","No signature","Signature required"]
# special_labels = ["Continue", "Acknowledge"]  # Additional valid labels

# def extract_options(response):
#     options = {}
#     labels = []
    
#     # Search for numeric options (e.g., "1. option")
#     options_match = re.findall(option_pattern, response, re.DOTALL)
    
#     # If options exist, add them to the list (trimming spaces)
#     if options_match:
#         labels.extend(option.strip() for option in options_match)
    
#     # Search for "yes/no" responses
#     yes_no_match = re.findall(yes_no_pattern, response, flags=re.IGNORECASE)
#     if yes_no_match:
#         labels.extend(["Yes", "No"])
    
#     # Filter labels to keep only specified ones
#     valid_labels = set(checkbox_keywords + radio_keywords + special_labels + package_type)
#     labels = [label for label in labels if label in valid_labels]
    
#     # Determine the correct type
#     if labels:
#         if any(keyword in labels for keyword in checkbox_keywords):
#             option_type = "checkbox"
#         elif all(keyword in radio_keywords for keyword in labels):
#             option_type = "radio"
#         else:
#             option_type = "radio"
#     else:
#         option_type = None

#     # Handle special responses
#     if "select from the \"Carrier option\" dropdown.".lower() in response.lower():
#         labels = ["Continue"]
#         option_type = "radio"
#     elif "shipping protection is provided by ups capital insurance agency".lower() in response.lower():
#         labels = ["Acknowledge"]
#         option_type = "radio"
    
#     # Do not alter the original response
#     cleaned_response = re.sub(option_pattern, '', response, flags=re.DOTALL).strip()
#     cleaned_response = re.sub(yes_no_pattern, '', cleaned_response, flags=re.IGNORECASE).strip()
#     cleaned_response = re.sub(empty_parentheses_pattern, '', cleaned_response).strip()  # Remove empty parentheses

#     # Update options dictionary
#     options["options"] = {"labels": labels, "type": option_type}

#     return cleaned_response, labels, options


navigation_data = {"navigation":{"receiver":"none","package":"none"}}

def navigating(navigating_response):
    print("navigation_elements --->",navigating_response)
    if navigating_response["receiver"] and navigating_response["package"]:
        navigation_data["navigation"]=navigating_response

    elif navigating_response["receiver"]=="none" and navigating_response["package"]:
        navigation_data["navigation"]["package"]=navigating_response["package"]
    elif navigating_response["receiver"]  and navigating_response["package"]=="none":
        navigation_data["navigation"]["receiver"]=navigating_response["receiver"]

    else:
        navigation_data["navigation"] = navigating_response

    return navigation_data


def extract_package_number(text):
    match = re.search(r"(?i)package\s*(\d+)", text)  # case-insensitive and captures number after "Package"
    return int(match.group(1)) if match else None


# Function to filter fields
def filter_fields(data, fields):
    return {key: data[key] for key in fields if key in data}
# Function to filter fields and check for empty values
def filter_and_find_empty_fields(data, fields, path_prefix=""):
    filtered_data = {}
    empty_fields = {}

    for key in fields:
        value = data.get(key)
        full_path = f"{path_prefix}.{key}" if path_prefix else key
        
        # Include the value in filtered_data if the field exists
        filtered_data[key] = value
        
        # Check if the field is empty ("" or 0 or [])
        if value == "" or value == 0 or value == []:
            empty_fields[full_path] = value

    return filtered_data, empty_fields

# def generate_collected_data(consignment):
#     selected_fields = ["firstName", "lastName", "address", "phone", "city", "state", "postalCode", "country"]
#     package_fields = ["deliveryInstructions", "height", "indications", "insuredValue", "type", "length", "serviceTypes", "weightOunces", "width"]

#     collected_json = {}
#     empty_fields = {}

#     # Process sender and pickup fields
#     collected_json["isSenderSameAsPickup"] = consignment.get("isSenderSameAsPickup", None)
    
#     collected_json["sender"], sender_empty = filter_and_find_empty_fields(consignment.get("sender", {}), selected_fields, "sender")
#     collected_json["pickup"], pickup_empty = filter_and_find_empty_fields(consignment.get("pickup", {}), selected_fields, "pickup")

#     empty_fields.update(sender_empty)
#     empty_fields.update(pickup_empty)

#     # Process shipments, receiver, and packages fields
#     shipments = []
#     for shipment_index, shipment in enumerate(consignment.get("shipments", [])):
#         shipment_data = {}
#         receiver, receiver_empty = filter_and_find_empty_fields(shipment.get("receiver", {}), selected_fields, f"shipments[{shipment_index}].receiver")
        
#         # Add receiver data and any empty fields found
#         shipment_data["receiver"] = receiver
#         empty_fields.update(receiver_empty)

#         # Process packages within each shipment
#         packages = []
#         for package_index, package in enumerate(shipment.get("packages", [])):
#             package_data, package_empty = filter_and_find_empty_fields(package, package_fields, f"shipments[{shipment_index}].packages[{package_index}]")
#             packages.append(package_data)
#             empty_fields.update(package_empty)

#         shipment_data["packages"] = packages
#         shipment_data["totalPackages"] = shipment.get("totalPackages", None)
#         shipments.append(shipment_data)

#     collected_json["shipments"] = shipments

#     return collected_json, empty_fields

def generate_collected_data(consignment):
    selected_fields = ["firstName", "lastName", "address", "phone", "city", "state", "postalCode", "country"]
    package_fields = ["serviceTypes", "type","length","width","height","weightOunces","insuredValue","deliveryInstructions",  "indications"]

    collected_json = {}
    empty_fields = {}

    # Process sender and pickup fields
    collected_json["isSenderSameAsPickup"] = consignment.get("isSenderSameAsPickup", None)
    
    collected_json["sender"], sender_empty = filter_and_find_empty_fields(consignment.get("sender", {}), selected_fields, "sender")
    collected_json["pickup"], pickup_empty = filter_and_find_empty_fields(consignment.get("pickup", {}), selected_fields, "pickup")

    empty_fields.update(sender_empty)
    empty_fields.update(pickup_empty)

    # Process shipments, receiver, and packages fields
    shipments = []
    for shipment_index, shipment in enumerate(consignment.get("shipments", [])):
        shipment_data = {}
        receiver, receiver_empty = filter_and_find_empty_fields(shipment.get("receiver", {}), selected_fields, f"receiver")
        
        # Add receiver data and any empty fields found
        shipment_data["receiver"] = receiver
        empty_fields.update(receiver_empty)

        # Process packages within each shipment
        packages = []
        for package_index, package in enumerate(shipment.get("packages", [])):
            package_data, package_empty = filter_and_find_empty_fields(package, package_fields, f"packages[{package_index+1}]")
            packages.append(package_data)
            empty_fields.update(package_empty)

        shipment_data["packages"] = packages
        shipment_data["totalPackages"] = shipment.get("totalPackages", None)
        shipments.append(shipment_data)

    collected_json["shipments"] = shipments

    return collected_json, empty_fields



def generate_questions(questions_dict):
    # Define a mapping of field names to user-friendly labels
    field_mapping = {
        'firstName': "first name",
        'lastName': "last name",
        'address': "address",
        'phone': "phone number",
        'city': "city",
        'state': "state",
        'postalCode': "postal code",
        'country': "country",
        'deliveryInstructions': "delivery instructions",
        'indications': "indications",
        'insuredValue': "insured value",
        'weightOunces': "weight in ounces",
        'width': "width",
        'height': "height",
        'length': "length",
        'serviceTypes': "service types"
    }
    
    questions = []
    
    for key, value in questions_dict.items():
        # Split the key by '.' and remove 'pickup' and 'shipments' related indices to get to the actual field
        key_parts = key.replace('[0]', '').replace('[1]', '').split('.')
        
        # Construct the question based on the parts of the key
        if key_parts[0] == 'pickup':
            question = f"Please provide pickup {field_mapping.get(key_parts[1], key_parts[1])}?"
        elif key_parts[0] == 'shipments':
            package_index = key_parts[1][-1]  # Package index, e.g., 0 or 1
            question = f"Please provide package {package_index} {field_mapping.get(key_parts[2], key_parts[2])}?"

        questions.append(question)
    
    return questions


def process_sentence(sentence):
    # Split the sentence into two parts at the first occurrence of "."
    parts = sentence.split(".", 1)
    
    # Find the sentence that contains the word "updated"
    for part in parts:
        if "updated" in part:
            # Check if a number follows "updated" and strip everything after "updated"
            match = re.search(r"(.*updated)(\s+\d+.*)", part)
            if match:
                updated_sentence = match.group(1).strip()
            else:
                updated_sentence = part.strip()
                
            # Return the processed "updated" sentence and any remaining part
            return updated_sentence + (". " + parts[1] if len(parts) > 1 else "")
    
    # If no "updated" sentence is found, return the original sentence
    return sentence

# def replace_encoded_values(data):
#     # Define mappings for different fields
#     service_types_mapping = {
#         4: "Pick-up & drop off",
#         1: "Packaging",
#         2: "Postage label"
#     }
#     package_types_mapping = {
#         3: "Box",
#         1: "Envelope",
#         2: "Letter"
#     }
#     delivery_instructions_mapping = {
#         0: "None",
#         1: "No signature",
#         2: "Signature required",
#         3: "Leave at Door",
#         4: "Ask for PIN at drop off"
#     }
#     indications_mapping = {
#         0: "None",
#         1: "Fragile Items",
#         2: "Liquids"
#     }

#     # Process each shipment
    
#     for shipment in data["shipments"]:
#         for package in shipment["packages"]:
#             # Replace service types
#             package["serviceTypes"] = [service_types_mapping.get(code, str(code)) for code in package["serviceTypes"]]
            
#             # Replace package type
#             package["type"] = package_types_mapping.get(package["type"], str(package["type"]))
            
#             # Replace delivery instructions
#             if isinstance(package["deliveryInstructions"], list):
#                 package["deliveryInstructions"] = [delivery_instructions_mapping.get(code, str(code)) for code in package["deliveryInstructions"]]
#             else:
#                 package["deliveryInstructions"] = [delivery_instructions_mapping.get(package["deliveryInstructions"], str(package["deliveryInstructions"]))]
            
#             # Replace indications
#             package["indications"] = [indications_mapping.get(code, str(code)) for code in package["indications"]]

#     return data

def replace_encoded_values(data):
    # Define mappings for different fields
    service_types_mapping = {
        4: "Pick-up & drop off",
        1: "Packaging",
        2: "Postage label"
    }
    package_types_mapping = {
        3: "Box",
        1: "Envelope",
        2: "Letter"
    }
    delivery_instructions_mapping = {
        0: "None",
        1: "No signature",
        2: "Signature required",
        3: "Leave at Door",
        4: "Ask for PIN at drop off"
    }
    indications_mapping = {
        0: "None",
        1: "Fragile Items",
        2: "Liquids"
    }

    # Process each shipment
    for shipment in data["shipments"]:
        packages = shipment["packages"]
        for package_key, package in packages.items():
            # Replace service types
            package["serviceTypes"] = [service_types_mapping.get(code, str(code)) for code in package["serviceTypes"]]

            # Replace package type
            package["type"] = package_types_mapping.get(package["type"], str(package["type"]))

            # Replace delivery instructions
            if isinstance(package["deliveryInstructions"], list):
                package["deliveryInstructions"] = [delivery_instructions_mapping.get(code, str(code)) for code in package["deliveryInstructions"]]
            else:
                package["deliveryInstructions"] = [delivery_instructions_mapping.get(package["deliveryInstructions"], str(package["deliveryInstructions"]))]
            
            # Replace indications
            package["indications"] = [indications_mapping.get(code, str(code)) for code in package["indications"]]

    return data
