import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Entrepreneurial Readiness Simulation",
    layout="wide"
)

# ------------- CONSTANTS -------------

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


# ------------- SESSION STATE SETUP -------------

if "step" not in st.session_state:
    st.session_state.step = 1

if "scores" not in st.session_state:
    st.session_state.scores = {dim: 0.0 for dim in DIMENSIONS}


# ------------- HELPER FUNCTIONS -------------

def next_step():
    st.session_state.step += 1


def prev_step():
    st.session_state.step -= 1


def text_score_length_based(text: str, min_words: int, max_words: int) -> float:
    """Simple heuristic: 0–5 score based on being within a target word range."""
    words = len(text.strip().split())
    if words == 0:
        return 0.0
    if words < min_words:
        return 2.0
    if min_words <= words <= max_words:
        return 5.0
    if words <= max_words * 2:
        return 4.0
    return 3.0


def calc_intake_scores():
    """Score from venture intake (Step 1)."""
    s = st.session_state

    # Vision & Problem Clarity: based on problem, audience, solution descriptions
    prob_score = text_score_length_based(s.problem_description, 20, 80)
    audience_score = text_score_length_based(s.audience_description, 15, 50)
    solution_score = text_score_length_based(s.solution_description, 20, 80)
    clarity = (prob_score + audience_score + solution_score) / 3.0

    # Motivation: based on why they care
    motivation = text_score_length_based(s.why_care, 20, 80)

    # Identity alignment: how strongly they feel this fits them (slider)
    identity = s.identity_fit

    # Market understanding: self-rated + some credit for defining audience
    market_understanding = (s.market_understanding_self + audience_score / 5.0) / 2.0

    # Resource access: directly from slider
    resource_access = s.resource_access

    # Skill alignment: self-rated
    skill_alignment = s.skill_alignment

    return {
        "Vision & Problem Clarity": clarity,
        "Internal Motivation": motivation,
        "Identity Alignment": identity,
        "Market Understanding": market_understanding,
        "Resource Access": resource_access,
        "Skill Alignment": skill_alignment,
    }


def calc_challenge_scores():
    """Score from behavior in challenges (Step 2)."""
    s = st.session_state

    # --- Clarity Compression Challenge ---
    pain_score = text_score_length_based(s.cc_pain, 10, 40)
    why_now_score = text_score_length_based(s.cc_why_now, 10, 40)
    proof_score = text_score_length_based(s.cc_proof, 10, 40)
    clarity_from_cc = (pain_score + why_now_score + proof_score) / 3.0

    # --- Prioritization Tradeoff ---
    total_tokens = (
        s.tokens_interviews
        + s.tokens_prototype
        + s.tokens_pitch
        + s.tokens_finance
        + s.tokens_brand
    )
    # Just in case user doesn't perfectly hit 10:
    if total_tokens == 0:
        total_tokens = 1

    share_interviews = s.tokens_interviews / total_tokens
    share_prototype = s.tokens_prototype / total_tokens
    share_pitch = s.tokens_pitch / total_tokens
    share_finance = s.tokens_finance / total_tokens
    share_brand = s.tokens_brand / total_tokens

    # Heuristic: good execution = interviews + prototype (learning + doing)
    execution_from_tokens = 5.0 * (0.6 * (share_interviews + share_prototype) + 0.4 * share_prototype)
    execution_from_tokens = max(0.0, min(5.0, execution_from_tokens))

    # Market understanding benefits from interviews & finance modeling
    market_from_tokens = 5.0 * (0.7 * share_interviews + 0.3 * share_finance)
    market_from_tokens = max(0.0, min(5.0, market_from_tokens))

    # Momentum gets boost from prototype + any distribution (pitch/brand)
    momentum_from_tokens = 5.0 * (0.5 * share_prototype + 0.5 * (share_pitch + share_brand) / 2.0)
    momentum_from_tokens = max(0.0, min(5.0, momentum_from_tokens))

    # --- Rejection Simulation ---
    rej_map = {
        "Explore what's behind the feedback": 5.0,
        "Reframe and ask for specifics": 4.5,
        "Defend your idea strongly": 3.0,
        "Shut down and move on": 1.0,
    }
    rejection_score = rej_map.get(s.rejection_response, 3.0)

    # --- Uncertainty Dilemma ---
    if s.uncertainty_choice == "Launch now with ~60% confidence (learn from market)":
        risk_tolerance = 4.5
        emotional_resilience = 4.0
    elif s.uncertainty_choice == "Wait 4 weeks for more data before launching":
        risk_tolerance = 3.0
        emotional_resilience = 3.5
    elif s.uncertainty_choice == "Pause indefinitely until things feel 'safe'":
        risk_tolerance = 1.5
        emotional_resilience = 2.0
    else:
        risk_tolerance = 3.0
        emotional_resilience = 3.0

    # Emotional resilience also influenced by rejection response
    emotional_resilience = (emotional_resilience + rejection_score) / 2.0

    # --- Momentum Challenge ---
    mc_scores = []
    for t in [s.momentum_step1, s.momentum_step2, s.momentum_step3]:
        mc_scores.append(text_score_length_based(t, 6, 25))
    momentum_from_mc = sum(mc_scores) / 3.0 if mc_scores else 0.0

    # Combine momentum from tokens + micro-steps
    momentum_total = (momentum_from_tokens + momentum_from_mc) / 2.0

    # Execution gets help from micro-steps
    execution_total = (execution_from_tokens + momentum_from_mc) / 2.0

    return {
        "Vision & Problem Clarity": clarity_from_cc,
        "Market Understanding": market_from_tokens,
        "Momentum Signals": momentum_total,
        "Execution Capacity": execution_total,
        "Emotional Resilience": emotional_resilience,
        "Risk Tolerance": risk_tolerance,
    }


