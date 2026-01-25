# Documentation Assistant Guide

**AI-Powered Help System for medBillDozer**

---

## Overview

The Documentation Assistant is an intelligent help system that appears in the sidebar of medBillDozer. It uses AI (OpenAI GPT or Google Gemini) to answer user questions by consulting the comprehensive documentation as its source of truth.

---

## Features

### 🤖 AI-Powered Responses

The assistant reads all documentation files and provides accurate answers to user questions:
- Quick Start Guide
- User Guide
- Documentation Index
- Project README

### ⚡ Quick Help Buttons

Four preset quick-help buttons for common questions:

1. **🚀 Getting Started** - "How do I get started with medBillDozer?"
2. **🔒 Privacy Info** - "Is my medical data private and secure?"
3. **💰 Savings** - "How do I interpret the savings estimates?"
4. **❓ Troubleshoot** - "My analysis failed. What should I do?"

### 💬 Conversation History

The assistant maintains a history of recent questions and answers during your session:
- Shows last 3 questions in expandable panels
- Clear history button to start fresh
- Most recent question expanded by default

### 🎯 Contextual Help

The assistant provides context-aware help messages based on your current action:

- **📝 Document Input** - Tips for preparing documents
- **🎯 Demo Documents** - How to use demo examples
- **⏳ Analyzing** - What's happening during analysis
- **✅ Results** - How to interpret findings
- **❌ Error** - Troubleshooting guidance

---

## How to Use

### Basic Usage

1. **Look at the sidebar** on the right side of the application
2. **Select an AI provider**: OpenAI or Gemini (requires API key)
3. **Click a quick help button** or **type your own question**
4. **Click "Ask Assistant"** to get an answer
5. **Review the response** in the expandable panel below

### Example Questions

**Getting Started:**
- "How do I install medBillDozer?"
- "What API keys do I need?"
- "Can I use this without an API key?"

**Using the App:**
- "How do I analyze my medical bill?"
- "What file formats are supported?"
- "Can I analyze multiple bills at once?"

**Understanding Results:**
- "What does 'duplicate charge' mean?"
- "How accurate are the savings estimates?"
- "What should I do if I find an error?"

**Privacy & Security:**
- "Where is my data stored?"
- "Is this HIPAA compliant?"
- "Which AI provider is most private?"

**Troubleshooting:**
- "Why did my analysis fail?"
- "I'm getting an API error. What do I do?"
- "No issues were found. Is that normal?"

---

## AI Provider Selection

### OpenAI (GPT-4o-mini)

**Pros:**
- Most accurate and comprehensive answers
- Excellent at interpreting complex questions
- Fast response times

**Cons:**
- Requires OpenAI API key
- Costs ~$0.001 per query

**Setup:**
```bash
export OPENAI_API_KEY="your-key-here"
```

### Google Gemini (2.0 Flash)

**Pros:**
- Very fast responses
- Good accuracy
- Often cheaper than OpenAI

**Cons:**
- Requires Google AI API key
- Slightly less detailed than GPT

**Setup:**
```bash
export GOOGLE_API_KEY="your-key-here"
```

---

## Technical Details

### How It Works

1. **Documentation Loading**: On startup, the assistant loads all documentation files into memory
2. **Context Building**: When you ask a question, it builds a comprehensive prompt containing:
   - All documentation content
   - Your specific question
   - Guidelines for answering accurately
3. **AI Processing**: The selected AI provider processes the prompt and generates an answer
4. **Response Display**: The answer appears in an expandable panel in the sidebar

### Documentation Sources

The assistant consults these files (in order):
1. `docs/QUICKSTART.md` - Quick start guide
2. `docs/USER_GUIDE.md` - Comprehensive user documentation
3. `docs/INDEX.md` - Documentation index and navigation
4. `docs/README.md` - Auto-generated overview

Total context: ~2,800 lines of documentation

### Response Quality

The assistant is instructed to:
- ✅ Answer ONLY from documentation (no hallucination)
- ✅ Be concise and helpful
- ✅ Provide specific section references when helpful
- ✅ Admit when it doesn't know
- ✅ Use friendly, supportive tone
- ✅ Include important disclaimers when relevant

---

## Contextual Help System

### Automatic Context Detection

The assistant displays different help messages based on your current activity:

| Context | When It Appears | Help Message |
|---------|----------------|--------------|
| **Input** | Document input area shown | Tips for pasting complete bill text |
| **Demo** | Demo documents section | How to use example documents |
| **Analyzing** | Analysis in progress | What's happening, typical wait time |
| **Results** | Analysis complete | How to interpret findings |
| **Error** | Something went wrong | Troubleshooting suggestions |

### Info Box Style

Contextual help appears as blue info boxes in the sidebar:
```
ℹ️ Document Input Help

Paste your complete medical bill, EOB, or receipt
text here. Include all details: headers, line items,
dates, and amounts.
```

