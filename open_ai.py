from groq import Groq

client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
    stream=False,
)

print(chat_completion.choices[0].message.content)