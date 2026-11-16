import json
import os
import re
from datetime import datetime, timedelta
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from openai import OpenAI
from serpapi import GoogleSearch

from starter_content import STARTER_LESSONS, STARTER_ROADMAP

# Absolute paths everywhere: under a WSGI server (PythonAnywhere) the working
# directory is NOT the project folder, so anything relying on os.getcwd() ends
# up in the wrong place.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

ARTICLE_CACHE = {}
CACHE = {}
MAX_CHAT_HISTORY_MESSAGES = 12
# Rough USD->INR rate for converting foreign shopping listings. Approximate by
# design; update this and the matching copy in mobo.html when it drifts.
USD_TO_INR = 95

# Every model-facing prompt gets these two. The first avoids the em-dash habit;
# the second is the house voice, so MoBo sounds like a person who is good with
# money rather than a brochure.
NO_EM_DASH = "Do not use em dashes in your writing. Use commas, colons, or separate sentences instead."
VOICE = (
    "Voice: write like a sensible older cousin who is good with money, talking to a teenager in India. "
    "Short sentences. Say the useful thing first. Use specific rupee amounts sized to pocket money "
    "(₹15 samosas, ₹299 recharges, ₹1,500 a month), not vague advice. "
    "Never open with phrases like 'In today's world', 'Great question' or 'Let's dive in'. "
    "Avoid 'it's important to', 'remember that', 'financial journey', 'empower', 'unlock' and 'game-changer'. "
    "No emojis and no exclamation marks. Do not praise or flatter the reader. "
    "If something is boring but matters, say so plainly. "
    + NO_EM_DASH
)

DECISION_FALLBACK_RESPONSE = (
    "I can't reach my brain right now, so I can't ask you the usual questions. "
    "Until I'm back, try this: wait 24 hours, then ask whether you'd still pay for it in cash. "
    "The Tools page can also show what it costs you over a year."
)
LEARNING_FALLBACK_RESPONSE = (
    "I couldn't get through just then. Give it a minute and ask again. "
    "If it keeps failing, carry on with the lesson and note down the bit that's confusing."
)

# Learning has its own tutor persona and its own session history, so it never
# collides with (or inherits the purchase-only guardrails of) the Decision coach.
LEARNING_SYSTEM_PROMPT = (
    "You are MoBo, the tutor inside PocketIQ's Learning mode.\n\n"
    "You help teenagers and young adults in India understand money: budgeting, saving, investing, "
    "credit, loans, taxes, inflation, interest, banking, UPI, insurance, earning, scams, and everyday "
    "money habits.\n\n"
    "Rules:\n"
    "1. Answer the question directly. Lead with the answer, then explain.\n"
    "2. Keep replies to 2 to 5 sentences unless the learner asks for more.\n"
    "3. Use everyday Indian examples in rupees: pocket money, UPI, recharges, canteen snacks, "
    "subscriptions, bus fare, a first job.\n"
    "4. If the learner is reading a roadmap step, tie your answer back to it when that helps.\n"
    "5. You are NOT the purchase-decision coach. Never deflect a question because it isn't about "
    "buying something. Concepts, definitions, examples, calculations and 'how does X work' are your job.\n"
    "6. Only redirect if a question has nothing to do with money or the learner's studies.\n"
    "7. Never invent real-world returns, guaranteed rates or personal investment advice. Explain how "
    "things work, and suggest talking to a trusted adult before any big decision.\n"
    "8. If the learner sounds confused, try a different example instead of repeating the same one.\n\n"
    + VOICE
)

DECISION_SYSTEM_PROMPT = (
    "You are MoBo, the PocketIQ decision coach. You help teenagers and young adults in India decide "
    "whether something they want to buy is actually worth it.\n\n"
    "How a conversation goes:\n"
    "1. When they mention wanting something, ask clarifying questions ONE AT A TIME. You want to know: "
    "the price, how much money they have or get each month, why they want it, how often they'd use it, "
    "and whether it replaces or duplicates something they already own.\n"
    "2. Skip any question they have already answered. Usually three or four questions is enough.\n"
    "3. Once you know enough, stop asking and give your final call. It should say whether this looks "
    "thought-through or impulsive, what else that money could do for them, and your recommendation.\n"
    "4. End the final call with a last line in exactly this form, using one of the three options:\n"
    "VERDICT: Go for it\n"
    "VERDICT: Think twice\n"
    "VERDICT: Wait and save\n"
    "Right after the VERDICT line, add one more line naming the thing they're deciding on, "
    "in two to five words with no price, like:\n"
    "ITEM: New wireless earbuds\n"
    "Never write a VERDICT or ITEM line before the final call.\n"
    "5. After the final call, do not ask more questions. If they push back, answer briefly and "
    "only change the verdict if they give you new information.\n\n"
    "Be honest. Sometimes the right answer is to buy it, and you should say so without hedging. "
    "Never lecture or make them feel judged for wanting something. "
    "Keep every message under 90 words. Stay on purchase decisions only.\n\n"
    + VOICE
)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Server-side sessions.
    #
    # Flask's default sessions live entirely inside a cookie, which browsers cap
    # at roughly 4093 bytes. Conversation history plus a ~1.5KB system prompt
    # runs close to that ceiling, and once it is crossed the browser silently
    # drops the cookie: the session resets mid-conversation and MoBo forgets
    # everything the user already told it. Storing sessions on disk keeps the
    # cookie down to a short session id and removes the size limit entirely,
    # so history length is bounded only by MAX_CHAT_HISTORY_MESSAGES.
    app.config.update(
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR=os.path.join(BASE_DIR, "flask_session"),
        SESSION_FILE_THRESHOLD=500,   # cachelib prunes oldest beyond this
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_USE_SIGNER=True,      # sign the session id in the cookie
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # Only send the cookie over HTTPS in production. Off locally so the
        # dev server over plain http still works.
        SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV", "").lower() == "production",
    )

    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
    Session(app)
    return app

