
# import requests
# import xml.etree.ElementTree as ET

# def validate_address(address_json):
#     usps_userid = "63S8NA0000125"  # Replace with your USPS API UserID
#     # url = "https://secure.shippingapis.com/ShippingAPI.dll"
#     url = "http://production.shippingapis.com/ShippingAPI.dll?API=Verify&XML={{xmlParam}}"
#     # Prepare the address fields
#     address1 = address_json.get("address1", "")
#     address2 = address_json.get("address2", "")
#     city = address_json.get("city", "")
#     state = address_json.get("state", "")
#     zip5 = address_json.get("zip5", "")
#     zip4 = address_json.get("zip4", "")

#     # Construct the XML request
#     xml_request = f"""
#     <AddressValidateRequest USERID="{usps_userid}">
#         <Revision>1</Revision>
#         <Address>
#             <Address1>{address1}</Address1>
#             <Address2>{address2}</Address2>
#             <City>{city}</City>
#             <State>{state}</State>
#             <Zip5>{zip5}</Zip5>
#             <Zip4>{zip4}</Zip4>
#         </Address>
#     </AddressValidateRequest>
#     """

#     # Make the request
#     params = {"XML": xml_request}
#     response = requests.get("http://production.shippingapis.com/ShippingAPI.dll?API=Verify&XML={{xml_request}}")

#     # Debugging: Print the full response
#     print("Response Status Code:", response.status_code)
#     print("Response Content:", response.text)

#     # Parse the XML response
#     root = ET.fromstring(response.content)

#     # Check for errors in the response
#     error = root.find("Error")
#     if error is not None:
#         return {
#             "error": error.find("Description").text if error.find("Description") else "Unknown error"
#         }

#     # Extract address information if no error
#     address_element = root.find("Address")
#     if address_element is None:
#         return {"error": "No Address element found in the response"}
    
#     address_info = {child.tag: child.text for child in address_element if child.tag and child.text}
#     return address_info

# # Example JSON address
# address_json = {
#     "address1": "Suite 1",
#     "address2": "123 Main Street",
#     "city": "New York",
#     "state": "NY",
#     "zip5": "10001",
#     "zip4": ""
# }

# validated_address = validate_address(address_json)
# print(validated_address)

# import requests
# import xml.etree.ElementTree as ET

# def validate_address(address_json):
#     usps_userid = "63S8NA0000125"  # Replace with your USPS API UserID
#     url = "https://secure.shippingapis.com/ShippingAPI.dll"
    
#     # Prepare the address fields
#     address1 = address_json.get("address1", "")
#     address2 = address_json.get("address2", "")
#     city = address_json.get("city", "")
#     state = address_json.get("state", "")
#     zip5 = address_json.get("zip5", "")
#     zip4 = address_json.get("zip4", "")

#     # Construct the XML request
#     xml_request = f"""<AddressValidateRequest USERID="{usps_userid}">
#         <Revision>1</Revision>
#         <Address>
#             <Address1>{address1}</Address1>
#             <Address2>{address2}</Address2>
#             <City>{city}</City>
#             <State>{state}</State>
#             <Zip5>{zip5}</Zip5>
#             <Zip4>{zip4}</Zip4>
#         </Address>
#     </AddressValidateRequest>"""

#     # Make the request
#     params = {"API": "Verify", "XML": xml_request}
#     response = requests.get(url, params=params)

#     # Debugging: Print the request details and response
#     print("Request URL:", response.url)
#     print("Response Status Code:", response.status_code)
#     print("Response Content:", response.text)

#     # Parse the XML response
#     root = ET.fromstring(response.content)

#     # Check for errors in the response
#     error = root.find("Error")
#     if error is not None:
#         return {
#             "error": error.find("Description").text if error.find("Description") else "Unknown error"
#         }

#     # Extract address information if no error
#     address_element = root.find("Address")
#     if address_element is None:
#         return {"error": "No Address element found in the response"}
    
#     address_info = {child.tag: child.text for child in address_element if child.tag and child.text}
#     return address_info

# # Example JSON address
# address_json = {
#     "address1": "Suite 1",
#     "address2": "123 Main Street",
#     "city": "New York",
#     "state": "NY",
#     "zip5": "10001",
#     "zip4": ""
# }

# validated_address = validate_address(address_json)
# print(validated_address)


import urllib.request
import xml.etree.ElementTree as ET

xml_request = f"""
        <?xml.version="1.0"?>
        <AddressValidateRequest.USERID="63S8NA0000125">
            <Revision>1</Revision>
            <Address.ID="0">
                <Address1>2335.S.State</Address1>
                <Address2>Suite.300</Address2>
                <City>Provo</City>
                <State>UT</State>
                <Zip5>84604</Zip5>
                <Zip4/>
        </Address>
    </AddressValidateRequest>"""

docString = xml_request
docString = docString.replace("\n","").replace("\t","")
docString = urllib.parse.quote_plus(docString)

url = "https://secure.shippingapis.com/ShippingAPI.dll?API=Verify&XML="+docString
print(url)
response = urllib.request.urlopen(url)
if response.getcode() != 200:
    print(response.info())
    exit()

contents = response.read()
print(contents)
root = ET.fromstring(contents)
for address in root.findall("Address"):
    print()
    print(address.find("Address1").text)
    print(address.find("Address2").text)
    print(address.find("City").text)
    print(address.find("State").text)
    print(address.find("Zip5").text)
    