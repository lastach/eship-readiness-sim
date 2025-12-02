import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

# ---------- DIMENSIONS (5 big buckets) ---------- #

DIMENSIONS = [
    "Clarity & Opportunity Insight",
    "Drive & Identity Fit",
    "Resilience & Emotional Regulation",
    "Bias to Action & Momentum",
    "Risk & Resource Readiness",
]

WEIGHTS = {
    "Clarity & Opportunity Insight": 20,
    "Drive & Identity Fit": 20,
    "Resilience & Emotional Regulation": 20,
    "Bias to Action & Momentum": 20,
    "Risk & Resource Readiness": 20,
}

DIM_DESCRIPTIONS = {
    "Clarity & Opportunity Insight": (
        "How clearly you see the problem, customer, and opportunity, and how grounded that is "
        "in real-world feedback rather than imagination alone."
    ),
    "Drive & Identity Fit": (
        "How deeply this venture aligns with your values, energy, and sense of self — and how "
        "likely you are to stay engaged when it’s not glamorous."
    ),
    "Resilience & Emotional Regulation": (
        "How you respond to stress, setbacks, rejection, and ambiguity — whether you shut down, "
        "white-knuckle through, or adjust and keep going."
    ),
    "Bias to Action & Momentum": (
        "Your tendency to translate ideas into concrete movement week after week, rather than "
        "circling in planning or overthinking."
    ),
    "Risk & Resource Readiness": (
        "Your relationship with risk, responsibilities, and runway — how realistic your safety "
        "net is and how you make decisions with incomplete information."
    ),
}

# ---------- MULTIPLE-CHOICE CONFIG ---------- #
# Each question: id -> {dim, prompt, options(list), scores(list aligned with options)}

MC_QUESTIONS = {
    # Clarity & Opportunity Insight
    "q_clarity_focus": {
        "dim": "Clarity & Opportunity Insight",
        "prompt": "When someone asks what you're building, which feels closest?",
        "options": [
            "I give a different answer depending on the day.",
            "I can describe the idea but usually in a long, winding way.",
            "I can describe who it's for and what it does in a couple of sentences.",
            "I can describe the specific problem, who has it, and the outcome they care about.",
        ],
        "scores": [1, 2, 4, 5],
    },
    "q_market_validation": {
        "dim": "Clarity & Opportunity Insight",
        "prompt": "How much have you tested your assumptions with real people?",
        "options": [
            "Mostly none yet — it's still in my head.",
            "I've had a few informal chats but nothing structured.",
            "I've done structured conversations or tests with people who fit my target.",
            "I've run structured tests and changed my idea based on what I learned.",
        ],
        "scores": [1, 2, 4, 5],
    },

    # Drive & Identity Fit
    "q_drive_when_hard": {
        "dim": "Drive & Identity Fit",
        "prompt": "Imagine 6 months of slow progress. What’s most likely to happen?",
        "options": [
            "I’d probably drift to a different idea or project.",
            "I’d keep dabbling but my energy would drop a lot.",
            "I’d stay engaged but need outside pressure or accountability.",
            "I’d still feel pulled to work on this because it matters to me.",
        ],
        "scores": [1, 2, 3, 5],
    },
    "q_energy_source": {
        "dim": "Drive & Identity Fit",
        "prompt": "What feels most true about why you want to do this venture?",
        "options": [
            "I mainly want out of my current job/situation.",
            "I like the idea of being a founder and calling my own shots.",
            "I’m excited by this problem and the people it affects.",
            "This problem connects to my story and feels personally meaningful.",
        ],
        "scores": [1, 2, 4, 5],
    },

    # Resilience & Emotional Regulation
    "q_rejection_pattern": {
        "dim": "Resilience & Emotional Regulation",
        "prompt": "After several lukewarm or negative responses in a row, what’s your usual pattern?",
        "options": [
            "I quietly drop the idea and focus on something else.",
            "I feel stung and mostly try to prove people wrong in my head.",
            "I note it but keep going without changing much.",
            "I ask what didn’t land and look for patterns across conversations before deciding what to change.",
        ],
        "scores": [1, 2, 3, 5],
    },
    "q_reset_routine": {
        "dim": "Resilience & Emotional Regulation",
        "prompt": "When you’re stressed or discouraged about the venture, what usually happens?",
        "options": [
            "I stay in that state and mostly avoid the venture for a while.",
            "I push through but feel pretty fried.",
            "I have some ways to reset, but I use them inconsistently.",
            "I have reliable ways to reset (sleep, exercise, reflection, etc.) and then re-engage.",
        ],
        "scores": [1, 2, 3, 5],
    },

    # Bias to Action & Momentum
    "q_free_hour": {
        "dim": "Bias to Action & Momentum",
        "prompt": "You unexpectedly get a free focused hour for your venture. What are you most likely to do?",
        "options": [
            "Scroll, read, or watch more content related to the space.",
            "Tidy up planning docs, slides, or a Notion page.",
            "Reach out to someone (customer, partner, advisor) or schedule conversations.",
            "Build or tweak something concrete that someone else can react to.",
        ],
        "scores": [1, 2, 4, 5],
    },
    "q_week_pattern": {
        "dim": "Bias to Action & Momentum",
        "prompt": "Over the last couple of months, which pattern best fits your progress?",
        "options": [
            "I think about it a lot but rarely take concrete steps.",
            "I work in big bursts and then stop for long stretches.",
            "Most weeks I move something forward, but it’s inconsistent.",
            "Most weeks I move a few specific, high-leverage things forward.",
        ],
        "scores": [1, 2, 3, 5],
    },

    # Risk & Resource Readiness
    "q_uncertainty_choice": {
        "dim": "Risk & Resource Readiness",
        "prompt": "You’re at ~60% confidence in your direction. What do you usually do?",
        "options": [
            "Wait until I feel much more certain before making a move.",
            "Make small, very safe moves but avoid real exposure.",
            "Make a clear decision, but only after extensive analysis.",
            "Make a decision, act, and adjust based on what I learn.",
        ],
        "scores": [1, 2, 3, 5],
    },
    "q_commitment_window": {
        "dim": "Risk & Resource Readiness",
        "prompt": "Realistically, how long could you pursue this with focused effort before needing a clear financial result?",
        "options": [
            "I would need it to pay off almost immediately.",
            "A few months with very limited downside.",
            "Around 6–12 months with some tradeoffs.",
            "A year or more with manageable risk to my life obligations.",
        ],
        "scores": [1, 2, 4, 5],
    },
}

