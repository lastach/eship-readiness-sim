import streamlit as st
import pandas as pd
import altair as alt
import random

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

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

# ============== GAME 1: CUSTOMER SIGNAL CARDS ==============

OPP_SCENARIOS = [
    {
        "key": "opp_1",
        "text": "20% of users export data weekly to fix errors via a manual spreadsheet workaround.",
        "is_opportunity": True,
    },
    {
        "key": "opp_2",
        "text": "Several users comment that they would like a dark mode theme someday.",
        "is_opportunity": False,
    },
    {
        "key": "opp_3",
        "text": "40% of users start a key workflow but never finish it.",
        "is_opportunity": True,
    },
    {
        "key": "opp_4",
        "text": "Your product gets lots of social media likes but modest repeat usage.",
        "is_opportunity": False,
    },
    {
        "key": "opp_5",
        "text": "Prospects say they’d “maybe use an app like this in the future.”",
        "is_opportunity": False,
    },
    {
        "key": "opp_6",
        "text": "Support tickets repeatedly mention the same bug that forces people to redo work.",
        "is_opportunity": True,
    },
    {
        "key": "opp_7",
        "text": "Several customers build their own scripts or integrations to work around missing functionality.",
        "is_opportunity": True,
    },
    {
        "key": "opp_8",
        "text": "A blog post about your space gets traffic, but almost nobody tries the product.",
        "is_opportunity": False,
    },
    {
        "key": "opp_9",
        "text": "You have a growing waitlist of people regularly following up asking when they can get access.",
        "is_opportunity": True,
    },
    {
        "key": "opp_10",
        "text": "Conference attendees say your booth was 'interesting', but few accept a follow-up call.",
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

# ============== GAME 5: FEATURE BUDGET (SELECT FEATURES ONLY) ==============

FEATURE_BUDGET = 20  # total cost budget (cannot exceed)

# A & G most important; then C/E; others much lower
VALUE_FEATURES = [
    {
        "key": "feat_a",
        "name": "Remove a bug causing 25% of users to abandon onboarding.",
        "cost": 7,
        "ideal_points": 5,
    },
    {
        "key": "feat_b",
        "name": "Add a dashboard theme option.",
        "cost": 3,
        "ideal_points": 1,
    },
    {
        "key": "feat_c",
        "name": "Add a guided checklist that helps new users complete the core workflow in their first session.",
        "cost": 6,
        "ideal_points": 4,
    },
    {
        "key": "feat_d",
        "name": "Ship an idea with no demand signals yet.",
        "cost": 5,
        "ideal_points": 1,
    },
    {
        "key": "feat_e",
        "name": "Run a small pilot with 10 ideal customers, including onboarding and follow-up.",
        "cost": 6,
        "ideal_points": 4,
    },
    {
        "key": "feat_f",
        "name": "Polish minor UI details that only existing power users occasionally notice.",
        "cost": 2,
        "ideal_points": 2,
    },
    {
        "key": "feat_g",
        "name": "Add instrumentation to capture where users drop off in key journeys.",
        "cost": 4,
        "ideal_points": 5,
    },
]


def compute_value_creation_score():
    selected = [f for f in VALUE_FEATURES if st.session_state.get(f["key"], False)]
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
        "prompt": "You need to understand why users churn, but have zero budget. What do you actually do first?",
        "options": [
            "Use existing signals (reviews, support tickets) and talk directly to a few churned users.",
            "Wait until you have budget for a formal study.",
            "Ask friends what they think about churn in general.",
            "Search online for articles and case studies about churn before talking to anyone.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_2": {
        "subdim": "Resourcefulness",
        "prompt": "You must launch a landing page today, but there’s no designer available.",
        "options": [
            "Use a no-code template tool and ship something basic.",
            "Wait for a designer so it looks polished.",
            "Write copy now and wait for design time later.",
            "Mock it up in a slide deck and send screenshots only.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_3": {
        "subdim": "Resourcefulness",
        "prompt": "You need to test a new feature idea and have no engineering time.",
        "options": [
            "Create a simple clickable mockup or fake-door test.",
            "Wait until engineers have time to build it properly.",
            "Write a long spec and share internally for feedback.",
            "Look at similar tools and treat the idea as validated if they exist.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_res_4": {
        "subdim": "Resourcefulness",
        "prompt": "You only have access to 10 potential users for early testing.",
        "options": [
            "Run deep interviews and observe their workflows.",
            "Run a big quantitative survey with them.",
            "Don’t test until you have a bigger audience.",
            "Read industry reports instead of talking to them.",
        ],
        "scores": [5, 3, 1, 2],
    },
    # Execution bias – Game 3
    "ms_exec_1": {
        "subdim": "Execution Bias",
        "prompt": "You have one afternoon to de-risk a new idea. What do you actually do?",
        "options": [
            "Run 5 quick user calls or a simple landing test.",
            "Write a 20-page strategy doc mapping the next 2 years.",
            "Brainstorm names and design a logo.",
            "Search online for examples and save them into a doc without contacting anyone.",
        ],
        "scores": [5, 1, 2, 2],
    },
    "ms_exec_2": {
        "subdim": "Execution Bias",
        "prompt": "You want to test interest in a potential feature. What’s your next step?",
        "options": [
            "Add a 'coming soon' button and track clicks plus follow-up.",
            "Build the full feature and launch quietly.",
            "Survey friends who are not in your target segment.",
            "Look at similar tools and treat that as enough validation.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "ms_exec_3": {
        "subdim": "Execution Bias",
        "prompt": "You’re unsure between two target segments. How do you proceed?",
        "options": [
            "Run two tiny tests in parallel and compare response.",
            "Pick one based purely on your intuition.",
            "Wait until you can do a full market study.",
            "Ask someone experienced which segment sounds more promising and choose that.",
        ],
        "scores": [5, 2, 1, 3],
    },
    "ms_exec_4": {
        "subdim": "Execution Bias",
        "prompt": "You’ve designed an experiment; results are noisy but lean one way. What do you do?",
        "options": [
            "Make a small decision in the direction of the signal and keep testing.",
            "Ignore it and wait for perfectly clear signal.",
            "Restart from scratch with a totally different idea.",
            "Ask an advisor whether they think you should trust the data.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "ms_exec_5": {
        "subdim": "Execution Bias",
        "prompt": "A teammate suggests a quick test that could kill your favorite idea. Your move?",
        "options": [
            "Run the test and be ready to pivot if it fails.",
            "Avoid the test; you don’t want to lose the idea.",
            "Delay the test until after other work is finished.",
            "Ask an advisor whether it is worth testing at all.",
        ],
        "scores": [5, 1, 2, 3],
    },
    # Resilience & adaptability – Game 4
    "ms_resil_1": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: A contractor delays a deliverable by 3 days. What do you do?",
        "options": [
            "Do nothing and simply push the timeline back.",
            "Replace the contractor entirely.",
            "Re-scope the sprint and adjust dependent work.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_2": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: Your acquisition cost jumps 40% overnight.",
        "options": [
            "Keep campaigns running and see what happens.",
            "Kill all paid channels immediately.",
            "Shift spend, test new creatives, and review funnel quality.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_3": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: A competitor suddenly drops prices by 70% in your space.",
        "options": [
            "Keep your current pricing and ignore it.",
            "Lower price slightly and hope to keep up.",
            "Refocus on a segment or offer where you compete on value, not price.",
        ],
        "scores": [1, 2, 5],
    },
}

RESOURCEFULNESS_QIDS = ["ms_res_1", "ms_res_2", "ms_res_3", "ms_res_4"]
EXEC_QIDS = [qid for qid, q in MINDSET_QUESTIONS.items() if q["subdim"] == "Execution Bias"]
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
        "prompt": "Trial users aren’t converting. What do you do first?",
        "options": [
            "Interview 5–10 recent trial users about their decision.",
            "Run a broad online survey with anyone you can find.",
            "Change the homepage headline based on your intuition.",
            "Read marketing articles instead of talking to users.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_mkt_2": {
        "skill": "Market Research & Marketing",
        "prompt": "You want to identify the best early adopters. What’s your move?",
        "options": [
            "Find a niche where the pain is sharp and design messaging just for them.",
            "Target everyone with the same message.",
            "Copy a competitor’s positioning.",
            "Ask an advisor who they think sounds more exciting.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_prod_1": {
        "skill": "Product & Technical",
        "prompt": "You can only ship one change this sprint. Which do you choose?",
        "options": [
            "A fix for a bug that blocks a key workflow.",
            "A 'nice to have' that a few users casually mentioned.",
            "A flashy new thing that will look good in demos.",
            "Ask an advisor for ideas and wait.",
        ],
        "scores": [5, 2, 3, 1],
    },
    "sk_prod_2": {
        "skill": "Product & Technical",
        "prompt": "You’re unsure whether a design is intuitive. What do you do?",
        "options": [
            "Do 5 quick usability tests with target users.",
            "Ship it now; you’ll hear complaints if it’s bad.",
            "Ask your team what they think.",
            "Search for design patterns and copy one without testing.",
        ],
        "scores": [5, 1, 3, 2],
    },
    "sk_sales_1": {
        "skill": "Sales & Networking",
        "prompt": "You have 10 warm leads and limited time. What’s your approach?",
        "options": [
            "Send tailored messages and schedule 1:1 conversations.",
            "Send a broad email blast and hope some respond.",
            "Post about your product on social media instead.",
            "Ask an advisor which lead to start with but delay outreach.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_sales_2": {
        "skill": "Sales & Networking",
        "prompt": "You meet someone who might be a great partner. What’s your next step?",
        "options": [
            "Suggest a small, concrete next step (intro, pilot, shared experiment).",
            "Ask for a big commitment immediately.",
            "Wait to see if they reach out to you.",
            "Send them a deck without a clear ask.",
        ],
        "scores": [5, 1, 2, 2],
    },
    "sk_fin_1": {
        "skill": "Financial Management",
        "prompt": "You have 3 months of runway left. What do you prioritize?",
        "options": [
            "Identify and cut low-ROI spend while doubling down on proven channels.",
            "Cut all spending, including things that fuel growth.",
            "Ignore runway and focus purely on product polish.",
            "Ask an advisor if they think you should be worried.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_fin_2": {
        "skill": "Financial Management",
        "prompt": "Your CAC is higher than expected but customers who close stay for years.",
        "options": [
            "Check payback period and LTV, then decide how much you can afford to spend.",
            "Shut off acquisition until CAC is lower.",
            "Ignore the numbers and focus on top-line growth.",
            "Search benchmarks and treat them as an exact template without checking your own numbers.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_ops_1": {
        "skill": "Operations",
        "prompt": "Support tickets are piling up. What’s your first move?",
        "options": [
            "Look for patterns and fix the top root causes.",
            "Hire more people immediately.",
            "Tell the team to 'work harder' this week.",
            "Ask an advisor if they think you need more staff.",
        ],
        "scores": [5, 2, 1, 2],
    },
    "sk_ops_2": {
        "skill": "Operations",
        "prompt": "A process works but only you know how to do it. What now?",
        "options": [
            "Document it and train someone else so it’s repeatable.",
            "Keep doing it yourself to save time.",
            "Pause the process entirely.",
            "Record a quick video and hope people figure it out.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_team_1": {
        "skill": "Team & Strategy",
        "prompt": "Traction is flat but a subset of users loves one use-case. What now?",
        "options": [
            "Focus your roadmap and messaging on the use-case that’s working.",
            "Keep trying to serve everyone with the same product.",
            "Pause all changes while you think about a new idea.",
            "Ask an advisor whether the niche is 'big enough'.",
        ],
        "scores": [5, 1, 2, 3],
    },
    "sk_team_2": {
        "skill": "Team & Strategy",
        "prompt": "Your team is busy, but progress on key metrics is slow.",
        "options": [
            "Narrow focus to a small number of high-leverage bets.",
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
    "Problem–Solution Fit",
    "Market Viability",
    "Business Model Soundness",
    "Go-to-Market Readiness",
    "Operational Feasibility",
    "Scalability Potential",
]
ACUMEN_DESCRIPTIONS = {
    "Problem–Solution Fit": "Real, urgent customer problem + clear solution that addresses it.",
    "Market Viability": "Defined target segment, reachable customers, credible demand, differentiation.",
    "Business Model Soundness": "Pricing, unit economics, cost structure, and path to profitability.",
    "Go-to-Market Readiness": "Validated channels, messaging, acquisition strategy.",
    "Operational Feasibility": "Ability to deliver reliably given tech, supply, and processes.",
    "Scalability Potential": "Model, market, and operations can grow without breaking.",
}

ACUMEN_QUESTIONS = {
    "ac_ps_fit": {
        "subdim": "Problem–Solution Fit",
        "prompt": "Which signal shows the strongest evidence that you’re solving a real problem?",
        "options": [
            "People say your idea is 'cool' in casual conversation.",
            "A segment of users repeatedly describes the same painful problem you address.",
            "Your landing page has a high click-through rate from ads.",
        ],
        "scores": [2, 5, 3],
    },
    "ac_ps_fit_2": {
        "subdim": "Problem–Solution Fit",
        "prompt": "You hear different problems from different users. What’s your next step?",
        "options": [
            "Pick the problem you personally like most.",
            "Cluster users by similar jobs and pains, and focus on one tight group first.",
            "Try to build a product that solves all of them at once.",
        ],
        "scores": [2, 5, 1],
    },
    "ac_market": {
        "subdim": "Market Viability",
        "prompt": "Which of these situations is most promising?",
        "options": [
            "Huge possible market, but you don’t know who to target first.",
            "A smaller, clearly defined group you can reliably reach.",
            "A big market with many competitors and no clear angle.",
        ],
        "scores": [3, 5, 2],
    },
    "ac_model": {
        "subdim": "Business Model Soundness",
        "prompt": "Which model is healthiest over time?",
        "options": [
            "High price point, but each customer costs more to serve than they pay.",
            "Moderate price, high margin, and a clear path to repeat purchases.",
            "Low price, unclear costs, and no idea how many customers you need.",
        ],
        "scores": [1, 5, 2],
    },
    "ac_gtm": {
        "subdim": "Go-to-Market Readiness",
        "prompt": "Which description sounds most ready to scale acquisition?",
        "options": [
            "You plan to grow mostly through word-of-mouth, but have no path to your first customers.",
            "You’ve tested a few acquisition channels and have one that reliably brings leads.",
            "You plan to 'go viral' but have no specific channels mapped.",
        ],
        "scores": [1, 5, 1],
    },
    "ac_ops": {
        "subdim": "Operational Feasibility",
        "prompt": "Which setup is most likely to deliver consistently?",
        "options": [
            "You rely on a manual process only you understand.",
            "You have documented processes and can train others to deliver.",
            "You plan to figure out delivery later once demand shows up.",
        ],
        "scores": [2, 5, 1],
    },
    "ac_scale": {
        "subdim": "Scalability Potential",
        "prompt": "Which of these scales best?",
        "options": [
            "Each new customer requires a lot of custom work from you.",
            "Most of the value is delivered through software or repeatable systems.",
            "You depend on rare, highly specialized human talent for every deal.",
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
    label_text = text + (f"  \n_{suffix}_" if suffix else "")
    label = f"✅ {label_text}" if selected else label_text
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
        selected = (current == opt_idx)
        label = f"✅ {opt}" if selected else opt
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
        sub_scores[sd] = round(sum(values[sd]) / len(values[sd]), 2) if values[sd] else 1.0
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
        skill_scores[skill] = round(sum(vals) / len(vals), 2) if vals else 1.0
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
        "10–25 hours most weeks": 4,
        "5–10 hours in irregular pockets": 3,
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
        sub_scores[sd] = round(sum(values[sd]) / len(values[sd]), 2) if values[sd] else 1.0
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
    return total, comp_scores, {
        "mindset": mindset_sub,
        "skills": skills_sub,
        "resources": res_sub,
        "acumen": ac_sub,
    }


def readiness_label(total_score):
    if total_score >= 85:
        return "High readiness to pursue or accelerate a venture."
    elif total_score >= 70:
        return "Strong potential — ready for more serious experiments."
    elif total_score >= 50:
        return "Early-stage readiness — good time to build specific muscles."
    else:
        return "Foundation-building phase — focus on learning and low-risk reps."


def suggestion_for_user(total_score, comp_scores):
    sorted_comps = sorted(COMPONENTS, key=lambda c: comp_scores[c])
    weakest = sorted_comps[0]
    second_weakest = sorted_comps[1] if len(sorted_comps) > 1 else None
    tail = (
        f"Focus on strengthening **{weakest}**"
        + (f" and **{second_weakest}**" if second_weakest else "")
        + " through small, low-risk experiments."
    )
    if total_score < 50:
        return (
            "You’re in a foundation-building phase; this is a good time to build skills "
            "without heavy pressure to launch. " + tail
        )
    elif total_score < 70:
        return (
            "You’re showing early-stage readiness; you can run real experiments while deliberately "
            "building your thinner areas. " + tail
        )
    elif total_score < 85:
        return (
            "You have strong potential and a solid base; you can keep advancing a venture while "
            "watching for bottlenecks. " + tail
        )
    else:
        return (
            "You’re showing high readiness; focus on building systems around your strengths and "
            "avoiding blind spots in weaker components. " + tail
        )

# ============== NAVIGATION ==============

PAGE_LABELS = [
    "Intro",
    "Game 1: Customer Signals",
    "Game 2: Constraint Cards",
    "Game 3: Next-Step Choices",
    "Game 4: Shock Cards",
    "Game 5: Feature Budget",
    "Skills Game",
    "Resources",
    "Venture-Building Knowledge",
    "Readiness Profile",
]

st.title("Entrepreneurial Readiness Simulation")

nav_cols = st.columns(len(PAGE_LABELS))
for i, label in enumerate(PAGE_LABELS):
    with nav_cols[i]:
        disabled = i > st.session_state.max_page
        if st.button(label, disabled=disabled, key=f"nav_{i}"):
            go_to(i)

st.write(f"Step {st.session_state.page + 1} of {len(PAGE_LABELS)}")
page = st.session_state.page

# ============== PAGES ==============

# Intro
if page == 0:
    st.subheader("Welcome")
    st.markdown(
        """
This is a **game-style simulation** to give you a snapshot of your current **entrepreneurial readiness**.

You’ll work through:

- **5 mini-games** on:
  - spotting meaningful signals,
  - handling constraints,
  - deciding under pressure,
  - reacting to shocks,
  - and prioritizing what to build.
- A **Skills Game** with self-ratings plus scenario rounds across core startup skills.
- A **Resources check** and a short **venture-building knowledge quiz**.
- A final **Readiness Profile** with component scores and suggestions for what to build next.
        """
    )
    if st.button("Start ▸"):
        go_to(1)

# Game 1 – customer signals
elif page == 1:
    st.subheader("Game 1: Customer Signals")
    st.caption("For each card, click if you believe it’s a **strong signal of real, fixable demand**.")

    cols = st.columns(3)
    for idx, sc in enumerate(OPP_SCENARIOS):
        with cols[idx % 3]:
            render_toggle_card_multi(sc["key"], sc["text"])

    if st.button("Next ▸"):
        go_to(2)

# Game 2 – constraint cards (one at a time)
elif page == 2:
    st.subheader("Game 2: Constraint Cards")
    st.caption("You’re working under real constraints. For each situation, pick the move you would actually make.")

    idx = st.session_state.res_q_idx
    idx = max(0, min(idx, len(RESOURCEFULNESS_QIDS) - 1))
    st.session_state.res_q_idx = idx

    current_qid = RESOURCEFULNESS_QIDS[idx]
    q = MINDSET_QUESTIONS[current_qid]
    st.markdown(f"_Decision {idx + 1} of {len(RESOURCEFULNESS_QIDS)}_")
    render_choice_cards(current_qid, q["prompt"], q["options"])

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("◂ Previous decision", disabled=(idx == 0)):
            st.session_state.res_q_idx -= 1
            st.rerun()
    with c2:
        if st.button("Next decision ▸", disabled=(idx == len(RESOURCEFULNESS_QIDS) - 1)):
            if st.session_state.get(f"{current_qid}_choice") is None:
                st.error("Please choose what you would actually do for this decision before moving on.")
            else:
                st.session_state.res_q_idx += 1
                st.rerun()
    with c3:
        if st.button("Continue to next game ▸"):
            missing = [qid for qid in RESOURCEFULNESS_QIDS if st.session_state.get(f"{qid}_choice") is None]
            if missing:
                st.error("Please make a choice for each decision before continuing.")
            else:
                go_to(3)

# Game 3 – execution bias
elif page == 3:
    st.subheader("Game 3: Next-Step Choices")
    st.caption("You have limited time and information. For each situation, pick what you would actually do next.")

    for qid in EXEC_QIDS:
        q = MINDSET_QUESTIONS[qid]
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(2)
    with c2:
        if st.button("Next ▸"):
            missing = [qid for qid in EXEC_QIDS if st.session_state.get(f"{qid}_choice") is None]
            if missing:
                st.error("Please choose what you’d actually do for each situation before continuing.")
            else:
                go_to(4)

# Game 4 – shock cards
elif page == 4:
    st.subheader("Game 4: Shock Cards")
    st.caption("Unexpected things happen. For each shock, choose how you’d respond in real life.")

    for qid in RESIL_QIDS:
        q = MINDSET_QUESTIONS[qid]
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(3)
    with c2:
        if st.button("Next ▸"):
            missing = [qid for qid in RESIL_QIDS if st.session_state.get(f"{qid}_choice") is None]
            if missing:
                st.error("Please choose how you’d respond to each shock before continuing.")
            else:
                go_to(5)

# Game 5 – feature budget (select features only)
elif page == 5:
    st.subheader("Game 5: Feature Budget")
    st.caption("You’re planning a sprint. You have a limited budget and multiple ways you could spend attention.")

    st.markdown(
        f"""
You have a budget of **{FEATURE_BUDGET} cost units** to allocate across these possible changes.

- Each card shows a **feature** and its **cost**.
- Click to select the features you would ship in this sprint.
- You can choose as many as you like, but you **cannot exceed the budget**.
        """
    )

    cols = st.columns(2)
    for i, f in enumerate(VALUE_FEATURES):
        with cols[i % 2]:
            suffix = f"Cost: {f['cost']}"
            render_toggle_card_multi(f["key"], f["name"], suffix=suffix)

    total_cost = sum(
        f["cost"] for f in VALUE_FEATURES if st.session_state.get(f["key"], False)
    )
    st.markdown(f"**Total cost used:** {total_cost} / {FEATURE_BUDGET}")

    over_budget = total_cost > FEATURE_BUDGET
    if over_budget:
        st.error("You are over budget. Deselect some features to continue.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(4)
    with c2:
        if st.button("Next ▸", disabled=over_budget):
            go_to(6)

# Skills Game
elif page == 6:
    st.subheader("Skills Game")
    st.caption(
        "First, a quick **self-assessment**. Then scenario rounds that simulate how you’d actually operate."
    )

    st.markdown("### Part 1 – Self-assessment")
    col1, col2 = st.columns(2)
    with col1:
        st.slider(
            "Finding and understanding customers",
            1, 5,
            st.session_state.get("s_skill_mkt", 3),
            key="s_skill_mkt",
        )
        st.slider(
            "Keeping day-to-day work running smoothly",
            1, 5,
            st.session_state.get("s_skill_ops", 3),
            key="s_skill_ops",
        )
        st.slider(
            "Budgeting, runway, and unit economics",
            1, 5,
            st.session_state.get("s_skill_fin", 3),
            key="s_skill_fin",
        )
    with col2:
        st.slider(
            "Shaping and building products people can use",
            1, 5,
            st.session_state.get("s_skill_prod", 3),
            key="s_skill_prod",
        )
        st.slider(
            "Selling and building relationships",
            1, 5,
            st.session_state.get("s_skill_sales", 3),
            key="s_skill_sales",
        )
        st.slider(
            "Aligning people and priorities toward a plan",
            1, 5,
            st.session_state.get("s_skill_team", 3),
            key="s_skill_team",
        )

    st.markdown("---")
    st.markdown("### Part 2 – Scenario Rounds")

    for skill in SKILL_AREAS:
        for qid in SKILL_SCENARIO_MAP[skill]:
            q = SKILL_QUESTIONS[qid]
            render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(5)
    with c2:
        if st.button("Next ▸"):
            missing = [
                qid for qid in SKILL_QUESTIONS.keys()
                if st.session_state.get(f"{qid}_choice") is None
            ]
            if missing:
                st.error("Please play through all skill scenarios before continuing.")
            else:
                go_to(7)

# Resources
elif page == 7:
    st.subheader("Resources")
    st.caption("Answer based on what you could realistically tap into over the next 3–6 months.")

    st.markdown("**Access to key resources (today):**")

    st.slider(
        "Money you could direct toward a venture.",
        1, 5,
        st.session_state.get("res_fin_level", 3),
        key="res_fin_level",
    )
    st.slider(
        "Tools, platforms, or infrastructure you already have access to.",
        1, 5,
        st.session_state.get("res_tech_level", 3),
        key="res_tech_level",
    )
    st.slider(
        "People you could involve (co-founders, contractors, employees).",
        1, 5,
        st.session_state.get("res_talent_level", 3),
        key="res_talent_level",
    )
    st.slider(
        "Connections to customers, partners, mentors, or gatekeepers.",
        1, 5,
        st.session_state.get("res_network_level", 3),
        key="res_network_level",
    )

    st.markdown("---")
    st.markdown("**Time pattern:**")

    def set_time_choice(value: str):
        st.session_state["res_time_pattern"] = value

    time_options = [
        "25+ hours most weeks",
        "10–25 hours most weeks",
        "5–10 hours in irregular pockets",
        "Rarely have focused time",
    ]
    current_time = st.session_state.get("res_time_pattern", None)
    cols = st.columns(2)
    for i, opt in enumerate(time_options):
        col = cols[i % 2]
        with col:
            selected = (current_time == opt)
            label = f"✅ {opt}" if selected else opt
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
        st.checkbox("Someone I can brainstorm with on strategy or decisions.", key="sup_brainstorm")
        st.checkbox("Someone who will give me honest feedback without shutting me down.", key="sup_tactical")
    with sup_cols[1]:
        st.checkbox("Someone who is emotionally in my corner when things get rough.", key="sup_emotional")
        st.checkbox("Someone willing to make intros or open doors.", key="sup_intros")

    st.markdown("**Typical reaction when you share an ambitious plan:**")

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
            selected = (current_react == opt)
            label = f"✅ {opt}" if selected else opt
            st.button(
                label,
                key=f"react_opt_{i}",
                use_container_width=True,
                on_click=set_reaction_choice,
                args=(opt,),
            )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(6)
    with c2:
        if st.button("Next ▸"):
            if st.session_state.get("res_time_pattern") is None or st.session_state.get("sup_reaction") is None:
                st.error("Please choose your time pattern and typical reaction before continuing.")
            else:
                go_to(8)

# Acumen
elif page == 8:
    st.subheader("Venture-Building Knowledge")
    st.caption("Quick questions on how you think about problems, markets, models, and scaling.")

    for qid, q in ACUMEN_QUESTIONS.items():
        render_choice_cards(qid, q["prompt"], q["options"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("◂ Back"):
            go_to(7)
    with c2:
        if st.button("Submit & see readiness profile ▸"):
            missing = [qid for qid in ACUMEN_QUESTIONS if st.session_state.get(f"{qid}_choice") is None]
            if missing:
                st.error("Please answer all questions before continuing.")
            else:
                st.session_state.submitted = True
                go_to(9)

# Results
elif page == 9:
    st.subheader("Readiness Profile")
    if not st.session_state.submitted:
        st.info("Work through the earlier games and click **Submit & see readiness profile** to view your results.")
    else:
        total_score, comp_scores, sub_scores = compute_overall_scores()
        st.metric("Entrepreneurial Readiness Score", f"{total_score} / 100")
        st.write(f"**Interpretation:** {readiness_label(total_score)}")
        st.write(suggestion_for_user(total_score, comp_scores))

        st.markdown("### Component Scores")
        df_comp = pd.DataFrame({
            "Component": COMPONENTS,
            "Score (1–5)": [comp_scores[c] for c in COMPONENTS],
            "Weight": [COMP_WEIGHTS[c] for c in COMPONENTS],
        })
        chart = (
            alt.Chart(df_comp)
            .mark_bar()
            .encode(
                x=alt.X("Score (1–5):Q", scale=alt.Scale(domain=[0, 5])),
                y=alt.Y("Component:N", sort="-x"),
                tooltip=["Component", "Score (1–5)", "Weight"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### Subdimension Details")
        st.markdown("**Mindset**")
        for sd in MINDSET_SUBDIMS:
            st.write(f"- **{sd} – {sub_scores['mindset'][sd]:.2f}/5** · {MINDSET_DESCRIPTIONS[sd]}")

        st.markdown("**Skills**")
        for sk in SKILL_AREAS:
            st.write(f"- **{sk} – {sub_scores['skills'][sk]:.2f}/5** · {SKILL_DESCRIPTIONS[sk]}")

        st.markdown("**Resources**")
        for rs in RESOURCE_SUBDIMS:
            st.write(f"- **{rs} – {sub_scores['resources'][rs]:.2f}/5** · {RESOURCE_DESCRIPTIONS[rs]}")

        st.markdown("**Entrepreneurship / Business Acumen**")
        for ac in ACUMEN_SUBDIMS:
            st.write(f"- **{ac} – {sub_scores['acumen'][ac]:.2f}/5** · {ACUMEN_DESCRIPTIONS[ac]}")

        if st.button("◂ Back to previous page"):
            go_to(8)
