import json
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Config for local Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm_config = {
    "model": "ollama/phi3",  # requires `ollama pull phi3`
    "base_url": OLLAMA_BASE_URL,
    "temperature": 0.2,
}

# Define evaluation scenarios
scenarios = [
    {
        "input": "Summarize the Microsoft AI Partner Playbook into 3 actionable steps for a CIO.",
        "expected_keywords": ["AI Business Solutions", "Copilot", "Secure AI Productivity"],
    },
    {
        "input": "Explain what agentic AI solutions are in one paragraph.",
        "expected_keywords": ["agents", "actions", "automation"],
    },
]

def run_eval():
    results = []

    # Define agents
    researcher = AssistantAgent(
        name="Researcher",
        system_message="Research relevant information.",
        llm_config=llm_config,
    )
    analyst = AssistantAgent(
        name="Analyst",
        system_message="Analyze findings and extract key themes.",
        llm_config=llm_config,
    )
    reporter = AssistantAgent(
        name="Reporter",
        system_message="Produce a concise executive summary.",
        llm_config=llm_config,
    )
    user = UserProxyAgent(name="User")

    for scenario in scenarios:
        groupchat = GroupChat(
            agents=[user, researcher, analyst, reporter],
            messages=[],
            max_round=6,
        )
        manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

        print(f"\n🔎 Running scenario: {scenario['input']}")
        user_response = user.initiate_chat(manager, message=scenario["input"])

        output_text = str(user_response)
        score = sum(1 for kw in scenario["expected_keywords"] if kw.lower() in output_text.lower())
        total = len(scenario["expected_keywords"])

        result = {
            "input": scenario["input"],
            "output": output_text,
            "score": f"{score}/{total}",
            "passed": score == total,
        }
        print(f"✅ Output: {output_text}")
        print(f"📊 Score: {result['score']} | Pass: {result['passed']}")

        results.append(result)

    # Save results
    os.makedirs("eval/results", exist_ok=True)
    with open("eval/results/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n📁 Evaluation complete. Results saved to eval/results/eval_results.json")

if __name__ == "__main__":
    run_eval()