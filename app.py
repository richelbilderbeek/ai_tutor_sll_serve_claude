"""AI tutor chatbot for SciLifeLab Serve.

A Gradio chat app that sends every conversation to an LLM together with a
system prompt that turns the LLM into a tutor.

Configuration (environment variables):
- LLM_API_KEY:   API key for the LLM provider (required, never commit it)
- LLM_BASE_URL:  base URL of an OpenAI-compatible API (optional,
                 defaults to the OpenAI API)
- LLM_MODEL:     model name (optional, default: gpt-4o-mini)
- TUTOR_PROMPT:  overrides the default tutor system prompt (optional)

Chat history lives only in the browser session: nothing is stored or logged,
as required by SciLifeLab Serve.
"""

import os

import gradio as gr
from openai import OpenAI

DEFAULT_TUTOR_PROMPT = """You are a friendly, patient tutor.
Your goal is to help the student learn, not to do their work for them.
- Do not give the final answer directly. Ask guiding questions and give hints.
- Break problems into small steps and check understanding after each step.
- When the student makes a mistake, point to where it is and let them retry.
- Adapt to the student's level; use simple language and concrete examples.
- Encourage the student and keep answers short.
- If the student shares personal or sensitive information, remind them not to."""

TUTOR_PROMPT = os.environ.get("TUTOR_PROMPT", DEFAULT_TUTOR_PROMPT)
MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
PORT = int(os.environ.get("PORT", "7860"))


def make_client():
    """Create the LLM client, or None if no API key is set."""
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=os.environ.get("LLM_BASE_URL") or None)


client = make_client()


def to_text(content):
    """Convert a Gradio message content to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    if isinstance(content, dict):
        return content.get("text", "")
    return str(content)


def build_messages(message, history):
    """Build the list of messages to send to the LLM."""
    messages = [{"role": "system", "content": TUTOR_PROMPT}]
    for turn in history:
        if turn.get("role") in ("user", "assistant"):
            messages.append({"role": turn["role"], "content": to_text(turn["content"])})
    messages.append({"role": "user", "content": message})
    return messages


def chat(message, history):
    """Stream the tutor's reply."""
    if client is None:
        yield "The tutor is not configured: the LLM_API_KEY environment variable is missing."
        return
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=build_messages(message, history),
            stream=True,
        )
        reply = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                reply += chunk.choices[0].delta.content
                yield reply
    except Exception as e:  # show a readable error instead of crashing
        yield f"Sorry, something went wrong contacting the language model ({type(e).__name__})."


demo = gr.ChatInterface(
    fn=chat,
    title="AI tutor",
    description=(
        "An AI tutor that helps you learn by asking questions and giving hints. "
        "Do not enter personal or sensitive information. "
        "Your conversation is not saved."
    ),
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=PORT)