app = create_app()


@app.context_processor
def inject_current_year():
    """Lets templates print the real year (the shared footer used a hardcoded one)."""
    return {"current_year": datetime.now().year}

# ------------------- OPENAI CLIENT -------------------

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def get_serpapi_key():
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing SERPAPI_API_KEY")
    return api_key


def build_compare_fallback(item1, item2):
    return {
        "item1": {
            "title": item1,
            "price": None,
            "image": None,
            "link": None,
            "source": None,
        },
        "item2": {
            "title": item2,
            "price": None,
            "image": None,
            "link": None,
            "source": None,
        },
        "price1_inr": None,
        "price2_inr": None,
        "ratio": 0,
        "note": "Live prices aren't available right now, so there's nothing to compare. Try again later.",
    }


def is_recurring_price(price_text):
    if not price_text:
        return False
    normalized = price_text.lower()
    recurring_markers = ["/mo", "per month", "monthly", "emi", "/month", "mo."]
    return any(marker in normalized for marker in recurring_markers)


def format_extracted_price(product):
    extracted_price = product.get("extracted_price")
    if extracted_price in (None, ""):
        return None

    try:
        value = float(extracted_price)
    except (TypeError, ValueError):
        return None

    currency = product.get("currency")
    if currency == "USD":
        return f"${value:,.2f}"
    if currency == "INR":
        return f"₹{value:,.0f}"
    if currency:
        return f"{currency} {value:,.2f}"
    return f"{value:,.2f}"


def build_source_link(product, query):
    return (
        product.get("link")
        or product.get("product_link")
        or product.get("serpapi_link")
        or f"https://www.google.com/search?tbm=shop&q={quote_plus(query)}"
    )


def normalize_product(product, query):
    raw_price = product.get("price")
    display_price = raw_price

    if is_recurring_price(raw_price):
        display_price = format_extracted_price(product) or raw_price

    return {
        "title": product.get("title"),
        "price": display_price,
        "image": product.get("thumbnail"),
        "link": build_source_link(product, query),
        "source": product.get("source") or product.get("seller") or product.get("merchant_name"),
        "is_recurring_price": is_recurring_price(raw_price),
    }


def choose_best_product(results, query):
    products = results.get("shopping_results", [])
    if not products:
        return None

    one_time_products = [
        product for product in products
        if product.get("price") and not is_recurring_price(product.get("price"))
    ]
    if one_time_products:
        return normalize_product(one_time_products[0], query)

    extracted_price_products = [
        product for product in products
        if product.get("extracted_price") not in (None, "")
    ]
    if extracted_price_products:
        return normalize_product(extracted_price_products[0], query)

    return normalize_product(products[0], query)


def build_article_cache_key(topic, context, step_summary):
    return "||".join([topic.strip(), context.strip(), step_summary.strip()])

# ------------------- ROUTES -------------------


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/mobo/<mode>')
def mobo_mode(mode):
    if mode not in ["learning", "decision", "compare"]:
        mode = "learning"
    return render_template("mobo.html", mode=mode)


