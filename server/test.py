import requests
import json
from dotenv import load_dotenv
import os
from rich import print

# Load environment variables from the .env file
load_dotenv()

# Get the OpenRouter API key from the environment
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY is not set in the environment variables")

# Define the question for the model
question = "How would you build the tallest building ever?"

# Set the OpenRouter API URL and headers
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
  "Authorization": f"Bearer {api_key}",  # Use your actual OpenRouter API key
  "Content-Type": "application/json"
}

# Payload for the request to OpenRouter API
payload = {
  "model": "qwen/qwen3-30b-a3b:free",  # Specify the model you want to use
  "messages": [{"role": "user", "content": question}],
  "stream": True  # Enable streaming
}

# Initialize an empty buffer to collect data chunks
buffer = ""

# Send the streaming request to OpenRouter API
with requests.post(url, headers=headers, json=payload, stream=True) as r:
    # Iterate over chunks of data as they come in
    for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
        buffer += chunk  # Add the chunk to the buffer

        while True:
            # Find the next complete SSE line
            line_end = buffer.find('\n')
            if line_end == -1:
                break  # No complete line, keep waiting

            # Extract the line and update the buffer
            line = buffer[:line_end].strip()
            buffer = buffer[line_end + 1:]

            if line.startswith('data: '):
                data = line[6:]  # Extract data after the 'data: ' prefix
                if data == '[DONE]':
                    break  # End of stream, model has finished generating

                try:
                    data_obj = json.loads(data)  # Parse the JSON data
                    content = data_obj["choices"][0]["delta"].get("content")
                    if content:
                        print(content, end="", flush=True)  # Print content as it arrives
                except json.JSONDecodeError:
                    pass  # Handle cases where data is not in valid JSON format
