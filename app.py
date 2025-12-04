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

COMP_WEIGHTS = {
    "Entrepreneurial Mindset": 25,
    "Entrepreneurial Skills": 25,
    "Resource Availability": 25,
    "Entrepreneurship / Business Acumen": 25,
}

# ---- Mindset subdimensions (each 5% inside 25%) ----
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

# ---- Skills subdimensions ----
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

# ---- Resource Availability subdimensions ----
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

# ---- Business Acumen subdimensions ----
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
    "Market Viability": "Reachable segment, credible demand, and meaningful differentiation.",
    "Business Model Soundness": "Pricing, unit economics, cost structure, and profitability path.",
    "Go-to-Market Readiness": "Channels, messaging, and acquisition strategy that actually reach users.",
    "Operational Feasibility": "Ability to deliver reliably given tech, supply, and processes.",
    "Scalability Potential": "Growth without the model or operations breaking.",
}

# ================== MINDSET MINI-GAMES (MC) ==================

# Each question: id -> {subdim, prompt, options, scores}
MINDSET_QUESTIONS = {
    # Opportunity Recognition
    "ms_opp_1": {
        "subdim": "Opportunity Recognition",
        "prompt": "You see these snippets from customer life:\n"
                  "A) 80% of users manually export data weekly to fix errors.\n"
                  "B) Some users say your UI colors are ugly.\n"
                  "C) A few people mention they'd 'maybe like an app someday'.\n"
                  "Which hides the most promising opportunity?",
        "options": [
            "The color complaints — aesthetics drive conversions.",
            "The manual weekly export to fix errors.",
            "The vague desire for an app someday.",
        ],
        "scores": [2, 5, 1],
    },
    "ms_opp_2": {
        "subdim": "Opportunity Recognition",
        "prompt": "You get this data:\n"
                  "• 5% of users abandon sign-up.\n"
                  "• 40% start a key workflow but never finish.\n"
                  "• 20% open marketing emails.\n"
                  "Where do you investigate first?",
        "options": [
            "Sign-up abandonment.",
            "Email open rate.",
            "The unfinished key workflow.",
        ],
        "scores": [3, 2, 5],
    },

    # Resourcefulness
    "ms_res_1": {
        "subdim": "Resourcefulness",
        "prompt": "You must understand why users churn. Budget: $0. What do you do first?",
        "options": [
            "Wait until you have budget for a survey or agency.",
            "Scrape existing reviews / support tickets and reach out directly.",
            "Ask your friends what they think about churn in general.",
        ],
        "scores": [1, 5, 2],
    },
    "ms_res_2": {
        "subdim": "Resourcefulness",
        "prompt": "You need a landing page by tomorrow. No designer available.",
        "options": [
            "Use a no-code template tool and ship a basic page.",
            "Wait until a designer is free so it looks polished.",
            "Write the copy now and hope the design appears later.",
        ],
        "scores": [5, 1, 2],
    },

    # Execution Bias
    "ms_exec_1": {
        "subdim": "Execution Bias",
        "prompt": "You have a new product idea and one free afternoon. What do you do?",
        "options": [
            "Brainstorm names and logo concepts.",
            "Run a one-page landing test or 5 quick user calls.",
            "Write a 20-page strategy doc for the next year.",
        ],
        "scores": [2, 5, 1],
    },
    "ms_exec_2": {
        "subdim": "Execution Bias",
        "prompt": "You want to test interest for a new feature. Which next step is best?",
        "options": [
            "Build the full feature and launch quietly.",
            "Add a 'coming soon' button and measure clicks + follow-up.",
            "Survey your friends on social media about it.",
        ],
        "scores": [2, 5, 3],
    },

    # Resilience & Adaptability
    "ms_resil_1": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: contractor delays delivery by 3 days.\nWhat do you do?",
        "options": [
            "Do nothing and hope it's fine.",
            "Fire the contractor and look for a new one.",
            "Re-scope the sprint and adjust dependent work.",
        ],
        "scores": [1, 2, 5],
    },
    "ms_resil_2": {
        "subdim": "Resilience & Adaptability",
        "prompt": "Shock: CAC jumps 40% overnight.\nWhat do you do?",
        "options": [
            "Keep the ads running — it might correct itself.",
            "Kill all paid channels immediately.",
            "Shift spend, test new creatives, and review funnel quality.",
        ],
        "scores": [1, 2, 5],
    },

    # Value Creation Focus
    "ms_value_1": {
        "subdim": "Value Creation Focus",
        "prompt": "You have capacity for only one change this week. Metrics:\n"
                  "• Feature A: loved by 5 users, no revenue impact.\n"
                  "• Feature B: removes a top complaint and saves time.\n"
                  "• Feature C: makes the dashboard look cooler.\nWhat do you ship?",
        "options": [
            "Feature A – deepen love with early users.",
            "Feature B – fix the top complaint and save time.",
            "Feature C – improve perceived polish.",
        ],
        "scores": [3, 5, 2],
    },
    "ms_value_2": {
        "subdim": "Value Creation Focus",
        "prompt": "You see five roadmap items. Which do you prioritize first?",
        "options": [
            "A low-effort cosmetic improvement.",
            "A feature requested by one loud user.",
            "A change that improves retention by solving a recurring pain.",
        ],
        "scores": [2, 3, 5],
    },
}