@app.route('/tools')
def tools():
    return render_template('tools.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ------------------- DECISION COACH -------------------

@app.route('/ask', methods=['POST'])
def ask():
    message = request.form.get('message', '').strip()
    if not message:
        return jsonify({'response': "Type what you're thinking of buying and I'll take it from there."})

    if 'chat_history' not in session:
        session['chat_history'] = [{"role": "system", "content": DECISION_SYSTEM_PROMPT}]

    chat_history = session['chat_history']
    chat_history.append({"role": "user", "content": message})

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()

        chat_history.append({"role": "assistant", "content": reply})
        if len(chat_history) > MAX_CHAT_HISTORY_MESSAGES:
            chat_history = [chat_history[0]] + chat_history[-(MAX_CHAT_HISTORY_MESSAGES - 1):]
        session['chat_history'] = chat_history

        return jsonify({'response': reply})

    except Exception as e:
        print("Ask error:", e)
        # Drop the message we just appended, so a retry doesn't send it twice.
        chat_history.pop()
        session['chat_history'] = chat_history
        return jsonify({'response': DECISION_FALLBACK_RESPONSE, 'offline': True})


@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    """Clear a conversation so the user can start fresh.

    Defaults to the decision chat; pass scope=learning or scope=all to clear
    the tutor history instead. The two histories are deliberately separate.
    """
    scope = request.form.get('scope', 'decision')

    if scope in ('decision', 'all'):
        session.pop('chat_history', None)
    if scope in ('learning', 'all'):
        session.pop('learning_chat_history', None)

    return jsonify({'ok': True, 'cleared': scope})


# ------------------- LEARNING TUTOR (separate from Decision) -------------------

@app.route('/ask_learning', methods=['POST'])
def ask_learning():
    message = request.form.get('message', '').strip()
    topic = request.form.get('topic', '').strip()
    context = request.form.get('context', '').strip()

    if not message:
        return jsonify({'response': "Type a question and I'll have a go at it."})

    if 'learning_chat_history' not in session:
        system_prompt = LEARNING_SYSTEM_PROMPT
        if context:
            system_prompt += f"\n\nThe learner described their situation as: {context}"
        session['learning_chat_history'] = [
            {"role": "system", "content": system_prompt}
        ]

    chat_history = session['learning_chat_history']

    # Tell the tutor which roadmap step the learner has open.
    user_content = message
    if topic:
        user_content = f"[The learner is currently reading the roadmap step: \"{topic}\"]\n\n{message}"

    chat_history.append({"role": "user", "content": user_content})

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            max_tokens=350
        )
        reply = response.choices[0].message.content.strip()

        chat_history.append({"role": "assistant", "content": reply})
        if len(chat_history) > MAX_CHAT_HISTORY_MESSAGES:
            chat_history = [chat_history[0]] + chat_history[-(MAX_CHAT_HISTORY_MESSAGES - 1):]
        session['learning_chat_history'] = chat_history

        return jsonify({'response': reply})

    except Exception as e:
        print("Ask learning error:", e)
        chat_history.pop()
        session['learning_chat_history'] = chat_history
        return jsonify({'response': LEARNING_FALLBACK_RESPONSE, 'offline': True})


# ------------------- LEARNING: ROADMAP AND LESSONS -------------------

def clean_roadmap(raw):
    """Keep only well-formed steps, so one bad item can't break the page."""
    steps = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if title:
            steps.append({"title": title, "summary": str(item.get("summary", "")).strip()})
    return steps[:10]


@app.route('/generate_roadmap', methods=['POST'])
def generate_roadmap():
    context = request.form.get("context", "").strip()
    if not context:
        return jsonify({"error": "Missing context"}), 400

    prompt = (
        "You are MoBo, a money mentor for teenagers in India.\n\n"
        f"Here is how the learner describes their situation:\n{context}\n\n"
        "Plan a personal roadmap of 8 to 10 steps that takes them from where they are now to "
        "noticeably more capable with money. Start at their actual level. If they already save, "
        "do not start with 'what is saving'. Order the steps so each one builds on the last, and "
        "make sure anything they said they want to get better at is covered.\n\n"
        "Each step has:\n"
        "- title: under 6 words, plain and specific, like a friend would say it. No 'Mastering', "
        "'Unlocking', '101', 'Basics of' or colons.\n"
        "- summary: one sentence under 18 words saying what they will be able to do afterwards.\n\n"
        "Return ONLY valid JSON, with nothing before or after it, in exactly this shape:\n"
        "[{\"title\": \"...\", \"summary\": \"...\"}, ...]\n"
        + NO_EM_DASH
    )

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700
        )
        text = response.choices[0].message.content.strip()

        try:
            roadmap = json.loads(text)
        except ValueError:
            # The model sometimes wraps the JSON in a code fence or a sentence.
            match = re.search(r'\[.*\]', text, re.S)
            roadmap = json.loads(match.group(0)) if match else []

        roadmap = clean_roadmap(roadmap)
        if len(roadmap) < 3:
            raise ValueError("Roadmap came back empty or malformed")

        return jsonify({"roadmap": roadmap})

    except Exception as e:
        print("Roadmap error:", e)
        # The hand-written starter roadmap, so Learning mode still works offline.
        return jsonify({"roadmap": STARTER_ROADMAP, "offline": True})


