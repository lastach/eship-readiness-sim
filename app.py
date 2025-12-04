import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

# ================== TOP-LEVEL COMPONENTS ==================

COMPONENTS = [
    "Entrepreneurial Mindset",
    "Entrepreneurial Skills",
    "Resource Availability",
    "Entrepreneurship / Business Acumen",
]

COMP_WEIGHTS = {c: 25 for c in COMPONENTS}

# ================== MINDSET (MINI-GAMES) ==================

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

# ---- Opportunity Recognition GAME (checkbox vignettes) ----

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
    """
    Score 1–5 based on how well they select the real pain scenarios.
    True positives help, false positives and misses hurt.
    """
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
        return 1.0  # fallback
    raw = tp - 0.5 * fp - fn
    max_raw = total_true  # best case: all true selected, no mistakes
    norm = max(0.0, min(1.0, raw / max_raw))  # 0–1
    return round(1 + 4 * norm, 2)  # map to 1–5


# ---- Value Creation GAME (priority points across features) ----

VALUE_FEATURES = [
    {
        "key": "feat_a",
        "name": "Feature A – Remove a bug causing 25% of users to abandon onboarding.",
        "ideal_points": 5,
    },
    {
        "key": "feat_b",
        "name": "Feature B – Add a cosmetic dashboard theme option.",
        "ideal_points": 1,
    },
    {
        "key": "feat_c",
        "name": "Feature C – Improve a workflow that power users run daily.",
        "ideal_points": 4,
    },
    {
        "key": "feat_d",
        "name": "Feature D – Experimental idea with no demand signals yet.",
        "ideal_points": 2,
    },
    {
        "key": "feat_e",
        "name": "Feature E – Reduce server costs by 10% (no user-facing change).",
        "ideal_points": 3,
    },
]

def compute_value_creation_score():
    """Score 1–5 based on how close their slider pattern is to the ideal."""
    diffs = []
    for f in VALUE_FEATURES:
        val = st.session_state.get(f["key"], 3)
        try:
            val = float(val)
        except Exception:
            val = 3.0
        diff = abs(val - f["ideal_points"])
        diffs.append(diff)
    if not diffs:
        return 1.0
    avg_diff = sum(diffs) / len(diffs)  # 0 = perfect, larger = worse
    norm = max(0.0, min(1.0, (4.0 - avg_diff) / 4.0))  # map 0–4 diff to 1–0
    return round(1 + 4 * norm, 2)


# ---- Mindset scenario rounds for other subdimensions ----

