from transformers import pipeline

# Load a pretrained summarization model
print("Loading NLP model...")

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

print("NLP model loaded successfully!")


def summarize_notice(notice):
    if not notice.strip():
        return "Please enter a notice."

    result = summarizer(
        notice,
        max_length=60,
        min_length=10,
        do_sample=False,
        truncation=True
    )

    return result[0]["summary_text"]


if __name__ == "__main__":
    notice = input("Paste your college notice:\n")

    summary = summarize_notice(notice)

    print("\nSimplified output:")
    print(summary)
