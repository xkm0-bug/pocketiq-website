"""The starter roadmap: eight hand-written lessons.

MoBo normally writes a roadmap and its lessons from what the learner says about
themselves. When the model can't be reached (no API key, no network, or a host
that blocks outbound calls), the site serves this instead, so Learning mode is
still worth using rather than showing an apology.

Titles here are matched exactly by /generate_article, so if you rename a step,
rename its key in STARTER_LESSONS too.
"""

STARTER_ROADMAP = [
    {"title": "Know your pocket money", "summary": "Add up everything that actually comes in each month."},
    {"title": "Track a week of spending", "summary": "Write down every rupee for seven days and see where it goes."},
    {"title": "Needs versus wants", "summary": "Sort your spending into two piles without lying to yourself."},
    {"title": "The 24-hour rule", "summary": "A simple wait that kills most impulse buys."},
    {"title": "Pay yourself first", "summary": "Save on the day money arrives, not from what's left."},
    {"title": "Set a savings goal", "summary": "Turn a thing you want into a monthly number and a date."},
    {"title": "How interest works", "summary": "Why money in a bank slowly grows, and why time matters."},
    {"title": "What a SIP actually is", "summary": "Small, regular investing, minus the jargon."},
]

STARTER_LESSONS = {
    "Know your pocket money": """
Most people can't say how much money they get in a month. They know the pocket money number, but not the rest: the ₹200 from a grandparent, the change left over from an errand, the Diwali envelope.

Start by writing all of it down for one month. Say you get ₹1,500 pocket money, ₹300 from relatives, and you keep about ₹100 in leftover change. Your real number is ₹1,900, not ₹1,500. That is about a quarter more than you thought you had, and you were probably spending it without noticing.

This is boring and it matters. Every other money skill, budgeting, saving, deciding whether you can afford something, depends on knowing this one number. If the number is wrong, everything built on it is wrong too.

Don't round up to feel better or round down to feel careful. Just write what came in.

**Try this week:** Open the notes app on your phone and list every rupee that came to you in the last 30 days. Add it up. That total is your monthly number.
""",
    "Track a week of spending": """
You don't need an app for this. You need seven days and some honesty.

Every time money leaves you, write down what it was and how much. ₹15 for a samosa. ₹20 for an auto share. ₹99 for a game top-up. UPI makes this easier than it used to be, because your payment history already has most of it. Cash is the part people forget.

At the end of the week, add it up by type: food, travel, phone, fun. Something will surprise you. For a lot of students it's the canteen. A ₹15 samosa every school day is about ₹350 a month, which is real money when your whole budget is ₹1,500.

The point isn't to feel bad about the samosa. It's to see it. You can't decide whether something is worth it if you don't know what it's costing you.

One week is enough to spot the pattern. You don't have to do this forever.

**Try this week:** Track every spend for seven days, cash included. On day seven, find your single biggest category.
""",
    "Needs versus wants": """
A need is something that causes a real problem if you skip it. A want is everything else. That sounds obvious until you try sorting your own spending.

A phone recharge is a need, because without it you can't call home or pay by UPI. The ₹299 plan with extra data for reels is partly a want. School shoes are a need. A third pair of sneakers is a want. Lunch is a need. Ordering in when there's food at home is a want.

Wants aren't bad. Spending on things you enjoy is half the point of having money. The trouble starts when wants get paid first and needs get whatever is left, or when you tell yourself a want is a need so you don't have to think about it.

A quick test: if you didn't buy it this month, what would actually happen? If the answer is "nothing much", it's a want.

**Try this week:** Take last week's spending and mark each item N or W. Add up the W pile. That's the money you have real choices about.
""",
    "The 24-hour rule": """
Most regret purchases happen fast. You see it, you want it, you pay, and a week later it's in a drawer.

The fix is a rule that sounds too simple to work: for anything over a set amount that you didn't plan to buy, wait 24 hours. Pick the amount yourself. If you get ₹1,500 a month, ₹300 is a sensible line.

Here is why it works. The wanting feeling is strongest in the first few minutes. Shopping apps know this, which is why they show timers and "only 2 left". A day later the feeling has usually faded, and you can ask a calmer question: do I still want this, and what am I giving up for it?

Sometimes the answer is yes. Then buy it, and enjoy it properly, because you chose it instead of falling into it. More often you'll have forgotten about it by morning.

Put it in your cart or screenshot it. That's allowed. You're not saying no, you're saying not yet.

**Try this week:** Set your own limit in rupees. The next time something crosses it, screenshot it and wait a day.
""",
    "Pay yourself first": """
The usual plan is to spend through the month and save whatever is left. The usual result is that nothing is left.

Flip the order. On the day money arrives, move your savings out first. Then spend the rest without guilt. If you get ₹1,500 and move ₹200 on day one, you live on ₹1,300. You'll adjust to ₹1,300 faster than you expect, the same way you'd adjust if your pocket money had always been ₹1,300.

Where you move it matters. Savings that sit in the same wallet or the same UPI account get spent. Give it to a parent to hold, put it in a separate bank account, or use a jar at home that's annoying to open. A little friction is the whole trick.

Start with an amount so small it feels silly. ₹100 is fine. The habit of doing it every month is worth more than the amount, and you can raise it later.

**Try this week:** Decide your number and where it will go. On the next day you receive money, move it before you buy anything.
""",
    "Set a savings goal": """
"I should save more" doesn't work, because there's nothing to aim at. "₹6,000 for headphones by next June" works, because it turns into a monthly number.

The math is one division. Price, minus what you already have, divided by what you can save each month, gives you how many months it takes. Headphones at ₹6,000, with ₹0 saved and ₹500 a month, take 12 months. If that's too long, you have three levers: save more each month, pick a cheaper version, or wait for a sale. ₹750 a month gets you there in 8.

Write the goal somewhere you'll see it, and keep the money separate from spending money. Watching the total climb is what keeps you going in month four, when it's stopped being exciting.

Be honest about the monthly number. A plan to save ₹1,000 from ₹1,500 will fail in three weeks. A plan to save ₹300 will actually happen.

The Goal Planner on the Tools page does this sum for you.

**Try this week:** Pick one thing you want that costs more than a month of pocket money. Work out how many months it would take.
""",
    "How interest works": """
When your money sits in a bank savings account, the bank pays you a small amount for keeping it there. That payment is interest. In India it's usually somewhere between 2.5 and 4 percent a year, depending on the bank.

On its own that's small. ₹1,000 at 3 percent earns ₹30 in a year. What makes it interesting is that next year you earn interest on ₹1,030, not ₹1,000. Your interest starts earning its own interest. This is called compounding.

Take a higher rate to see it clearly. ₹1,000 at 6 percent becomes ₹1,060 after one year. After two years it's ₹1,123.60, not ₹1,120. That extra ₹3.60 is interest on interest. It looks like nothing, but over 20 or 30 years it becomes most of the total.

That's why starting early beats starting big. Time is doing the work, and you have more of it than any adult you know.

Interest also runs the other way. When you borrow, on a loan or a credit card, you're the one paying it, and the rates are much higher.

**Try this week:** Ask a parent what interest rate their savings account pays. Work out what ₹5,000 would earn in a year at that rate.
""",
    "What a SIP actually is": """
SIP stands for Systematic Investment Plan. Ignore the name. It means putting the same amount of money into a mutual fund every month, automatically.

A mutual fund pools money from lots of people and buys shares in many companies at once. You own a small slice of all of them, so one company doing badly doesn't sink you. Many funds let you start a SIP with ₹500 a month, some with ₹100.

Putting in ₹500 a month for 10 years means you've invested ₹60,000. If the fund grew at 10 percent a year, you'd have roughly ₹1 lakh. But that 10 percent is an assumption, not a promise. Funds go up and down, some years they lose money, and nobody can tell you what yours will do.

The regular monthly habit helps here. When prices are low your ₹500 buys more, and when they're high it buys less, so you don't have to guess the right moment.

If you're under 18 you can't open one alone. A parent or guardian has to do it with you, which is a good reason to have the conversation.

**Try this week:** Ask an adult at home whether anyone in the family has a SIP, and how long it's been running.
""",
}
