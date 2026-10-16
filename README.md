# book-companion-stack

Companion code for **Agentic AI in E-Commerce — A Practitioner's Guide**
by Mehmet Gökçe (Leanpub, Early Access).

Every code example in the book exists here as a runnable file with a test
next to it. Release tags track the book: check out the tag for the chapter
you are reading and the repository is in exactly the state the text describes.

| Tag | Book version | Contents |
|-----|--------------|----------|
| `v0.1.1-ch1` | v0.1 (Chapter 1) | `scripts/hello_agent.py` on `claude-sonnet-5-5`; picks the text block, handles refusal and `max_tokens` |
| `v0.1-ch1` | v0.1 (Chapter 1, superseded) | first version on `claude-sonnet-5`; kept so old links still resolve |

Later tags add the data pipeline, the Docker setup, and the shopping
assistant as their chapters are published.

## Run Chapter 1

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/MehmetGoekce/book-companion-stack.git
cd book-companion-stack
git checkout v0.1.1-ch1
uv sync
export ANTHROPIC_API_KEY=sk-ant-...
uv run python scripts/hello_agent.py
```

The script makes a single call to Claude and prints the answer. It is not
an agent yet — no tools, no memory, no product data. That is the point of
Chapter 1; Chapters 3 and 4 turn it into one.

## Tests

The tests run without an API key and without network access:

```bash
uv run --group dev pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE).
