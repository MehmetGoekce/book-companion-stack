"""First agent in 10 lines (Chapter 1.6).

Source-of-truth for the snippet printed in Chapter 1.6 of *Agentic AI in
E-Commerce*. Ships in the companion repo at ``scripts/hello_agent.py``.

This is not yet an agent: it has no tools, no memory, and no access to
real product data. It is a single LLM call that proves the setup works
before Chapters 3 and 4 turn it into a real shopping assistant.

Run:

    export ANTHROPIC_API_KEY=sk-ant-...
    python scripts/hello_agent.py
"""

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system=(
        "You are a helpful shopping assistant for an outdoor sports store. "
        "You recommend products based on the customer's needs. "
        "Be specific about features and explain why you recommend each product."
    ),
    messages=[
        {"role": "user", "content": "What trail running shoes do you recommend for muddy terrain?"}
    ],
)

print(response.content[0].text)
