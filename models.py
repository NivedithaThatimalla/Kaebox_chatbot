from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
# from langchain.embeddings import OpenAIEmbeddings # Import OpenAIEmbeddings from the new package
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import json
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

OPENAI_KEY = config.get('openai', 'api_key')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", OPENAI_KEY))


async def generate_gpt_response(conversation):
    creation = client.chat.completions.create(  # Use acreate for async completion
        model="gpt-4o",
        messages=conversation,
        max_tokens=200,
        temperature=0.1
    )
    import json
    from datetime import datetime

    # Create a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    completion_tokens = creation.usage.completion_tokens
    prompt_tokens = creation.usage.prompt_tokens

    # Prepare the new entry
    new_entry = {
        "gpt4_input_tokens": prompt_tokens,
        "gpt4_output_tokens": completion_tokens
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
    return creation.choices[0].message.content
    # response = json.loads(creation.choices[0].message.content)["response1"]
    # print("creation.choices[0]..................................",creation)
    return creation.choices[0].message.content
    # return response.choices[0].message["content"]

async def get_details(original_response,conversation_message):
    response_message = conversation_message[0][0]["content"]
    conversation_message = str(conversation_message)
    print("response_message-->",response_message)
    classification_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""You are an advanced message classifier that can identify SINGLE OR MULTIPLE categories for shipping-related messages.. You will analyze the provided conversation {conversation_message} to determine the most appropriate classification based on assistant and user conversation.
                Important_Note: If a user message contains updates or changes related to a specific section, classify it under the relevant section mentioned by the user.
                ### Note ### : Strictly not classify ambiguously use your intelligence to classify the response message . if it single one just return single section.
## Classification Categories
 
### Primary Categories
1. sender_details
   - Contact information, name, address of sender
   - Updates to sender information
   - Sender ID or reference numbers
 
2. pickup_details
   - "Is the pickup address is same as sender address"
   - Pickup contact information
   - Pickup location
   - Pickup window
   - Special pickup instructions
   - Access codes or restrictions
 
3. recipient_details
   - Package Delivery address
   - Recipient contact information
   - Recipient preferences
   - Updates to recipient information
 
4. number_of_packages
   - Quantity of items to be shipped
   - Package count inquiries
   - Updates to package quantities
   - Triggers: "how many packages", "number of packages to ship", "How many packages are you planning to ship?"
 
5. package_information
   - Service type selection  - pickup and drop off, packaging, postage label
   - Package type specification - box, letter, envelope
   - Triggers: "What is the package type for Package "
6. package_dimensions
   - Length, width, height measurements
   - Weight specifications (pounds/ounces)
   - Size category selection
   - Dimensional updates
   - Triggers: "Please provide the dimensions (length, width, height in inches) for Package", "What is the weight in pounds or ounces for Package"
7. shipping
   - Delivery instructions - No signature,  Signature required, Leave at the Door, Ask for PIN at drop-off (local only)
   - Package indications - Fragile items, liquids
   - Insurance coverage requests
   - Coverage value specifications
   - Triggers: "What is the insurance coverage value for Package", "What are the delivery instructions for Package", "What are the package indications for Package"
8. checkout
   - terms and conditions
 
9. other_messages
   - General inquiries
   - Status updates
   - Non-classified content
   
## Classification Rules
 
1. Priority Rules:
   - Updated information takes precedence over existing categorization
   - When multiple categories apply, prioritize the most specific category
   - For pickup date/time queries, classify as 'packages'
 
2. Context Analysis:
   - Consider previous messages in {conversation_message} for context
   - Use context especially for sender/pickup/receiver classifications
   - Look for implicit references to categories
 
3. Disambiguation Rules:
   - When message contains multiple intents, prioritize the primary action
   - For unclear messages, use conversation history for context
   - Default to 'other_messages' only when no other category clearly applies

## Multiple Classification Rules
1. Identify ALL relevant categories that apply to the message
2. Return classifications as a JSON array
3. Be comprehensive in category matching
4. Prioritize specificity and context
 
## Response Format

{{
    "response2": ["category1", "category2", ...],
    "response3": {{
        "receiver": "<receiver_number|none>",
        "package": "<package_number|none>"
    }}
}}

 
## Classification Examples
 
### Input Examples and Expected Classifications:
1. "I need to change the pickup address to 123 Main St" → "pickup_details"
2. "Can you add insurance for $500?" → "shipping"
3. "The package weighs 5 pounds" → "package_dimensions"
4. "I'm shipping 3 boxes" → "number_of_packages"
5. "Is this a residential address for the sender? (Yes/No)" → "sender_details"
6. "How many packages are you planning to ship?" → "number_of_packages"
7. "Now go to the 'Shipping' above to select the carrier type and delivery preferences for Package" → "other_messages"
 
## Example of Single Classificaions:
1. "Provide pickup Firstname" 
   → ["pickup_details"]
2. "Provide Sender's Phone number" 
   → ["sender_details"]
## Examples of Multiple Classifications:
1. "I have a package that is 5x4x3 inches and needs special handling" 
   → ["package_dimensions", "shipping"]
2. "Sending 2 packages to John's address with insurance" 
   → ["number_of_packages", "recipient_details", "shipping"]
3. "Update sender address and package weight" 
   → ["sender_details", "package_dimensions"]

   
### Special Cases:
1. Updates: "Please update the recipient's phone number to..." → "recipient_details"
2. Multiple Intents: "Need to add insurance and change pickup time" → "shipping" (insurance takes priority)
3. Pickup Scheduling: "What time can you pick up?" → "packages"
 
## Processing Instructions
1. Analyze {response_message} for keywords and phrases
2. Check against category criteria
3. Consider conversation context from {conversation_message}
4. Extract receiver/package numbers if present
5. Format response in specified JSON structure
6. Do not include additional text or explanations"""
            },
        ],
        max_tokens=200,
        temperature=0.1
    )

    # Extract response safely
    try:
        # Get the classification response for response2
        response_content = classification_response.choices[0].message.content
        # print("classification_response tokens....................",classification_response)
        import json
        from datetime import datetime

        # Create a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        completion_tokens = classification_response.usage.completion_tokens
        prompt_tokens = classification_response.usage.prompt_tokens

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

        response_content = str(response_content).strip('```json').strip('```')     
        print("classification response before json loading", response_content)  
        response_content = json.loads(response_content)
        # Construct the JSON with response1 directly from your input (bypassing the model)
        try:
            result = {
                "response1": original_response,  # Use the original message directly
                "response2": response_content["response2"],  # Ensure response2 is handled by the model
                "response3": response_content["response3"]
            }
        except:
            result = {
                "response1": original_response,  # Use the original message directly
                "response2": response_content["response2"],  # Ensure response2 is handled by the model
                "response3": {
                        "receiver": "none",
                        "package": "none"
                            }
                        }
        result = json.dumps(result)
        print("gpt results are ---- >",result)
        return result
    except (KeyError, IndexError) as e:
        print(f"Error accessing classification response: {e}")
        return None
    


# Load the vector store from disk
embeddings = OpenAIEmbeddings(api_key=OPENAI_KEY)
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# # Vector DB Context Fetcher
# def get_vector_db_context(query):
#     llm = ChatOpenAI(temperature=0.0, api_key=OPENAI_KEY)
#     memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         memory=memory,
#     )
#     response = conversation_chain.invoke({'question': query})
#     return response['chat_history'][-1].content

import asyncio

async def get_vector_db_context(query):
    retriever = vectorstore.as_retriever()
    results = retriever.get_relevant_documents(query)
    return results[0].page_content if results else None