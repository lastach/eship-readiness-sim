import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import defaultdict

st.set_page_config(page_title="LaunchX Entrepreneurial Readiness", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = 0
if "scene_choices" not in st.session_state:
    st.session_state.scene_choices = {}
if "self_assess" not in st.session_state:
    st.session_state.self_assess = {f"slider_{i}": 5 for i in range(8)}
if "reflections" not in st.session_state:
    st.session_state.reflections = {"motivation": "", "failure": "", "vision": ""}
if "email" not in st.session_state:
    st.session_state.email = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "results" not in st.session_state:
    st.session_state.results = None

ARCHETYPES = {
    "Visionary": {
        "icon": "&#9733;",
        "tagline": "Sees the future before it arrives",
        "description": "Big picture thinker who inspires others with bold ideas and spots opportunities others miss.",
        "strengths": ["Future thinking", "Inspiring others", "Spotting opportunities"],
        "gaps": ["Detail execution", "Patience with process", "Financial planning"],
        "complement": "Analyst",
        "complement_why": "You need someone who stress tests your ideas with data and keeps you grounded in reality."
    },
    "Builder": {
        "icon": "&#9654;",
        "tagline": "Makes things happen, period",
        "description": "Action oriented executor who ships fast and iterates based on real world feedback.",
        "strengths": ["Speed of execution", "Hands on problem solving", "Customer focus"],
        "gaps": ["Strategic planning", "Delegation", "Long term vision"],
        "complement": "Visionary",
        "complement_why": "You need someone who lifts your eyes from the daily grind and paints the bigger picture."
    },
    "Analyst": {
        "icon": "&#9679;",
        "tagline": "Lets data light the way",
        "description": "Systematic thinker who makes decisions based on evidence and rigorous analysis.",
        "strengths": ["Financial modeling", "Risk assessment", "Strategic thinking"],
        "gaps": ["Speed of action", "Comfort with ambiguity", "People skills"],
        "complement": "Connector",
        "complement_why": "You need someone who builds the relationships and community you tend to analyze from a distance."
    },
    "Connector": {
        "icon": "&#9830;",
        "tagline": "Builds bridges, grows networks",
        "description": "Relationship builder who creates opportunities through people and deep community bonds.",
        "strengths": ["Networking", "Team building", "Partnership development"],
        "gaps": ["Solo execution", "Financial analysis", "Saying no"],
        "complement": "Builder",
        "complement_why": "You need someone who turns your relationships into tangible products and delivered results."
    },
    "Resilient Adapter": {
        "icon": "&#10022;",
        "tagline": "Bends without breaking",
        "description": "Flexible thinker who learns from everything and pivots gracefully when needed.",
        "strengths": ["Adaptability", "Learning from failure", "Creative pivoting"],
        "gaps": ["Committing to one direction", "Building systems", "Scaling"],
        "complement": "Analyst",
        "complement_why": "You need someone who brings structure to your flexibility and helps you build repeatable processes."
    }
}

ANALYSIS_MAPS = {
    "motivation": {
        "impact": {"keywords": ["impact", "change", "world", "difference", "better"], "trait": "Impact Driven", "insight": "You are driven by the desire to make meaningful change in the world. This gives you powerful purpose and resilience."},
        "freedom": {"keywords": ["freedom", "independence", "own boss", "control", "autonomy"], "trait": "Autonomy Seeker", "insight": "Freedom and control matter deeply to you. This fuels your determination to build something of your own."},
        "money": {"keywords": ["money", "wealth", "income", "financial", "rich"], "trait": "Financial Motivator", "insight": "Financial reward is a key driver. Channel this into building a sustainable, profitable venture."},
        "create": {"keywords": ["create", "build", "make", "invent", "design"], "trait": "Creator Mindset", "insight": "You love bringing something new into existence. Your hands-on creativity will be an asset."},
        "solve": {"keywords": ["solve", "problem", "fix", "help", "improve"], "trait": "Problem Solver", "insight": "You are motivated by solving real problems. This customer focus will keep you grounded."},
        "lead": {"keywords": ["lead", "team", "people", "hire", "inspire"], "trait": "Leadership Drive", "insight": "Building and leading a team excites you. Invest in developing your leadership skills early."},
        "learn": {"keywords": ["learn", "grow", "challenge", "skill", "master"], "trait": "Growth Oriented", "insight": "You see entrepreneurship as a learning journey. This mindset will serve you well through uncertainty."},
        "passion": {"keywords": ["passion", "love", "excited", "care", "proud"], "trait": "Passion Driven", "insight": "Your passion will sustain you through the tough early days. Make sure the idea itself excites you."},
        "tech": {"keywords": ["technology", "app", "software", "ai", "digital"], "trait": "Tech Oriented", "insight": "You see technology as a key lever. Consider both tech-enabled and tech-independent paths."},
        "community": {"keywords": ["community", "local", "social", "people", "connection"], "trait": "Community Focused", "insight": "Community impact matters to you. Build your venture with genuine relationships at the core."}
    },
    "failure": {
        "growth": {"keywords": ["learn", "lesson", "growth", "reflect", "understand"], "trait": "Growth Mindset", "insight": "You extract learning from setbacks. This trait will accelerate your growth as a founder."},
        "persist": {"keywords": ["try again", "persist", "kept going", "never gave up", "again"], "trait": "Persistence", "insight": "You do not give up easily. Persistence is the trait most successful founders cite as critical."},
        "adapt": {"keywords": ["adapt", "change", "pivot", "different", "approach"], "trait": "Adaptability", "insight": "You respond to failure by changing course. This flexibility will help you survive early stage uncertainty."},
        "support": {"keywords": ["help", "friend", "mentor", "advice", "support"], "trait": "Support Seeking", "insight": "You lean on others when challenged. Strong advisory relationships will be invaluable in your journey."},
        "plan": {"keywords": ["plan", "strategy", "analyze", "figure out", "map"], "trait": "Strategic Recovery", "insight": "You respond to failure with strategic thinking. This analytical approach will serve you well."},
        "emotion": {"keywords": ["feel", "emotion", "hard", "difficult", "stress"], "trait": "Emotional Awareness", "insight": "You acknowledge the emotional weight of setbacks. This self awareness builds resilience."},
        "account": {"keywords": ["responsibility", "my fault", "own it", "accountable", "blame"], "trait": "Accountability", "insight": "You own your mistakes. This maturity will build trust with your team and investors."},
        "speed": {"keywords": ["quick", "fast", "immediately", "right away", "urgent"], "trait": "Rapid Response", "insight": "You respond quickly to problems. Balance speed with strategic thinking for best results."}
    },
    "vision": {
        "startup": {"keywords": ["company", "startup", "business", "founded", "build"], "trait": "Entrepreneurial Vision", "insight": "You see yourself as an entrepreneur and founder. This identity will sustain your commitment."},
        "team": {"keywords": ["team", "employees", "culture", "hire", "organization"], "trait": "Organization Builder", "insight": "You envision building a team and culture. Focus on hiring and retention from day one."},
        "impact": {"keywords": ["impact", "change", "better world", "community", "difference"], "trait": "Impact Driven", "insight": "Impact is central to your vision. This purpose will attract talented people to your cause."},
        "freedom": {"keywords": ["freedom", "flexible", "own schedule", "autonomy", "control"], "trait": "Lifestyle Design", "insight": "You want freedom in how you work. Define what success looks like before you start."},
        "expert": {"keywords": ["expert", "leader", "industry", "speaking", "authority"], "trait": "Thought Leadership", "insight": "You see yourself as a recognized expert. Build your personal brand alongside your company."},
        "portfolio": {"keywords": ["multiple", "portfolio", "investments", "various", "diverse"], "trait": "Portfolio Thinker", "insight": "You may want multiple ventures or income streams. Think about how your current venture fits the bigger picture."},
        "balance": {"keywords": ["family", "balance", "life", "happy", "wellbeing"], "trait": "Holistic Vision", "insight": "You want success AND a good life. Protect your wellbeing and define boundaries early."},
        "innovate": {"keywords": ["innovation", "cutting edge", "new", "disrupt", "future"], "trait": "Innovation Focus", "insight": "You want to create something truly new and disruptive. This ambition is powerful, but temper it with customer truth."}
    }
}

def analyze_text(text, analysis_map):
    text_lower = text.lower()
    matched = []
    for key, item in analysis_map.items():
        keywords = item["keywords"]
        if any(kw in text_lower for kw in keywords):
            matched.append({
                "trait": item["trait"],
                "insight": item["insight"]
            })
    return matched

def compute_archetype(scene_choices, reflection_matches, self_assess):
    scores = {arch: 0 for arch in ARCHETYPES.keys()}

    scene_archetype_map = {
        ("scene_0", 0): "Builder",
        ("scene_0", 1): "Analyst",
        ("scene_0", 2): "Connector",
        ("scene_0", 3): "Analyst",
        ("scene_1", 0): "Resilient Adapter",
        ("scene_1", 1): "Connector",
        ("scene_1", 2): "Analyst",
        ("scene_1", 3): "Builder",
        ("scene_2", 0): "Builder",
        ("scene_2", 1): "Analyst",
        ("scene_2", 2): "Resilient Adapter",
        ("scene_2", 3): "Connector",
        ("scene_3", 0): "Visionary",
        ("scene_3", 1): "Builder",
        ("scene_3", 2): "Analyst",
        ("scene_3", 3): "Connector",
        ("scene_4", 0): "Visionary",
        ("scene_4", 1): "Builder",
        ("scene_4", 2): "Analyst",
        ("scene_4", 3): "Resilient Adapter",
    }

    for scene, choice_idx in scene_choices.items():
        key = (scene, choice_idx)
        if key in scene_archetype_map:
            scores[scene_archetype_map[key]] += 15

    for trait_data in reflection_matches:
        trait = trait_data["trait"]
        trait_map = {
            "Impact Driven": "Visionary",
            "Autonomy Seeker": "Builder",
            "Financial Motivator": "Analyst",
            "Creator Mindset": "Builder",
            "Problem Solver": "Connector",
            "Leadership Drive": "Connector",
            "Growth Oriented": "Resilient Adapter",
            "Passion Driven": "Visionary",
            "Tech Oriented": "Builder",
            "Community Focused": "Connector",
            "Persistence": "Builder",
            "Adaptability": "Resilient Adapter",
            "Support Seeking": "Connector",
            "Strategic Recovery": "Analyst",
            "Emotional Awareness": "Resilient Adapter",
            "Accountability": "Analyst",
            "Rapid Response": "Builder",
            "Organization Builder": "Connector",
            "Thought Leadership": "Visionary",
            "Portfolio Thinker": "Analyst",
            "Holistic Vision": "Visionary",
            "Innovation Focus": "Visionary"
        }
        if trait in trait_map:
            scores[trait_map[trait]] += 8

    slider_archetype_map = {
        0: "Visionary",
        1: "Builder",
        2: "Analyst",
        3: "Connector",
        4: "Builder",
        5: "Resilient Adapter",
        6: "Connector",
        7: "Analyst"
    }

    for i, value in enumerate(self_assess.values()):
        arch = slider_archetype_map[i]
        scores[arch] += (value - 5) * 2

    primary = max(scores, key=scores.get)
    primary_score = scores[primary]
    secondary = None
    threshold = primary_score * 0.8

    for arch, score in scores.items():
        if arch != primary and score >= threshold:
            secondary = arch if secondary is None else (secondary if scores[secondary] > score else arch)

    return primary, secondary, scores

def compute_dimension_scores(scene_choices, self_assess):
    dim_scores = {"mindset": 0, "skills": 0, "resources": 0, "acumen": 0}
    dim_counts = {"mindset": 0, "skills": 0, "resources": 0, "acumen": 0}

    scene_dim_map = {
        ("scene_0", 0): "skills",
        ("scene_0", 1): "acumen",
        ("scene_0", 2): "resources",
        ("scene_0", 3): "acumen",
        ("scene_1", 0): "mindset",
        ("scene_1", 1): "resources",
        ("scene_1", 2): "acumen",
        ("scene_1", 3): "skills",
        ("scene_2", 0): "mindset",
        ("scene_2", 1): "skills",
        ("scene_2", 2): "mindset",
        ("scene_2", 3): "resources",
        ("scene_3", 0): "mindset",
        ("scene_3", 1): "skills",
        ("scene_3", 2): "acumen",
        ("scene_3", 3): "resources",
        ("scene_4", 0): "mindset",
        ("scene_4", 1): "acumen",
        ("scene_4", 2): "acumen",
        ("scene_4", 3): "resources",
    }

    for scene, choice_idx in scene_choices.items():
        key = (scene, choice_idx)
        if key in scene_dim_map:
            dim = scene_dim_map[key]
            dim_scores[dim] += 12
            dim_counts[dim] += 1

    slider_dim_map = [
        "mindset",
        "mindset",
        "acumen",
        "resources",
        "skills",
        "mindset",
        "skills",
        "resources"
    ]

    for i, value in enumerate(self_assess.values()):
        dim = slider_dim_map[i]
        dim_scores[dim] += value * 1.5
        dim_counts[dim] += 1

    for dim in dim_scores:
        if dim_counts[dim] > 0:
            dim_scores[dim] = min(100, dim_scores[dim] / dim_counts[dim] * 1.2)
        else:
            dim_scores[dim] = 50

    return dim_scores

def overall_readiness(dim_scores):
    weights = {"mindset": 0.30, "skills": 0.25, "resources": 0.20, "acumen": 0.25}
    overall = sum(dim_scores[dim] * weights[dim] for dim in dim_scores)
    return min(100, overall)

def readiness_label(score):
    if score >= 75:
        return ("Ready to Launch", "#22c55e", "You have strong alignment across the key dimensions of entrepreneurial readiness.")
    elif score >= 55:
        return ("Strong Foundation", "#3b82f6", "You have solid potential with some key areas to develop before launch.")
    elif score >= 35:
        return ("Building Momentum", "#f59e0b", "You are on the right path. Focus on building skills and resources.")
    else:
        return ("Early Explorer", "#8b5cf6", "You are at the beginning of your entrepreneurial journey. Every step counts.")

def generate_coaching(archetype, dim_scores, overall):
    coaching = []

    if dim_scores["mindset"] < 50:
        coaching.append("Work on your comfort with ambiguity: take on projects with unclear outcomes to build your tolerance for uncertainty.")
    elif len(coaching) == 0:
        coaching.append("Leverage your mindset strength: mentor others who struggle with ambiguity and help them build resilience.")

    if dim_scores["skills"] < 50:
        coaching.append("Build execution skills: find a mentor who ships fast and spend time learning their craft through observation and collaboration.")
    elif len(coaching) == 1:
        coaching.append("Channel your execution skills: lead a project or initiative where your speed of action creates real value.")

    if dim_scores["resources"] < 50:
        coaching.append("Expand your network intentionally: attend founder meetups, invest in your personal brand, and build genuine relationships with other entrepreneurs.")
    elif len(coaching) == 2:
        coaching.append("Strengthen partnerships: your network is a core asset. Deepen relationships and think about how to create mutual value.")

    if len(coaching) < 3:
        if dim_scores["acumen"] < 50:
            coaching.append("Develop financial literacy: learn the basics of unit economics, runway, and fundraising through courses or mentorship.")
        else:
            coaching.append("Use your financial mindset to stress test your idea: build a simple model and validate your assumptions before you commit resources.")

    return coaching[:3]

def go_to(page_num):
    st.session_state.page = page_num

def render_progress(current_page):
    pages = ["Welcome", "FreshLoop Scenario", "Self-Assessment", "Email", "Results"]
    progress_html = f'<div style="text-align: center; margin-bottom: 2rem; color: #666; font-size: 14px;">Step {current_page + 1} of 5: {pages[current_page]}</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def page_welcome():
    render_progress(0)

    hero_html = '''
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 3rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">Entrepreneurial Readiness Simulation</h1>
        <p style="margin: 0; font-size: 1.2rem; opacity: 0.95;">Discover your founder archetype, assess your startup readiness, and learn what you need to succeed.</p>
    </div>
    '''
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown("### What You'll Discover")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- **Your Founder Archetype:** which of five founder types you naturally embody")
        st.markdown("- **Readiness Score:** your startup readiness across four critical dimensions")
    with col2:
        st.markdown("- **Personalized Analysis:** deep insights based on your choices and reflections")
        st.markdown("- **Your Team Complement:** which archetype you should recruit to balance your strengths")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
    st.markdown("Takes about 12 to 15 minutes. There are no right answers, only YOUR answers.")
    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    footer_html = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 2rem;">Brought to you by LaunchX</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Begin the Simulation", key="welcome_begin", use_container_width=True):
            go_to(1)
            st.rerun()