---

## Best Practices

### For Users

**✅ DO:**
- Use quick help buttons for common questions
- Ask specific questions for better answers
- Read the full answer before asking follow-ups
- Check documentation links for deeper information

**❌ DON'T:**
- Ask questions outside the scope of medBillDozer
- Expect medical, legal, or financial advice
- Assume answers are 100% complete (verify with docs)
- Paste sensitive information into questions

### For Developers

**Extending the Assistant:**

1. **Add More Quick Help Buttons:**
   Edit `_modules/ui/doc_assistant.py`, add buttons in `render_doc_assistant()`

2. **Add Contextual Help:**
   Edit the `help_messages` dict in `render_contextual_help()`

3. **Update Documentation:**
   The assistant automatically picks up changes to docs files

4. **Change AI Settings:**
   Modify `get_answer_openai()` or `get_answer_gemini()` to adjust:
   - Model selection
   - Temperature (response creativity)
   - Max tokens (response length)

---

## Limitations

### What the Assistant CAN Do

✅ Answer questions about medBillDozer features
✅ Explain how to use the application
✅ Provide troubleshooting guidance
✅ Clarify documentation content
✅ Reference specific documentation sections

### What the Assistant CANNOT Do

❌ Provide medical advice
❌ Give legal guidance
❌ Interpret your specific bills (use the main analysis for that)
❌ Answer questions not covered in documentation
❌ Guarantee results or outcomes
❌ Make decisions for you

---

## Privacy & Data

### What Gets Sent to AI Providers

When you ask a question:
- ✅ Your question text
- ✅ All documentation content (public information)
- ❌ Your medical bills (NOT sent)
- ❌ Analysis results (NOT sent)
- ❌ Personal information (NOT sent)

### Data Retention

- **medBillDozer**: Conversation history cleared on browser close
- **AI Providers**: Subject to their data policies
  - [OpenAI Privacy Policy](https://openai.com/privacy)
  - [Google Privacy Policy](https://policies.google.com/privacy)

---

## Troubleshooting

### "API key error"

**Problem**: AI provider can't authenticate

**Solutions:**
1. Set the correct environment variable:
   - OpenAI: `export OPENAI_API_KEY="..."`
   - Gemini: `export GOOGLE_API_KEY="..."`
2. Restart the application
3. Check API key is valid and has credits

### "No response / Timeout"

**Problem**: AI provider not responding

**Solutions:**
1. Check internet connection
2. Try the other AI provider
3. Wait and try again (provider may be busy)
4. Check API service status

### "Answer doesn't make sense"

**Problem**: AI generated incorrect response

**Solutions:**
1. Rephrase your question more specifically
2. Try the other AI provider
3. Check the documentation directly
4. Clear history and try again

### "Assistant not appearing"

**Problem**: Sidebar doesn't show assistant

**Solutions:**
1. Refresh the browser page
2. Check browser console for errors
3. Verify `doc_assistant.py` is in `_modules/ui/`
4. Ensure documentation files exist in `docs/`

---

## Future Enhancements

Potential improvements for future versions:

- 🔮 **Multi-turn conversations** - Remember context from previous questions
- 🔍 **Smart search** - Suggest related documentation sections
- 📊 **Usage analytics** - Track common questions to improve docs
- 🌐 **Offline mode** - Local embedding-based search without API
- 🎨 **Rich formatting** - Code examples, tables, images in responses
- 🔔 **Proactive tips** - Suggest help based on user behavior
- 🌍 **Multi-language** - Answer questions in user's language

---

## API Reference

### DocumentationAssistant Class

```python
class DocumentationAssistant:
    """AI-powered documentation assistant."""

    def __init__(self):
        """Initialize and load documentation files."""

    def get_answer(self, question: str, provider: str = "openai") -> str:
        """Get AI-generated answer to question.

        Args:
            question: User's question
            provider: 'openai' or 'gemini'

        Returns:
            Answer text based on documentation
        """

    def search_docs(self, query: str) -> List[Dict]:
        """Search documentation for keyword matches.

        Args:
            query: Search term

        Returns:
            List of matching sections with previews
        """
```

### UI Functions

```python
def render_doc_assistant():
    """Render the documentation assistant in sidebar."""

def render_contextual_help(context: str):
    """Show context-aware help message.

    Args:
        context: 'input', 'demo', 'analyzing', 'results', or 'error'
    """
```

---

## Credits

The Documentation Assistant is powered by:
- **OpenAI GPT-4o-mini** or **Google Gemini 2.0 Flash**
- **medBillDozer Documentation** (2,800+ lines)
- **Streamlit** UI framework

---

## Feedback

Found a bug or have a suggestion?
- Report issues on GitHub
- Tag with `documentation-assistant` label
- Include: question asked, provider used, response received

---

**Happy documenting!** 🤖📚