MINDSET_QUESTIONS = {
    # Resourcefulness
    "ms_res_1": {
        "subdim": "Resourcefulness",
        "prompt": "No Budget for Research: You must understand why users churn. You have: zero budget.",
        "options": [
            "Pause until you have budget for a proper study.",
            "Scrape public reviews / support tickets and ask a few users directly.",
            "Ask friends what they think about churn in general.",
        ],
        "scores": [1, 5, 2],
    },
    "ms_res_2": {
        "subdim": "Resourcefulness",
        "prompt": "No Designer Available: You must produce a landing page today.",
        "options": [
            "Use a no-code template tool and ship something basic.",
            "Wait for a designer so it looks polished.",
            "Write copy now and hope design time appears later.",
        ],
        "scores": [5, 1, 2],
    },
    "ms_res_3": {
        "subdim": "Resourcefulness",
        "prompt": "No Engineering Time: You need to test a new feature idea.",
        "options": [
            "Create a simple clickable mockup or fake-door test.",
            "Wait until engineers have time to build it properly.",
            "Describe the idea in a long doc and share it internally.",
        ],
        "scores": [5, 1, 2],
    },

    # Execution Bias
    "ms_exec_1": {
        "subdim": "Execution Bias",
        "prompt": "You have one afternoon to de-risk a new idea. What do you do?",
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
        "prompt": "You’re unsure between two target segments.",
        "options": [
            "Pick one based purely on your intuition.",
            "Run two tiny tests in parallel and compare response.",
            "Wait until you can do a full market study.",
        ],
        "scores": [2, 5, 1],
    },

    # Resilience & Adaptability
    "ms_resil_1": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: Contractor delays by 3 days. What do you do?",
        "options": [
            "Do nothing and hope it’s fine.",
            "Replace the contractor entirely.",
            "Re-scope the sprint and adjust dependent work.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_2": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: CAC jumps 40% overnight. What do you do?",
        "options": [
            "Keep campaigns running and see what happens.",
            "Kill all paid channels immediately.",
            "Shift spend, test new creatives, and review funnel quality.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_3": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: Competitor drops price by 70% (predatory). What do you do?",
        "options": [
            "Keep your current pricing and ignore it.",
            "Lower price slightly and hope to keep up.",
            "Pivot toward a segment where you compete on value, not price.",
        ],
        "scores": [1, 2, 5],
    },
}

# ================== SKILLS ==================

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
        "prompt": "Round 1 – Market Research: Trial users aren’t converting. What do you do first?",
        "options": [
            "Run a broad online survey with anyone you can find.",
            "Interview 5–10 recent trial users about their decision.",
            "Change the homepage headline based on your intuition.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round2": {
        "skill": "Product & Technical",
        "prompt": "Round 2 – Product: You can only ship one feature this sprint.",
        "options": [
            "A 'nice to have' that a few users casually mentioned.",
            "A fix for a bug that blocks a key workflow.",
            "A flashy new feature that will look good in demos.",
        ],
        "scores": [2, 5, 3],
    },
    "sk_round3": {
        "skill": "Sales & Networking",
        "prompt": "Round 3 – Sales: You have 10 warm leads and limited time. What’s your approach?",
        "options": [
            "Send a generic email blast and hope some respond.",
            "Send tailored messages and schedule 1:1 conversations.",
            "Post about your product on social media instead.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round4": {
        "skill": "Financial Management",
        "prompt": "Round 4 – Financials: You have 3 months of runway left. What do you prioritize?",
        "options": [
            "Cut all spending, including things that fuel growth.",
            "Identify and cut low-ROI spend while doubling down on proven channels.",
            "Ignore runway and focus purely on product polish.",
        ],
        "scores": [2, 5, 1],
    },
    "sk_round5": {
        "skill": "Team & Strategy",
        "prompt": "Round 5 – Strategy: Traction is flat but a subset of users loves one use-case.",
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
    # Operations: self-rating only
}

# ================== RESOURCES ==================

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
    "Support": "Emotional and practical support from people in your life.",
}

# ================== BUSINESS ACUMEN ==================

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
    "Go-to-Market Readiness": "Validated channels, messaging, and acquisition strategy.",
    "Operational Feasibility": "Ability to deliver reliably given tech, supply, and processes.",
    "Scalability Potential": "Model, market, and operations can grow without breaking.",
}

ACUMEN_QUESTIONS = {
    "ac_ps_fit": {
        "subdim": "Problem–Solution Fit",
        "prompt": "Which signal best reflects strong problem–solution fit?",
        "options": [
            "People say your idea is 'cool' in casual conversation.",
            "A segment of users repeatedly describes the same painful problem you address.",
            "Your landing page has a high click-through rate from ads.",
        ],
        "scores": [2, 5, 3],
    },
    "ac_market": {
        "subdim": "Market Viability",
        "prompt": "Which situation suggests stronger market viability?",
        "options": [
            "Huge total market, but you don’t know who to target first.",
            "A smaller, clearly defined segment that you can reliably reach.",
            "A big market with many competitors and no clear angle.",
        ],
        "scores": [3, 5, 2],
    },
    "ac_model": {
        "subdim": "Business Model Soundness",
        "prompt": "Which business model is most sound?",
        "options": [
            "High price point, but each customer costs more to serve than they pay.",
            "Moderate price, high margin, with a clear path to repeat purchases.",
            "Low price, unclear costs, and no idea how many customers you need.",
        ],
        "scores": [1, 5, 2],
    },
    "ac_gtm": {
        "subdim": "Go-to-Market Readiness",
        "prompt": "Which describes better go-to-market readiness?",
        "options": [
            "You plan to 'go viral' but have no concrete channels.",
            "You’ve tested a few acquisition channels and have one that reliably brings leads.",
            "You intend to rely on word-of-mouth only.",
        ],
        "scores": [1, 5, 2],
    },
    "ac_ops": {
        "subdim": "Operational Feasibility",
        "prompt": "Which situation is most operationally feasible?",
        "options": [
            "You rely on a fragile, manual process only you understand.",
            "You have documented processes and can train others to deliver reliably.",
            "You assume you’ll figure out delivery once demand shows up.",
        ],
        "scores": [2, 5, 1],
    },
    "ac_scale": {
        "subdim": "Scalability Potential",
        "prompt": "Which model has better scalability potential?",
        "options": [
            "Each new customer requires a lot of custom work from you.",
            "Most of the value is delivered through software or repeatable systems.",
            "You depend on rare, highly specialized human talent for every deal.",
        ],
        "scores": [2, 5, 1],
    },
}

# ================== SESSION STATE & HELPERS ==================

if "step" not in st.session_state:
    st.session_state.step = 1

def next_step():
    st.session_state.step = min(3, st.session_state.step + 1)

def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)

def get_mc_score(qdict, qid: str):
    q = qdict[qid]
    ans = st.session_state.get(qid)
    if not ans or ans not in q["options"]:
        return None
    idx = q["options"].index(ans)
    return float(q["scores"][idx])

# ----- Mindset scoring -----

def compute_mindset_scores():
    # collect lists per subdimension, average to 1–5
    values = {s: [] for s in MINDSET_SUBDIMS}

    # Opportunity Recognition game
    values["Opportunity Recognition"].append(compute_opportunity_score())

    # Value Creation game
    values["Value Creation Focus"].append(compute_value_creation_score())

    # Resourcefulness / Execution / Resilience scenarios
    for qid, q in MINDSET_QUESTIONS.items():
        score = get_mc_score(MINDSET_QUESTIONS, qid)
        if score is None:
            continue
        values[q["subdim"]].append(score)

    sub_scores = {}
    for sd in MINDSET_SUBDIMS:
        if values[sd]:
            sub_scores[sd] = round(sum(values[sd]) / len(values[sd]), 2)
        else:
            sub_scores[sd] = 1.0  # baseline if unanswered

    overall = round(sum(sub_scores.values()) / len(MINDSET_SUBDIMS), 2)
    return overall, sub_scores

# ----- Skills scoring -----

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
        if vals:
            skill_scores[skill] = round(sum(vals) / len(vals), 2)
        else:
            skill_scores[skill] = 1.0
    overall = round(sum(skill_scores.values()) / len(SKILL_AREAS), 2)
    return overall, skill_scores

# ----- Resource scoring -----

def compute_resource_scores():
    has_money = st.session_state.get("res_money", False)
    has_tech = st.session_state.get("res_tech", False)
    has_talent = st.session_state.get("res_talent", False)
    has_network = st.session_state.get("res_network", False)

    # Direct: checked = 5, unchecked = 1
    sub_scores = {
        "Financial Resources": 5.0 if has_money else 1.0,
        "Technology & Infrastructure": 5.0 if has_tech else 1.0,
        "Talent / Team": 5.0 if has_talent else 1.0,
        "Network": 5.0 if has_network else 1.0,
    }

    time_choice = st.session_state.get("res_time")
    time_map = {
        "40 or more hours": 5,
        "20 to 40 hours": 4,
        "Fewer than 20 hours": 2,
    }
    sub_scores["Time"] = float(time_map.get(time_choice, 1))

    sup_personal = st.session_state.get("res_sup_personal", 3)
    sup_prof = st.session_state.get("res_sup_prof", 3)
    sup_ent = st.session_state.get("res_sup_ent", 3)
    support_score = (sup_personal + sup_prof + sup_ent) / 3.0
    sub_scores["Support"] = round(float(support_score), 2)

    overall = round(sum(sub_scores.values()) / len(sub_scores), 2)
    return overall, sub_scores

# ----- Acumen scoring -----

def compute_acumen_scores():
    values = {s: [] for s in ACUMEN_SUBDIMS}
    for qid, q in ACUMEN_QUESTIONS.items():
        s = get_mc_score(ACUMEN_QUESTIONS, qid)
        if s is None:
            continue
        values[q["subdim"]].append(s)

    sub_scores = {}
    for sd in ACUMEN_SUBDIMS:
        if values[sd]:
            sub_scores[sd] = round(sum(values[sd]) / len(values[sd]), 2)
        else:
            sub_scores[sd] = 1.0
    overall = round(sum(sub_scores.values()) / len(ACUMEN_SUBDIMS), 2)
    return overall, sub_scores

# ----- Overall -----

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
            "Your profile suggests you’re in a **foundation-building phase**. "
            "This is a great moment to build skills and understanding without heavy pressure to launch. "
            + tail
        )
    elif total_score < 70:
        return (
            "You’re showing **early-stage readiness**. You can absolutely run real experiments, "
            "while deliberately working on the thinner parts of your foundation. "
            + tail
        )
    elif total_score < 85:
        return (
            "You have **strong potential** and a solid base. You can keep moving forward on a venture, "
            "while keeping an eye on weaker components so they don’t become bottlenecks. "
            + tail
        )
    else:
        return (
            "You’re showing **high entrepreneurial readiness**. At this stage, focus more on building systems "
            "around your strengths than on fixing gaps — but watching your relatively weaker component(s) "
            "will help avoid blind spots as you scale. "
            + tail
        )