# ================== SKILL MINI-GAME ==================

SKILL_QUESTIONS = {
    "sk_round1": {
        "skill": "Market Research & Marketing",
        "prompt": "Round 1 – Market Research: You want to understand why trial users don't convert. What do you do first?",
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

# Map technical/ops
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
    # Operations will rely on self-rating only in this version
}

# ================== BUSINESS ACUMEN MINI-GAME ==================

ACUMEN_QUESTIONS = {
    "ac_ps_fit": {
        "subdim": "Problem–Solution Fit",
        "prompt": "You’re evaluating problem–solution fit. Which signal matters most?",
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
    sums = {s: 0.0 for s in MINDSET_SUBDIMS}
    counts = {s: 0 for s in MINDSET_SUBDIMS}
    for qid, q in MINDSET_QUESTIONS.items():
        score = get_mc_score(MINDSET_QUESTIONS, qid)
        if score is not None:
            sd = q["subdim"]
            sums[sd] += score
            counts[sd] += 1
    sub_scores = {}
    for sd in MINDSET_SUBDIMS:
        sub_scores[sd] = round(sums[sd] / counts[sd], 2) if counts[sd] > 0 else 0.0
    # overall mindset = average of subdimensions
    overall = round(sum(sub_scores.values()) / len(MINDSET_SUBDIMS), 2) if MINDSET_SUBDIMS else 0.0
    return overall, sub_scores

# ----- Skills scoring -----
def compute_skill_scores():
    skill_scores = {}
    for skill in SKILL_AREAS:
        vals = []
        slider_key = SKILL_SLIDER_MAP.get(skill)
        if slider_key:
            val = st.session_state.get(slider_key)
            if val is not None:
                vals.append(float(val))
        scenario_ids = SKILL_SCENARIO_MAP.get(skill, [])
        for sid in scenario_ids:
            s = get_mc_score(SKILL_QUESTIONS, sid)
            if s is not None:
                vals.append(s)
        skill_scores[skill] = round(sum(vals) / len(vals), 2) if vals else 0.0
    overall = round(sum(skill_scores.values()) / len(SKILL_AREAS), 2) if SKILL_AREAS else 0.0
    return overall, skill_scores

# ----- Resource Availability scoring -----
def compute_resource_scores():
    # checkboxes
    has_money = st.session_state.get("res_money", False)
    has_tech = st.session_state.get("res_tech", False)
    has_talent = st.session_state.get("res_talent", False)
    has_network = st.session_state.get("res_network", False)

    resource_flags = [has_money, has_tech, has_talent, has_network]
    base_count = sum(1 for f in resource_flags if f)
    # normalize 0–4 to approx 1–5
    base_resource_score = 1 + (base_count / 4.0) * 4 if base_count > 0 else 1

    # Time
    time_choice = st.session_state.get("res_time")
    time_map = {
        "40 or more hours": 5,
        "20 to 40 hours": 4,
        "Fewer than 20 hours": 2,
    }
    time_score = time_map.get(time_choice, 1)

    # Support (three sliders)
    sup_personal = st.session_state.get("res_sup_personal", 3)
    sup_prof = st.session_state.get("res_sup_prof", 3)
    sup_ent = st.session_state.get("res_sup_ent", 3)
    support_score = (sup_personal + sup_prof + sup_ent) / 3.0

    sub_scores = {
        "Financial Resources": 5.0 if has_money else 2.0 if base_count > 0 else 1.0,
        "Technology & Infrastructure": 5.0 if has_tech else 2.0 if base_count > 0 else 1.0,
        "Talent / Team": 5.0 if has_talent else 2.0 if base_count > 0 else 1.0,
        "Network": 5.0 if has_network else 2.0 if base_count > 0 else 1.0,
        "Time": float(time_score),
        "Support": round(float(support_score), 2),
    }

    overall = round(sum(sub_scores.values()) / len(sub_scores), 2)
    return overall, sub_scores

# ----- Business Acumen scoring -----
def compute_acumen_scores():
    sums = {s: 0.0 for s in ACUMEN_SUBDIMS}
    counts = {s: 0 for s in ACUMEN_SUBDIMS}

    for qid, q in ACUMEN_QUESTIONS.items():
        score = get_mc_score(ACUMEN_QUESTIONS, qid)
        if score is not None:
            sd = q["subdim"]
            sums[sd] += score
            counts[sd] += 1

    sub_scores = {}
    for sd in ACUMEN_SUBDIMS:
        sub_scores[sd] = round(sums[sd] / counts[sd], 2) if counts[sd] > 0 else 0.0

    overall = round(sum(sub_scores.values()) / len(sub_scores), 2) if ACUMEN_SUBDIMS else 0.0
    return overall, sub_scores

# ----- Overall scoring -----
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
        weight = COMP_WEIGHTS[comp]
        total += (score / 5.0) * weight
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
    # find weakest components
    sorted_comps = sorted(COMPONENTS, key=lambda c: comp_scores[c])
    weakest = sorted_comps[0]
    second_weakest = sorted_comps[1] if len(sorted_comps) > 1 else None

    tail = f"Focus on strengthening **{weakest}**" + (f" and **{second_weakest}**" if second_weakest else "") + \
           " through small, low-risk experiments."

    if total_score < 50:
        return (
            "Your profile suggests you’re in a **foundation-building phase**. "
            "This is a great moment to build skills and understanding without heavy pressure to launch. "
            + tail
        )
    elif total_score < 70:
        return (
            "You’re showing **early-stage readiness**. You can absolutely run real experiments, "
            "while deliberately working on the parts of your foundation that are thinner. "
            + tail
        )
    elif total_score < 85:
        return (
            "You have **strong potential** and a solid base. You can keep moving forward on a venture, "
            "while keeping an eye on your weaker components so they don’t become bottlenecks. "
            + tail
        )
    else:
        return (
            "You’re showing **high entrepreneurial readiness**. At this stage, your focus is less on fixing "
            "gaps and more on building systems around your strengths. Still, watching your relatively weaker "
            "component(s) will help avoid blind spots as you scale. "
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

# ---------- STEP 1: MINDSET MINI-GAMES ----------

if st.session_state.step == 1:
    st.subheader("Step 1 · Entrepreneurial Mindset Mini-Games")
    st.markdown("These quick scenarios look at how you tend to think and respond as a founder.")

    for subdim in MINDSET_SUBDIMS:
        st.markdown(f"#### {subdim}")
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

    st.info("Use the sidebar to move to Step 2 once you’ve answered the mindset scenarios.")

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
