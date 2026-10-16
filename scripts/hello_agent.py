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
    model="claude-sonnet-5-5",
    max_tokens=4096,
    system=(
        "You are a helpful shopping assistant for an outdoor sports store. "
        "You recommend products based on the customer's needs. "
        "Be specific about features and explain why you recommend each product."
    ),
    messages=[
        {"role": "user", "content": "What trail running shoes do you recommend for muddy terrain?"}
    ],
)

# The model may decline, or run out of room: check why it stopped before reading.
if response.stop_reason == "refusal":
    raise SystemExit("The model declined this request.")

# The reply is a list of blocks; thinking blocks can come first, so pick the text.
print("".join(block.text for block in response.content if block.type == "text"))

if response.stop_reason == "max_tokens":
    print("\n[Answer cut off at max_tokens. Raise the limit and run again.]")