# ---------- SLIDER CONFIG (1 per dimension) ---------- #

SLIDERS = [
    {
        "key": "s_clarity",
        "dim": "Clarity & Opportunity Insight",
        "label": "How clear does the opportunity feel in your own mind right now?",
    },
    {
        "key": "s_drive",
        "dim": "Drive & Identity Fit",
        "label": "How strong is your internal pull to work on *this* venture (not just 'something entrepreneurial')?",
    },
    {
        "key": "s_resilience",
        "dim": "Resilience & Emotional Regulation",
        "label": "How confident are you in your ability to stay emotionally steady when things are bumpy?",
    },
    {
        "key": "s_action",
        "dim": "Bias to Action & Momentum",
        "label": "How often do you turn thoughts about your venture into concrete actions in a typical week?",
    },
    {
        "key": "s_risk_resources",
        "dim": "Risk & Resource Readiness",
        "label": "How supported and resourced do you feel to experiment with this (time, money, energy, responsibilities)?",
    },
]

# ---------- SESSION STATE ---------- #

if "step" not in st.session_state:
    st.session_state.step = 1

if "scores" not in st.session_state:
    st.session_state.scores = {dim: 0.0 for dim in DIMENSIONS}


def next_step():
    st.session_state.step = min(3, st.session_state.step + 1)


def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)


def get_mc_score(qid: str):
    """Return score for a multiple-choice question; None if placeholder / unanswered."""
    qconf = MC_QUESTIONS[qid]
    ans = st.session_state.get(qid)
    if not ans or ans not in qconf["options"]:
        return None
    idx = qconf["options"].index(ans)
    return float(qconf["scores"][idx])


def compute_dimension_scores():
    sums = {d: 0.0 for d in DIMENSIONS}
    counts = {d: 0 for d in DIMENSIONS}

    # sliders
    for s in SLIDERS:
        val = st.session_state.get(s["key"])
        if val is not None:
            sums[s["dim"]] += float(val)
            counts[s["dim"]] += 1

    # multiple choice
    for qid, qconf in MC_QUESTIONS.items():
        score = get_mc_score(qid)
        if score is not None:
            dim = qconf["dim"]
            sums[dim] += score
            counts[dim] += 1

    # average per dimension
    scores = {}
    for dim in DIMENSIONS:
        if counts[dim] > 0:
            scores[dim] = round(sums[dim] / counts[dim], 2)
        else:
            scores[dim] = 0.0
    return scores


def compute_total_score(dim_scores):
    total = 0.0
    for dim, score in dim_scores.items():
        weight = WEIGHTS[dim]
        total += (score / 5.0) * weight
    return round(total, 1)


def readiness_label(total_score):
    if total_score >= 85:
        return "Launch-ready"
    elif total_score >= 70:
        return "Strong potential – refine weak spots"
    elif total_score >= 50:
        return "Early-stage readiness"
    else:
        return "Conceptual phase – shore up foundations first"


def critical_gates_ok(scores):
    # use the big 3: Drive, Resilience, Action
    return (
        scores["Drive & Identity Fit"] >= 3.0
        and scores["Resilience & Emotional Regulation"] >= 3.0
        and scores["Bias to Action & Momentum"] >= 3.0
    )


