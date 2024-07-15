import os
import json
from openai import AzureOpenAI

from openai_tools import get_db_schema, query_db
from openai_service import chat_completion_request, pretty_print_conversation, client

tool_metadata = [{
            "type": "function",
            "function": query_db.openai_metadata  
        }]

print(tool_metadata)


tools2 = [
    {
        "type": "function",
        "function": {
            "name": f"{get_db_schema.__name__}",
            "description": f"{get_db_schema.__doc__}",
            "parameters": {
                "type": "object",
                "properties": {}
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": f"{query_db.__name__}",
            "description": f"{query_db.__doc__}",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                This parameter is a valid SQL query that will be executed on the database.
                                This query should be a SELECT statement that returns a result based on the database schema.
                                """,
                    }
                },
                "required": ["query"]
            },
        }
    }
]
print(f"\n {query_db.openai_metadata} \n")
messages = []
messages.append({"role": "system", "content": f"You're an AI assistant helping a user with a database. The database schema is {get_db_schema()}."}) 
messages.append({"role": "user", "content": "Which order included the priciest product?"})
chat_response = chat_completion_request(
    messages=messages, 
    tools=[
        {
            "type": "function",
            "function": query_db.openai_metadata
        }
    ], 
    tool_choice="auto"
)

print(chat_response)
print("\n")
response_message = chat_response.choices[0].message 
messages.append(response_message)
print(response_message)
print("\n")

# Step 2: determine if the response from the model includes a tool call.   
tool_calls = response_message.tool_calls

'''
def tools_callings(tool_calls:str) -> list:
    for i in range(0,len(tool_calls)):
        tool_call_id = tool_calls[i].id
        tool_function_name = tool_calls[i].function.name
        tool_arguments_dict = eval(tool_calls[i].function.arguments)

        # Step 3: Call the function and retrieve results. Append the results to the messages list. 
        if tool_function_name == f'{get_db_schema.__name__}':
            
            try:
                schema = get_db_schema()
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content": schema
                })  
            except Exception as e:
                raise e   

        if tool_function_name == f'{query_db.__name__}':
            try:
                results = query_db(tool_arguments_dict['query'])
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content":results
                })
            except Exception as e:
                raise e
    
    return messages

if tool_calls:
    messages = tools_callings(tool_calls)
    model_response_with_function_call = client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=messages,
    )  # get a new response from the model where it can see the function response
    print(model_response_with_function_call.choices[0].message.content)
else: # Model did not identify a function to call, result can be returned to the user
    print(response_message.content)


'''        
if tool_calls:
    # If true the model will return the name of the tool / function to call and the argument(s)  
    tool_call_id = tool_calls[0].id
    tool_function_name = tool_calls[0].function.name
    tool_query_string = eval(tool_calls[0].function.arguments)["query"]
         

    if tool_function_name == f'{query_db.__name__}':
        results = query_db(tool_query_string)
        # Convert dictionary to JSON
        results_json = json.dumps(results)
        
        messages.append({
            "role":"tool", 
            "tool_call_id":tool_call_id, 
            "name": tool_function_name, 
            "content":results_json
        })
        
        # Step 4: Invoke the chat completions API with the function response appended to the messages list
        # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
        model_response_with_function_call = client.chat.completions.create(
            model="gpt-35-turbo-16k",
            messages=messages,

        )  # get a new response from the model where it can see the function response
        print(model_response_with_function_call.choices[0].message.content)
    else: 
        print(f"Error: function {tool_function_name} does not exist")
else: 
    # Model did not identify a function to call, result can be returned to the user 
    print(response_message.content) 

