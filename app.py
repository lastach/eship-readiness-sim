import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

# ============== TOP-LEVEL COMPONENTS & DIMENSIONS ==============

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

# ============== GAME 1: CUSTOMER SIGNALS (OPPORTUNITY) ==============

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


# ============== GAME 5: FEATURE PRIORITY (VALUE CREATION) ==============

VALUE_FEATURES = [
    {
        "key": "feat_a",
        "name": "Remove a bug causing 25% of users to abandon onboarding.",
        "ideal_points": 5,
    },
    {
        "key": "feat_b",
        "name": "Add a cosmetic dashboard theme option.",
        "ideal_points": 1,
    },
    {
        "key": "feat_c",
        "name": "Improve a workflow that power users run daily.",
        "ideal_points": 4,
    },
    {
        "key": "feat_d",
        "name": "Ship an experimental idea with no demand signals yet.",
        "ideal_points": 2,
    },
    {
        "key": "feat_e",
        "name": "Reduce server costs by 10% (no user-facing change).",
        "ideal_points": 3,
    },
]


def compute_value_creation_score():
    diffs = []
    for f in VALUE_FEATURES:
        val = st.session_state.get(f["key"], 3)
        try:
            val = float(val)
        except Exception:
            val = 3.0
        diffs.append(abs(val - f["ideal_points"]))
    if not diffs:
        return 1.0
    avg_diff = sum(diffs) / len(diffs)
    norm = max(0.0, min(1.0, (4.0 - avg_diff) / 4.0))
    return round(1 + 4 * norm, 2)


# ============== GAMES 2–4: MINDSET SCENARIOS ==============

