import os,re,copy,requests,random
from datetime import date
import time

insurance_cache = {}

# Function to get insurance quote and update consignment details
def insurance_quote(auth_token, consignment_details, package_number):
    try:
        start_time = time.time()
        # Extract insured value from consignment details (first shipment's first package)
        insured_value = consignment_details['shipments'][0]['packages'][int(package_number)-1].get('insuredValue', 100)  # Default value set to 100 if not provided
        print("insured value in function ----------> ", insured_value)
        print("Fetching new insurance details from API")

        # Fetch sender and recipient details for the API request
        origin_details = consignment_details['sender']
        destination_details = consignment_details['shipments'][0]['receiver']

        # Generate random Bill of Lading (BOL) value for the insurance request
        bol_value = random.randint(100000000000000000, 999999999999999999)

        # Prepare the payload for the insurance API request
        insurance_payload = {
            "status": "unCONFIRMED",
            "partnerId": "0801839513",
            "shipDate": str(date.today()),
            "bol": str(bol_value),
            "insuredValue": insured_value,
            "carrier": "UPS",
            "shipmentType": "3",  # Assuming 3 refers to parcel shipment type
            "originAddress1": origin_details["address"],
            "originCity": origin_details["city"],
            "originState": origin_details["state"],
            "originPostalCode": origin_details["postalCode"],
            "originCountry": origin_details["country"],
            "destinationAddress1": destination_details["address"],
            "destinationCity": destination_details["city"],
            "destinationState": destination_details["state"],
            "destinationPostalCode": destination_details["postalCode"],
            "destinationCountry": destination_details["country"],
            "packageQuantity": str(len(consignment_details['shipments'][0]['packages'])),
            "referenceFields": "8373057"
        }

        # Set headers for the API request
        headers = {'Authorization': f'{auth_token}'}
        url = "https://api-staging.kaebox.com:44301/api/services/app/UpsCapital/InsuranceQuote"
        
        # Make the API request to fetch the insurance quote
        response = requests.post(url, json=insurance_payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("Insurance details are updated----")
            print(f"Insurance api time:{time.time()-start_time:.4f}seconds")
            return {'insurance_details':{
                "insuranceQuoteId": data['result']['quoteId'],
                "insuranceCost": data['result']['premiumAmount'],
                "insuredValue": data['result']["quoteInfo"]["shipmentInfo"]["insuredValue"]
            }}
        else:
            # print(f"Insurance API error: {response.status_code}, {response.content}")

            return {'insurance_details':{
                "insuranceQuoteId": "",
                "insuranceCost": 0,
                "insuredValue": 0
            }}
        
        # return insurance_cache  # Return updated consignment details

    except Exception as e:
        print(f"Error in insurance_quote function: {e}")
        
        return consignment_details  # Return unchanged consignment details in case of error



def sharedPayment(auth_token,consignment_id,shared_phone_num,sharedamount):

    payment_url = "https://api-staging.kaebox.com:44301/api/services/consumer/CreditCard/InitiatePaymentForSharedShipment"
    get_url = f"https://api-staging.kaebox.com:44301/api/services/consumer/Consignment/Get?id={consignment_id}"


    payload={
            "consignmentId": consignment_id,
            "sharedUserPhoneNumber": shared_phone_num,
            "paymentAmountForOtherUser":sharedamount
            }
    headers = {'Authorization': f'{auth_token}'}
    response = requests.post(payment_url, json=payload, headers=headers)
        
    if response.status_code == 200:
        print("Shared Payment API Called!----")
        get_response = requests.get(get_url, headers=headers)
        if get_response.status_code == 200:
            data = get_response.json()
            print("appppppppppppppppppppppppppiiiiiiiiiiii",data)
            sharedpayment_data = data["result"].get("consignmentSharedPayment")
            return sharedpayment_data

    else:
        print(f"SharedPayment API error: {response.status_code}, {response.content}")
        return None  # Return unchanged consignment details if API fails
    

def getInvoice(auth_token,consignment_details):
    url = "https://api-staging.kaebox.com:44301/api/services/consumer/Consignment/GetInvoiceForConsignment"
    package_id = consignment_details["shipments"][0]["packages"][0].get("id","")
    payload = {
            id: package_id
        }
    headers = {'Authorization': f'{auth_token}'}


def paymentWithCoupon(auth_token,consignment_details):
    url = "https://api-staging.kaebox.com:44301/api/services/consumer/CreditCard/InitiatePaymentWithCoupon"
    package_id = consignment_details["shipments"][0]["packages"][0].get("id","")
    payload = {
                    "consignmentId": package_id,
                    "couponCode": "123456"
                }
    headers = {'Authorization': f'{auth_token}'}



def uploadBeforePickupImage(auth_token,consignment_details):
    url = "https://api-staging.kaebox.com:44301/api/services/consumer/Parcel/UploadBeforePickupImage"
    package_id = consignment_details["shipments"][0]["packages"][0].get("id","")
    payload = {
                "parcelId": package_id
                }
    
    headers = {'Authorization': f'{auth_token}'}
    response = requests.post(url, json=payload, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        print("before pickupimage  API Called!----")
        return data["result"]["imageId"]
    
    #output
        """        {
                "result": {
                    "imageId": "9e7304b7-2c87-ef11-8473-0022481f1721",
                    "contentType": "image/png",
                    "description": "Package Before Pickup",
                    "filename": "test.png"
                },
                "targetUrl": null,
                "success": true,
                "error": null,
                "unAuthorizedRequest": false,
                "__abp": true
            }
        """

    else:
        # print(f"Insurance API error: {response.status_code}, {response.content}")
        return consignment_details  # Return unchanged consignment details if API fails


def getBeforePickupImage(auth_token,consignment_details):
    url = "https://api-staging.kaebox.com:44301/api/services/consumer/Parcel/GetBeforePickupImage"
    payload = {
                "parcelId": "dd20d27b-8aa3-4965-4c4d-08dce9505d67"
                }
    
    headers = {'Authorization': f'{auth_token}'}
    response = requests.post(url, json=payload, headers=headers)
        
    if response.status_code == 200:
        data = response.json()
        print("before pickupimage  API Called!----")
        return data["result"]
    
    #output
        """        {
                "result": {
                    "imageId": "9e7304b7-2c87-ef11-8473-0022481f1721",
                    "contentType": "image/png",
                    "description": "Package Before Pickup",
                    "filename": "test.png"
                },
                "targetUrl": null,
                "success": true,
                "error": null,
                "unAuthorizedRequest": false,
                "__abp": true
            }
        """
        
    else:
        # print(f"Insurance API error: {response.status_code}, {response.content}")
        return consignment_details  # Return unchanged consignment details if API fails