def combine_scores(intake_scores, challenge_scores):
    combined = {}
    for dim in DIMENSIONS:
        vals = []
        if dim in intake_scores:
            vals.append(intake_scores[dim])
        if dim in challenge_scores:
            vals.append(challenge_scores[dim])
        if vals:
            combined[dim] = sum(vals) / len(vals)
        else:
            combined[dim] = 0.0
    return combined


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


# ------------- UI -------------

st.title("Entrepreneurial Readiness Simulation")
st.caption("Bring your own venture, make decisions under pressure, and see your readiness profile.")

with st.sidebar:
    st.header("Navigation")
    step = st.session_state.step
    st.write(f"Current step: **{step}** / 3")
    if step > 1:
        st.button("⬅️ Back", on_click=prev_step)
    if step < 3:
        st.button("➡️ Next", on_click=next_step)


# ------------- STEP 1: VENTURE INTAKE -------------

if st.session_state.step == 1:
    st.subheader("Step 1: Describe Your Venture")

    st.markdown(
        "This simulation works on *your* real or intended business. "
        "Give enough detail that the later challenges feel real."
    )

    st.text_input(
        "Venture Name (working title is fine):",
        key="venture_name",
        placeholder="e.g., 'Clarity Coaching for Founders'",
    )

    st.text_area(
        "1. What problem are you trying to solve?",
        key="problem_description",
        height=130,
        placeholder="Describe the pain in concrete terms. What is broken, frustrating, or inefficient?",
    )

    st.text_area(
        "2. Who specifically experiences this problem?",
        key="audience_description",
        height=130,
        placeholder="Be as specific as possible (segment, role, context, etc.).",
    )

    st.text_area(
        "3. What do you think your solution looks like?",
        key="solution_description",
        height=130,
        placeholder="What are people actually doing, using, or buying from you?",
    )

    st.text_area(
        "4. Why do *you* care deeply about this problem?",
        key="why_care",
        height=130,
        placeholder="Connect to your personal story, values, or long-term interests.",
    )

    st.selectbox(
        "Current stage of your venture:",
        options=["Idea only", "Some validation", "MVP built", "Early traction", "Scaling"],
        key="venture_stage",
    )

    st.markdown("### Quick Self-Checks")

    col1, col2 = st.columns(2)

    with col1:
        st.slider(
            "How strongly does this venture feel like a natural fit with who you are?",
            min_value=1,
            max_value=5,
            value=4,
            key="identity_fit",
        )

        st.slider(
            "How would you rate your current understanding of your target market?",
            min_value=1,
            max_value=5,
            value=3,
            key="market_understanding_self",
        )

    with col2:
        st.slider(
            "How much time / financial runway / support do you realistically have?",
            min_value=1,
            max_value=5,
            value=3,
            key="resource_access",
        )

        st.slider(
            "How well do your skills match what this venture needs (today, not ideally)?",
            min_value=1,
            max_value=5,
            value=3,
            key="skill_alignment",
        )

    st.info(
        "When you're ready, move to Step 2 using the sidebar. "
        "You can come back and edit this anytime."
    )


# ------------- STEP 2: CHALLENGES -------------

