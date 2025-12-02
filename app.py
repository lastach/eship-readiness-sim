import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

# ------------------ CONSTANTS ------------------ #

DIMENSIONS = [
    "Vision & Problem Clarity",
    "Internal Motivation",
    "Emotional Resilience",
    "Risk Tolerance",
    "Execution Capacity",
    "Resource Access",
    "Skill Alignment",
    "Market Understanding",
    "Identity Alignment",
    "Momentum Signals",
]

WEIGHTS = {
    "Vision & Problem Clarity": 15,
    "Internal Motivation": 15,
    "Emotional Resilience": 10,
    "Risk Tolerance": 10,
    "Execution Capacity": 15,
    "Resource Access": 10,
    "Skill Alignment": 10,
    "Market Understanding": 5,
    "Identity Alignment": 5,
    "Momentum Signals": 5,
}

# Multiple-choice answer → score mappings (1–5)
ANSWER_SCORES = {
    "q_stage": {
        "I just have a vague idea and haven't written anything down.": 1,
        "I have a clear concept but haven't done anything with it yet.": 2,
        "I've done some basic thinking and notes, but no real testing.": 3,
        "I've talked to a few people and/or made a rough mockup.": 4,
        "I've run tests, pilots, or early sales conversations.": 5,
    },
    "q_clarity": {
        "I'm not really sure what problem I'm solving.": 1,
        "I know the problem, but I'm fuzzy on who it's really for.": 2,
        "I can describe the problem and a general target group.": 3,
        "I can describe a specific customer and their situation.": 4,
        "I have a very specific customer, context, and clear pain point.": 5,
    },
    "q_market_validation": {
        "I've never spoken to anyone who has this problem.": 1,
        "I've talked informally to 1–2 people.": 2,
        "I've had several casual conversations with people who seem to have this problem.": 3,
        "I've run a few structured interviews or small tests.": 4,
        "I've run structured interviews/tests and seen clear demand signals.": 5,
    },
    "q_overwhelm": {
        "I tend to freeze and avoid the work.": 1,
        "I bounce between tasks without much progress.": 2,
        "I push through but feel scattered and drained.": 3,
        "I pause, regroup, and then choose 1–2 priorities.": 4,
        "I calmly reset, choose the highest-leverage actions, and move.": 5,
    },
    "q_priorities": {
        "I mostly research and gather more information.": 2,
        "I mostly work on branding, visuals, or website.": 2,
        "I mostly refine the idea in documents or slides.": 3,
        "I mostly talk to potential customers or users.": 4,
        "I mostly talk to customers and build simple things they can react to.": 5,
    },
    "q_rejection": {
        "I feel discouraged and avoid bringing it up again.": 1,
        "I argue for why they're wrong.": 2,
        "I shrug and move on to something else.": 2,
        "I ask a few questions but mostly defend my idea.": 3,
        "I get curious, ask specific questions, and look for patterns in the feedback.": 5,
    },
    "q_uncertainty": {
        "I delay decisions until I feel sure.": 1,
        "I delay big decisions but make small ones.": 2,
        "I can decide with partial info but it stresses me.": 3,
        "I usually decide with partial info and adjust quickly if needed.": 4,
        "I prefer to move with partial info and learn as I go.": 5,
    },
    "q_week_pattern": {
        "I think about it a lot but rarely take concrete action.": 1,
        "I work in bursts and then stop for long stretches.": 2,
        "I move something forward most weeks, but inconsistently.": 3,
        "I move something forward most weeks in a focused way.": 4,
        "I reliably move concrete tasks forward every week.": 5,
    },
}

# ------------------ SESSION STATE ------------------ #

if "step" not in st.session_state:
    st.session_state.step = 1

if "scores" not in st.session_state:
    st.session_state.scores = {dim: 0.0 for dim in DIMENSIONS}


def next_step():
    st.session_state.step = min(3, st.session_state.step + 1)


def prev_step():
    st.session_state.step = max(1, st.session_state.step - 1)