def page_scenario():
    render_progress(1)

    st.markdown("### The FreshLoop Scenario")
    st.markdown("You and two friends have been brainstorming FreshLoop, a service that rescues unsold food from local restaurants and grocers, repackages it into affordable meal kits, and delivers them to budget conscious families. A competitor just launched nearby. The clock is ticking.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    scenes = [
        {
            "title": "Scene 1: The Spark",
            "narrative": "Your group chat is blowing up. Your friend Maya says \"We need to launch NOW before they expand here.\" Your other friend Jordan says \"We should study what they are doing first and learn from their mistakes.\" You have a free Saturday coming up. What is your move?",
            "options": [
                "Hit the streets: talk to 20 restaurant owners this Saturday and gauge real interest before anything else",
                "Draft a one page business model and rough financial projection to see if the numbers even work",
                "Create a compelling pitch deck and start recruiting more people who could help make this real",
                "Research the competitor thoroughly: sign up for their service, read their reviews, map their strategy"
            ]
        },
        {
            "title": "Scene 2: The Reality Check",
            "narrative": "You crunch some numbers. To get FreshLoop off the ground, you need about 5,000 dollars for packaging, a delivery vehicle rental, and initial marketing. Your personal savings can cover maybe half. Jordan has some money saved but is hesitant. Maya is all in but broke.",
            "options": [
                "Bootstrap it: start with just bikes and minimal packaging. Prove the concept before spending real money",
                "Apply to three local startup competitions and grants. Free money and free publicity.",
                "Build a detailed financial model showing exactly when you break even, then decide how much to invest",
                "Pre-sell meal kits to 50 families at a discount. Use their payments to fund the first batch."
            ]
        },
        {
            "title": "Scene 3: The Team Tension",
            "narrative": "Two weeks in, tensions are rising. Maya wants to move fast and start delivering immediately, even if the product is rough. Jordan wants to perfect the recipes and branding first. You are caught in the middle and both are looking to you to break the tie.",
            "options": [
                "Side with Maya: launch a rough version this weekend and improve based on real customer feedback",
                "Side with Jordan: take two more weeks to get the branding and recipes right before anyone sees it",
                "Propose a compromise: do a small private beta with 10 families, then polish based on their input",
                "Call a team meeting to realign on shared vision and roles so this conflict does not keep resurfacing"
            ]
        },
        {
            "title": "Scene 4: The Pivot Signal",
            "narrative": "Your first 10 beta customers love the food but keep asking the same question: \"Can we choose our own meals instead of getting a surprise box?\" This would require rebuilding your entire ordering system. You are three weeks from your planned public launch.",
            "options": [
                "Delay the launch and build a simple online menu. Customers are telling you exactly what they want.",
                "Launch as planned with surprise boxes, but add a feedback form. Revisit customization in month two.",
                "Run the numbers: how many more customers would customization attract vs. the cost of building it?",
                "Talk to all 10 customers personally. Understand the deeper need before deciding how to respond."
            ]
        },
        {
            "title": "Scene 5: The Opportunity Knock",
            "narrative": "A local food bank director sees your Instagram page and calls. She wants to partner: her organization would refer families to FreshLoop in exchange for a 20 percent discount. It could mean 200 new customers overnight, but at thinner margins. Your team is already stretched thin.",
            "options": [
                "Say yes immediately. This kind of growth opportunity does not come twice. Figure out logistics later.",
                "Say yes, but negotiate: offer 10 percent discount and a 60 day ramp up period so you can scale operations",
                "Build a spreadsheet model of the partnership economics before committing to anything",
                "Invite her to coffee. Explore the partnership but also ask who else she knows in the community."
            ]
        }
    ]

    for scene_idx, scene in enumerate(scenes):
        scene_key = f"scene_{scene_idx}"

        st.markdown(f"### {scene['title']}")
        st.markdown(scene["narrative"])

        scenario_card = f'''
        <div style="background: #fefce8; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
            <strong>Your Decision:</strong>
        </div>
        '''
        st.markdown(scenario_card, unsafe_allow_html=True)

        selected_idx = st.radio(
            "Choose one:",
            range(len(scene["options"])),
            format_func=lambda i: scene["options"][i],
            key=scene_key,
            label_visibility="collapsed"
        )

        st.session_state.scene_choices[scene_key] = selected_idx

        insight_text = ""
        if scene_idx == 0:
            insights = [
                "You lead with action and customer engagement. This real world focus will keep you grounded.",
                "You validate the core business model before jumping in. This financial discipline reduces risk.",
                "You see team and momentum as critical early. Building early buy in is a strength.",
                "You learn from others before committing resources. This research mindset is valuable."
            ]
            insight_text = insights[selected_idx]
        elif scene_idx == 1:
            insights = [
                "You embrace constraints and learn to do more with less. This resourcefulness is a founder superpower.",
                "You actively seek external validation and funding. Smart founders pursue all channels.",
                "You stress test your idea before investing heavily. This rigor will serve you well.",
                "You find creative ways to fund growth. Pre-selling is a powerful signal of demand."
            ]
            insight_text = insights[selected_idx]
        elif scene_idx == 2:
            insights = [
                "You trust your instincts and learn fast. Speed to market can be an advantage.",
                "You believe in getting the fundamentals right. Quality and brand matter to you.",
                "You find middle paths that preserve team harmony while still moving forward. This balance is rare.",
                "You recognize that vision and roles must align. Strong founders invest in team alignment."
            ]
            insight_text = insights[selected_idx]
        elif scene_idx == 3:
            insights = [
                "You listen to your customers and follow where the market leads. This customer obsession will scale you.",
                "You balance customer feedback with execution momentum. Shipping matters.",
                "You make data informed decisions. Running the numbers prevents costly mistakes.",
                "You deepen customer relationships to understand root needs. This empathy is a strength."
            ]
            insight_text = insights[selected_idx]
        elif scene_idx == 4:
            insights = [
                "You see transformational opportunities and act decisively. Growth mindset will propel you.",
                "You negotiate thoughtfully to win win outcomes. This is how strong partnerships are built.",
                "You let data guide scaling decisions. Financial discipline will keep your venture healthy.",
                "You leverage your network to compound growth. Relationships are your leverage."
            ]
            insight_text = insights[selected_idx]

        insight_html = f'''
        <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 1rem; border-radius: 6px; margin: 1rem 0;">
            <strong>What This Reveals:</strong> {insight_text}
        </div>
        '''
        st.markdown(insight_html, unsafe_allow_html=True)

        st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continue to Self Assessment", key="scenario_continue", use_container_width=True):
            go_to(2)
            st.rerun()

