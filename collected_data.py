# # Function to filter fields
# import json
# def filter_fields(data, fields):
#    return {key: data[key] for key in fields if key in data}

# def filter_fields_for_packages(data, fields):
#    return {key: data[key] for key in fields if key in data}

# def refined_consignment_details(consignment):
#    # Fields to extract
#    selected_fields = ["firstName", "lastName", "address", "city", "state", "postalCode", "country", "phone"]
#    package_fields = ["serviceTypes","type", "length","width", "height","weightOunces", "insuredValue", "deliveryInstructions",  "indications" ]

#    # Build new JSON structure
#    collected_json = {
#       "isSenderSameAsPickup": consignment.get("isSenderSameAsPickup", None),
#       "sender": filter_fields(consignment.get("sender", {}), selected_fields),
#       "pickup": filter_fields(consignment.get("pickup", {}), selected_fields),
#       "shipments": [
#          {
#                "receiver": filter_fields(shipment.get("receiver", {}), selected_fields),
#                "packages": [
#                   filter_fields_for_packages(package, package_fields) for package in shipment.get("packages", [])
#                ],
#                "totalPackages": shipment.get("totalPackages", None)
#          }
#          for shipment in consignment.get("shipments", [])
#       ]
#    }
#    collected_data = json.dumps(collected_json, indent=4)

#    return collected_data


import json

def filter_fields(data, fields):
    return {key: data[key] for key in fields if key in data}

def filter_fields_for_packages(data, fields):
    return {key: data[key] for key in fields if key in data}

def refined_consignment_details(consignment):
    # Fields to extract
    selected_fields = ["firstName", "lastName", "address", "city", "state", "postalCode", "country", "phone"]
    package_fields = ["serviceTypes", "type", "length", "width", "height", "weightOunces", "insuredValue", "deliveryInstructions", "indications"]

    # Build new JSON structure
    collected_json = {
        "isSenderSameAsPickup": consignment.get("isSenderSameAsPickup", None),
        "sender": filter_fields(consignment.get("sender", {}), selected_fields),
        "pickup": filter_fields(consignment.get("pickup", {}), selected_fields),
        "shipments": [
            {
                "receiver": filter_fields(shipment.get("receiver", {}), selected_fields),
                "packages": {
                    f"package{index + 1}": filter_fields_for_packages(package, package_fields)
                    for index, package in enumerate(shipment.get("packages", []))
                },
                "totalPackages": shipment.get("totalPackages", None)
            }
            for shipment in consignment.get("shipments", [])
        ]
    }

    collected_data = json.dumps(collected_json, indent=4)

    return collected_data
