# ai_tutor_sll_serve_claude

An AI tutor chatbot, to be hosted on [SciLifeLab Serve](https://serve.scilifelab.se).

It is a [Gradio](https://www.gradio.app/) chat app that sends each conversation
to a large language model (LLM) with a system prompt that makes the LLM act as
a tutor: it asks guiding questions and gives hints instead of answers.

## Files

| File                                     | Purpose                                     |
|------------------------------------------|---------------------------------------------|
| `app.py`                                 | The chatbot, including the tutor prompt     |
| `requirements.txt`                       | Python packages                             |
| `start-script.sh`                        | Start script, as required by Serve          |
| `Dockerfile`                             | Builds the image (non-root user, UID 1000)  |
| `.github/workflows/docker-image-ghcr.yml`| Publishes the image on ghcr.io on each push |

## Configuration

The app is configured with environment variables:

| Variable       | Required | Default          | Meaning                                  |
|----------------|----------|------------------|------------------------------------------|
| `LLM_API_KEY`  | yes      |                  | API key of the LLM provider              |
| `LLM_BASE_URL` | no       | OpenAI API       | Base URL of any OpenAI-compatible API    |
| `LLM_MODEL`    | no       | `gpt-4o-mini`    | Model name                               |
| `TUTOR_PROMPT` | no       | see `app.py`     | Replaces the default tutor system prompt |

**Never commit the API key**: the code of apps on Serve must be public.

## Run locally

```bash
docker build --platform linux/amd64 -t ai-tutor:v1 .
docker run --rm -it -p 7860:7860 -e LLM_API_KEY=your-key ai-tutor:v1
```

Then open <http://localhost:7860>.

## Deploy on SciLifeLab Serve

1. Push to `main`. GitHub Actions publishes the image as
   `ghcr.io/richelbilderbeek/ai_tutor_sll_serve_claude:<short-commit-sha>`.
2. Make the package public (GitHub → your profile → Packages →
   `ai_tutor_sll_serve_claude` → Package settings → Change visibility).
3. On Serve, create a project, then a *Custom app* (or *Gradio app*) with:
   - Port: `7860`
   - Image: `ghcr.io/richelbilderbeek/ai_tutor_sll_serve_claude:<short-commit-sha>`
   - Storage: none
   - Visibility: *Link* while testing
4. Ask the Serve team (serve@scilifelab.se) how to provide `LLM_API_KEY`
   to the app as a secret.

To update, push again and change the image tag in the app settings
to the new short commit SHA (Serve does not re-fetch an existing tag).

## Serve rules that apply

- No user accounts and no stored conversations: history only lives
  in the browser session.
- No sensitive data: the app tells users not to enter any.
- Do not log what users type.
