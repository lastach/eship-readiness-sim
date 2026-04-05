import streamlit as st
import pandas as pd
import altair as alt
import random
import time
import re

st.set_page_config(
    page_title="ThermaLoop | Entrepreneurial Readiness Simulation",
    page_icon="🔥",
    layout="wide",
)

# ============== CUSTOM CSS FOR GAME-LIKE FEEL ==============
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(170deg, #0d1117 0%, #161b22 100%);
    color: #e6edf3;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }

/* ── Typography ── */
h1, h2, h3 { color: #58a6ff !important; }
h1 { font-size: 2.2rem !important; letter-spacing: -0.5px; }

/* ── Progress bar ── */
.progress-outer {
    background: #21262d; border-radius: 12px; height: 18px;
    margin: 0.8rem 0 1.6rem 0; overflow: hidden;
    border: 1px solid #30363d;
}
.progress-inner {
    height: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #238636 0%, #2ea043 50%, #56d364 100%);
    transition: width 0.6s ease;
    display: flex; align-items: center; justify-content: flex-end;
    padding-right: 8px; font-size: 11px; color: #fff; font-weight: 600;
}

/* ── Narrative box ── */
.narrative-box {
    background: #161b22; border-left: 4px solid #58a6ff;
    border-radius: 8px; padding: 1.2rem 1.4rem; margin: 1rem 0 1.6rem 0;
    font-size: 1.05rem; line-height: 1.6; color: #c9d1d9;
}
.narrative-box em { color: #79c0ff; }

/* ── Scenario card ── */
.scenario-card {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    font-size: 0.95rem; color: #c9d1d9;
}
.scenario-card strong { color: #58a6ff; }

/* ── Game header badge ── */
.game-badge {
    display: inline-block; background: #238636; color: #fff;
    font-weight: 700; font-size: 0.75rem; letter-spacing: 1.2px;
    padding: 4px 12px; border-radius: 20px; margin-bottom: 0.6rem;
    text-transform: uppercase;
}

/* ── Score card (results) ── */
.score-big {
    text-align: center; padding: 2rem;
    background: linear-gradient(135deg, #161b22, #0d1117);
    border: 2px solid #30363d; border-radius: 16px;
    margin-bottom: 1.5rem;
}
.score-big .number { font-size: 4rem; font-weight: 800; color: #58a6ff; }
.score-big .label { font-size: 1.1rem; color: #8b949e; margin-top: 0.4rem; }

/* ── Coaching box ── */
.coaching-box {
    background: #0d1117; border: 1px solid #238636;
    border-radius: 10px; padding: 1.2rem 1.4rem; margin: 1rem 0;
    font-size: 1rem; line-height: 1.6; color: #c9d1d9;
}
.coaching-box strong { color: #56d364; }

/* ── Button styling ── */
.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all 0.2s ease !important;
    color: #c9d1d9 !important;
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
}
.stButton > button:hover {
    background-color: #21262d !important;
    border-color: #58a6ff !important;
    color: #e6edf3 !important;
}

/* ── Step counter ── */
.step-counter {
    color: #8b949e; font-size: 0.85rem; margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


# ============== GLOBAL CONSTANTS ==============
COMPONENTS = [
    "Entrepreneurial Mindset",
    "Entrepreneurial Skills",
    "Resource Availability",
    "Entrepreneurship / Business Acumen",
]
COMP_WEIGHTS = {c: 25 for c in COMPONENTS}

MINDSET_SUBDIMS = [
    "Opportunity Recognition",
    "Resourcefulness",
    "Execution Bias",
    "Resilience & Adaptability",
    "Value Creation Focus",
]

MINDSET_DESCRIPTIONS = {
    "Opportunity Recognition": "Seeing unmet needs, behavior gaps, and potential value before others.",
    "Resourcefulness": "Creatively acquiring, leveraging, and recombining limited resources.",
    "Execution Bias": "Moving quickly, testing, iterating, and deciding with incomplete information.",
    "Resilience & Adaptability": "Staying steady and adjusting intelligently when conditions change.",
    "Value Creation Focus": "Prioritizing customers, real problems, and business impact over ego or ideas.",
}

# ============== NARRATIVE CONTEXT ==============
THERMALOOP_INTRO = """
You're **Alex**, the founder of **ThermaLoop** — a smart ventilation retrofit kit that cuts
building energy costs by up to 30% without ripping out existing HVAC systems.

You left your job six weeks ago. You have a working prototype, a handful of interested
building managers, and a shrinking savings account. Every decision from here shapes whether
ThermaLoop becomes a real business — or a good idea that never quite made it.

**This simulation puts you in the founder's seat.** You'll face real startup decisions across
five rounds, then assess your skills, resources, and business knowledge. At the end, you'll
get an honest readiness profile — not a grade, but a map of where you're strong and where
to focus next.
"""

GAME_NARRATIVES = {
    1: """*Week 3. Your inbox is full of mixed signals.* Building managers say different things.
Some love the concept. Others are polite but vague. A few are already hacking together their
own solutions. **Your job: separate real demand from noise.** Flag only the signals that
suggest genuine, actionable market opportunity.""",

    2: """*Week 5. Reality check.* You've got no budget for user research, no designer on call,
and limited engineering time. Welcome to startup life. **For each constraint, pick the move
you'd actually make** — not the textbook answer, the real one.""",

    3: """*Week 7. Time is ticking.* You've got limited runway and too many possible next steps.
The difference between founders who make it and those who don't often comes down to what they
do *next* — not what they plan. **Pick what you'd actually do in each situation.**""",

    4: """*Week 9. Things just went sideways.* A contractor missed a deadline. Your costs spiked.
A competitor made a move. Shocks like these are normal — how you respond defines your trajectory.
**Choose your real reaction, not the one that sounds best.**""",

    5: """*Week 11. Sprint planning.* You've got a budget of **{budget} cost units** and a list of
possible changes. Some are high-impact. Some feel productive but aren't. You can't do everything.
**Pick the features you'd actually ship this sprint** — stay within budget.""",

    6: """*Self-assessment checkpoint.* Before the next phase, rate yourself honestly on six core
startup skills. Then prove it — scenario rounds will test how you'd actually operate in each area.
**The gap between self-rating and scenario performance is often where the real insight lives.**""",

    7: """*Resource inventory.* Building a venture isn't just about hustle — it's about what you
can realistically tap into. Money, tools, people, connections, time, and support all matter.
**Answer based on what's actually available to you in the next 3–6 months.**""",

    8: """*Final round: Venture-building knowledge.* These questions test how you think about
problems, markets, business models, and growth. There are no trick questions — just real
tradeoffs that founders face every day.""",
}

# ============== GAME 1: CUSTOMER SIGNAL CARDS ==============
OPP_SCENARIOS = [
    {
        "key": "opp_1",
        "text": "20% of building managers export HVAC data weekly to fix errors via a manual spreadsheet workaround.",
        "is_opportunity": True,
    },
    {
        "key": "opp_2",
        "text": "Several building managers mention they'd like a mobile app dashboard 'someday.'",
        "is_opportunity": False,
    },
    {
        "key": "opp_3",
        "text": "40% of prospects start your demo workflow but never finish it.",
        "is_opportunity": True,
    },
    {
        "key": "opp_4",
        "text": "Your LinkedIn posts about smart ventilation get lots of likes but modest demo signups.",
        "is_opportunity": False,
    },
    {
        "key": "opp_5",
        "text": "Prospects say they'd 'maybe try a retrofit kit like this in the future.'",
        "is_opportunity": False,
    },
    {
        "key": "opp_6",
        "text": "Support emails repeatedly mention the same calibration bug that forces managers to redo setups.",
        "is_opportunity": True,
    },
    {
        "key": "opp_7",
        "text": "Several building managers have rigged their own sensor workarounds to get data ThermaLoop should provide.",
        "is_opportunity": True,
    },
    {
        "key": "opp_8",
        "text": "An industry blog post about smart ventilation trends gets traffic, but almost nobody requests a demo.",
        "is_opportunity": False,
    },
    {
        "key": "opp_9",
        "text": "You have a growing waitlist of building managers regularly following up asking when they can get access.",
        "is_opportunity": True,
    },
    {
        "key": "opp_10",
        "text": "Conference attendees say your booth was 'interesting,' but few accept a follow-up call.",
        "is_opportunity": False,
    },
]


def compute_opportunity_score():
    tp = fp = fn = 0
    for sc in OPP_SCENARIOS:
        selected = st.session_state.get(sc["key"], False)
        if sc["is_opportunity"]:
            if selected:
                tp += 1
            else:
                fn += 1
        else:
            if selected:
                fp += 1
    total_true = sum(1 for s in OPP_SCENARIOS if s["is_opportunity"])
    if total_true == 0:
        return 1.0
    raw = tp - 0.5 * fp - fn
    max_raw = total_true
    norm = max(0.0, min(1.0, raw / max_raw))
    return round(1 + 4 * norm, 2)


# ============== GAME 5: FEATURE BUDGET ==============
FEATURE_BUDGET = 20

VALUE_FEATURES = [
    {
        "key": "feat_a",
        "name": "Fix a calibration bug causing 25% of new installs to fail on first setup.",
        "cost": 7,
        "ideal_points": 5,
    },
    {
        "key": "feat_b",
        "name": "Add a dashboard color theme option.",
        "cost": 3,
        "ideal_points": 1,
    },
    {
        "key": "feat_c",
        "name": "Build a guided setup wizard that walks managers through their first retrofit in under 15 minutes.",
        "cost": 6,
        "ideal_points": 4,
    },
    {
        "key": "feat_d",
        "name": "Ship an experimental 'air quality mood ring' feature with no demand signals yet.",
        "cost": 5,
        "ideal_points": 1,
    },
    {
        "key": "feat_e",
        "name": "Run a small pilot with 10 ideal building managers, including onboarding and follow-up.",
        "cost": 6,
        "ideal_points": 4,
    },
    {
        "key": "feat_f",
        "name": "Polish minor dashboard details that only power users occasionally notice.",
        "cost": 2,
        "ideal_points": 2,
    },
    {
        "key": "feat_g",
        "name": "Add instrumentation to capture where managers drop off during setup.",
        "cost": 4,
        "ideal_points": 5,
    },
]


def compute_value_creation_score():
    selected = [
        f for f in VALUE_FEATURES if st.session_state.get(f["key"], False)
    ]
    if not selected:
        return 1.0
    selected_value = sum(f["ideal_points"] for f in selected)
    max_possible = sum(f["ideal_points"] for f in VALUE_FEATURES)
    norm = max(0.0, min(1.0, selected_value / max_possible))
    return round(1 + 4 * norm, 2)


# ============== MINDSET GAMES 2–4 ==============
MINDSET_QUESTIONS = {
    # Resourcefulness – Game 2
    "ms_res_1": {
        "subdim": "Resourcefulness",
        "prompt": "You need to understand why building managers drop ThermaLoop after install, but you have zero budget for research. What do you actually do first?",
        "options": [
            "Use existing signals (support tickets, cancellation emails) and talk directly to a few churned managers.",
            "Wait until you have budget for a formal study.",
            "Ask friends what they think about churn in general.",
            "Search online for articles about HVAC customer retention before talking to anyone.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_2": {
        "subdim": "Resourcefulness",
        "prompt": "You need to launch a landing page for ThermaLoop today, but your designer just quit.",
        "options": [
            "Use a no-code template tool and ship something basic that communicates the value prop.",
            "Wait for a new designer so it looks polished.",
            "Write copy now and wait for design time later.",
            "Mock it up in a slide deck and send screenshots to prospects.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_3": {
        "subdim": "Resourcefulness",
        "prompt": "You want to test a new 'predictive maintenance alert' feature but have no engineering time this month.",
        "options": [
            "Create a simple clickable mockup or fake-door test to gauge interest.",
            "Wait until engineers have time to build it properly.",
            "Write a long spec and share internally for feedback.",
            "Look at similar IoT tools and treat the idea as validated if they have it.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_4": {
        "subdim": "Resourcefulness",
        "prompt": "You only have access to 10 building managers for early testing of ThermaLoop.",
        "options": [
            "Run deep interviews and observe their actual workflows and pain points.",
            "Run a big quantitative survey with them.",
            "Don't test until you have a bigger audience.",
            "Read industry reports about smart buildings instead of talking to them.",
        ],
        "scores": [5, 3, 1, 2],
    },
    # Execution bias – Game 3
    "ms_exec_1": {
        "subdim": "Execution Bias",
        "prompt": "You have one afternoon to de-risk the ThermaLoop concept before a potential investor meeting. What do you actually do?",
        "options": [
            "Run 5 quick calls with building managers or set up a simple landing page test.",
            "Write a 20-page strategy doc mapping the next 2 years.",
            "Brainstorm product names and design a new logo.",
            "Search online for competitor examples and save them into a doc without contacting anyone.",
        ],
        "scores": [5, 1, 2, 2],
    },
    "ms_exec_2": {
        "subdim": "Execution Bias",
        "prompt": "You want to test interest in a 'multi-zone control' upgrade for ThermaLoop. What's your next step?",
        "options": [
            "Add a 'coming soon' button in the dashboard and track clicks plus follow-up interest.",
            "Build the full feature and launch quietly.",
            "Survey friends who don't manage buildings.",
            "Look at competitor feature lists and treat that as enough validation.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "ms_exec_3": {
        "subdim": "Execution Bias",
        "prompt": "You're torn between targeting small office buildings vs. large residential complexes. How do you proceed?",
        "options": [
            "Run two tiny tests in parallel — different landing pages — and compare response rates.",
            "Pick one based purely on your intuition.",
            "Wait until you can do a full market study.",
            "Ask a mentor which segment sounds more promising and go with that.",
        ],
        "scores": [5, 2, 1, 3],
    },
    "ms_exec_4": {
        "subdim": "Execution Bias",
        "prompt": "You ran a pilot with 10 buildings. Results are noisy but lean positive. What do you do?",
        "options": [
            "Make a small decision in the direction of the signal and keep testing.",
            "Ignore it and wait for perfectly clear data.",
            "Restart from scratch with a totally different approach.",
            "Ask an advisor whether they think you should trust the pilot data.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_exec_5": {
        "subdim": "Execution Bias",
        "prompt": "Your co-founder suggests a quick test that could disprove your core assumption about energy savings. Your move?",
        "options": [
            "Run the test and be ready to pivot if it fails.",
            "Avoid the test; you don't want to undermine the pitch.",
            "Delay the test until after the funding round.",
            "Ask an advisor whether it's worth testing at all.",
        ],
        "scores": [5, 1, 2, 3],
    },
    # Resilience & adaptability – Game 4
    "ms_resil_1": {
        "subdim": "Resilience & Adaptability",
        "prompt": "⚡ SHOCK: Your hardware contractor delays a critical sensor shipment by 3 weeks — right before your pilot launch.",
        "options": [
            "Do nothing and simply push the pilot timeline back.",
            "Replace the contractor entirely.",
            "Re-scope the pilot, adjust dependent work, and communicate proactively with pilot customers.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_2": {
        "subdim": "Resilience & Adaptability",
        "prompt": "⚡ SHOCK: Your customer acquisition cost jumps 40% overnight after a platform changes its ad algorithm.",
        "options": [
            "Keep campaigns running and see what happens.",
            "Kill all paid channels immediately.",
            "Shift spend, test new creatives, explore organic channels, and review funnel quality.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_3": {
        "subdim": "Resilience & Adaptability",
        "prompt": "⚡ SHOCK: A well-funded competitor suddenly launches a 'free tier' smart ventilation product in your space.",
        "options": [
            "Keep your current pricing and ignore them.",
            "Lower your price significantly and hope to keep up.",
            "Refocus on a segment or offer where you compete on value, service, and outcomes — not price.",
        ],
        "scores": [1, 2, 5],
    },
}

RESOURCEFULNESS_QIDS = ["ms_res_1", "ms_res_2", "ms_res_3", "ms_res_4"]
EXEC_QIDS = [
    qid
    for qid, q in MINDSET_QUESTIONS.items()
    if q["subdim"] == "Execution Bias"
]
RESIL_QIDS = ["ms_resil_1", "ms_resil_2", "ms_resil_3"]

# ============== SKILLS GAME ==============
SKILL_AREAS = [
    "Market Research & Marketing",
    "Operations",
    "Financial Management",
    "Product & Technical",
    "Sales & Networking",
    "Team & Strategy",
]

SKILL_DESCRIPTIONS = {
    "Market Research & Marketing": "Finding, understanding, and reaching the right customers.",
    "Operations": "Designing and running reliable processes and delivery.",
    "Financial Management": "Budgeting, runway, unit economics, and trade-offs.",
    "Product & Technical": "Designing and building solutions users can actually use.",
    "Sales & Networking": "Selling value and building relationships that move things forward.",
    "Team & Strategy": "Aligning people and priorities toward a coherent direction.",
}

SKILL_QUESTIONS = {
    "sk_mkt_1": {
        "skill": "Market Research & Marketing",
        "prompt": "ThermaLoop trial users aren't converting to paid. What do you do first?",
        "options": [
            "Interview 5–10 recent trial users about their decision.",
            "Run a broad online survey with anyone you can find.",
            "Change the homepage headline based on your intuition.",
            "Read marketing articles instead of talking to actual prospects.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_mkt_2": {
        "skill": "Market Research & Marketing",
        "prompt": "You want to identify the best early adopters for ThermaLoop. What's your move?",
        "options": [
            "Find a niche where the energy pain is sharpest and design messaging just for them.",
            "Target every building type with the same message.",
            "Copy a competitor's positioning.",
            "Ask a mentor who they think sounds like the right customer.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_prod_1": {
        "skill": "Product & Technical",
        "prompt": "You can only ship one change to ThermaLoop this sprint. Which do you choose?",
        "options": [
            "A fix for a calibration bug that blocks first-time setup.",
            "A 'nice to have' dashboard widget a few users casually mentioned.",
            "A flashy new visualization that will look good in demos.",
            "Ask an advisor for ideas and wait.",
        ],
        "scores": [5, 2, 3, 1],
    },
    "sk_prod_2": {
        "skill": "Product & Technical",
        "prompt": "You're unsure whether the ThermaLoop setup flow is intuitive. What do you do?",
        "options": [
            "Do 5 quick usability tests with target building managers.",
            "Ship it now; you'll hear complaints if it's bad.",
            "Ask your team what they think is confusing.",
            "Search for UX patterns and copy one without testing.",
        ],
        "scores": [5, 1, 3, 2],
    },
    "sk_sales_1": {
        "skill": "Sales & Networking",
        "prompt": "You have 10 warm leads from a building management conference and limited time. What's your approach?",
        "options": [
            "Send tailored messages referencing your conversation and schedule 1:1 demos.",
            "Send a broad email blast and hope some respond.",
            "Post about ThermaLoop on LinkedIn instead.",
            "Ask a mentor which lead to start with but delay outreach.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_sales_2": {
        "skill": "Sales & Networking",
        "prompt": "You meet someone at a conference who manages 50 buildings. They seem interested. What's your next step?",
        "options": [
            "Suggest a concrete next step — a small pilot in one of their buildings.",
            "Ask for a purchase commitment immediately.",
            "Wait to see if they reach out to you.",
            "Send them a deck without a clear ask or next step.",
        ],
        "scores": [5, 1, 2, 2],
    },
    "sk_fin_1": {
        "skill": "Financial Management",
        "prompt": "ThermaLoop has 3 months of runway left. What do you prioritize?",
        "options": [
            "Identify and cut low-ROI spend while doubling down on what's driving pipeline.",
            "Cut all spending, including things that fuel growth.",
            "Ignore runway and focus purely on perfecting the product.",
            "Ask a mentor if they think you should be worried yet.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_fin_2": {
        "skill": "Financial Management",
        "prompt": "Your cost to acquire a building manager is higher than expected, but those who convert stay for years.",
        "options": [
            "Check payback period and LTV, then decide how much you can afford to spend per customer.",
            "Shut off acquisition until the cost comes down.",
            "Ignore the numbers and focus on top-line growth.",
            "Search benchmarks and treat them as an exact template without checking your own data.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_ops_1": {
        "skill": "Operations",
        "prompt": "ThermaLoop support tickets are piling up. What's your first move?",
        "options": [
            "Look for patterns and fix the top root causes generating tickets.",
            "Hire more support staff immediately.",
            "Tell the team to 'work harder' this week.",
            "Ask a mentor if they think you need more staff.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_ops_2": {
        "skill": "Operations",
        "prompt": "The ThermaLoop install process works, but only you know how to do it. What now?",
        "options": [
            "Document it and train someone else so it's repeatable and you're not a bottleneck.",
            "Keep doing it yourself — it's faster.",
            "Pause installs while you figure out a better system.",
            "Record a quick video and hope people figure it out.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_team_1": {
        "skill": "Team & Strategy",
        "prompt": "Overall traction is flat, but one segment — mid-size office buildings — loves ThermaLoop. What now?",
        "options": [
            "Focus your roadmap and messaging on the segment that's working.",
            "Keep trying to serve every building type equally.",
            "Pause all changes while you think about pivoting.",
            "Ask a mentor whether the niche is 'big enough.'",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_team_2": {
        "skill": "Team & Strategy",
        "prompt": "Your small ThermaLoop team is busy, but progress on key metrics is slow.",
        "options": [
            "Narrow focus to a small number of high-leverage bets tied to your top metric.",
            "Add more projects so nobody is idle.",
            "Let each person pick whatever they want to work on.",
            "Share a productivity framework and hope habits shift.",
        ],
        "scores": [5, 1, 2, 3],
    },
}

SKILL_SLIDER_MAP = {
    "Market Research & Marketing": "s_skill_mkt",
    "Operations": "s_skill_ops",
    "Financial Management": "s_skill_fin",
    "Product & Technical": "s_skill_prod",
    "Sales & Networking": "s_skill_sales",
    "Team & Strategy": "s_skill_team",
}

SKILL_SCENARIO_MAP = {
    "Market Research & Marketing": ["sk_mkt_1", "sk_mkt_2"],
    "Operations": ["sk_ops_1", "sk_ops_2"],
    "Financial Management": ["sk_fin_1", "sk_fin_2"],
    "Product & Technical": ["sk_prod_1", "sk_prod_2"],
    "Sales & Networking": ["sk_sales_1", "sk_sales_2"],
    "Team & Strategy": ["sk_team_1", "sk_team_2"],
}

# ============== RESOURCES ==============
RESOURCE_SUBDIMS = [
    "Financial Resources",
    "Technology & Infrastructure",
    "Talent / Team",
    "Network",
    "Time",
    "Support",
]

RESOURCE_DESCRIPTIONS = {
    "Financial Resources": "Cash, savings, or funding you could realistically apply to a venture.",
    "Technology & Infrastructure": "Access to tools, platforms, or infrastructure to build and deliver.",
    "Talent / Team": "People you could involve: co-founders, employees, freelancers, or advisors.",
    "Network": "Connections to customers, partners, mentors, or gatekeepers.",
    "Time": "Hours per week you can reliably invest.",
    "Support": "Emotional and practical support for ambitious goals.",
}

# ============== ACUMEN QUIZ ==============
ACUMEN_SUBDIMS = [
    "Problem\u2013Solution Fit",
    "Market Viability",
    "Business Model Soundness",
    "Go-to-Market Readiness",
    "Operational Feasibility",
    "Scalability Potential",
]

ACUMEN_DESCRIPTIONS = {
    "Problem\u2013Solution Fit": "Real, urgent customer problem + clear solution that addresses it.",
    "Market Viability": "Defined target segment, reachable customers, credible demand, differentiation.",
    "Business Model Soundness": "Pricing, unit economics, cost structure, and path to profitability.",
    "Go-to-Market Readiness": "Validated channels, messaging, acquisition strategy.",
    "Operational Feasibility": "Ability to deliver reliably given tech, supply, and processes.",
    "Scalability Potential": "Model, market, and operations can grow without breaking.",
}

ACUMEN_QUESTIONS = {
    "ac_ps_fit": {
        "subdim": "Problem\u2013Solution Fit",
        "prompt": "Which signal shows the strongest evidence that ThermaLoop solves a real problem?",
        "options": [
            "People say the concept is 'cool' in casual conversation.",
            "A segment of building managers repeatedly describes the same painful problem ThermaLoop addresses.",
            "Your landing page has a high click-through rate from ads.",
        ],
        "scores": [2, 5, 3],
    },
    "ac_ps_fit_2": {
        "subdim": "Problem\u2013Solution Fit",
        "prompt": "You hear different problems from different types of buildings. What's your next step?",
        "options": [
            "Pick the problem you personally find most interesting.",
            "Cluster buildings by similar needs and pains, and focus on one tight group first.",
            "Try to build a product that solves all of them at once.",
        ],
        "scores": [2, 5, 1],
    },
    "ac_market": {
        "subdim": "Market Viability",
        "prompt": "Which of these market situations is most promising for ThermaLoop?",
        "options": [
            "Huge possible market (all commercial buildings), but you don't know who to target first.",
            "A smaller, clearly defined group (mid-size offices in the Northeast) you can reliably reach.",
            "A big market with many HVAC competitors and no clear angle.",
        ],
        "scores": [3, 5, 2],
    },
    "ac_model": {
        "subdim": "Business Model Soundness",
        "prompt": "Which business model is healthiest over time?",
        "options": [
            "High price point, but each install costs more to deliver than the customer pays.",
            "Moderate price, high margin, and a clear path to recurring monitoring revenue.",
            "Low price, unclear costs, and no idea how many buildings you need to break even.",
        ],
        "scores": [1, 5, 2],
    },
    "ac_gtm": {
        "subdim": "Go-to-Market Readiness",
        "prompt": "Which description sounds most ready to scale customer acquisition?",
        "options": [
            "You plan to grow through word-of-mouth, but have no path to your first 10 customers.",
            "You've tested a few channels and have one that reliably brings qualified building manager leads.",
            "You plan to 'go viral' at a trade show but have no follow-up process mapped.",
        ],
        "scores": [1, 5, 1],
    },
    "ac_ops": {
        "subdim": "Operational Feasibility",
        "prompt": "Which setup is most likely to deliver ThermaLoop installs consistently?",
        "options": [
            "You rely on a manual process only you understand.",
            "You have documented install procedures and can train technicians to deliver.",
            "You plan to figure out delivery logistics after demand shows up.",
        ],
        "scores": [2, 5, 1],
    },
    "ac_scale": {
        "subdim": "Scalability Potential",
        "prompt": "Which of these ThermaLoop approaches scales best?",
        "options": [
            "Each install requires extensive custom engineering from you personally.",
            "Most of the value is delivered through standardized hardware + software, with minimal custom work.",
            "You depend on rare, highly specialized HVAC engineers for every installation.",
        ],
        "scores": [2, 5, 1],
    },
}

# ============== SESSION STATE ==============
if "page" not in st.session_state:
    st.session_state.page = 0
if "max_page" not in st.session_state:
    st.session_state.max_page = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "res_q_idx" not in st.session_state:
    st.session_state.res_q_idx = 0

# one-time defaults for resources/support
if "defaults_initialized" not in st.session_state:
    defaults = {
        "res_fin_level": 3,
        "res_tech_level": 3,
        "res_talent_level": 3,
        "res_network_level": 3,
        "res_time_pattern": None,
        "sup_brainstorm": False,
        "sup_tactical": False,
        "sup_emotional": False,
        "sup_intros": False,
        "sup_reaction": None,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)
    st.session_state.defaults_initialized = True


def go_to(page_idx: int):
    st.session_state.page = page_idx
    if page_idx > st.session_state.max_page:
        st.session_state.max_page = page_idx
    st.rerun()


# ============== UI HELPERS ==============
def toggle_flag(state_key: str):
    st.session_state[state_key] = not st.session_state.get(state_key, False)


def set_choice(state_key: str, value):
    st.session_state[state_key] = value


def ensure_order(order_key: str, n: int):
    if order_key not in st.session_state:
        order = list(range(n))
        random.shuffle(order)
        st.session_state[order_key] = order
    return st.session_state[order_key]


def render_toggle_card_multi(state_key: str, text: str, suffix: str = ""):
    selected = st.session_state.get(state_key, False)
    label_text = text + (f" \n_{suffix}_" if suffix else "")
    label = f"\u2705 {label_text}" if selected else label_text
    st.button(
        label,
        key=f"btn_{state_key}",
        use_container_width=True,
        on_click=toggle_flag,
        args=(state_key,),
    )


def render_choice_cards(qid: str, prompt: str, options: list):
    st.markdown(f"**{prompt}**")
    order = ensure_order(f"{qid}_order", len(options))
    current = st.session_state.get(f"{qid}_choice", None)
    for pos, opt_idx in enumerate(order):
        opt = options[opt_idx]
        selected = current == opt_idx
        label = f"\u2705 {opt}" if selected else opt
        st.button(
            label,
            key=f"{qid}_opt_{pos}",
            use_container_width=True,
            on_click=set_choice,
            args=(f"{qid}_choice", opt_idx),
        )
    st.markdown("---")


def get_mc_score(qdict, qid: str):
    q = qdict[qid]
    idx = st.session_state.get(f"{qid}_choice", None)
    if idx is None:
        return None
    if 0 <= idx < len(q["scores"]):
        return float(q["scores"][idx])
    return None


def render_progress_bar(current_page, total_pages):
    pct = int((current_page / (total_pages - 1)) * 100) if total_pages > 1 else 0
    st.markdown(
        f"""<div class="progress-outer">
            <div class="progress-inner" style="width:{pct}%">{pct}%</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_narrative(text):
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = html.replace('\n', '<br>')
    st.markdown(f'<div class="narrative-box">{html}</div>', unsafe_allow_html=True)


def render_game_badge(label):
    st.markdown(f'<div class="game-badge">{label}</div>', unsafe_allow_html=True)


# ============== SCORING FUNCTIONS ==============
def compute_mindset_scores():
    values = {s: [] for s in MINDSET_SUBDIMS}
    values["Opportunity Recognition"].append(compute_opportunity_score())
    values["Value Creation Focus"].append(compute_value_creation_score())
    for qid, q in MINDSET_QUESTIONS.items():
        s = get_mc_score(MINDSET_QUESTIONS, qid)
        if s is None:
            continue
        values[q["subdim"]].append(s)
    sub_scores = {}
    for sd in MINDSET_SUBDIMS:
        sub_scores[sd] = (
            round(sum(values[sd]) / len(values[sd]), 2) if values[sd] else 1.0
        )
    overall = round(sum(sub_scores.values()) / len(MINDSET_SUBDIMS), 2)
    return overall, sub_scores


def compute_skill_scores():
    skill_scores = {}
    for skill in SKILL_AREAS:
        vals = []
        slider_key = SKILL_SLIDER_MAP.get(skill)
        if slider_key is not None:
            v = st.session_state.get(slider_key)
            if v is not None:
                vals.append(float(v))
        for sid in SKILL_SCENARIO_MAP.get(skill, []):
            s = get_mc_score(SKILL_QUESTIONS, sid)
            if s is not None:
                vals.append(s)
        skill_scores[skill] = (
            round(sum(vals) / len(vals), 2) if vals else 1.0
        )
    overall = round(sum(skill_scores.values()) / len(SKILL_AREAS), 2)
    return overall, skill_scores


def compute_resource_scores():
    fin = float(st.session_state.get("res_fin_level", 3))
    tech = float(st.session_state.get("res_tech_level", 3))
    talent = float(st.session_state.get("res_talent_level", 3))
    network = float(st.session_state.get("res_network_level", 3))
    time_choice = st.session_state.get("res_time_pattern")
    time_map = {
        "25+ hours most weeks": 5,
        "10\u201325 hours most weeks": 4,
        "5\u201310 hours in irregular pockets": 3,
        "Rarely have focused time": 1,
    }
    time_score = float(time_map.get(time_choice, 2))
    support_count = 0
    for key in ["sup_brainstorm", "sup_emotional", "sup_tactical", "sup_intros"]:
        if st.session_state.get(key, False):
            support_count += 1
    support_react = st.session_state.get("sup_reaction")
    react_map = {
        "Mostly encouraging and try to help": 5,
        "Neutral or politely interested": 3,
        "Often skeptical or discouraging": 1,
    }
    react_score = float(react_map.get(support_react, 3))
    support_base = 1 + (support_count / 4.0) * 4
    support_score = round((support_base + react_score) / 2.0, 2)
    sub_scores = {
        "Financial Resources": fin,
        "Technology & Infrastructure": tech,
        "Talent / Team": talent,
        "Network": network,
        "Time": time_score,
        "Support": support_score,
    }
    overall = round(sum(sub_scores.values()) / len(sub_scores), 2)
    return overall, sub_scores


def compute_acumen_scores():
    values = {s: [] for s in ACUMEN_SUBDIMS}
    for qid, q in ACUMEN_QUESTIONS.items():
        s = get_mc_score(ACUMEN_QUESTIONS, qid)
        if s is None:
            continue
        values[q["subdim"]].append(s)
    sub_scores = {}
    for sd in ACUMEN_SUBDIMS:
        sub_scores[sd] = (
            round(sum(values[sd]) / len(values[sd]), 2) if values[sd] else 1.0
        )
    overall = round(sum(sub_scores.values()) / len(ACUMEN_SUBDIMS), 2)
    return overall, sub_scores


def compute_overall_scores():
    mindset_overall, mindset_sub = compute_mindset_scores()
    skills_overall, skills_sub = compute_skill_scores()
    res_overall, res_sub = compute_resource_scores()
    ac_overall, ac_sub = compute_acumen_scores()
    comp_scores = {
        "Entrepreneurial Mindset": mindset_overall,
        "Entrepreneurial Skills": skills_overall,
        "Resource Availability": res_overall,
        "Entrepreneurship / Business Acumen": ac_overall,
    }
    total = 0.0
    for comp, score in comp_scores.items():
        total += (score / 5.0) * COMP_WEIGHTS[comp]
    total = round(total, 1)
    return (
        total,
        comp_scores,
        {
            "mindset": mindset_sub,
            "skills": skills_sub,
            "resources": res_sub,
            "acumen": ac_sub,
        },
    )


def readiness_label(total_score):
    if total_score >= 85:
        return "\U0001f680 High readiness — you're positioned to pursue or accelerate a venture."
    elif total_score >= 70:
        return "\U0001f4aa Strong potential — ready for more serious experiments and real-world traction."
    elif total_score >= 50:
        return "\U0001f331 Early-stage readiness — good time to build specific muscles through low-risk reps."
    else:
        return "\U0001f9f1 Foundation-building phase — focus on learning, testing, and stacking small wins."


def coaching_narrative(total_score, comp_scores, sub_scores):
    """Generate personalized coaching narrative based on scores."""
    sorted_comps = sorted(COMPONENTS, key=lambda c: comp_scores[c])
    weakest = sorted_comps[0]
    strongest = sorted_comps[-1]

    # Find weakest subdimension across all categories
    all_subs = []
    sub_labels = {
        "mindset": "Mindset",
        "skills": "Skills",
        "resources": "Resources",
        "acumen": "Business Acumen",
    }
    for cat, subs in sub_scores.items():
        for name, score in subs.items():
            all_subs.append((name, score, sub_labels[cat]))
    all_subs.sort(key=lambda x: x[1])
    weakest_sub = all_subs[0] if all_subs else None
    strongest_sub = all_subs[-1] if all_subs else None

    lines = []

    if total_score >= 85:
        lines.append(
            f"You're showing strong readiness across the board. Your top area is **{strongest}** "
            f"— lean into that as your competitive edge."
        )
    elif total_score >= 70:
        lines.append(
            f"You've got a solid foundation. **{strongest}** is clearly a strength for you. "
            f"The biggest unlock right now is probably in **{weakest}** — that's where focused "
            f"attention will compound fastest."
        )
    elif total_score >= 50:
        lines.append(
            f"You're in early-stage territory, which is exactly where most founders start. "
            f"Your strongest area is **{strongest}**, which gives you something real to build from. "
            f"**{weakest}** is your biggest gap — and addressing it doesn't require a huge leap, "
            f"just deliberate practice."
        )
    else:
        lines.append(
            f"You're in foundation-building mode. That's not a verdict — it's a starting point. "
            f"**{strongest}** shows you have genuine capacity. Start there and use it as a "
            f"launchpad to build **{weakest}** through small, low-risk experiments."
        )

    if weakest_sub:
        lines.append(
            f"\n\nYour thinnest specific area is **{weakest_sub[0]}** ({weakest_sub[1]:.1f}/5, "
            f"under {weakest_sub[2]}). That's your highest-leverage development target."
        )

    if strongest_sub:
        lines.append(
            f"Your strongest specific area is **{strongest_sub[0]}** ({strongest_sub[1]:.1f}/5) "
            f"— protect and leverage that."
        )

    return "\n\n".join(lines)


# ============== NAVIGATION ==============
PAGE_LABELS = [
    "Intro",
    "Round 1: Customer Signals",
    "Round 2: Constraints",
    "Round 3: Execution",
    "Round 4: Shocks",
    "Round 5: Sprint Planning",
    "Skills Assessment",
    "Resources",
    "Business Knowledge",
    "Readiness Profile",
]

TOTAL_PAGES = len(PAGE_LABELS)

# ── Header ──
st.markdown("## \U0001f525 ThermaLoop | Entrepreneurial Readiness Simulation")
render_progress_bar(st.session_state.page, TOTAL_PAGES)

# ── Minimal nav (step counter only) ──
st.markdown(
    f'<div class="step-counter">{PAGE_LABELS[st.session_state.page]} &nbsp;·&nbsp; '
    f"Step {st.session_state.page + 1} of {TOTAL_PAGES}</div>",
    unsafe_allow_html=True,
)

page = st.session_state.page

# ============== PAGES ==============

# ── Intro ──
if page == 0:
    st.markdown("### The Setup")
    render_narrative(THERMALOOP_INTRO)

    st.markdown("#### What you'll do:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**5 Decision Rounds** testing your entrepreneurial mindset:
1. Spot real customer signals vs. noise
2. Navigate real constraints with zero budget
3. Make fast calls with incomplete info
4. React to unexpected shocks
5. Prioritize a sprint under budget pressure
""")
    with col2:
        st.markdown("""
**3 Assessment Sections** mapping your readiness:
- Skills self-rating + scenario proof
- Resource inventory
- Venture-building knowledge check

Then: your **Readiness Profile** — an honest map, not a grade.
""")

    st.markdown("---")
    if st.button("\U0001f3ae  Begin Simulation", use_container_width=True):
        go_to(1)

# ── Game 1: Customer Signals ──
elif page == 1:
    render_game_badge("Round 1 of 5 — Mindset")
    st.markdown("### Customer Signals")
    render_narrative(GAME_NARRATIVES[1])

    st.markdown("**Tap each card you believe represents a strong signal of real, fixable demand.**")
    cols = st.columns(2)
    for idx, sc in enumerate(OPP_SCENARIOS):
        with cols[idx % 2]:
            render_toggle_card_multi(sc["key"], sc["text"])

    flagged = sum(1 for sc in OPP_SCENARIOS if st.session_state.get(sc["key"], False))
    st.caption(f"{flagged} signal(s) flagged")

    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("Continue \u25b8", use_container_width=True):
            go_to(2)

# ── Game 2: Constraint Cards ──
elif page == 2:
    render_game_badge("Round 2 of 5 — Mindset")
    st.markdown("### Constraint Cards")
    render_narrative(GAME_NARRATIVES[2])

    idx = st.session_state.res_q_idx
    idx = max(0, min(idx, len(RESOURCEFULNESS_QIDS) - 1))
    st.session_state.res_q_idx = idx
    current_qid = RESOURCEFULNESS_QIDS[idx]
    q = MINDSET_QUESTIONS[current_qid]

    st.markdown(f"**Decision {idx + 1} of {len(RESOURCEFULNESS_QIDS)}**")
    render_choice_cards(current_qid, q["prompt"], q["options"])

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("\u25c2 Previous", disabled=(idx == 0)):
            st.session_state.res_q_idx -= 1
            st.rerun()
    with c2:
        if st.button(
            "Next decision \u25b8",
            disabled=(idx == len(RESOURCEFULNESS_QIDS) - 1),
        ):
            if st.session_state.get(f"{current_qid}_choice") is None:
                st.error("Make a choice before moving on.")
            else:
                st.session_state.res_q_idx += 1
                st.rerun()
    with c3:
        if st.button("Continue to Round 3 \u25b8"):
            missing = [
                qid
                for qid in RESOURCEFULNESS_QIDS
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error(
                    f"You still have {len(missing)} decision(s) to make before continuing."
                )
            else:
                go_to(3)

# ── Game 3: Execution Bias ──
elif page == 3:
    render_game_badge("Round 3 of 5 — Mindset")
    st.markdown("### Next-Step Choices")
    render_narrative(GAME_NARRATIVES[3])

    for qid in EXEC_QIDS:
        q = MINDSET_QUESTIONS[qid]
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(2)
    with c2:
        if st.button("Continue \u25b8", use_container_width=True):
            missing = [
                qid
                for qid in EXEC_QIDS
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error(
                    f"You still have {len(missing)} situation(s) to respond to."
                )
            else:
                go_to(4)

# ── Game 4: Shock Cards ──
elif page == 4:
    render_game_badge("Round 4 of 5 — Mindset")
    st.markdown("### Shock Cards")
    render_narrative(GAME_NARRATIVES[4])

    for qid in RESIL_QIDS:
        q = MINDSET_QUESTIONS[qid]
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(3)
    with c2:
        if st.button("Continue \u25b8", use_container_width=True):
            missing = [
                qid
                for qid in RESIL_QIDS
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error("Respond to all shocks before continuing.")
            else:
                go_to(5)

# ── Game 5: Feature Budget ──
elif page == 5:
    render_game_badge("Round 5 of 5 — Mindset")
    st.markdown("### Sprint Planning")
    render_narrative(GAME_NARRATIVES[5].format(budget=FEATURE_BUDGET))

    cols = st.columns(2)
    for i, f in enumerate(VALUE_FEATURES):
        with cols[i % 2]:
            suffix = f"Cost: {f['cost']} units"
            render_toggle_card_multi(f["key"], f["name"], suffix=suffix)

    total_cost = sum(
        f["cost"]
        for f in VALUE_FEATURES
        if st.session_state.get(f["key"], False)
    )
    remaining = FEATURE_BUDGET - total_cost

    if remaining >= 0:
        st.markdown(
            f"**Budget:** {total_cost} / {FEATURE_BUDGET} used &nbsp;·&nbsp; "
            f"**{remaining} units remaining**"
        )
    else:
        st.error(
            f"Over budget by {abs(remaining)} units. Deselect something to continue."
        )

    over_budget = total_cost > FEATURE_BUDGET

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(4)
    with c2:
        if st.button("Continue to Skills Assessment \u25b8", disabled=over_budget, use_container_width=True):
            go_to(6)

# ── Skills Game ──
elif page == 6:
    render_game_badge("Skills Assessment")
    st.markdown("### Startup Skills")
    render_narrative(GAME_NARRATIVES[6])

    st.markdown("#### Part 1 — Self-Rating")
    st.caption("Be honest — there's no advantage to inflating these. The scenario rounds will test the reality.")
    col1, col2 = st.columns(2)
    with col1:
        st.slider(
            "Finding and understanding customers",
            1, 5, st.session_state.get("s_skill_mkt", 3), key="s_skill_mkt",
        )
        st.slider(
            "Keeping operations running smoothly",
            1, 5, st.session_state.get("s_skill_ops", 3), key="s_skill_ops",
        )
        st.slider(
            "Budgeting, runway, and unit economics",
            1, 5, st.session_state.get("s_skill_fin", 3), key="s_skill_fin",
        )
    with col2:
        st.slider(
            "Shaping and building usable products",
            1, 5, st.session_state.get("s_skill_prod", 3), key="s_skill_prod",
        )
        st.slider(
            "Selling and building relationships",
            1, 5, st.session_state.get("s_skill_sales", 3), key="s_skill_sales",
        )
        st.slider(
            "Aligning people and priorities",
            1, 5, st.session_state.get("s_skill_team", 3), key="s_skill_team",
        )

    st.markdown("---")
    st.markdown("#### Part 2 — Scenario Rounds")
    st.caption("Now prove it. How would you actually handle these situations?")
    for skill in SKILL_AREAS:
        for qid in SKILL_SCENARIO_MAP[skill]:
            q = SKILL_QUESTIONS[qid]
            render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(5)
    with c2:
        if st.button("Continue \u25b8", use_container_width=True):
            missing = [
                qid
                for qid in SKILL_QUESTIONS.keys()
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error(
                    f"You still have {len(missing)} scenario(s) to complete."
                )
            else:
                go_to(7)

# ── Resources ──
elif page == 7:
    render_game_badge("Resource Inventory")
    st.markdown("### Your Resources")
    render_narrative(GAME_NARRATIVES[7])

    st.markdown("**Access to key resources (realistically, in the next 3–6 months):**")
    st.slider(
        "Money you could direct toward a venture",
        1, 5, st.session_state.get("res_fin_level", 3), key="res_fin_level",
    )
    st.slider(
        "Tools, platforms, or infrastructure you already have",
        1, 5, st.session_state.get("res_tech_level", 3), key="res_tech_level",
    )
    st.slider(
        "People you could involve (co-founders, contractors, advisors)",
        1, 5, st.session_state.get("res_talent_level", 3), key="res_talent_level",
    )
    st.slider(
        "Connections to customers, partners, mentors, or gatekeepers",
        1, 5, st.session_state.get("res_network_level", 3), key="res_network_level",
    )

    st.markdown("---")
    st.markdown("**Your time pattern:**")

    def set_time_choice(value: str):
        st.session_state["res_time_pattern"] = value

    time_options = [
        "25+ hours most weeks",
        "10\u201325 hours most weeks",
        "5\u201310 hours in irregular pockets",
        "Rarely have focused time",
    ]
    current_time = st.session_state.get("res_time_pattern", None)
    cols = st.columns(2)
    for i, opt in enumerate(time_options):
        col = cols[i % 2]
        with col:
            selected = current_time == opt
            label = f"\u2705 {opt}" if selected else opt
            st.button(
                label,
                key=f"time_opt_{i}",
                use_container_width=True,
                on_click=set_time_choice,
                args=(opt,),
            )

    st.markdown("---")
    st.markdown("**Support for ambitious goals:**")
    sup_cols = st.columns(2)
    with sup_cols[0]:
        st.checkbox(
            "Someone I can brainstorm with on strategy or decisions.",
            key="sup_brainstorm",
        )
        st.checkbox(
            "Someone who gives honest feedback without shutting me down.",
            key="sup_tactical",
        )
    with sup_cols[1]:
        st.checkbox(
            "Someone emotionally in my corner when things get rough.",
            key="sup_emotional",
        )
        st.checkbox(
            "Someone willing to make intros or open doors.",
            key="sup_intros",
        )

    st.markdown("**When you share an ambitious plan, people around you typically:**")

    def set_reaction_choice(value: str):
        st.session_state["sup_reaction"] = value

    react_options = [
        "Mostly encouraging and try to help",
        "Neutral or politely interested",
        "Often skeptical or discouraging",
    ]
    current_react = st.session_state.get("sup_reaction", None)
    cols_r = st.columns(3)
    for i, opt in enumerate(react_options):
        col = cols_r[i]
        with col:
            selected = current_react == opt
            label = f"\u2705 {opt}" if selected else opt
            st.button(
                label,
                key=f"react_opt_{i}",
                use_container_width=True,
                on_click=set_reaction_choice,
                args=(opt,),
            )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(6)
    with c2:
        if st.button("Continue \u25b8", use_container_width=True):
            if (
                st.session_state.get("res_time_pattern") is None
                or st.session_state.get("sup_reaction") is None
            ):
                st.error(
                    "Select your time pattern and typical reaction before continuing."
                )
            else:
                go_to(8)

# ── Acumen ──
elif page == 8:
    render_game_badge("Final Round")
    st.markdown("### Venture-Building Knowledge")
    render_narrative(GAME_NARRATIVES[8])

    for qid, q in ACUMEN_QUESTIONS.items():
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("\u25c2 Back"):
            go_to(7)
    with c2:
        if st.button(
            "\U0001f4ca  See Your Readiness Profile",
            use_container_width=True,
        ):
            missing = [
                qid
                for qid in ACUMEN_QUESTIONS
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error("Answer all questions before viewing your profile.")
            else:
                st.session_state.submitted = True
                go_to(9)

# ── Results ──
elif page == 9:
    st.markdown("### Your Readiness Profile")

    if not st.session_state.submitted:
        st.info(
            "Complete all rounds and click **See Your Readiness Profile** to view your results."
        )
    else:
        total_score, comp_scores, sub_scores = compute_overall_scores()

        # ── Big score ──
        st.markdown(
            f"""<div class="score-big">
                <div class="number">{total_score}</div>
                <div class="label">out of 100 · Entrepreneurial Readiness</div>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown(f"**{readiness_label(total_score)}**")

        # ── Coaching narrative ──
        st.markdown("---")
        st.markdown("#### What This Means For You")
        coaching = coaching_narrative(total_score, comp_scores, sub_scores)
        st.markdown(
            f'<div class="coaching-box">{coaching}</div>',
            unsafe_allow_html=True,
        )

        # ── Component bar chart ──
        st.markdown("---")
        st.markdown("#### Component Breakdown")
        df_comp = pd.DataFrame(
            {
                "Component": COMPONENTS,
                "Score": [comp_scores[c] for c in COMPONENTS],
            }
        )
        chart = (
            alt.Chart(df_comp)
            .mark_bar(cornerRadiusEnd=6, color="#238636")
            .encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 5]), title="Score (1–5)"),
                y=alt.Y("Component:N", sort="-x", title=""),
                tooltip=["Component", "Score"],
            )
            .properties(height=220)
            .configure_axis(labelColor="#8b949e", titleColor="#8b949e")
            .configure_view(stroke=None)
        )
        st.altair_chart(chart, use_container_width=True)

        # ── Subdimension detail ──
        st.markdown("---")
        st.markdown("#### Deep Dive")

        with st.expander("Entrepreneurial Mindset", expanded=False):
            for sd in MINDSET_SUBDIMS:
                score = sub_scores["mindset"][sd]
                bar_pct = int((score / 5) * 100)
                st.markdown(
                    f"**{sd}** — {score:.1f}/5 · {MINDSET_DESCRIPTIONS[sd]}"
                )
                st.progress(bar_pct / 100)

        with st.expander("Entrepreneurial Skills", expanded=False):
            for sk in SKILL_AREAS:
                score = sub_scores["skills"][sk]
                st.markdown(
                    f"**{sk}** — {score:.1f}/5 · {SKILL_DESCRIPTIONS[sk]}"
                )
                st.progress(int((score / 5) * 100) / 100)

        with st.expander("Resource Availability", expanded=False):
            for rs in RESOURCE_SUBDIMS:
                score = sub_scores["resources"][rs]
                st.markdown(
                    f"**{rs}** — {score:.1f}/5 · {RESOURCE_DESCRIPTIONS[rs]}"
                )
                st.progress(int((score / 5) * 100) / 100)

        with st.expander("Business Acumen", expanded=False):
            for ac in ACUMEN_SUBDIMS:
                score = sub_scores["acumen"][ac]
                st.markdown(
                    f"**{ac}** — {score:.1f}/5 · {ACUMEN_DESCRIPTIONS[ac]}"
                )
                st.progress(int((score / 5) * 100) / 100)

        st.markdown("---")
        if st.button("\u25c2 Back to Business Knowledge"):
            go_to(8)