def page_selfassessment():
    render_progress(2)

    st.markdown("### Self Assessment: Rate Yourself")
    st.markdown("Answer honestly. These ratings help us understand your instinctive tendencies.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    sliders = [
        ("Comfort with Ambiguity", "I prefer clear plans", "I thrive in uncertainty"),
        ("Bias Toward Action", "I think before I act", "I act and adjust"),
        ("Financial Literacy", "Numbers intimidate me", "I think in spreadsheets"),
        ("Network Strength", "I know few entrepreneurs", "My network is deep"),
        ("Creative Problem Solving", "I follow proven methods", "I invent new approaches"),
        ("Resilience Under Pressure", "Stress slows me down", "Pressure fuels me"),
        ("Leadership Confidence", "I prefer to follow", "I naturally lead"),
        ("Market Awareness", "I focus on my idea", "I obsess over customers")
    ]

    for i, (label, low_label, high_label) in enumerate(sliders):
        st.markdown(f"**{label}**")
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        with col1:
            st.caption(low_label)
        with col5:
            st.caption(high_label)

        value = st.slider(
            label,
            min_value=1,
            max_value=10,
            value=st.session_state.self_assess.get(f"slider_{i}", 5),
            key=f"slider_{i}",
            label_visibility="collapsed"
        )
        st.session_state.self_assess[f"slider_{i}"] = value

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Reflections: Your Story")
    st.markdown("Your answers to these prompts will reveal deeper patterns in your entrepreneurial mindset.")

    st.markdown("**1. What draws you to entrepreneurship? What would you build if you knew you could not fail?**")
    reflection_1 = st.text_area(
        "Reflection 1",
        value=st.session_state.reflections.get("motivation", ""),
        key="ref_1",
        label_visibility="collapsed",
        height=100
    )
    st.session_state.reflections["motivation"] = reflection_1

    if len(reflection_1) > 20:
        matches_1 = analyze_text(reflection_1, ANALYSIS_MAPS["motivation"])
        if matches_1:
            patterns_html = '<div style="background: #f5f3ff; border-left: 4px solid #6366f1; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;"><strong>Detected Patterns:</strong> '
            patterns_html += ', '.join([m["trait"] for m in matches_1])
            patterns_html += '</div>'
            st.markdown(patterns_html, unsafe_allow_html=True)

    st.markdown("**2. Describe a time you faced a significant setback. How did you respond, and what did you learn?**")
    reflection_2 = st.text_area(
        "Reflection 2",
        value=st.session_state.reflections.get("failure", ""),
        key="ref_2",
        label_visibility="collapsed",
        height=100
    )
    st.session_state.reflections["failure"] = reflection_2

    if len(reflection_2) > 20:
        matches_2 = analyze_text(reflection_2, ANALYSIS_MAPS["failure"])
        if matches_2:
            patterns_html = '<div style="background: #f5f3ff; border-left: 4px solid #6366f1; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;"><strong>Detected Patterns:</strong> '
            patterns_html += ', '.join([m["trait"] for m in matches_2])
            patterns_html += '</div>'
            st.markdown(patterns_html, unsafe_allow_html=True)

    st.markdown("**3. Imagine your life five years from now. What does your ideal professional life look like?**")
    reflection_3 = st.text_area(
        "Reflection 3",
        value=st.session_state.reflections.get("vision", ""),
        key="ref_3",
        label_visibility="collapsed",
        height=100
    )
    st.session_state.reflections["vision"] = reflection_3

    if len(reflection_3) > 20:
        matches_3 = analyze_text(reflection_3, ANALYSIS_MAPS["vision"])
        if matches_3:
            patterns_html = '<div style="background: #f5f3ff; border-left: 4px solid #6366f1; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;"><strong>Detected Patterns:</strong> '
            patterns_html += ', '.join([m["trait"] for m in matches_3])
            patterns_html += '</div>'
            st.markdown(patterns_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continue to Email", key="assess_continue", use_container_width=True):
            go_to(3)
            st.rerun()

def page_email():
    render_progress(3)

    st.markdown("### Your Personalized Profile is Ready")
    st.markdown("Enter your email to unlock your complete results, including your founder archetype, readiness scores, and personalized coaching recommendations.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        name = st.text_input("Name (optional)", value=st.session_state.name, key="email_name")
        st.session_state.name = name
    with col2:
        email = st.text_input("Email address", value=st.session_state.email, key="email_input")
        st.session_state.email = email

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Unlock My Results", key="email_unlock", use_container_width=True):
            if "@" in email and len(email) > 5:
                all_matches = []
                all_matches.extend(analyze_text(st.session_state.reflections["motivation"], ANALYSIS_MAPS["motivation"]))
                all_matches.extend(analyze_text(st.session_state.reflections["failure"], ANALYSIS_MAPS["failure"]))
                all_matches.extend(analyze_text(st.session_state.reflections["vision"], ANALYSIS_MAPS["vision"]))

                primary_arch, secondary_arch, arch_scores = compute_archetype(
                    st.session_state.scene_choices,
                    all_matches,
                    st.session_state.self_assess
                )

                dim_scores = compute_dimension_scores(
                    st.session_state.scene_choices,
                    st.session_state.self_assess
                )

                overall = overall_readiness(dim_scores)
                label, color, description = readiness_label(overall)

                st.session_state.results = {
                    "primary_arch": primary_arch,
                    "secondary_arch": secondary_arch,
                    "arch_scores": arch_scores,
                    "dim_scores": dim_scores,
                    "overall": overall,
                    "label": label,
                    "color": color,
                    "label_desc": description,
                    "reflection_matches": all_matches,
                    "coaching": generate_coaching(primary_arch, dim_scores, overall)
                }

                go_to(4)
                st.rerun()
            else:
                st.error("Please enter a valid email address.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
    footer_html = '<div style="text-align: center; color: #888; font-size: 12px;">Brought to you by LaunchX. We respect your privacy.</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

def page_results():
    render_progress(4)

    if not st.session_state.results:
        st.error("Results not available. Please restart.")
        return

    results = st.session_state.results
    primary = results["primary_arch"]
    secondary = results["secondary_arch"]
    arch_data = ARCHETYPES[primary]
    dim_scores = results["dim_scores"]
    overall = results["overall"]
    label = results["label"]
    color = results["color"]

    score_ring_html = f'''
    <div style="text-align: center; margin: 2rem 0;">
        <div style="width: 200px; height: 200px; margin: 0 auto; border-radius: 50%; background: linear-gradient(135deg, {color}33 0%, {color}11 100%); border: 8px solid {color}; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <div style="font-size: 3rem; font-weight: bold; color: {color};">{int(overall)}</div>
            <div style="font-size: 1.2rem; color: #333;">{label}</div>
        </div>
    </div>
    '''
    st.markdown(score_ring_html, unsafe_allow_html=True)

    st.markdown(results["label_desc"])

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Founder Archetype")

    archetype_card = f'''
    <div style="background: linear-gradient(135deg, #f5f3ff 0%, #eff6ff 100%); border-left: 4px solid #6366f1; padding: 1.5rem; border-radius: 8px; text-align: center;">
        <div style="font-size: 3rem;">{arch_data["icon"]}</div>
        <h2 style="margin: 0.5rem 0; color: #333;">{primary}</h2>
        <p style="margin: 0.5rem 0; color: #666; font-size: 1.1rem; font-style: italic;">{arch_data["tagline"]}</p>
        <p style="margin: 0.5rem 0; color: #555;">{arch_data["description"]}</p>
    </div>
    '''
    st.markdown(archetype_card, unsafe_allow_html=True)

    if secondary:
        st.markdown(f"**Secondary Archetype:** You also show strong {secondary} tendencies. This combination gives you unique strengths.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Readiness Dimensions")

    dim_order = ["mindset", "skills", "resources", "acumen"]
    dim_labels = ["Mindset (30%)", "Skills (25%)", "Resources (20%)", "Acumen (25%)"]
    dim_colors = ["#8b5cf6", "#3b82f6", "#22c55e", "#f59e0b"]

    for dim, label, color in zip(dim_order, dim_labels, dim_colors):
        score = dim_scores[dim]
        percent = int(score)

        bar_html = f'''
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: bold; color: #333;">{label}</span>
                <span style="color: {color}; font-weight: bold;">{percent}/100</span>
            </div>
            <div style="width: 100%; height: 12px; background: #f1f5f9; border-radius: 6px; overflow: hidden;">
                <div style="width: {percent}%; height: 100%; background: linear-gradient(90deg, {color}aa 0%, {color} 100%);"></div>
            </div>
        </div>
        '''
        st.markdown(bar_html, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Strengths and Growth Areas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Your Core Strengths**")
        for strength in arch_data["strengths"]:
            st.markdown(f"- {strength}")

    with col2:
        st.markdown("**Growth Opportunities**")
        for gap in arch_data["gaps"]:
            st.markdown(f"- {gap}")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Who You Need On Your Team")

    complement_arch = arch_data["complement"]
    complement_data = ARCHETYPES[complement_arch]

    complement_card = f'''
    <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 1.5rem; border-radius: 8px;">
        <h4 style="margin-top: 0;">The {complement_arch}</h4>
        <p style="margin: 0.5rem 0; color: #555;">{arch_data["complement_why"]}</p>
        <p style="margin: 0.5rem 0; color: #666; font-style: italic; font-size: 0.95rem;">{complement_data["description"]}</p>
    </div>
    '''
    st.markdown(complement_card, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Self Assessment Profile")

    slider_labels = [
        "Ambiguity",
        "Action Bias",
        "Financial",
        "Network",
        "Creative",
        "Resilience",
        "Leadership",
        "Market"
    ]

    slider_data = []
    f/r i, label in enumerate(slider_labels):
        slider_data.append({
            "Dimension": label,
            "Score": st.session_state.self_assess[f"slider_{i}"]
        })

    df_sliders = pd.DataFrame(slider_data)

    chart = alt.Chart(df_sliders).mark_barh(color="#6366f1").encode(
        y=alt.Y("Dimension:N", sort="-x"),
        x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 10])),
        tooltip=["Dimension", "Score"]
    ).properties(height=250, width=400)

    st.altair_chart(chart, use_container_width=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### What Your Reflections Reveal")

    if results["reflection_matches"]:
        seen_traits = set()
        for match in results["reflection_matches"]:
            trait = match["trait"]
            if trait not in seen_traits:
                insight = match["insight"]
                analysis_html = f'''
                <div style="background: #f5f3ff; border-left: 4px solid #6366f1; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;">
                    <strong>{trait}:</strong> {insight}
                </div>
                '''
                st.markdown(analysis_html, unsafe_allow_html=True)
                seen_traits.add(trait)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Coaching Recommendations")

    for i, recommendation in enumerate(results["coaching"], 1):
        coaching_html = f'''
        <div style="background: #fff7ed; border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 6px; margin: 0.5rem 0;">
            <strong>Action {i}:</strong> {recommendation}
        </div>
        '''
        st.markdown(coaching_html, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Archetype Breakdown")

    arch_scores_list = []
    for arch, score in results["arch_scores"].items():
        arch_scores_list.append({"Archetype": arch, "Affinity": max(0, score)})

    df_archs = pd.DataFrame(arch_scores_list).sort_values("Affinity", ascending=True)

    colors = ["#6366f1", "#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6"]
    chart = alt.Chart(df_archs).mark_barh().encode(
        y=alt.Y("Archetype:N", sort="-x"),
        x="Affinity:Q",
        color=alt.Color("Archetype:N", scale=alt.Scale(domain=list(ARCHETYPES.keys()), range=colors), legend=None)
    ).properties(height=250)

    st.altair_chart(chart, use_container_width=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Ready to Take the Next Step?")

    cta_card = '''
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
        <h3 style="margin-top: 0;">LaunchX Helps Aspiring Entrepreneurs Turn Potential Into Action</h3>
        <p style="margin: 1rem 0; font-size: 1.05rem;">Your simulation reveals your strengths and growth areas. LaunchX programs are designed to help you build the specific skills you need to launch successfully.</p>
        <p style="margin: 1rem 0; font-size: 0.95rem; opacity: 0.95;">[CTA: Laurie will customize this section with specific LaunchX program information]</p>
    </div>
    '''
    st.markdown(cta_card, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Disclaimer")
    st.caption("This simulation is designed for educational exploration. Your entrepreneurial potential is shaped by many factors beyond what any simulation can measure. Use these insights as a starting point for growth, not as a ceiling on possibility.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    footer_html = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 2rem;">Brought to you by LaunchX</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

if st.session_state.page == 0:
    page_welcome()
elif st.session_state.page == 1:
    page_scenario()
elif st.session_state.page == 2:
    page_selfassessment()
elif st.session_state.page == 3:
    page_email()
elif st.session_state.page == 4:
    page_results()