elif st.session_state.step == 2:
    st.subheader("Step 2: Behavioral Challenges")

    st.markdown("These scenarios stress-test how you **think and act** as a founder.")

    st.markdown("### A. Clarity Compression Challenge")
    st.write("Imagine you have 90 seconds to explain your venture to a busy investor.")

    st.text_area("The Pain (what hurts for your customer?):", key="cc_pain", height=90)
    st.text_area("Why Now (why is this timely / urgent?):", key="cc_why_now", height=90)
    st.text_area("The Proof (any evidence, traction, or credibility?):", key="cc_proof", height=90)

    st.markdown("---")
    st.markdown("### B. Prioritization Tradeoff")

    st.write(
        "You have **10 Action Tokens** to spend this week. Distribute them across activities. "
        "Then reality hits and you lose 4 tokens (we'll see how you allocated anyway)."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.number_input("Customer interviews", min_value=0, max_value=10, value=3, key="tokens_interviews")
        st.number_input("Prototype / MVP build", min_value=0, max_value=10, value=3, key="tokens_prototype")

    with col2:
        st.number_input("Pitch / narrative refinement", min_value=0, max_value=10, value=2, key="tokens_pitch")

    with col3:
        st.number_input("Financial modeling / runway", min_value=0, max_value=10, value=1, key="tokens_finance")
        st.number_input("Brand / website / visuals", min_value=0, max_value=10, value=1, key="tokens_brand")

    tokens_total = (
        st.session_state.tokens_interviews
        + st.session_state.tokens_prototype
        + st.session_state.tokens_pitch
        + st.session_state.tokens_finance
        + st.session_state.tokens_brand
    )
    st.caption(f"Current total tokens allocated: **{tokens_total}** (target: 10)")

    st.markdown("---")
    st.markdown("### C. Rejection Simulation")

    st.write(
        "You pitch your idea to 5 potential customers and 4 say some version of:\n"
        "_'This is interesting, but I don't think it's a priority for me right now.'_"
    )

    st.radio(
        "How do you most likely respond?",
        options=[
            "Explore what's behind the feedback",
            "Reframe and ask for specifics",
            "Defend your idea strongly",
            "Shut down and move on",
        ],
        key="rejection_response",
    )

    st.markdown("---")
    st.markdown("### D. Uncertainty Dilemma")

    st.write(
        "You are at a decision point:\n"
        "- You have **60% confidence** in your current direction.\n"
        "- You could launch now and learn from the market.\n"
        "- Or you could wait 4 weeks to gather more data.\n"
        "- Or pause until you feel 'truly ready'."
    )

    st.radio(
        "What do you actually choose?",
        options=[
            "Launch now with ~60% confidence (learn from market)",
            "Wait 4 weeks for more data before launching",
            "Pause indefinitely until things feel 'safe'",
        ],
        key="uncertainty_choice",
    )

    st.markdown("---")
    st.markdown("### E. Momentum Challenge")

    st.write("List the **first three concrete steps** you would take in the next 7 days:")

    st.text_input("Step 1:", key="momentum_step1", placeholder="e.g., Schedule 5 customer interviews for next week")
    st.text_input("Step 2:", key="momentum_step2", placeholder="e.g., Build click-through prototype of landing page")
    st.text_input("Step 3:", key="momentum_step3", placeholder="e.g., Set up simple waitlist form and share with X group")

    st.info("When you're satisfied with your answers, move to Step 3 in the sidebar to see your readiness profile.")


# ------------- STEP 3: RESULTS -------------

elif st.session_state.step == 3:
    st.subheader("Step 3: Your Readiness Profile")

    intake_scores = calc_intake_scores()
    challenge_scores = calc_challenge_scores()
    combined = combine_scores(intake_scores, challenge_scores)
    total_score = compute_total_score(combined)
    gates_ok = critical_gates_ok(combined)
    archetype = readiness_archetype(combined)

    st.session_state.scores = combined

    col_top_left, col_top_right = st.columns([2, 1])

    with col_top_left:
        st.markdown("### Overall Score")
        st.metric("Entrepreneurial Readiness Score", f"{total_score} / 100")
        st.write(f"**Interpretation:** {readiness_label(total_score)}")

        if not gates_ok:
            st.warning(
                "⚠️ One or more critical gates (Emotional Resilience, Execution Capacity, Internal Motivation) "
                "are below 3/5. This suggests focusing on strengthening your personal foundation "
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
            "Score (1–5)": [round(combined[d], 2) for d in DIMENSIONS],
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

    st.markdown("---")
    st.markdown("### Suggestions for Focus")

    sorted_dims = sorted(DIMENSIONS, key=lambda d: combined[d], reverse=True)
    strengths = sorted_dims[:2]
    growth = sorted_dims[-2:]

    st.write("**Top strengths:**")
    for d in strengths:
        st.write(f"- **{d}** – {combined[d]:.2f}/5")

    st.write("**Most important growth areas:**")
    for d in growth:
        st.write(f"- **{d}** – {combined[d]:.2f}/5")

    st.info(
        "You can go back to Steps 1 and 2 in the sidebar, adjust your answers, "
        "and see how your readiness profile changes. This is a simulation, not a judgment."
    )