def get_answer_score(key: str):
    """Return score for multiple-choice answer; None if placeholder or unanswered."""
    mapping = ANSWER_SCORES.get(key, {})
    ans = st.session_state.get(key)
    if not ans or ans not in mapping:
        return None
    return mapping[ans]


# ------------------ SCORING ------------------ #

def compute_dimension_scores():
    sums = {d: 0.0 for d in DIMENSIONS}
    counts = {d: 0 for d in DIMENSIONS}

    def add(dim, value):
        if value is None:
            return
        sums[dim] += float(value)
        counts[dim] += 1

    # --- Step 1: sliders (self-ratings) ---

    add("Internal Motivation", st.session_state.get("s_motivation"))
    add("Identity Alignment", st.session_state.get("s_identity"))
    add("Resource Access", st.session_state.get("s_resources"))
    add("Skill Alignment", st.session_state.get("s_skills"))
    add("Risk Tolerance", st.session_state.get("s_risk_base"))
    add("Emotional Resilience", st.session_state.get("s_resilience_base"))
    add("Execution Capacity", st.session_state.get("s_execution_self"))
    add("Market Understanding", st.session_state.get("s_market_self"))

    # Multiple choice – foundation
    add("Momentum Signals", get_answer_score("q_stage"))
    add("Execution Capacity", get_answer_score("q_stage"))

    clarity_score = get_answer_score("q_clarity")
    add("Vision & Problem Clarity", clarity_score)
    add("Market Understanding", clarity_score)

    market_val_score = get_answer_score("q_market_validation")
    add("Market Understanding", market_val_score)
    add("Vision & Problem Clarity", market_val_score)

    # --- Step 2: scenarios ---

    overwhelm = get_answer_score("q_overwhelm")
    add("Emotional Resilience", overwhelm)
    add("Execution Capacity", overwhelm)

    priorities = get_answer_score("q_priorities")
    add("Execution Capacity", priorities)
    add("Market Understanding", priorities)
    add("Momentum Signals", priorities)

    rejection = get_answer_score("q_rejection")
    add("Emotional Resilience", rejection)
    add("Risk Tolerance", rejection)

    uncertainty = get_answer_score("q_uncertainty")
    add("Risk Tolerance", uncertainty)
    add("Emotional Resilience", uncertainty)

    week_pattern = get_answer_score("q_week_pattern")
    add("Momentum Signals", week_pattern)
    add("Execution Capacity", week_pattern)

    # Final averages
    scores = {}
    for dim in DIMENSIONS:
        if counts[dim] > 0:
            scores[dim] = round(sums[dim] / counts[dim], 2)
        else:
            scores[dim] = 0.0
    return scores


def compute_total_score(dimension_scores):
    total = 0.0
    for dim, score in dimension_scores.items():
        weight = WEIGHTS.get(dim, 0)
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
        return "Conceptual phase – focus on foundations"


def critical_gates_ok(scores):
    return (
        scores["Emotional Resilience"] >= 3.0
        and scores["Execution Capacity"] >= 3.0
        and scores["Internal Motivation"] >= 3.0
    )


def readiness_archetype(scores):
    ex = scores["Execution Capacity"]
    vi = scores["Vision & Problem Clarity"]
    em = scores["Emotional Resilience"]
    ri = scores["Risk Tolerance"]

    if vi >= 4 and ex < 3:
        return "🚀 The Fired-Up Visionary"
    if ex >= 4 and em < 3:
        return "🌊 The Overstretched Operator"
    if ri < 3 and em >= 3.5:
        return "🧠 The Cautious Strategist"
    if ex >= 4 and vi >= 4 and em >= 3.5:
        return "🔧 The Scrappy Builder"
    return "🔍 The Thoughtful Explorer"


# ------------------ UI LAYOUT ------------------ #

st.title("Entrepreneurial Readiness Simulation")
st.caption("Self-assessment and scenario simulation across 10 readiness dimensions.")

