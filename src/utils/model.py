from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

def get_model(model_name: str = 'claude-sonnet-4-20250514') -> ChatAnthropic:
  if model_name.startswith('claude'):
    model = ChatAnthropic(model=model_name)
  elif model_name.startswith('gpt'):
    model = ChatOpenAI(model=model_name)
  else:
    raise ValueError(f"Model {model_name} not supported")
  return model