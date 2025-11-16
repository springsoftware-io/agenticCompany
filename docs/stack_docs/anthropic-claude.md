# Anthropic Claude API Documentation

**Official Docs:** https://docs.anthropic.com/

## Overview
Claude is Anthropic's family of AI models. We use Claude API version 0.40.0 for AI-powered code generation and task automation.

## Key Features
- Advanced language understanding and code generation
- Long context windows (up to 200K tokens)
- Streaming responses support
- Function calling capabilities
- Vision support (image understanding)

## Authentication
```python
import anthropic

client = anthropic.Anthropic(
    api_key="your-api-key"  # Set via ANTHROPIC_API_KEY env var
)
```

## Basic Usage in SeedGPT

### Creating Messages
```python
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "Your prompt here"}
    ]
)
```

### Streaming Responses
```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Hello"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Models Available
- **claude-3-5-sonnet-20241022**: Most capable, best for complex tasks
- **claude-3-opus**: Highest performance for difficult tasks
- **claude-3-sonnet**: Balanced performance and speed
- **claude-3-haiku**: Fastest, most compact

## Rate Limits & Pricing
- Rate limits vary by tier (check console.anthropic.com)
- Pricing based on input/output tokens
- Monitor usage through Anthropic Console

## Best Practices
1. **Use system prompts** for consistent behavior
2. **Stream responses** for better UX
3. **Handle rate limits** with exponential backoff
4. **Cache prompts** when possible to reduce costs
5. **Set appropriate max_tokens** to control costs

## Error Handling
```python
from anthropic import APIError, APIConnectionError, RateLimitError

try:
    response = client.messages.create(...)
except RateLimitError:
    # Handle rate limit
    pass
except APIConnectionError:
    # Handle connection issues
    pass
except APIError as e:
    # Handle other API errors
    print(f"Error: {e}")
```

## Environment Variables
```bash
ANTHROPIC_API_KEY=your-api-key-here
```

## Resources
- API Reference: https://docs.anthropic.com/en/api
- Python SDK: https://github.com/anthropics/anthropic-sdk-python
- Console: https://console.anthropic.com
- Pricing: https://www.anthropic.com/pricing

## Version Used in SeedGPT
```
anthropic==0.40.0
```