# ================== UI ==================

st.title("Entrepreneurial Readiness Simulation")
st.caption("A mini-simulation to assess mindset, skills, resources, and entrepreneurial acumen.")

with st.sidebar:
    st.header("Navigation")
    step = st.session_state.step
    st.write(f"Current step: **{step} / 3**")
    if step > 1:
        st.button("⬅️ Back", on_click=prev_step)
    if step < 3:
        st.button("➡️ Next", on_click=next_step)

# ---------- STEP 1: MINDSET GAMES ----------

if st.session_state.step == 1:
    st.subheader("Step 1 · Entrepreneurial Mindset Mini-Games")

    # Opportunity Recognition game
    st.markdown("### Opportunity Recognition")
    st.caption(MINDSET_DESCRIPTIONS["Opportunity Recognition"])
    st.markdown(
        "For each scenario below, **check the ones you believe hide a real, solvable pain with strong demand signals.**"
    )
    for sc in OPP_SCENARIOS:
        st.checkbox(sc["text"], key=sc["key"])

    st.markdown("---")

    # Resourcefulness, Execution, Resilience – scenario rounds
    for subdim in ["Resourcefulness", "Execution Bias", "Resilience & Adaptability"]:
        st.markdown(f"### {subdim}")
        st.caption(MINDSET_DESCRIPTIONS[subdim])
        for qid, q in MINDSET_QUESTIONS.items():
            if q["subdim"] != subdim:
                continue
            st.radio(
                q["prompt"],
                options=["(select one)"] + q["options"],
                key=qid,
            )
        st.markdown("")

    st.markdown("---")

    # Value Creation Focus game
    st.markdown("### Value Creation Focus")
    st.caption(MINDSET_DESCRIPTIONS["Value Creation Focus"])
    st.markdown(
        "Imagine you have **10 units of priority** to allocate across these five potential changes. "
        "Use the sliders to reflect where you would put more or less emphasis. Don’t worry about summing perfectly to 10; "
        "we’re looking at the **relative** pattern."
    )
    for f in VALUE_FEATURES:
        st.slider(
            f["name"],
            min_value=0,
            max_value=5,
            value=3,
            key=f["key"],
        )

    st.info("Use the sidebar to move to Step 2 once you’ve played the mindset games.")

