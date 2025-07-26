Organized Guide to LLM Techniques and Implementations
This document compiles and structures the provided information on advanced LLM techniques using OpenAI APIs. It is organized by section for easy reference, retaining all key code examples, implementation details, and recommendations. Each section includes summaries, prompts, tools, code snippets, and important notes to facilitate integration into your LLM-based agentic project.

Section 1: Structured Outputs for Multi-Agent Systems (Aug 6, 2024)
This section demonstrates building a multi-agent system for data analysis using Structured Outputs (with strict: true for schema enforcement). Agents include Triaging, Data Processing, Analysis, and Visualization. It mitigates performance issues from too many tools by grouping them logically.

Key Benefits
Improves performance by specializing agents for sub-tasks.
Uses function calling with strict schemas to guarantee output format.
Environment Setup
python

Collapse

Wrap

Run

Copy
from openai import OpenAI
from IPython.display import Image
import json
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
client = OpenAI()
MODEL = "gpt-4o-2024-08-06"
System Prompts
Triaging Agent: Routes queries to relevant agents.
python

Collapse

Wrap

Run

Copy
triaging_system_prompt = """You are a Triaging Agent. Your role is to assess the user's query and route it to the relevant agents. The agents available are:
- Data Processing Agent: Cleans, transforms, and aggregates data.
- Analysis Agent: Performs statistical, correlation, and regression analysis.
- Visualization Agent: Creates bar charts, line charts, and pie charts.

Use the send_query_to_agents tool to forward the user's query to the relevant agents. Also, use the speak_to_user tool to get more information from the user if needed."""
Data Processing Agent:
python

Collapse

Wrap

Run

Copy
processing_system_prompt = """You are a Data Processing Agent. Your role is to clean, transform, and aggregate data using the following tools:
- clean_data
- transform_data
- aggregate_data"""
Analysis Agent:
python

Collapse

Wrap

Run

Copy
analysis_system_prompt = """You are an Analysis Agent. Your role is to perform statistical, correlation, and regression analysis using the following tools:
- stat_analysis
- correlation_analysis
- regression_analysis"""
Visualization Agent:
python

Collapse

Wrap

Run

Copy
visualization_system_prompt = """You are a Visualization Agent. Your role is to create bar charts, line charts, and pie charts using the following tools:
- create_bar_chart
- create_line_chart
- create_pie_chart"""
Tool Definitions
Tools are defined with strict: true for schema enforcement.

Triaging Tools:
python

Collapse

Wrap

Run

Copy
triage_tools = [
    {
        "type": "function",
        "function": {
            "name": "send_query_to_agents",
            "description": "Sends the user query to relevant agents based on their capabilities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agents": {"type": "array", "items": {"type": "string"}, "description": "An array of agent names to send the query to."},
                    "query": {"type": "string", "description": "The user query to send."}
                },
                "required": ["agents", "query"]
            }
        },
        "strict": True
    }
]
Preprocessing Tools (clean_data, transform_data, aggregate_data): Similar structure with parameters for data, rules, etc., and strict: true.
Analysis Tools (stat_analysis, correlation_analysis, regression_analysis): Parameters for data, variables, etc.
Visualization Tools (create_bar_chart, create_line_chart, create_pie_chart): Parameters for data, axes, labels.
Tool Execution Logic
Handles tool calls and appends results to conversation history.

python

Collapse

Wrap

Run

Copy
def execute_tool(tool_calls, messages):
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_arguments = json.loads(tool_call.function.arguments)
        if tool_name == 'clean_data':
            cleaned_df = clean_data(tool_arguments['data'])
            cleaned_data = {"cleaned_data": cleaned_df.to_dict()}
            messages.append({"role": "tool", "name": tool_name, "content": json.dumps(cleaned_data)})
            print('Cleaned data: ', cleaned_df)
        # ... (similar for other tools)
    return messages
Agent Handlers
Each sub-agent processes queries with its prompt and tools.

python

Collapse

Wrap

Run

Copy
def handle_data_processing_agent(query, conversation_messages):
    messages = [{"role": "system", "content": processing_system_prompt}]
    messages.append({"role": "user", "content": query})
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0, tools=preprocess_tools)
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])
    execute_tool(response.choices[0].message.tool_calls, conversation_messages)
# ... (similar for analysis and visualization)
User Query Handling
Routes query through triaging and executes sub-agents.

python

Collapse

Wrap

Run

Copy
def handle_user_message(user_query, conversation_messages=[]):
    user_message = {"role": "user", "content": user_query}
    conversation_messages.append(user_message)
    messages = [{"role": "system", "content": triaging_system_prompt}]
    messages.extend(conversation_messages)
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0, tools=triage_tools)
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == 'send_query_to_agents':
            agents = json.loads(tool_call.function.arguments)['agents']
            query = json.loads(tool_call.function.arguments)['query']
            for agent in agents:
                if agent == "Data Processing Agent":
                    handle_data_processing_agent(query, conversation_messages)
                # ... (similar for other agents)
    return conversation_messages