def readiness_archetype(scores):
    c = scores["Clarity & Opportunity Insight"]
    d = scores["Drive & Identity Fit"]
    r = scores["Resilience & Emotional Regulation"]
    a = scores["Bias to Action & Momentum"]
    k = scores["Risk & Resource Readiness"]

    if c >= 4 and d >= 4 and a < 3:
        return "🧠 The Insightful Planner"
    if d >= 4 and a >= 4 and r < 3:
        return "⚡ The Driven Sprinter"
    if a >= 4 and k < 3:
        return "🎲 The Bold Gambler"
    if c >= 4 and d >= 4 and r >= 3.5 and a >= 3.5 and k >= 3:
        return "🔧 The Emerging Builder"
    return "🔍 The Thoughtful Explorer"


# ---------- UI SHELL ---------- #

st.title("Entrepreneurial Readiness Simulation")
st.caption("Five core dimensions of readiness, based on how you actually think and behave.")

with st.sidebar:
    st.header("Navigation")
    step = st.session_state.step
    st.write(f"Current step: **{step} / 3**")
    if step > 1:
        st.button("⬅️ Back", on_click=prev_step)
    if step < 3:
        st.button("➡️ Next", on_click=next_step)

# ---------- STEP 1: SLIDERS & SOME MC ---------- #

if st.session_state.step == 1:
    st.subheader("Step 1 · Baseline Self-View")

    st.markdown("Use the sliders to rate yourself honestly **right now**, not ideally.")

    for sconf in SLIDERS:
        st.slider(
            sconf["label"],
            min_value=1,
            max_value=5,
            value=3,
            key=sconf["key"],
        )

    st.markdown("---")
    st.markdown("### Quick Sense of Your Venture")

    # Two core MC questions from different dimensions
    for qid in ["q_clarity_focus", "q_energy_source"]:
        q = MC_QUESTIONS[qid]
        st.radio(
            q["prompt"],
            options=["(select one)"] + q["options"],
            key=qid,
        )

    st.info("Use the sidebar to go to Step 2 when you’re ready.")

# ---------- STEP 2: REMAINING SCENARIOS ---------- #

elif st.session_state.step == 2:
    st.subheader("Step 2 · How You Tend to Behave in Practice")

    # Group questions by dimension for nicer layout
    for dim in DIMENSIONS:
        st.markdown(f"#### {dim}")
        for qid, qconf in MC_QUESTIONS.items():
            if qconf["dim"] != dim:
                continue
            # Skip ones already asked in Step 1
            if qid in ["q_clarity_focus", "q_energy_source"]:
                continue
            st.radio(
                qconf["prompt"],
                options=["(select one)"] + qconf["options"],
                key=qid,
            )
        st.markdown("")

    st.info("Use the sidebar to go to Step 3 to view your readiness profile.")

# ---------- STEP 3: RESULTS ---------- #

elif st.session_state.step == 3:
    st.subheader("Step 3 · Your Readiness Profile")

    dim_scores = compute_dimension_scores()
    st.session_state.scores = dim_scores

    total_score = compute_total_score(dim_scores)
    gates_ok = critical_gates_ok(dim_scores)
    archetype = readiness_archetype(dim_scores)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Overall Score")
        st.metric("Entrepreneurial Readiness Score", f"{total_score} / 100")
        st.write(f"**Interpretation:** {readiness_label(total_score)}")
        if not gates_ok:
            st.warning(
                "One or more foundational dimensions (Drive & Identity Fit, Resilience, "
                "Bias to Action) is below 3/5. That doesn't mean 'don't do it', but it "
                "does mean your personal foundation deserves attention in parallel."
            )

    with col_right:
        st.markdown("### Archetype")
        st.write(f"**{archetype}**")

    st.markdown("---")
    st.markdown("### Dimension Breakdown")

    df = pd.DataFrame(
        {
            "Dimension": DIMENSIONS,
            "Score (1–5)": [dim_scores[d] for d in DIMENSIONS],
            "Weight": [WEIGHTS[d] for d in DIMENSIONS],
        }
    )
    st.dataframe(df, use_container_width=True)

    st.markdown("### Readiness Chart")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Score (1–5):Q", scale=alt.Scale(domain=[0, 5])),
            y=alt.Y("Dimension:N", sort="-x"),
            tooltip=["Dimension", "Score (1–5)", "Weight"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("### What Each Dimension Is Looking At")

    for dim in DIMENSIONS:
        st.markdown(f"**{dim} – {dim_scores[dim]:.2f}/5**")
        st.write(DIM_DESCRIPTIONS[dim])

    st.info(
        "You can go back to Steps 1 and 2, change your answers, and see how your profile shifts. "
        "This is a snapshot of readiness today, not a verdict on your potential."
    )