# ---------- STEP 2: SKILLS + RESOURCES ----------

elif st.session_state.step == 2:
    st.subheader("Step 2 · Skills & Resource Game")

    st.markdown("### A. Self-Rated Skills")
    st.caption("Rate your current level in each area. Honest, current-state answers are most useful.")

    col1, col2 = st.columns(2)
    with col1:
        st.slider("Market Research & Marketing", 1, 5, 3, key="s_skill_mkt")
        st.slider("Operations", 1, 5, 3, key="s_skill_ops")
        st.slider("Financial Management", 1, 5, 3, key="s_skill_fin")
    with col2:
        st.slider("Product & Technical", 1, 5, 3, key="s_skill_prod")
        st.slider("Sales & Networking", 1, 5, 3, key="s_skill_sales")
        st.slider("Team & Strategy", 1, 5, 3, key="s_skill_team")

    st.markdown("---")
    st.markdown("### B. Skill Scenario – 5 Quick Rounds")
    st.caption("Each round reflects a different skill area. Choose what you would *actually* do.")

    for qid, q in SKILL_QUESTIONS.items():
        st.radio(
            q["prompt"],
            options=["(select one)"] + q["options"],
            key=qid,
        )

    st.markdown("---")
    st.markdown("### C. Resource Availability")

    st.markdown("**Which resources are realistically accessible to you right now?**")
    st.caption("Think about what you could draw on within the next 1–3 months, not hypothetically.")
    colr1, colr2 = st.columns(2)
    with colr1:
        st.checkbox("Money / financial resources", key="res_money")
        st.checkbox("Technology & infrastructure (tools, platforms, etc.)", key="res_tech")
        st.checkbox("Talent / team (co-founders, employees, freelancers)", key="res_talent")
    with colr2:
        st.checkbox("Network (customers, partners, mentors, gatekeepers)", key="res_network")

    st.markdown("**Time per week you can dedicate to a venture (on average):**")
    st.radio(
        "",
        options=["(select one)", "40 or more hours", "20 to 40 hours", "Fewer than 20 hours"],
        key="res_time",
    )

    st.markdown("**Support from people in your life:**")
    colsup1, colsup2, colsup3 = st.columns(3)
    with colsup1:
        st.slider("Support for personal goals", 1, 5, 3, key="res_sup_personal")
    with colsup2:
        st.slider("Support for professional goals", 1, 5, 3, key="res_sup_prof")
    with colsup3:
        st.slider("Support for entrepreneurial goals", 1, 5, 3, key="res_sup_ent")

    st.info("Use the sidebar to move to Step 3 for business acumen and your results.")