Recommendations
Use strict schemas to enforce outputs.
Group tools by agent to avoid performance degradation.
Simulate tool executions for brevity in examples.
Section 2: Function Calling with an OpenAPI Specification
Converts OpenAPI specs into function definitions for chat completions. Enables intelligent API calls based on user instructions.

Setup
python

Collapse

Wrap

Run

Copy
import os
import json
import jsonref
from openai import OpenAI
import requests
from pprint import pp
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
OpenAPI Spec Parsing
python

Collapse

Wrap

Run

Copy
def openapi_to_functions(openapi_spec):
    functions = []
    for path, methods in openapi_spec["paths"].items():
        for method, spec_with_ref in methods.items():
            spec = jsonref.replace_refs(spec_with_ref)
            function_name = spec.get("operationId")
            desc = spec.get("description") or spec.get("summary", "")
            schema = {"type": "object", "properties": {}}
            req_body = spec.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if req_body:
                schema["properties"]["requestBody"] = req_body
            params = spec.get("parameters", [])
            if params:
                param_properties = {param["name"]: param["schema"] for param in params if "schema" in param}
                schema["properties"]["parameters"] = {"type": "object", "properties": param_properties}
            functions.append({"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema}})
    return functions
Recommendations
Resolve JSON references ($ref) to avoid duplication.
Use operationId as function name.
Extract descriptions and parameters from spec fields.
Section 3: Using Tool Required for Customer Service
Forces tool calls with tool_choice='required'. Demonstrates a customer service flow with instructions and tools.

Setup
python

Collapse

Wrap

Run

Copy
import json
from openai import OpenAI
import os
client = OpenAI()
GPT_MODEL = 'gpt-4-turbo'
Tools and Instructions
python

Collapse

Wrap

Run

Copy
tools = [
    {"type": "function", "function": {"name": "speak_to_user", "description": "Use this to speak to the user...", "parameters": {...}}},
    {"type": "function", "function": {"name": "get_instructions", "description": "Used to get instructions...", "parameters": {...}}}
]
INSTRUCTIONS = [{"type": "fraud", "instructions": "..."}, ...]
assistant_system_prompt = """You are a customer service assistant..."""
Message Handling
python

Collapse

Wrap

Run

Copy
def submit_user_message(user_query, conversation_messages=[]):
    respond = False
    user_message = {"role":"user","content": user_query}
    conversation_messages.append(user_message)
    print(f"User: {user_query}")
    while respond is False:
        messages = [{"role": "system", "content": assistant_system_prompt}]
        [messages.append(x) for x in conversation_messages]
        response = client.chat.completions.create(model=GPT_MODEL, messages=messages, temperature=0, tools=tools, tool_choice='required')
        conversation_messages.append(response.choices[0].message)
        respond, conversation_messages = execute_function(response.choices[0].message,conversation_messages)
    return conversation_messages
Function Execution
python

Collapse

Wrap

Run

Copy
def execute_function(function_calls,messages):
    for function_call in function_calls.tool_calls:
        function_id = function_call.id
        function_name = function_call.function.name
        print(f"Calling function {function_name}")
        function_arguments = json.loads(function_call.function.arguments)
        if function_name == 'get_instructions':
            respond = False
            instruction_name = function_arguments['problem']
            instructions = [inst['instructions'] for inst in INSTRUCTIONS if inst['type'] == instruction_name][0]
            messages.append({"tool_call_id": function_id, "role": "tool", "name": function_name, "content": instructions})
        elif function_name == 'speak_to_user':
            respond = True
            messages.append({"tool_call_id": function_id, "role": "tool", "name": function_name, "content": function_arguments['message']})
            print(f"Assistant: {function_arguments['message']}")
    return (respond, messages)
Recommendations
Use tool_choice='required' for deterministic tool use.
Define exit points for control in flows like customer service.
Section 4: Introduction to Structured Outputs
Guarantees responses adhere to JSON schemas using strict: true. Examples: Math tutor, text summarization, entity extraction.

Math Tutor Example
python

Collapse

Wrap

Run

Copy
from pydantic import BaseModel
class MathReasoning(BaseModel):
    class Step(BaseModel):
        explanation: str
        output: str
    steps: list[Step]
    final_answer: str

def get_math_solution(question: str):
    completion = client.beta.chat.completions.parse(model=MODEL, messages=[...], response_format=MathReasoning)
    return completion.choices[0].message
Text Summarization Example
python

Collapse

Wrap

Run

Copy
class ArticleSummary(BaseModel):
    invented_year: int
    summary: str
    inventors: list[str]
    description: str
    class Concept(BaseModel):
        title: str
        description: str
    concepts: list[Concept]

def get_article_summary(text: str):
    completion = client.beta.chat.completions.parse(model=MODEL, temperature=0.2, messages=[...], response_format=ArticleSummary)
    return completion.choices[0].message.parsed
Entity Extraction Example
python

Collapse

Wrap

Run

Copy
from enum import Enum
class Category(str, Enum):
    shoes = "shoes"
    jackets = "jackets"
    tops = "tops"
    bottoms = "bottoms"

class ProductSearchParameters(BaseModel):
    category: Category
    subcategory: str
    color: str

def get_response(user_input, context):
    response = client.chat.completions.create(model=MODEL, temperature=0, messages=[...], tools=[openai.pydantic_function_tool(ProductSearchParameters, name="product_search", description="...")])
    return response.choices[0].message.tool_calls
Recommendations
Use Pydantic models with SDK parse helper for schemas.
Handle refusals via the refusal field for safety.
Section 5: Orchestrating Agents: Routines and Handoffs
Defines routines (prompts + tools) and handoffs (agents transferring control). Implements execution loops and function schemas.

Agent Definition
python

Collapse

Wrap

Run

Copy
from pydantic import BaseModel
class Agent(BaseModel):
    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: str = "You are a helpful Agent"
    tools: list = []
Function to Schema
python

Collapse

Wrap

Run

Copy
import inspect
def function_to_schema(func) -> dict:
    # ... (maps Python types to JSON schema)
    return {"type": "function", "function": {...}}
Execution Loop
python

Collapse

Wrap

Run

Copy
def run_full_turn(agent, messages):
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()
    while True:
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools_map = {tool.__name__: tool for tool in current_agent.tools}
        response = client.chat.completions.create(model=agent.model, messages=[{"role": "system", "content": current_agent.instructions}] + messages, tools=tool_schemas or None)
        message = response.choices[0].message
        messages.append(message)
        if message.content: print(f"{current_agent.name}:", message.content)
        if not message.tool_calls: break
        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools_map)
            if type(result) is Agent: current_agent = result; result = f"Transferred to {current_agent.name}."
            result_message = {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            messages.append(result_message)
    return Response(agent=current_agent, messages=messages[num_init_messages:])
Recommendations
Use routines for task grouping.
Implement handoffs via return types (e.g., Agent object).
Section 6: Web Search and States with Responses API
Stateful API for multi-turn, multimodal interactions with hosted tools like web_search.

Basic Usage
python

Collapse

Wrap

Run

Copy
response = client.responses.create(model="gpt-4o-mini", input="tell me a joke")
print(response.output[0].content[0].text)
With Web Search
python

Collapse

Wrap

Run

Copy
response = client.responses.create(model="gpt-4o", input="What's the latest news about AI?", tools=[{"type": "web_search"}])
Multimodal Example
python

Collapse

Wrap

Run

Copy
response_multimodal = client.responses.create(model="gpt-4o", input=[{"role": "user", "content": [{"type": "input_text", "text": "..."}, {"type": "input_image", "image_url": "..."}]}], tools=[{"type": "web_search"}])
Recommendations
Use for stateful conversations and hosted tools to reduce round trips.
Fork responses for branching conversations.
Section 7: Parallel Agents with the OpenAI Agents SDK
Runs multiple agents in parallel on the same input for efficiency.

Agent Definitions
python

Collapse

Wrap

Run

Copy
from agents import Agent, Runner
features_agent = Agent(name="FeaturesAgent", instructions="Extract the key product features from the review.")
# ... (similar for pros_cons_agent, sentiment_agent, recommend_agent)
meta_agent = Agent(name="MetaAgent", instructions="Combine them into a concise executive summary...")
Parallel Execution
python

Collapse

Wrap

Run

Copy
async def run_agent(agent, review_text: str):
    return await Runner.run(agent, review_text)

async def run_agents(review_text: str):
    responses = await asyncio.gather(*(run_agent(agent, review_text) for agent in parallel_agents))
    labeled_summaries = [f"### {resp.last_agent.name}\n{resp.final_output}" for resp in responses]
    collected_summaries = "\n".join(labeled_summaries)
    final_summary = await run_agent(meta_agent, collected_summaries)
    print('Final summary:', final_summary.final_output)
Recommendations
Parallelize for latency reduction on independent tasks.
Use "agent as tool" for dynamic planning.
Section 8: Multi-Agent Portfolio Collaboration with OpenAI Agents SDK
Orchestrates specialist agents (Macro, Fundamental, Quantitative) under a Portfolio Manager for investment analysis.

Architecture
Hub-and-spoke: Portfolio Manager coordinates specialists as tools.
Tools: MCP servers, managed tools (Code Interpreter, WebSearch), custom functions (FRED API).
Head PM Agent Code
python

Collapse

Wrap

Run

Copy
from agents import Agent, ModelSettings, function_tool
def build_head_pm_agent(fundamental, macro, quant, memo_edit_tool):
    # ... (defines tools from agents, parallel runner)
    return Agent(name="Head Portfolio Manager Agent", instructions=load_prompt("pm_base.md") + DISCLAIMER, model="gpt-4.1", tools=[...], model_settings=ModelSettings(parallel_tool_calls=True, tool_choice="auto", temperature=0))
Workflow Execution
python

Collapse

Wrap

Run

Copy
async def run_workflow():
    # ... (builds agents, runs Runner on head PM with query)
Recommendations
Use "agent as tool" for control and parallelism.
Modular prompts for consistency and auditability.
Trace workflows for observability.