with st.sidebar:
    st.header("Navigation")
    step = st.session_state.step
    st.write(f"Current step: **{step} / 3**")
    if step > 1:
        st.button("⬅️ Back", on_click=prev_step)
    if step < 3:
        st.button("➡️ Next", on_click=next_step)

# ------------------ STEP 1 ------------------ #

if st.session_state.step == 1:
    st.subheader("Step 1: Foundation – Where Are You Now?")

    st.markdown("#### Venture Stage & Clarity")

    opt_stage = [
        "(select one)",
        "I just have a vague idea and haven't written anything down.",
        "I have a clear concept but haven't done anything with it yet.",
        "I've done some basic thinking and notes, but no real testing.",
        "I've talked to a few people and/or made a rough mockup.",
        "I've run tests, pilots, or early sales conversations.",
    ]
    st.selectbox(
        "Which best describes your current stage with this venture?",
        options=opt_stage,
        key="q_stage",
    )

    opt_clarity = [
        "(select one)",
        "I'm not really sure what problem I'm solving.",
        "I know the problem, but I'm fuzzy on who it's really for.",
        "I can describe the problem and a general target group.",
        "I can describe a specific customer and their situation.",
        "I have a very specific customer, context, and clear pain point.",
    ]
    st.selectbox(
        "How clear is the problem and who it's for?",
        options=opt_clarity,
        key="q_clarity",
    )

    opt_market = [
        "(select one)",
        "I've never spoken to anyone who has this problem.",
        "I've talked informally to 1–2 people.",
        "I've had several casual conversations with people who seem to have this problem.",
        "I've run a few structured interviews or small tests.",
        "I've run structured interviews/tests and seen clear demand signals.",
    ]
    st.selectbox(
        "How much direct validation have you done with real people?",
        options=opt_market,
        key="q_market_validation",
    )

    st.markdown("#### Self-Ratings (Sliders)")

    col1, col2 = st.columns(2)

    with col1:
        st.slider(
            "Internal motivation to work on this specific problem",
            1, 5, 3, key="s_motivation",
        )
        st.slider(
            "How much this venture feels like a natural expression of who you are (identity fit)",
            1, 5, 3, key="s_identity",
        )
        st.slider(
            "Time / financial runway / support you realistically have",
            1, 5, 3, key="s_resources",
        )
        st.slider(
            "Comfort making decisions without having all the data (baseline risk tolerance)",
            1, 5, 3, key="s_risk_base",
        )

    with col2:
        st.slider(
            "How well your current skills match what this venture needs",
            1, 5, 3, key="s_skills",
        )
        st.slider(
            "Your ability to stay steady and recover when things are stressful",
            1, 5, 3, key="s_resilience_base",
        )
        st.slider(
            "Your ability to consistently move ideas into concrete action",
            1, 5, 3, key="s_execution_self",
        )
        st.slider(
            "Your understanding of your target market today",
            1, 5, 3, key="s_market_self",
        )

    st.info("Use the sidebar to go to Step 2 when you’re ready.")


# ------------------ STEP 2 ------------------ #

