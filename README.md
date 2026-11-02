# TCAI Model 001 Lite

## Overview

TCAI Model 001 Lite is a experimental artificial intelligence system made by Azul991354 just for fun because of boredom. Even though it started as an idea it has a strong system behind it. The system is built using Flask. It uses JSON files to keep data safe. This helps with making API keys for users. It also helps with custom system instructions. Learning new things without needing a complicated database.

## How It Works

The system works with main parts that copy some of the ways language models act and handle different situations:

1. **Multi-User API Key Architecture**:

People can make a key that is different for each user. The key starts with the letters `tcAI_`. Then has a random string of letters and numbers (like `tcAI_xxxxxxxxxxxx`). Each key is like a box inside a big file called `tcai_database.json`. This file keeps the memory and settings for each person.

2. **Dual-Layer System Prompt System**:

The model uses two kinds of instructions:

**Core Identity Prompt**: This is an instruction that says the model is TCAI Model 001 Lite made by Azul991354. This keeps the models identity the same.

**Custom User Prompt**: People can change the way the model acts using the `/api/set-address. The model mixes the instruction with what the user wants during the thinking process.

3. **Associative Learning Engine**:

of always giving the same answers TCAI has a way to learn. Using the `/api/teach` address people can add examples. These examples are like questions and answers. They are stored in the users memory file.

4. **. Chat Processing**:

When someone sends a message to `/api/chat` the system checks the users memory. It uses the instructions the user made and the new examples. Then it gives back a response that fits the conversation.

## API Endpoints Reference

### 1. Create API Key

- **Endpoint**: `POST /api/create-key`

- **Description**: Makes a key and starts a new profile for the user.

- **Response**: Gives back the api_key`.

### 2. Set Custom System Prompt

- **Endpoint**: `POST /api/set-prompt`

- **Header**: `Authorization: Bearer tcAI_your_key_here`

- **Body**: `{"system_prompt": "Your custom persona description }`

- **Description**: Changes the instructions the model follows.

### 3. Teach the Model

- **Endpoint**: `POST /api/teach`

- **Header**: `Authorization: Bearer tcAI_your_key_here`

- **Body**: `{": "trigger text" "response": "desired model response or code snippet"}`

- **Description**: Adds new knowledge to the users memory.

### 4. Chat Inference

- **Endpoint**: `POST /api/chat`

- **Header**: `Authorization: Bearer tcAI_your_key_here`

- **Body**: `{"message": "user input query"}`

- **Description**: Handles the message using the instructions and the knowledge the user added.

## Deployment and Persistence

The system works well on cloud services like Render. It uses files to save data. To keep the system running all the time people can use a service, like UptimeRobot. This service checks the page (`/`) every five minutes. This helps the system not go to sleep when no one is using it.