LESSON_LEVELS = {
    "standard": (
        "Write 170 to 220 words. Use plain paragraphs, with at most one short bulleted list. "
        "Include one worked example with real rupee amounts."
    ),
    "simpler": (
        "Explain it as if to a 12 year old who has never heard the term. Under 150 words. "
        "One everyday example. Do not use a finance word without explaining it in the same sentence."
    ),
    "deeper": (
        "Go one level deeper than a beginner lesson, in 250 to 300 words. Explain why it works, "
        "show a worked calculation with rupee amounts, and name one mistake people commonly make."
    ),
}


def offline_lesson(topic):
    """A hand-written lesson if we have one for this step, otherwise an honest placeholder."""
    if topic in STARTER_LESSONS:
        return STARTER_LESSONS[topic].strip()
    return (
        f"MoBo couldn't be reached, so this lesson on **{topic}** hasn't been written yet.\n\n"
        "Lessons here are written for you when you open them, which needs a working connection "
        "to the model. Tap **Try again** in a minute.\n\n"
        "**Meanwhile:** write down the one thing about this topic you'd most like explained. "
        "When MoBo is back, ask exactly that."
    )


@app.route('/generate_article', methods=['POST'])
def generate_article():
    topic = request.form.get('topic', '').strip()
    context = request.form.get('context', '').strip()
    step_summary = request.form.get('summary', '').strip()
    level = request.form.get('level', 'standard').strip()
    if level not in LESSON_LEVELS:
        level = "standard"

    if not topic:
        return jsonify({'article': "There's no lesson selected. Tap a step on your roadmap."})

    cache_key = build_article_cache_key(topic, context, step_summary) + "||" + level
    if cache_key in ARTICLE_CACHE:
        return jsonify({'article': ARTICLE_CACHE[cache_key]})

    context_block = ""
    if context:
        context_block += f"What the learner said about themselves: {context}\n"
    if step_summary:
        context_block += f"What this step is meant to cover: {step_summary}\n"

    prompt = (
        "You are MoBo, a money mentor for teenagers in India.\n\n"
        f"{context_block}\n"
        f"Write the lesson for the roadmap step: '{topic}'.\n"
        f"{LESSON_LEVELS[level]}\n"
        "Write it for this particular learner. If they mentioned an amount, a goal or a problem, "
        "use it in the example instead of a generic one.\n"
        "Do not repeat the title. Open with a specific situation this learner would recognise from "
        "their own week, not a definition and not 'let's say' or 'imagine'.\n"
        "Do not end paragraphs with a moral or a summary sentence. Skip words like 'impulsively', "
        "'priorities', 'mindful' and 'wisely'.\n"
        "Use rupees for every amount.\n"
        "Do not write a 'Key takeaways' section. End with one line that starts with "
        "'**Try this week:**' followed by a single small action they could actually do.\n"
        + VOICE
    )

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=650
        )

        article = response.choices[0].message.content.strip() if response and response.choices else ""
        if not article:
            raise ValueError("Empty lesson")

        ARTICLE_CACHE[cache_key] = article
        return jsonify({'article': article})

    except Exception as e:
        print("Lesson error:", e)
        return jsonify({'article': offline_lesson(topic), 'offline': True})


# ------------------- COMPARE -------------------

def get_product_data(query):
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": get_serpapi_key(),
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    try:
        return choose_best_product(results, query)
    except Exception:
        return None


def parse_price_to_inr(price_str):
    if not price_str:
        return None

    # INR
    match_inr = re.search(r"(₹|Rs\.?|INR)\s?([\d,]+)", price_str)
    if match_inr:
        return float(match_inr.group(2).replace(",", ""))

    # USD -> INR
    match_usd = re.search(r"\$ ?([\d,]+)", price_str)
    if match_usd:
        usd = float(match_usd.group(1).replace(",", ""))
        return usd * USD_TO_INR

    return None


@app.route('/compare_items', methods=['POST'])
def compare_items():
    item1 = request.form.get('item1', '').strip()
    item2 = request.form.get('item2', '').strip()

    if not item1 or not item2:
        return jsonify({'error': "Fill in both sides so there's something to compare."})

    try:
        def clean_query(q):
            if len(q.split()) == 1:
                return q + " best price"
            return q

        data1 = get_product_data(clean_query(item1))
        data2 = get_product_data(clean_query(item2))

        if not data1 or not data2:
            return jsonify({'error': "Couldn't find one of those. Try the exact model name, like \"MacBook Air M2\"."})

        p1 = parse_price_to_inr(data1.get("price"))
        p2 = parse_price_to_inr(data2.get("price"))

        if p1 and p2 and p2 != 0:
            ratio = round(p1 / p2, 1)
        else:
            ratio = 0

        return jsonify({
            "item1": data1,
            "item2": data2,
            "price1_inr": p1,
            "price2_inr": p2,
            "ratio": ratio
        })

    except Exception as e:
        print("Compare error:", e)
        return jsonify(build_compare_fallback(item1, item2))


if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