MINDSET_QUESTIONS = {
    # Constraint cards (Resourcefulness – 7 cards as in doc)
    "ms_res_1": {
        "subdim": "Resourcefulness",
        "prompt": "You need to understand why users churn, but have zero budget. What do you do first?",
        "options": [
            "Pause until you have budget for a proper study.",
            "Use existing signals (public reviews, support tickets) and talk directly to a few users.",
            "Ask friends what they think about churn in general.",
        ],
        "scores": [1, 5, 2],
    },
    "ms_res_2": {
        "subdim": "Resourcefulness",
        "prompt": "You must launch a landing page today, but there’s no designer available.",
        "options": [
            "Use a no-code template tool and ship something basic.",
            "Wait for a designer so it looks polished.",
            "Write copy now and hope design time appears later.",
        ],
        "scores": [5, 1, 2],
    },
    "ms_res_3": {
        "subdim": "Resourcefulness",
        "prompt": "You need to test a new feature idea and have no engineering time.",
        "options": [
            "Create a simple clickable mockup or fake-door test.",
            "Wait until engineers have time to build it properly.",
            "Write a long spec and share internally for feedback.",
        ],
        "scores": [5, 1, 2],
    },
    "ms_res_4": {
        "subdim": "Resourcefulness",
        "prompt": "You only have access to 10 potential users for early testing.",
        "options": [
            "Run deep interviews and observe their workflows.",
            "Run a big quantitative survey with them.",
            "Don’t test until you have a bigger audience.",
        ],
        "scores": [5, 3, 1],
    },
    "ms_res_5": {
        "subdim": "Resourcefulness",
        "prompt": "Metrics are missing on an important funnel step.",
        "options": [
            "Do manual spot-checks and reconstruct the funnel from raw logs.",
            "Rebuild the full analytics stack before doing anything else.",
            "Ignore the gap for now.",
        ],
        "scores": [5, 3, 1],
    },
    "ms_res_6": {
        "subdim": "Resourcefulness",
        "prompt": "You can’t get time with senior decision-makers.",
        "options": [
            "Talk to front-line staff or assistants who see the real workflow.",
            "Send a very long email and wait.",
            "Pause until a formal meeting is offered.",
        ],
        "scores": [5, 3, 1],
    },
    "ms_res_7": {
        "subdim": "Resourcefulness",
        "prompt": "Your primary outreach tool breaks mid-campaign.",
        "options": [
            "Switch channels or use a scrappier workaround.",
            "Spend days trying to fix the tool first.",
            "Stop the campaign until it’s resolved.",
        ],
        "scores": [5, 3, 1],
    },
    # Next-step choices (Execution bias)
    "ms_exec_1": {
        "subdim": "Execution Bias",
        "prompt": "You have one afternoon to de-risk a new idea. What do you actually do?",
        "options": [
            "Write a 20-page strategy doc mapping the next 2 years.",
            "Run 5 quick user calls or a simple landing test.",
            "Brainstorm names and design a logo.",
        ],
        "scores": [1, 5, 2],
    },
    "ms_exec_2": {
        "subdim": "Execution Bias",
        "prompt": "You want to test interest in a potential feature. What’s your next step?",
        "options": [
            "Build the full feature and launch quietly.",
            "Add a 'coming soon' button and track clicks + follow-up.",
            "Survey friends who are not in your target segment.",
        ],
        "scores": [2, 5, 1],
    },
    "ms_exec_3": {
        "subdim": "Execution Bias",
        "prompt": "You’re unsure between two target segments. How do you proceed?",
        "options": [
            "Pick one based purely on your intuition.",
            "Run two tiny tests in parallel and compare response.",
            "Wait until you can do a full market study.",
        ],
        "scores": [2, 5, 1],
    },
    # Shock cards (Resilience & adaptability)
    "ms_resil_1": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: A contractor delays a deliverable by 3 days. What do you do?",
        "options": [
            "Do nothing and hope it’s fine.",
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

# ============== SKILLS ==============

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
    "Team & Strategy": "Aligning people, priorities, and plans toward a coherent direction.",
}

SKILL_QUESTIONS = {
    "sk_round1": {
        "skill": "Market Research & Marketing",
        "prompt": "Trial users aren’t converting. What do you do first?",
        "options": [
            "Run a broad online survey with anyone you can find.",
            "Interview 5–10 recent trial users about their decision.",
            "Change the homepage headline based on your intuition.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round2": {
        "skill": "Product & Technical",
        "prompt": "You can only ship one change this sprint. Which do you choose?",
        "options": [
            "A 'nice to have' that a few users casually mentioned.",
            "A fix for a bug that blocks a key workflow.",
            "A flashy new thing that will look good in demos.",
        ],
        "scores": [2, 5, 3],
    },
    "sk_round3": {
        "skill": "Sales & Networking",
        "prompt": "You have 10 warm leads and limited time. What’s your approach?",
        "options": [
            "Send a generic email blast and hope some respond.",
            "Send tailored messages and schedule 1:1 conversations.",
            "Post about your product on social media instead.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round4": {
        "skill": "Financial Management",
        "prompt": "You have 3 months of runway left. What do you prioritize?",
        "options": [
            "Cut all spending, including things that fuel growth.",
            "Identify and cut low-ROI spend while doubling down on proven channels.",
            "Ignore runway and focus purely on product polish.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round5": {
        "skill": "Team & Strategy",
        "prompt": "Traction is flat but a subset of users loves one use-case. What now?",
        "options": [
            "Keep trying to serve everyone with the same product.",
            "Focus your roadmap and messaging on the use-case that’s working.",
            "Pause all changes while you think about a new idea.",
        ],
        "scores": [2, 5, 1],
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
    "Market Research & Marketing": ["sk_round1"],
    "Product & Technical": ["sk_round2"],
    "Sales & Networking": ["sk_round3"],
    "Financial Management": ["sk_round4"],
    "Team & Strategy": ["sk_round5"],
}

# ============== RESOURCES (NEW TIME & SUPPORT LOGIC) ==============

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

# ============== BUSINESS ACUMEN ==============

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
            "You plan to 'go viral' but have no concrete channels.",
            "You’ve tested a few acquisition channels and have one that reliably brings leads.",
            "You intend to rely on word-of-mouth only.",
        ],
        "scores": [1, 5, 2],
    },
    "ac_ops": {
        "subdim": "Operational Feasibility",
        "prompt": "Which setup is most likely to deliver consistently?",
        "options": [
            "You rely on a fragile, manual process only you understand.",
            "You have documented processes and can train others to deliver.",
            "You assume you’ll figure out delivery once demand shows up.",
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

# ============== STATE & HELPERS ==============

if "page" not in st.session_state:
    st.session_state.page = 0
if "max_page" not in st.session_state:
    st.session_state.max_page = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False


def go_to(page_idx: int):
    st.session_state.page = page_idx
    if page_idx > st.session_state.max_page:
        st.session_state.max_page = page_idx
    st.experimental_rerun()


def get_mc_score(qdict, qid: str):
    q = qdict[qid]
    ans = st.session_state.get(qid)
    if not ans or ans not in q["options"]:
        return None
    idx = q["options"].index(ans)
    return float(q["scores"][idx])


# ----- scoring -----

def compute_mindset_scores():
    values = {s: [] for s in MINDSET_SUBDIMS}
    values["Opportunity Recognition"].append(compute_opportunity_score())
    values["Value Creation Focus"].append(compute_value_creation_score())
    for qid, q in MINDSET_QUESTIONS.items():
        score = get_mc_score(MINDSET_QUESTIONS, qid)
        if score is None:
            continue
        values[q["subdim"]].append(score)
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
    # resource strength sliders
    fin = float(st.session_state.get("res_fin_level", 3))
    tech = float(st.session_state.get("res_tech_level", 3))
    talent = float(st.session_state.get("res_talent_level", 3))
    network = float(st.session_state.get("res_network_level", 3))

    # time: realistic pattern options
    time_choice = st.session_state.get("res_time_pattern")
    time_map = {
        "I can consistently protect 25+ hours most weeks.": 5,
        "I can usually protect 10–25 hours, with some weeks disrupted.": 4,
        "I have 5–10 hours in irregular pockets.": 3,
        "I rarely have focused time; it’s hard to commit consistently.": 1,
    }
    time_score = float(time_map.get(time_choice, 2))

    # support: people + reaction
    support_count = 0
    for key in ["sup_brainstorm", "sup_emotional", "sup_tactical", "sup_intros"]:
        if st.session_state.get(key, False):
            support_count += 1
    support_react = st.session_state.get("sup_reaction")
    react_map = {
        "They’re mostly encouraging and try to help.": 5,
        "They’re neutral or politely interested.": 3,
        "They tend to be skeptical or discouraging.": 1,
    }
    react_score = float(react_map.get(support_react, 3))
    support_base = 1 + (support_count / 4.0) * 4  # 0–4 mapped to 1–5
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
        return "High readiness to pursue/accelerate a venture."
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


# ============== PAGE SETUP & NAV ==============

PAGE_LABELS = [
    "Game 1: Customer Signals",
    "Game 2: Constraint Cards",
    "Game 3: Next-Step Choices",
    "Game 4: Shock Cards",
    "Game 5: Feature Board",
    "Skills Game",
    "Resources",
    "Venture-Building Knowledge",
    "Readiness Profile",
]

st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("Entrepreneurial Readiness Simulation")

nav_cols = st.columns(len(PAGE_LABELS))
for i, label in enumerate(PAGE_LABELS):
    with nav_cols[i]:
        disabled = i > st.session_state.max_page
        if st.button(label, disabled=disabled, key=f"nav_{i}"):
            go_to(i)

st.write(f"Step {st.session_state.page + 1} of {len(PAGE_LABELS)}")

page = st.session_state.page

# ============== PAGE CONTENTS ==============

# Game 1 – customer tiles
if page == 0:
    st.subheader("Game 1: Customer Signals")
    st.caption("Scan short customer situations and tag the ones that hide real, solvable pain.")
    card_cols = st.columns(2)
    for idx, sc in enumerate(OPP_SCENARIOS):
        col = card_cols[idx % 2]
        with col:
            st.container(border=True)
            st.checkbox(sc["text"], key=sc["key"])
    if st.button("Next ▸"):
        go_to(1)

# Game 2 – constraint cards
elif page == 1:
    st.subheader("Game 2: Constraint Cards")
    st.caption("For each constraint, pick how you’d actually respond if this were your project.")
    for qid, q in MINDSET_QUESTIONS.items():
        if q["subdim"] != "Resourcefulness":
            continue
        st.markdown(f"**{q['prompt']}**")
        st.radio(
            "",
            options=["(select one)"] + q["options"],
            key=qid,
        )
        st.markdown("---")
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(0)
    if cols[1].button("Next ▸"):
        go_to(2)

# Game 3 – execution choices
elif page == 2:
    st.subheader("Game 3: Next-Step Choices")
    st.caption("Given limited time or information, choose what you’d actually do next.")
    for qid, q in MINDSET_QUESTIONS.items():
        if q["subdim"] != "Execution Bias":
            continue
        st.markdown(f"**{q['prompt']}**")
        st.radio(
            "",
            options=["(select one)"] + q["options"],
            key=qid,
        )
        st.markdown("---")
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(1)
    if cols[1].button("Next ▸"):
        go_to(3)

# Game 4 – shock cards
elif page == 3:
    st.subheader("Game 4: Shock Cards")
    st.caption("React to unexpected shocks in a way that keeps the venture healthy.")
    for qid, q in MINDSET_QUESTIONS.items():
        if q["subdim"] != "Resilience & Adaptability":
            continue
        st.markdown(f"**{q['prompt']}**")
        st.radio(
            "",
            options=["(select one)"] + q["options"],
            key=qid,
        )
        st.markdown("---")
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(2)
    if cols[1].button("Next ▸"):
        go_to(4)

# Game 5 – feature priority
elif page == 4:
    st.subheader("Game 5: Feature Board")
    st.caption("You have limited prioritization points. Use sliders to show what you’d actually focus on.")
    st.markdown("Imagine you have 10 units of priority to allocate across these possible changes.")
    for f in VALUE_FEATURES:
        st.slider(
            f["name"],
            min_value=0,
            max_value=5,
            value=3,
            key=f["key"],
        )
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(3)
    if cols[1].button("Next ▸"):
        go_to(5)

# Skills page
elif page == 5:
    st.subheader("Skills Game")
    st.caption("Quick self-ratings plus a short scenario path.")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("How confident are you in finding and understanding customers?", 1, 5, 3, key="s_skill_mkt")
        st.slider("How confident are you in keeping day-to-day operations running smoothly?", 1, 5, 3, key="s_skill_ops")
        st.slider("How confident are you in budgeting and managing runway?", 1, 5, 3, key="s_skill_fin")
    with col2:
        st.slider("How confident are you in shaping and building products people can use?", 1, 5, 3, key="s_skill_prod")
        st.slider("How confident are you in selling and building relationships?", 1, 5, 3, key="s_skill_sales")
        st.slider("How confident are you in aligning people and priorities?", 1, 5, 3, key="s_skill_team")
    st.markdown("---")
    st.markdown("**Scenario Rounds**")
    for qid, q in SKILL_QUESTIONS.items():
        st.markdown(f"**{q['prompt']}**")
        st.radio(
            "",
            options=["(select one)"] + q["options"],
            key=qid,
        )
        st.markdown("---")
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(4)
    if cols[1].button("Next ▸"):
        go_to(6)

# Resources page (with revised time & support)
elif page == 6:
    st.subheader("Resources")
    st.caption("Indicate how strong your resource base is today (not hypothetically).")

    st.markdown("**Access to key resources (today):**")
    st.slider("Money you could realistically direct toward a venture in the next 3–6 months.", 1, 5, 3, key="res_fin_level")
    st.slider("Tools, platforms, or infrastructure you already have access to.", 1, 5, 3, key="res_tech_level")
    st.slider("People you could involve (co-founders, contractors, employees).", 1, 5, 3, key="res_talent_level")
    st.slider("Connections to customers, partners, mentors, or gatekeepers.", 1, 5, 3, key="res_network_level")

    st.markdown("---")
    st.markdown("**Time pattern:**")
    st.radio(
        "",
        options=[
            "(select one)",
            "I can consistently protect 25+ hours most weeks.",
            "I can usually protect 10–25 hours, with some weeks disrupted.",
            "I have 5–10 hours in irregular pockets.",
            "I rarely have focused time; it’s hard to commit consistently.",
        ],
        key="res_time_pattern",
    )

    st.markdown("---")
    st.markdown("**Support for ambitious goals:**")
    st.caption("Who can you realistically lean on when building something hard?")
    sup_cols = st.columns(2)
    with sup_cols[0]:
        st.checkbox("Someone I can brainstorm with on strategy or decisions.", key="sup_brainstorm")
        st.checkbox("Someone who will give me honest feedback without shutting me down.", key="sup_tactical")
    with sup_cols[1]:
        st.checkbox("Someone who is emotionally in my corner when things get rough.", key="sup_emotional")
        st.checkbox("Someone willing to make intros or open doors.", key="sup_intros")
    st.radio(
        "When I share an ambitious plan, the typical reaction from people around me is:",
        options=[
            "(select one)",
            "They’re mostly encouraging and try to help.",
            "They’re neutral or politely interested.",
            "They tend to be skeptical or discouraging.",
        ],
        key="sup_reaction",
    )

    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(5)
    if cols[1].button("Next ▸"):
        go_to(7)

# Acumen page
elif page == 7:
    st.subheader("Venture-Building Knowledge")
    st.caption("How you think about problem fit, markets, business models, and scaling.")
    for subdim in ACUMEN_SUBDIMS:
        for qid, q in ACUMEN_QUESTIONS.items():
            if q["subdim"] != subdim:
                continue
            st.markdown(f"**{q['prompt']}**")
            st.radio(
                "",
                options=["(select one)"] + q["options"],
                key=qid,
            )
            st.markdown("---")
    cols = st.columns(2)
    if cols[0].button("◂ Back"):
        go_to(6)
    if cols[1].button("Submit & see readiness profile ▸"):
        st.session_state.submitted = True
        go_to(8)

# Results page
elif page == 8:
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
            go_to(7)