# ---------- STEP 3: BUSINESS ACUMEN + RESULTS ----------

elif st.session_state.step == 3:
    st.subheader("Step 3 · Entrepreneurship / Business Acumen & Results")

    st.markdown("### A. Business Acumen Scenarios")
    st.caption("These focus on your understanding of how venture components work, not your current idea.")

    for subdim in ACUMEN_SUBDIMS:
        st.markdown(f"#### {subdim}")
        st.caption(ACUMEN_DESCRIPTIONS[subdim])
        for qid, q in ACUMEN_QUESTIONS.items():
            if q["subdim"] != subdim:
                continue
            st.radio(
                q["prompt"],
                options=["(select one)"] + q["options"],
                key=qid,
            )
        st.markdown("")

    st.markdown("---")
    st.markdown("### B. Your Readiness Profile")

    total_score, comp_scores, sub_scores = compute_overall_scores()

    st.markdown("#### Overall Score")
    st.metric("Entrepreneurial Readiness Score", f"{total_score} / 100")
    st.write(f"**Interpretation:** {readiness_label(total_score)}")
    st.write(suggestion_for_user(total_score, comp_scores))

    st.markdown("#### Component Scores")
    df_comp = pd.DataFrame(
        {
            "Component": COMPONENTS,
            "Score (1–5)": [comp_scores[c] for c in COMPONENTS],
            "Weight": [COMP_WEIGHTS[c] for c in COMPONENTS],
        }
    )

    chart = (
        alt.Chart(df_comp)
        .mark_bar()
        .encode(
            x=alt.X("Score (1–5):Q", scale=alt.Scale(domain=[0, 5])),
            y=alt.Y("Component:N", sort="-x"),
            tooltip=["Component", "Score (1–5)", "Weight"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("### C. Subdimension Details")

    st.markdown("**Entrepreneurial Mindset**")
    for sd in MINDSET_SUBDIMS:
        st.write(f"- **{sd} – {sub_scores['mindset'][sd]:.2f}/5** · {MINDSET_DESCRIPTIONS[sd]}")

    st.markdown("**Entrepreneurial Skills**")
    for sk in SKILL_AREAS:
        st.write(f"- **{sk} – {sub_scores['skills'][sk]:.2f}/5** · {SKILL_DESCRIPTIONS[sk]}")

    st.markdown("**Resource Availability**")
    for rs in RESOURCE_SUBDIMS:
        st.write(f"- **{rs} – {sub_scores['resources'][rs]:.2f}/5** · {RESOURCE_DESCRIPTIONS[rs]}")

    st.markdown("**Entrepreneurship / Business Acumen**")
    for ac in ACUMEN_SUBDIMS:
        st.write(f"- **{ac} – {sub_scores['acumen'][ac]:.2f}/5** · {ACUMEN_DESCRIPTIONS[ac]}")

    st.info(
        "You can go back to Steps 1 and 2, adjust your answers, and see how your profile changes. "
        "This simulation is a snapshot of readiness today, not a verdict on your long-term potential."
    )
