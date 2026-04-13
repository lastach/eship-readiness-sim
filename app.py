import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import defaultdict

st.set_page_config(page_title="Entrepreneurial Readiness Simulation", layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit's default menu, footer, and header
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = 0
if "exercise_step" not in st.session_state:
    st.session_state.exercise_step = 0
if "time_budget" not in st.session_state:
    st.session_state.time_budget = {"build": 8, "sell": 8, "operate": 6, "market": 6, "team": 6, "strategy": 6}
if "money_budget" not in st.session_state:
    st.session_state.money_budget = {"product": 20, "sales": 15, "ops": 15, "marketing": 15, "hires": 20, "reserve": 15}
if "energy_audit" not in st.session_state:
    st.session_state.energy_audit = {}
if "self_assess" not in st.session_state:
    st.session_state.self_assess = {f"slider_{i}": 5 for i in range(6)}
if "reflections" not in st.session_state:
    st.session_state.reflections = {"motivation": "", "failure": "", "vision": ""}
if "name" not in st.session_state:
    st.session_state.name = ""
if "results" not in st.session_state:
    st.session_state.results = None

# =============================================================================
# FOUNDER TYPES
# Based on founding team functional roles: what each person naturally does
# =============================================================================

ARCHETYPES = {
    "Builder": {
        "icon": "🔨",
        "tagline": "Creates the product, solves the problem",
        "description": "You are driven to make things. Whether it is code, hardware, a service model, or a physical product, you find energy in turning ideas into something real. You iterate fast, learn by doing, and measure progress by what you have shipped.",
        "strengths": ["Product development", "Technical problem solving", "Rapid prototyping and iteration"],
        "gaps": ["Delegating instead of doing", "Customer acquisition strategy", "Organizational systems"],
        "complement": "Business Development",
        "complement_why": "You build great products, but products do not sell themselves. You need someone who opens doors, closes deals, and brings revenue in the door while you focus on making the product better.",
        "entrecomp_weight": {"ideas": 0.45, "resources": 0.20, "action": 0.35}
    },
    "Business Development": {
        "icon": "🤝",
        "tagline": "Opens doors and drives revenue",
        "description": "You are energized by relationships, deals, and growth. You see partnerships where others see strangers, and you have a natural talent for understanding what people need and positioning your offering to match. Revenue follows where you go.",
        "strengths": ["Sales and deal closing", "Partnership building", "Customer discovery and market sensing"],
        "gaps": ["Product details and technical depth", "Process documentation", "Saying no to opportunities"],
        "complement": "Operations",
        "complement_why": "You bring in deals and relationships, but someone needs to make sure the team can actually deliver on your promises. You need an operator who builds the systems to scale what you sell.",
        "entrecomp_weight": {"ideas": 0.30, "resources": 0.45, "action": 0.25}
    },
    "Operations": {
        "icon": "⚙️",
        "tagline": "Builds the engine that makes it run",
        "description": "You bring order to chaos. While others chase the next big idea or the next big deal, you are the one making sure the team is aligned, the budget is tracked, and the plan is actually getting executed. You see inefficiency as a problem worth solving.",
        "strengths": ["Systems design and process optimization", "Financial planning and analysis", "Team coordination and project management"],
        "gaps": ["Comfort with ambiguity and pivots", "External relationship building", "Generating new ideas under pressure"],
        "complement": "Marketing",
        "complement_why": "You keep everything running smoothly, but startups also need someone who shapes the story and builds the brand. You need a marketer who creates the narrative that attracts customers and talent.",
        "entrecomp_weight": {"ideas": 0.15, "resources": 0.35, "action": 0.50}
    },
    "Marketing": {
        "icon": "📣",
        "tagline": "Shapes the story and builds the brand",
        "description": "You understand people, culture, and communication. You know how to take something complex and make it compelling. You think about positioning, audience, and narrative, and you have a sense for what will resonate before anyone else does.",
        "strengths": ["Brand positioning and storytelling", "Audience insight and market research", "Content creation and communication strategy"],
        "gaps": ["Financial modeling and unit economics", "Technical product decisions", "Operational follow through"],
        "complement": "Builder",
        "complement_why": "You craft the story and build demand, but you need a builder who creates the product that lives up to the brand promise. Without a great product behind the message, marketing falls flat.",
        "entrecomp_weight": {"ideas": 0.40, "resources": 0.35, "action": 0.25}
    }
}

# =============================================================================
# ENTRECOMP READINESS DIMENSIONS
# European Commission validated framework: 3 areas, mapped to simulation scoring
# Ideas & Opportunities: spotting opportunities, creativity, vision, valuing ideas, ethical thinking
# Resources: self-awareness, motivation, mobilizing resources, financial literacy, mobilizing others
# Into Action: taking initiative, planning, coping with uncertainty, working with others, learning through experience
# =============================================================================

READINESS_DIMS = {
    "ideas": {
        "label": "Ideas & Opportunities",
        "description": "Your ability to spot opportunities, generate creative solutions, and envision what could be.",
        "color": "#8b5cf6",
        "weight": 0.30
    },
    "resources": {
        "label": "Resources",
        "description": "Your ability to mobilize people, money, knowledge, and support for your venture.",
        "color": "#3b82f6",
        "weight": 0.35
    },
    "action": {
        "label": "Into Action",
        "description": "Your ability to take initiative, plan and manage, and cope with uncertainty along the way.",
        "color": "#22c55e",
        "weight": 0.35
    }
}

# =============================================================================
# TEXT ANALYSIS MAPS for reflections
# =============================================================================

ANALYSIS_MAPS = {
    "motivation": {
        "impact": {"keywords": ["impact", "change", "world", "difference", "better"], "trait": "Impact Driven", "insight": "You are driven by the desire to make meaningful change in the world. This gives you powerful purpose and resilience."},
        "freedom": {"keywords": ["freedom", "independence", "own boss", "control", "autonomy"], "trait": "Autonomy Seeker", "insight": "Freedom and control matter deeply to you. This fuels your determination to build something of your own."},
        "money": {"keywords": ["money", "wealth", "income", "financial", "rich"], "trait": "Financial Motivator", "insight": "Financial reward is a key driver. Channel this into building a sustainable, profitable venture."},
        "create": {"keywords": ["create", "build", "make", "invent", "design"], "trait": "Creator Mindset", "insight": "You love bringing something new into existence. Your hands on creativity will be an asset."},
        "solve": {"keywords": ["solve", "problem", "fix", "help", "improve"], "trait": "Problem Solver", "insight": "You are motivated by solving real problems. This customer focus will keep you grounded."},
        "lead": {"keywords": ["lead", "team", "people", "hire", "inspire"], "trait": "Leadership Drive", "insight": "Building and leading a team excites you. Invest in developing your leadership skills early."},
        "learn": {"keywords": ["learn", "grow", "challenge", "skill", "master"], "trait": "Growth Oriented", "insight": "You see entrepreneurship as a learning journey. This mindset will serve you well through uncertainty."},
        "passion": {"keywords": ["passion", "love", "excited", "care", "proud"], "trait": "Passion Driven", "insight": "Your passion will sustain you through the tough early days. Make sure the idea itself excites you."},
        "tech": {"keywords": ["technology", "app", "software", "ai", "digital"], "trait": "Tech Oriented", "insight": "You see technology as a key lever. Consider both tech enabled and tech independent paths."},
        "community": {"keywords": ["community", "local", "social", "people", "connection"], "trait": "Community Focused", "insight": "Community impact matters to you. Build your venture with genuine relationships at the core."},
        "market": {"keywords": ["market", "brand", "audience", "story", "content"], "trait": "Market Aware", "insight": "You think about audiences and messaging naturally. This market sense will shape your go to market strategy."},
        "sell": {"keywords": ["sell", "customer", "deal", "revenue", "partner"], "trait": "Revenue Minded", "insight": "You see business through the lens of customers and deals. This commercial instinct is a founder strength."}
    },
    "failure": {
        "growth": {"keywords": ["learn", "lesson", "growth", "reflect", "understand"], "trait": "Growth Mindset", "insight": "You extract learning from setbacks. This trait will accelerate your growth as a founder."},
        "persist": {"keywords": ["try again", "persist", "kept going", "never gave up", "again"], "trait": "Persistence", "insight": "You do not give up easily. Persistence is the trait most successful founders cite as critical."},
        "adapt": {"keywords": ["adapt", "change", "pivot", "different", "approach"], "trait": "Adaptability", "insight": "You respond to failure by changing course. This flexibility will help you survive early stage uncertainty."},
        "support": {"keywords": ["help", "friend", "mentor", "advice", "support"], "trait": "Support Seeking", "insight": "You lean on others when challenged. Strong advisory relationships will be invaluable in your journey."},
        "plan": {"keywords": ["plan", "strategy", "analyze", "figure out", "map"], "trait": "Strategic Recovery", "insight": "You respond to failure with strategic thinking. This analytical approach will serve you well."},
        "emotion": {"keywords": ["feel", "emotion", "hard", "difficult", "stress"], "trait": "Emotional Awareness", "insight": "You acknowledge the emotional weight of setbacks. This self awareness builds resilience."},
        "account": {"keywords": ["responsibility", "my fault", "own it", "accountable", "blame"], "trait": "Accountability", "insight": "You own your mistakes. This maturity will build trust with your team and investors."},
        "speed": {"keywords": ["quick", "fast", "immediately", "right away", "urgent"], "trait": "Rapid Response", "insight": "You respond quickly to problems. Balance speed with strategic thinking for best results."},
        "system": {"keywords": ["process", "system", "organize", "structure", "method"], "trait": "Systems Thinker", "insight": "You respond to setbacks by building better systems. This operational instinct prevents repeat failures."}
    },
    "vision": {
        "startup": {"keywords": ["company", "startup", "business", "founded", "build"], "trait": "Entrepreneurial Vision", "insight": "You see yourself as an entrepreneur and founder. This identity will sustain your commitment."},
        "team": {"keywords": ["team", "employees", "culture", "hire", "organization"], "trait": "Organization Builder", "insight": "You envision building a team and culture. Focus on hiring and retention from day one."},
        "impact": {"keywords": ["impact", "change", "better world", "community", "difference"], "trait": "Impact Driven", "insight": "Impact is central to your vision. This purpose will attract talented people to your cause."},
        "freedom": {"keywords": ["freedom", "flexible", "own schedule", "autonomy", "control"], "trait": "Lifestyle Design", "insight": "You want freedom in how you work. Define what success looks like before you start."},
        "expert": {"keywords": ["expert", "leader", "industry", "speaking", "authority"], "trait": "Thought Leadership", "insight": "You see yourself as a recognized expert. Build your personal brand alongside your company."},
        "portfolio": {"keywords": ["multiple", "portfolio", "investments", "various", "diverse"], "trait": "Portfolio Thinker", "insight": "You may want multiple ventures or income streams. Think about how your current venture fits the bigger picture."},
        "balance": {"keywords": ["family", "balance", "life", "happy", "wellbeing"], "trait": "Holistic Vision", "insight": "You want success AND a good life. Protect your wellbeing and define boundaries early."},
        "innovate": {"keywords": ["innovation", "cutting edge", "new", "disrupt", "future"], "trait": "Innovation Focus", "insight": "You want to create something truly new and disruptive. This ambition is powerful, but temper it with customer truth."},
        "brand": {"keywords": ["brand", "known", "reputation", "recognition", "platform"], "trait": "Brand Vision", "insight": "You see the power of brand and recognition. Building a strong brand early creates lasting competitive advantage."},
        "scale": {"keywords": ["scale", "grow", "expand", "big", "global"], "trait": "Scale Ambition", "insight": "You think big about growth. Pair this ambition with strong operational foundations."}
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

# =============================================================================
# SCORING: Founder Type
# =============================================================================

def compute_archetype(time_budget, money_budget, energy_audit, reflection_matches, self_assess):
    scores = {arch: 0 for arch in ARCHETYPES.keys()}

    # ---- Time budget signals (hours out of 40) ----
    # Each hour allocated counts toward the linked archetype
    time_arch_map = {
        "build": "Builder",
        "sell": "Business Development",
        "operate": "Operations",
        "market": "Marketing",
        "team": "Operations",
        "strategy": "Builder",  # strategic thinking leans slightly Builder/visionary
    }
    for category, hours in time_budget.items():
        arch = time_arch_map.get(category)
        if arch:
            # Each hour = 1.5 points toward archetype
            scores[arch] += hours * 1.5

    # ---- Money budget signals ($K out of $100K) ----
    money_arch_map = {
        "product": "Builder",
        "sales": "Business Development",
        "ops": "Operations",
        "marketing": "Marketing",
        "hires": "Operations",
        "reserve": "Operations",  # reserving cash reflects operational discipline
    }
    for category, dollars in money_budget.items():
        arch = money_arch_map.get(category)
        if arch:
            # Each $1K = 0.6 points
            scores[arch] += dollars * 0.6

    # ---- Energy audit signals ----
    # Each task tagged with a primary archetype; rating value: Drain = -5, Neutral = 0, Energize = +10
    energy_task_archetype = {
        "code": "Builder",
        "cold_email": "Business Development",
        "financial_model": "Operations",
        "linkedin_post": "Marketing",
        "standup": "Operations",
        "investor_pitch": "Business Development",
        "competitive_research": "Marketing",
        "onboarding_process": "Operations",
    }
    rating_values = {"drain": -5, "neutral": 0, "energize": 10}
    for task, arch in energy_task_archetype.items():
        rating = energy_audit.get(task, "neutral")
        scores[arch] += rating_values.get(rating, 0)

    # Reflection trait mapping to founder types
    trait_map = {
        "Impact Driven": "Marketing",
        "Autonomy Seeker": "Builder",
        "Financial Motivator": "Operations",
        "Creator Mindset": "Builder",
        "Problem Solver": "Builder",
        "Leadership Drive": "Operations",
        "Growth Oriented": "Builder",
        "Passion Driven": "Marketing",
        "Tech Oriented": "Builder",
        "Community Focused": "Business Development",
        "Market Aware": "Marketing",
        "Revenue Minded": "Business Development",
        "Persistence": "Builder",
        "Adaptability": "Marketing",
        "Support Seeking": "Business Development",
        "Strategic Recovery": "Operations",
        "Emotional Awareness": "Marketing",
        "Accountability": "Operations",
        "Rapid Response": "Builder",
        "Systems Thinker": "Operations",
        "Growth Mindset": "Builder",
        "Entrepreneurial Vision": "Builder",
        "Organization Builder": "Operations",
        "Thought Leadership": "Marketing",
        "Portfolio Thinker": "Business Development",
        "Holistic Vision": "Operations",
        "Innovation Focus": "Builder",
        "Lifestyle Design": "Business Development",
        "Brand Vision": "Marketing",
        "Scale Ambition": "Business Development"
    }

    for trait_data in reflection_matches:
        trait = trait_data["trait"]
        if trait in trait_map:
            scores[trait_map[trait]] += 8

    # Slider contributions to founder type
    # Sliders: 0=Opportunity Spotting (ideas), 1=Action Orientation (action),
    # 2=Financial Literacy (resources), 3=People & Network (resources),
    # 4=Uncertainty Tolerance (action), 5=Communication & Persuasion (ideas)
    slider_archetype_map = {
        0: "Builder",
        1: "Builder",
        2: "Operations",
        3: "Business Development",
        4: "Operations",
        5: "Marketing"
    }

    for i, value in enumerate(self_assess.values()):
        if i in slider_archetype_map:
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

# =============================================================================
# SCORING: EntreComp Readiness Dimensions
# =============================================================================

def compute_dimension_scores(time_budget, money_budget, energy_audit, self_assess):
    dim_scores = {"ideas": 0, "resources": 0, "action": 0}

    # Base score: everyone starts with some readiness
    for dim in dim_scores:
        dim_scores[dim] = 25

    # ---- Time budget signals: each category maps to EntreComp dimension ----
    time_dim_map = {
        "build": "action",
        "sell": "resources",
        "operate": "resources",
        "market": "ideas",
        "team": "resources",
        "strategy": "ideas",
    }
    for category, hours in time_budget.items():
        dim = time_dim_map.get(category)
        if dim:
            dim_scores[dim] += hours * 0.8

    # ---- Money budget signals ----
    money_dim_map = {
        "product": "action",
        "sales": "resources",
        "ops": "resources",
        "marketing": "ideas",
        "hires": "resources",
        "reserve": "resources",
    }
    for category, dollars in money_budget.items():
        dim = money_dim_map.get(category)
        if dim:
            dim_scores[dim] += dollars * 0.3

    # ---- Energy audit: energizing tasks add to relevant dimension ----
    energy_task_dim = {
        "code": "action",
        "cold_email": "resources",
        "financial_model": "resources",
        "linkedin_post": "ideas",
        "standup": "resources",
        "investor_pitch": "resources",
        "competitive_research": "ideas",
        "onboarding_process": "action",
    }
    rating_values = {"drain": -2, "neutral": 1, "energize": 4}
    for task, dim in energy_task_dim.items():
        rating = energy_audit.get(task, "neutral")
        dim_scores[dim] += rating_values.get(rating, 0)

    # Sliders: mapped to EntreComp areas
    # 0: Opportunity Spotting -> ideas
    # 1: Action Orientation -> action
    # 2: Financial Literacy -> resources
    # 3: People & Network -> resources
    # 4: Uncertainty Tolerance -> action
    # 5: Communication & Persuasion -> ideas
    slider_dim_map = {0: "ideas", 1: "action", 2: "resources", 3: "resources", 4: "action", 5: "ideas"}

    for i, value in enumerate(self_assess.values()):
        if i in slider_dim_map:
            dim = slider_dim_map[i]
            dim_scores[dim] += (value / 10.0) * 15

    # Cap at 100
    for dim in dim_scores:
        dim_scores[dim] = min(100, dim_scores[dim])

    return dim_scores

def overall_readiness(dim_scores):
    weights = {dim: READINESS_DIMS[dim]["weight"] for dim in READINESS_DIMS}
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

# =============================================================================
# COACHING: personalized based on archetype + dimension scores
# =============================================================================

def generate_coaching(primary_arch, dim_scores, overall):
    coaching = []
    arch_data = ARCHETYPES[primary_arch]

    # Dimension-based coaching tailored to founder type
    if dim_scores["ideas"] < 50:
        type_specific = {
            "Builder": "Lift your eyes from the build: schedule weekly time to research market trends, talk to non-customers, and explore adjacent opportunities.",
            "Business Development": "Strengthen your pitch with deeper opportunity analysis. Spend time mapping the competitive landscape before your next sales conversation.",
            "Operations": "Build structured time for creative exploration into your process. Innovation does not always come from efficiency; sometimes you need to brainstorm freely.",
            "Marketing": "Ground your creative instincts in customer research. Talk to 10 potential users this month and let their language shape your messaging."
        }
        coaching.append(type_specific.get(primary_arch, "Invest time in spotting and evaluating new opportunities through customer conversations and market research."))
    elif dim_scores["ideas"] >= 70:
        coaching.append("Your opportunity radar is strong. Now focus on validating your best ideas quickly with real customers before investing heavily.")

    if dim_scores["resources"] < 50:
        type_specific = {
            "Builder": "Great products need funding and people. Start building relationships with potential advisors, investors, and early customers before you need them.",
            "Business Development": "You open doors well; now make sure the financials back up your promises. Build a basic financial model and track your unit economics.",
            "Operations": "You manage resources well, but are you mobilizing enough of them? Expand your network beyond your current circle to find the capital and talent you need.",
            "Marketing": "Strong brands attract resources. Build a pitch deck that tells your story compellingly, and use it to attract advisors and early believers."
        }
        coaching.append(type_specific.get(primary_arch, "Focus on building the financial literacy, network, and resource base you will need to launch."))
    elif dim_scores["resources"] >= 70:
        coaching.append("Your resource base is solid. Leverage your network and financial skills to create unfair advantages for your venture.")

    if dim_scores["action"] < 50:
        type_specific = {
            "Builder": "You have the skills to build, but are you shipping fast enough? Set a 2 week deadline to get something in front of a real user.",
            "Business Development": "Deals in your pipeline only matter when they close. Push yourself to move faster from conversation to commitment.",
            "Operations": "Your plans are thorough, but startups reward speed. Try launching a minimum version of your process and iterating from there.",
            "Marketing": "Campaigns in draft do not build brands. Ship your content before it feels perfect and learn from real audience feedback."
        }
        coaching.append(type_specific.get(primary_arch, "Focus on taking initiative and learning through action, even when conditions feel uncertain."))
    elif dim_scores["action"] >= 70:
        coaching.append("You take action with confidence. Make sure your speed is paired with reflection so you learn from each experiment.")

    if len(coaching) < 3:
        # Add a team-specific coaching recommendation
        complement = arch_data["complement"]
        coaching.append(f"Find your {complement} counterpart. {arch_data['complement_why']}")

    return coaching[:3]

# =============================================================================
# UI HELPERS
# =============================================================================

def scroll_to_top():
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    js = '''<script>
        var top = window.parent.document.querySelector('section.main');
        if (top) top.scrollTop = 0;
    </script>'''
    st.components.v1.html(js, height=0)

def go_to(page_num):
    st.session_state.page = page_num
    st.session_state.exercise_step = 0

def render_progress(current_page, exercise_step=None):
    pages = ["Welcome", "Founder Exercises", "About You", "Reflections", "Your Results"]
    exercise_labels = ["Time Budget", "Money Budget", "Energy Audit"]
    if exercise_step is not None and current_page == 1:
        progress_text = f"Exercise {exercise_step + 1} of 3: {exercise_labels[exercise_step]}"
    else:
        step_idx = current_page if current_page < 4 else 4
        progress_text = f"Step {step_idx + 1} of 5: {pages[min(current_page, 4)]}"
    progress_html = f'<div style="text-align: center; margin-bottom: 2rem; color: #666; font-size: 14px;">{progress_text}</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def render_back_button(go_to_page):
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("Back", key=f"back_to_{go_to_page}", use_container_width=True):
            go_to(go_to_page)
            st.rerun()

# =============================================================================
# PAGE: Welcome
# =============================================================================

def page_welcome():
    scroll_to_top()
    render_progress(0)

    hero_html = '''
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 3rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1 style="margin: 0 0 0.5rem 0; font-size: 2.5rem;">Entrepreneurial Readiness Simulation</h1>
        <p style="margin: 0; font-size: 1.2rem; opacity: 0.95;">Discover your founder type and startup readiness</p>
    </div>
    '''
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown("### What You'll Discover")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🔨 **Your Founder Type** which of four founding team roles you naturally fill: Builder, Business Development, Operations, or Marketing")
        st.markdown("📈 **Readiness Score** your startup readiness across the three EntreComp dimensions used by researchers worldwide")
    with col2:
        st.markdown("💡 **Personalized Analysis** deep insights based on how you'd allocate time, money, and energy as a founder")
        st.markdown("🤝 **Your Team Complement** which founder type you should recruit to balance your strengths")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Let's Go", key="welcome_begin", use_container_width=True):
            go_to(1)
            st.rerun()

    st.caption("About 12-15 minutes. Three founder exercises (time, money, energy), a short self-assessment, and three reflections.")

    footer_html = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 2rem;">Entrepreneurial Readiness Simulation</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

# =============================================================================
# PAGE: Founder Exercises (replaces multiple-choice scenarios with
# allocation-based mechanics that reveal how you'd actually spend time,
# money, and energy as a founder)
# =============================================================================

TIME_CATEGORIES = [
    ("build", "🔨 Building the product", "Writing code, soldering hardware, shipping features"),
    ("sell", "🤝 Customer & sales work", "Cold outreach, demos, closing deals, discovery calls"),
    ("operate", "⚙️ Operations & finance", "Bookkeeping, metrics dashboards, systems, processes"),
    ("market", "📣 Marketing & story", "Content, brand, social posts, PR, positioning"),
    ("team", "👥 Team & hiring", "Recruiting, 1:1s, standups, culture"),
    ("strategy", "🔭 Strategy & research", "Competitive research, thinking time, opportunity scouting"),
]

MONEY_CATEGORIES = [
    ("product", "🔨 Product R&D", "Prototyping, tools, components, contractors"),
    ("sales", "🤝 Sales & BD", "Sales rep, travel, CRM, partner events"),
    ("ops", "⚙️ Operations & finance tools", "Accounting, legal, compliance, dashboards"),
    ("marketing", "📣 Marketing & PR", "Content, ads, brand design, launch events"),
    ("hires", "👥 Key hires", "First full-time hire, stipends, onboarding"),
    ("reserve", "💰 Cash reserve", "Runway buffer — unallocated for surprises"),
]

ENERGY_TASKS = [
    ("code", "Writing code or building a prototype"),
    ("cold_email", "Cold-emailing a potential customer"),
    ("financial_model", "Building a financial model in a spreadsheet"),
    ("linkedin_post", "Writing a LinkedIn post to market your company"),
    ("standup", "Running a team standup and setting weekly priorities"),
    ("investor_pitch", "Pitching investors in a conference room"),
    ("competitive_research", "Researching competitors and mapping the market"),
    ("onboarding_process", "Designing an onboarding process for a new hire"),
]


def page_scenario():
    scroll_to_top()
    render_progress(1, st.session_state.exercise_step)

    if st.session_state.exercise_step == 0:
        st.markdown("### The ThermaLoop Launch Pad")
        st.markdown(
            "You're getting ThermaLoop — a smart ventilation retrofit kit — off the ground. "
            "Instead of picking from a list of answers, you'll show us how you'd actually spend "
            "your time, your money, and your energy as a founder. Your allocations and ratings "
            "will reveal your founder type and readiness profile."
        )
        st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("#### Exercise 1 of 3: Your First Week (40 hours)")
        st.markdown(
            "You have **40 hours** for your first full week working on ThermaLoop. "
            "Allocate them across the six categories below — exactly 40 hours total. "
            "Use the +/- buttons or type directly."
        )

        # Render number inputs for each category
        cols = st.columns(2)
        for i, (key, label, helptext) in enumerate(TIME_CATEGORIES):
            with cols[i % 2]:
                st.markdown(f"**{label}**")
                st.caption(helptext)
                current = st.session_state.time_budget.get(key, 0)
                val = st.number_input(
                    label,
                    min_value=0,
                    max_value=40,
                    value=int(current),
                    step=1,
                    key=f"time_{key}",
                    label_visibility="collapsed",
                )
                st.session_state.time_budget[key] = val

        total = sum(st.session_state.time_budget.values())
        remaining = 40 - total

        if total == 40:
            st.success(f"✅ Perfect — all 40 hours allocated.")
        elif total < 40:
            st.warning(f"⚠️ You have **{remaining} hours** left to allocate ({total}/40 used).")
        else:
            st.error(f"❌ You've allocated **{total} hours** — that's {total - 40} over budget. Trim somewhere.")

        # Live preview of where their time is going
        st.markdown("##### Your Time Mix")
        if total > 0:
            chart_data = pd.DataFrame([
                {"Category": label.split(" ", 1)[1] if " " in label else label, "Hours": st.session_state.time_budget.get(key, 0)}
                for key, label, _ in TIME_CATEGORIES
            ])
            chart = alt.Chart(chart_data).mark_bar(color="#6366f1").encode(
                y=alt.Y("Category:N", sort="-x"),
                x=alt.X("Hours:Q", scale=alt.Scale(domain=[0, 40])),
                tooltip=["Category", "Hours"],
            ).properties(height=220)
            st.altair_chart(chart, use_container_width=True)

        st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Back", key="ex1_back", use_container_width=True):
                go_to(0)
                st.rerun()
        with col3:
            if total == 40:
                if st.button("Next: Money Budget", key="ex1_next", use_container_width=True):
                    st.session_state.exercise_step = 1
                    st.rerun()
            else:
                st.button("Next: Money Budget", key="ex1_next_disabled", use_container_width=True, disabled=True)
                st.caption("Allocate exactly 40 hours to continue.")

    elif st.session_state.exercise_step == 1:
        st.markdown("### Exercise 2 of 3: Your $100K Budget")
        st.markdown(
            "A grant, angel, or family round just gave ThermaLoop **$100,000** in seed capital. "
            "Allocate it across six buckets in $1K increments. Total must equal $100K."
        )

        cols = st.columns(2)
        for i, (key, label, helptext) in enumerate(MONEY_CATEGORIES):
            with cols[i % 2]:
                st.markdown(f"**{label}**")
                st.caption(helptext)
                current = st.session_state.money_budget.get(key, 0)
                val = st.number_input(
                    f"{key}_amount",
                    min_value=0,
                    max_value=100,
                    value=int(current),
                    step=1,
                    key=f"money_{key}",
                    label_visibility="collapsed",
                    help="In thousands of dollars",
                )
                st.session_state.money_budget[key] = val
                st.caption(f"${val}K")

        total_money = sum(st.session_state.money_budget.values())
        remaining_money = 100 - total_money
        if total_money == 100:
            st.success(f"✅ Perfect — all $100K allocated.")
        elif total_money < 100:
            st.warning(f"⚠️ You have **${remaining_money}K** left to allocate (${total_money}K/$100K used).")
        else:
            st.error(f"❌ You've allocated **${total_money}K** — that's ${total_money - 100}K over budget. Trim somewhere.")

        st.markdown("##### Your Capital Allocation")
        if total_money > 0:
            chart_data = pd.DataFrame([
                {"Category": label.split(" ", 1)[1] if " " in label else label, "Amount ($K)": st.session_state.money_budget.get(key, 0)}
                for key, label, _ in MONEY_CATEGORIES
            ])
            chart = alt.Chart(chart_data).mark_bar(color="#22c55e").encode(
                y=alt.Y("Category:N", sort="-x"),
                x=alt.X("Amount ($K):Q", scale=alt.Scale(domain=[0, 100])),
                tooltip=["Category", "Amount ($K)"],
            ).properties(height=220)
            st.altair_chart(chart, use_container_width=True)

        st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Back", key="ex2_back", use_container_width=True):
                st.session_state.exercise_step = 0
                st.rerun()
        with col3:
            if total_money == 100:
                if st.button("Next: Energy Audit", key="ex2_next", use_container_width=True):
                    st.session_state.exercise_step = 2
                    st.rerun()
            else:
                st.button("Next: Energy Audit", key="ex2_next_disabled", use_container_width=True, disabled=True)
                st.caption("Allocate exactly $100K to continue.")

    else:  # exercise_step == 2
        st.markdown("### Exercise 3 of 3: Energy Audit")
        st.markdown(
            "For each founder task, mark whether it **drains** you, is **neutral**, or **energizes** you. "
            "Be honest — this is about what genuinely pulls you forward, not what you think you should pick."
        )

        for key, task in ENERGY_TASKS:
            current = st.session_state.energy_audit.get(key, "neutral")
            st.markdown(f"**{task}**")
            idx_map = {"drain": 0, "neutral": 1, "energize": 2}
            labels = ["😴 Drains me", "😐 Neutral", "⚡ Energizes me"]
            selected_label = st.radio(
                task,
                labels,
                index=idx_map.get(current, 1),
                key=f"energy_{key}",
                horizontal=True,
                label_visibility="collapsed",
            )
            value_map = {labels[0]: "drain", labels[1]: "neutral", labels[2]: "energize"}
            st.session_state.energy_audit[key] = value_map[selected_label]
            st.markdown('<div style="height: 1px; background: #f3f4f6; margin: 0.75rem 0;"></div>', unsafe_allow_html=True)

        # Count energizers
        energizer_count = sum(1 for v in st.session_state.energy_audit.values() if v == "energize")
        drain_count = sum(1 for v in st.session_state.energy_audit.values() if v == "drain")
        st.info(f"You marked **{energizer_count}** task(s) as energizing and **{drain_count}** as draining.")

        st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Back", key="ex3_back", use_container_width=True):
                st.session_state.exercise_step = 1
                st.rerun()
        with col3:
            if st.button("Next: About You", key="ex3_next", use_container_width=True):
                go_to(2)
                st.rerun()
    return


# =============================================================================
# PAGE: Self Assessment (sliders mapped to EntreComp)
# =============================================================================

def page_selfassessment():
    scroll_to_top()
    render_progress(2)
    render_back_button(1)

    st.markdown("### About You: Where Do You Naturally Fall?")
    st.markdown("There are no right answers here. Just slide to wherever feels most true for you.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    # Sliders mapped to EntreComp areas:
    # 0: Opportunity Spotting -> Ideas & Opportunities
    # 1: Action Orientation -> Into Action
    # 2: Financial Literacy -> Resources
    # 3: People & Network -> Resources
    # 4: Uncertainty Tolerance -> Into Action
    # 5: Communication & Persuasion -> Ideas & Opportunities
    sliders = [
        ("Opportunity Spotting", "I wait for clear signals", "I spot possibilities early"),
        ("Action Orientation", "I think before I act", "I act and adjust"),
        ("Financial Literacy", "Numbers intimidate me", "I think in spreadsheets"),
        ("People and Network", "I know few entrepreneurs", "My network runs deep"),
        ("Uncertainty Tolerance", "I prefer clear plans", "I thrive in ambiguity"),
        ("Communication and Persuasion", "I keep ideas to myself", "I sell ideas naturally")
    ]

    for i, (label, low_label, high_label) in enumerate(sliders):
        st.markdown(f"**{label}**")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.caption(low_label)
        with col3:
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

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Next: Reflections", key="assess_continue", use_container_width=True):
            go_to(3)
            st.rerun()

# =============================================================================
# PAGE: Reflections
# =============================================================================

def page_reflections():
    scroll_to_top()
    render_progress(3)
    render_back_button(2)

    st.markdown("### Reflections: Your Story")
    st.markdown("Your answers to these prompts will reveal deeper patterns in your entrepreneurial mindset. Be honest and thoughtful.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("**1. What draws you to entrepreneurship? What would you build if you knew you could not fail?**")
    st.caption("Write at least a few sentences for the best insights.")
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
    st.caption("The more detail you share, the more accurate your profile.")
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
    st.caption("Dream big. There are no wrong answers here.")
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

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Next: Unlock Results", key="reflections_continue", use_container_width=True):
            go_to(4)
            st.rerun()

# =============================================================================
# PAGE: Reveal Results (no email capture — optional first name only)
# =============================================================================

def page_reveal():
    scroll_to_top()
    render_progress(4)
    render_back_button(3)

    st.markdown("### Your Founder Profile is Ready")

    teaser_html = '''
    <div style="background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%); border: 2px dashed #6366f1; padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; color: #666; margin: 0;">Your founder type is ready to be revealed.</p>
        <p style="color: #999; font-size: 0.95rem; margin: 0.5rem 0 0 0;">Personalized readiness scores and coaching recommendations, based on how you actually allocated your time, money, and energy.</p>
    </div>
    '''
    st.markdown(teaser_html, unsafe_allow_html=True)

    st.markdown("Optionally tell us your first name so we can personalize your report:")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    name = st.text_input("First name (optional)", value=st.session_state.name, key="reveal_name")
    st.session_state.name = name

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Show My Results", key="reveal_show", use_container_width=True):
            all_matches = []
            all_matches.extend(analyze_text(st.session_state.reflections["motivation"], ANALYSIS_MAPS["motivation"]))
            all_matches.extend(analyze_text(st.session_state.reflections["failure"], ANALYSIS_MAPS["failure"]))
            all_matches.extend(analyze_text(st.session_state.reflections["vision"], ANALYSIS_MAPS["vision"]))

            primary_arch, secondary_arch, arch_scores = compute_archetype(
                st.session_state.time_budget,
                st.session_state.money_budget,
                st.session_state.energy_audit,
                all_matches,
                st.session_state.self_assess,
            )

            dim_scores = compute_dimension_scores(
                st.session_state.time_budget,
                st.session_state.money_budget,
                st.session_state.energy_audit,
                st.session_state.self_assess,
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
                "coaching": generate_coaching(primary_arch, dim_scores, overall),
            }

            go_to(5)
            st.rerun()

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
    footer_html = '<div style="text-align: center; color: #888; font-size: 12px;">No email required. Your answers stay on your device.</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

# =============================================================================
# PAGE: Results
# =============================================================================

def page_results():
    scroll_to_top()
    render_progress(5)

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

    user_name = st.session_state.name.strip()
    if user_name:
        greeting = f"{user_name}, your"
    else:
        greeting = "Your"

    score_ring_html = f'''
    <div style="text-align: center; margin: 2rem 0;">
        <div style="font-size: 1.3rem; color: #555; margin-bottom: 1rem;">{greeting} Readiness Score</div>
        <div style="width: 200px; height: 200px; margin: 0 auto; border-radius: 50%; background: linear-gradient(135deg, {color}33 0%, {color}11 100%); border: 8px solid {color}; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <div style="font-size: 3rem; font-weight: bold; color: {color};">{int(overall)}</div>
            <div style="font-size: 1.2rem; color: #333;">{label}</div>
        </div>
    </div>
    '''
    st.markdown(score_ring_html, unsafe_allow_html=True)

    st.markdown(results["label_desc"])

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Founder Type")

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
        st.markdown(f"**Secondary Type:** You also show strong {secondary} tendencies. This combination gives you unique strengths on a founding team.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Your Readiness Profile (EntreComp)")

    entrecomp_note = '''
    <div style="background: #f5f3ff; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem; color: #666;">
        Based on the <strong>EntreComp Framework</strong>, the European Commission's validated model of entrepreneurial competence used by educators and researchers worldwide.
    </div>
    '''
    st.markdown(entrecomp_note, unsafe_allow_html=True)

    for dim_key, dim_info in READINESS_DIMS.items():
        score = dim_scores[dim_key]
        percent = int(score)
        weight_pct = int(dim_info["weight"] * 100)

        bar_html = f'''
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="font-weight: bold; color: #333;">{dim_info["label"]} ({weight_pct}%)</span>
                <span style="color: {dim_info["color"]}; font-weight: bold;">{percent}/100</span>
            </div>
            <div style="width: 100%; height: 12px; background: #f1f5f9; border-radius: 6px; overflow: hidden;">
                <div style="width: {percent}%; height: 100%; background: linear-gradient(90deg, {dim_info["color"]}aa 0%, {dim_info["color"]} 100%);"></div>
            </div>
            <div style="color: #888; font-size: 0.85rem; margin-top: 0.3rem;">{dim_info["description"]}</div>
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
        <h4 style="margin-top: 0;">{complement_data["icon"]} The {complement_arch}</h4>
        <p style="margin: 0.5rem 0; color: #555;">{arch_data["complement_why"]}</p>
        <p style="margin: 0.5rem 0; color: #666; font-style: italic; font-size: 0.95rem;">{complement_data["description"]}</p>
    </div>
    '''
    st.markdown(complement_card, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    with st.expander("Your Self Assessment Profile", expanded=False):
        slider_labels = [
            "Opportunity Spotting",
            "Action Orientation",
            "Financial Literacy",
            "People & Network",
            "Uncertainty Tolerance",
            "Communication & Persuasion"
        ]

        slider_data = []
        for i, label_s in enumerate(slider_labels):
            slider_data.append({
                "Dimension": label_s,
                "Score": st.session_state.self_assess.get(f"slider_{i}", 5)
            })

        df_sliders = pd.DataFrame(slider_data)

        chart = alt.Chart(df_sliders).mark_bar(color="#6366f1").encode(
            y=alt.Y("Dimension:N", sort="-x"),
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 10])),
            tooltip=["Dimension", "Score"]
        ).properties(height=250, width=400)

        st.altair_chart(chart, use_container_width=True)

    with st.expander("What Your Reflections Reveal", expanded=False):
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
        else:
            st.markdown("Write more in your reflections to unlock deeper pattern analysis.")

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

    with st.expander("Founder Type Breakdown", expanded=False):
        arch_scores_list = []
        for arch, score in results["arch_scores"].items():
            arch_scores_list.append({"Type": arch, "Affinity": max(0, score)})

        df_archs = pd.DataFrame(arch_scores_list).sort_values("Affinity", ascending=True)

        colors = ["#6366f1", "#3b82f6", "#22c55e", "#f59e0b"]
        chart = alt.Chart(df_archs).mark_bar().encode(
            y=alt.Y("Type:N", sort="-x"),
            x="Affinity:Q",
            color=alt.Color("Type:N", scale=alt.Scale(domain=list(ARCHETYPES.keys()), range=colors), legend=None)
        ).properties(height=250)

        st.altair_chart(chart, use_container_width=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Challenge a Friend")
    share_url = "https://eship-readiness-sim.streamlit.app"
    challenge_html = f'''
    <div style="background: #f0fdf4; border: 2px solid #22c55e; padding: 1.5rem; border-radius: 8px; text-align: center;">
        <p style="margin-top: 0; color: #333;">Found the simulation valuable? Challenge a friend to discover their founder type too.</p>
        <p style="color: #666; font-size: 0.95rem;">The more founders who understand their strengths, the stronger our entrepreneurial community becomes.</p>
        <div style="margin-top: 1rem;">
            <input type="text" value="{share_url}" readonly style="width: 70%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 6px; text-align: center; font-size: 0.9rem; color: #333; background: white;" onclick="this.select();" />
        </div>
        <p style="color: #999; font-size: 0.8rem; margin-bottom: 0; margin-top: 0.5rem;">Click the link above to select it, then copy and share!</p>
    </div>
    '''
    st.markdown(challenge_html, unsafe_allow_html=True)

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Start Over", key="results_restart", use_container_width=True):
            st.session_state.page = 0
            st.session_state.exercise_step = 0
            st.session_state.time_budget = {"build": 8, "sell": 8, "operate": 6, "market": 6, "team": 6, "strategy": 6}
            st.session_state.money_budget = {"product": 20, "sales": 15, "ops": 15, "marketing": 15, "hires": 20, "reserve": 15}
            st.session_state.energy_audit = {}
            st.session_state.self_assess = {f"slider_{i}": 5 for i in range(6)}
            st.session_state.reflections = {"motivation": "", "failure": "", "vision": ""}
            st.session_state.name = ""
            st.session_state.results = None
            st.rerun()

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("### Disclaimer")
    st.caption("This simulation is designed for educational exploration. Your entrepreneurial potential is shaped by many factors beyond what any simulation can measure. Use these insights as a starting point for growth, not as a ceiling on possibility.")

    st.markdown('<div style="height: 1px; background: #e5e7eb; margin: 1.5rem 0;"></div>', unsafe_allow_html=True)

    footer_html = '<div style="text-align: center; color: #888; font-size: 13px; margin-top: 2rem;">Entrepreneurial Readiness Simulation</div>'
    st.markdown(footer_html, unsafe_allow_html=True)

# =============================================================================
# ROUTING
# =============================================================================

if st.session_state.page == 0:
    page_welcome()
elif st.session_state.page == 1:
    page_scenario()
elif st.session_state.page == 2:
    page_selfassessment()
elif st.session_state.page == 3:
    page_reflections()
elif st.session_state.page == 4:
    page_reveal()
elif st.session_state.page == 5:
    page_results()
