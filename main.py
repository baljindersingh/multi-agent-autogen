from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os

# Configure Ollama endpoint (local LLM)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Shared config for agents
llm_config = {
    "model": "ollama/phi3",  # requires `ollama pull phi3`
    "base_url": OLLAMA_BASE_URL,
    "temperature": 0.2,
}

# Define agents
researcher = AssistantAgent(
    name="Researcher",
    system_message="You are a research assistant. Retrieve and summarize factual information from provided context or documents.",
    llm_config=llm_config,
)

analyst = AssistantAgent(
    name="Analyst",
    system_message="You are an analyst. Interpret research findings, identify key themes, and highlight business relevance.",
    llm_config=llm_config,
)

reporter = AssistantAgent(
    name="Reporter",
    system_message="You are a senior communicator. Present insights as an executive summary in clear, actionable language.",
    llm_config=llm_config,
)

# User proxy agent (acts as end-user)
user = UserProxyAgent(name="User")

# Multi-agent group chat
groupchat = GroupChat(
    agents=[user, researcher, analyst, reporter],
    messages=[],
    max_round=6  # limit to avoid infinite loops
)

manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)

if __name__ == "__main__":
    print("Starting Multi-Agent AutoGen demo with Ollama (phi3)...\n")
    user.initiate_chat(
        manager,
        message="Summarize the Microsoft AI Partner Playbook into 3 actionable steps for a CIO."
    )