elif st.session_state.step == 2:
    st.subheader("Step 2: Scenarios – How Do You Tend to Act?")

    st.markdown("#### When You Feel Overwhelmed By Everything You *Could* Do")

    opt_overwhelm = [
        "(select one)",
        "I tend to freeze and avoid the work.",
        "I bounce between tasks without much progress.",
        "I push through but feel scattered and drained.",
        "I pause, regroup, and then choose 1–2 priorities.",
        "I calmly reset, choose the highest-leverage actions, and move.",
    ]
    st.radio(
        "What most closely matches your typical pattern?",
        options=opt_overwhelm,
        key="q_overwhelm",
    )

    st.markdown("#### What You Usually Prioritize")

    opt_priorities = [
        "(select one)",
        "I mostly research and gather more information.",
        "I mostly work on branding, visuals, or website.",
        "I mostly refine the idea in documents or slides.",
        "I mostly talk to potential customers or users.",
        "I mostly talk to customers and build simple things they can react to.",
    ]
    st.radio(
        "Where do you usually spend your limited time first?",
        options=opt_priorities,
        key="q_priorities",
    )

    st.markdown("#### Handling Rejection or Lukewarm Feedback")

    opt_rejection = [
        "(select one)",
        "I feel discouraged and avoid bringing it up again.",
        "I argue for why they're wrong.",
        "I shrug and move on to something else.",
        "I ask a few questions but mostly defend my idea.",
        "I get curious, ask specific questions, and look for patterns in the feedback.",
    ]
    st.radio(
        "If you get several lukewarm responses in a row, how do you tend to react?",
        options=opt_rejection,
        key="q_rejection",
    )

    st.markdown("#### Decisions Under Uncertainty")

    opt_uncertainty = [
        "(select one)",
        "I delay decisions until I feel sure.",
        "I delay big decisions but make small ones.",
        "I can decide with partial info but it stresses me.",
        "I usually decide with partial info and adjust quickly if needed.",
        "I prefer to move with partial info and learn as I go.",
    ]
    st.radio(
        "Which best describes how you approach important decisions when information is incomplete?",
        options=opt_uncertainty,
        key="q_uncertainty",
    )

    st.markdown("#### Weekly Momentum Pattern")

    opt_week = [
        "(select one)",
        "I think about it a lot but rarely take concrete action.",
        "I work in bursts and then stop for long stretches.",
        "I move something forward most weeks, but inconsistently.",
        "I move something forward most weeks in a focused way.",
        "I reliably move concrete tasks forward every week.",
    ]
    st.radio(
        "Over the past couple of months, which pattern best fits you?",
        options=opt_week,
        key="q_week_pattern",
    )

    st.info("Use the sidebar to go to Step 3 to view your readiness profile.")


# ------------------ STEP 3 ------------------ #

elif st.session_state.step == 3:
    st.subheader("Step 3: Your Readiness Profile")

    scores = compute_dimension_scores()
    st.session_state.scores = scores

    total_score = compute_total_score(scores)
    gates_ok = critical_gates_ok(scores)
    archetype = readiness_archetype(scores)

    col_top_left, col_top_right = st.columns([2, 1])

    with col_top_left:
        st.markdown("### Overall Score")
        st.metric("Entrepreneurial Readiness Score", f"{total_score} / 100")
        st.write(f"**Interpretation:** {readiness_label(total_score)}")

        if not gates_ok:
            st.warning(
                "One or more critical gates (Emotional Resilience, Execution Capacity, "
                "Internal Motivation) are below 3/5. Focus on strengthening your foundation "
                "before fully committing."
            )

    with col_top_right:
        st.markdown("### Archetype")
        st.write(f"**{archetype}**")

    st.markdown("---")
    st.markdown("### Dimension Breakdown")

    df = pd.DataFrame(
        {
            "Dimension": DIMENSIONS,
            "Score (1–5)": [scores[d] for d in DIMENSIONS],
            "Weight": [WEIGHTS[d] for d in DIMENSIONS],
        }
    )
    st.dataframe(df, use_container_width=True)

    st.markdown("### Readiness Bar Chart")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Score (1–5):Q", scale=alt.Scale(domain=[0, 5])),
            y=alt.Y("Dimension:N", sort="-x"),
            tooltip=["Dimension", "Score (1–5)", "Weight"],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("### Suggestions for Focus")

    sorted_dims = sorted(DIMENSIONS, key=lambda d: scores[d], reverse=True)
    strengths = sorted_dims[:2]
    growth = sorted_dims[-2:]

    st.write("**Top strengths:**")
    for d in strengths:
        st.write(f"- **{d}** – {scores[d]:.2f}/5")

    st.write("**Most important growth areas:**")
    for d in growth:
        st.write(f"- **{d}** – {scores[d]:.2f}/5")

    st.info(
        "You can go back to Steps 1 and 2 in the sidebar, adjust your answers, "
        "and see how your readiness profile changes."
    )
