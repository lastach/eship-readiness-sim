import streamlit as st
import pandas as pd
import altair as alt
import re
import math

# ═══════════════════════════════════════════════════════════
# ENTREPRENEURIAL READINESS SIMULATION
# A narrative-driven, archetype-based assessment
# ═══════════════════════════════════════════════════════════

st.set_page_config(page_title="Entrepreneurial Readiness Simulation", layout="wide", initial_sidebar_state="collapsed")

# ══════════════════ LIGHT THEME CSS ══════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global light background */
.stApp {
    background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 50%, #faf8ff 100%);
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
div[data-testid="stSidebarNav"] { display: none; }

/* Main container */
.block-container {
    max-width: 900px;
    padding: 2rem 1rem 3rem 1rem;
}

/* Hero card */
.hero-card {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
}
.hero-card h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: white;
}
.hero-card p {
    font-size: 1.1rem;
    opacity: 0.92;
    line-height: 1.6;
    color: white;
}

/* Content cards */
.content-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8e8f0;
}

/* Scenario card */
.scenario-card {
    background: linear-gradient(135deg, #fefce8 0%, #fff7ed 100%);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid #f59e0b;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.scenario-card h3 {
    color: #92400e;
    margin-bottom: 0.5rem;
}
.scenario-card p {
    color: #78350f;
    line-height: 1.7;
}

/* Insight boxes */
.insight-box {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #22c55e;
}
.insight-box p { color: #166534; margin: 0; line-height: 1.6; }

.coaching-box {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #f59e0b;
}
.coaching-box p { color: #92400e; margin: 0; line-height: 1.6; }

.complement-box {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #3b82f6;
}
.complement-box p { color: #1e40af; margin: 0; line-height: 1.6; }

/* Score display */
.score-ring {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

/* Archetype badge */
.archetype-badge {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
}
.archetype-badge h2 {
    color: white;
    margin-bottom: 0.5rem;
    font-size: 1.6rem;
}
.archetype-badge p { color: rgba(255,255,255,0.9); line-height: 1.5; }

/* Dim bar container */
.dim-bar-container {
    margin: 0.75rem 0;
}
.dim-bar-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #374151;
}
.dim-bar-track {
    background: #e5e7eb;
    border-radius: 8px;
    height: 14px;
    overflow: hidden;
}
.dim-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.6s ease;
}

/* Progress indicator */
.progress-dots {
    display: flex;
    justify-content: center;
    gaay: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Reflection analysis */
.analysis-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    border: 1px solid #e8e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* Hide sidebar */
section[data-testid="stSidebar"] { display: none; }

</style>
""", unsafe_allow_html=True)


# ══════════════════ ARCHETYPE DEFINITIONS ══════════════════

ARCHETYPES = {
    "Visionary": {
        "icon": "ð­",
        "tagline": "You see futures others can't imagine",
        "desc": "You're energized by big ideas, new possibilities, and paradigm shifts. You naturally spot trends before they're obvious and love painting a compelling picture of what could be. Your superpower is inspiring others to believe in a vision that doesn't exist yet.",
        "strengths": ["Big-picture thinking", "Trend spotting", "Inspiring storytelling", "Creative ideation"],
        "gaps": ["Operational follow-through", "Detail management", "Financial planning", "Patience with incremental progress"],
        "complement": "The Builder",
        "complement_why": "A Builder grounds your vision into executable plans, handles the operational details you find draining, and turns your big ideas into tangible milestones. Together you dream big AND deliver.",
    },
    "Builder": {
        "icon": "ð¨",
        "tagline": "You turn ideas into reality, brick by brick",
        "desc": "You thrive on execution — taking something from concept to working product. You're happiest when you're building, shipping, and iterating. You have a natural sense for what's feasible and how to get things done with limited resources.",
        "strengths": ["Execution speed", "Product development", "Resourcefulness", "Iterative improvement"],
        "gaps": ["Long-range strategic thinking", "Market positioning", "Delegation", "Networking and partnerships"],
        "complement": "The Visionary",
        "complement_why": "A Visionary helps you lift your head from the build and see where the market is heading. They bring the storytelling and big-picture strategy that ensures you're building the right thing, not just building things right.",
    },
    "Analyst": {
        "icon": "ð",
        "tagline": "You find truth in the data others overlook",
        "desc": "You're driven by evidence, patterns, and rigorous thinking. You naturally question assumptions and dig into data before making decisions. Your superpower is reducing risk through thorough analysis and spotting flaws before they become costly.",
        "strengths": ["Data-driven decisions", "Risk assessment", "Financial modeling", "Critical thinking"],
        "gaps": ["Bias toward over-analysis", "Speed of decision-making", "Comfort with ambiguity", "Emotional persuasion"],
        "complement": "The Connector",
        "complement_why": "A Connector brings the relatiality, brick by brick",
        "desc": "You thrive on execution — taking something from concept to working product. You're happiest when you're building, shipping, and iterating. You have a natural sense for what's feasible and how to get things done with limited resources.",
        "strengths": ["Execution speed", "Product development", "Resourcefulness", "Iterative improvement"],
        "gaps": ["Long-range strategic thinking", "Market positioning", "Delegation", "Networking and partnerships"],
        "complement": "The Visionary",
        "complement_why": "A Visionary helps you lift your head from the build and see where the market is heading. They bring the storytelling and big-picture strategy that ensures you're building the right thing, not just building things right.",
    },
    "Analyst": {
        "icon": "ð",
        "tagline": "You find truth in the data others overlook",
        "desc": "You're driven by evidence, patterns, and rigorous thinking. You naturally question assumptions and dig into data before making decisions. Your superpower is reducing risk through thorough analysis and spotting flaws before they become costly.",
        "strengths": ["Data-driven decisions", "Risk assessment", "Financial modeling", "Critical thinking"],
        "gaps": ["Bias toward over-analysis", "Speed of decision-making", "Comfort with ambiguity", "Emotional persuasion"],
        "complement": "The Connector",
        "complement_why": "A Connector brings the relationship intelligence and persuasion skills you need. While you ensure decisions are sound, they open doors, build partnerships, and rally people around the opportunity — turning your analysis into action.",
    },
    "Connector": {
        "icon": "ð¤",
        "tagline": "You build bridges between people, ideas, and opportunities",
        "desc": "You're a natural relationship builder who sees opportunities in the spaces between people. You intuitively understand what motivates others and can bring diverse groups together around a common goal. Your network IS your net worth.",
        "strengths": ["Relationship building", "Persuasion and sales", "Partnership development", "Team recruitment"],
        "gaps": ["Solo execution", "Technical depth", "Financial rigor", "Saying no to opportunities"],
        "complement": "The Analyst",
        "complement_why": "An Analyst brings the rigor and data discipline to complement your people skills. While you open doors and close deals, they ensure the numbers work and the strategy is sound — preventing overcommitment and ensuring sustainable growth.",
    },
    "Resilient Adapter": {
        "icon": "ð±",
        "tagline": "You bend without breaking and find a way through anything",
        "desc": "You're defined by grit, flexibility, and an uncanny ability to pivot when plans fall apart. You don't just survive setbacks — you learn from them faster than anyone. Your superpower is maintaining momentum when everyone else wants to quit.",
        "strengths": ["Resilience under pressure", "Rapid pivoting", "Learning from failure", "Emotional steadiness"],
        "gaps": ["Committing to one direction", "Proactive planning", "Leveraging early wins", "Delegating before crisis"],
        "complement": "The Builder",
        "complement_why": "A Builder helps channel your adaptability into consistent forward progress. While you keep the team steady through storms, they ensure you're accumulating tangible results and not just surviving — but actually advancing.",
    },
}


# ══════════════════ SCENARIO: THE FRESHLOOP STORY ══════════════════
# A single immersive narrative with 5 decision points (all on one page)

STORY_INTRO = """You and two friends have been brainstorming a business idea for months: <strong>FreshLoop</strong> — a service
that rescues unsold food from local restaurants and grocers, repackages it into affordable meal kits,
and delivers them to budget-conscious families. You've been talking about it forever. Today, you just found out
that a competing service launched in a neighboring city last week. The clock is ticking."""

SCENES = [
    {
        "title": "ð¥ Scene 1: The Spark",
        "narrative": "Your group chat is blowing up. Your friend Maya says <em>\"We need to launch NOW before they expand here.\"</em> Your other friend Jordan says <em>\"We should study what they're doing first and learn from their mistakes.\"</em> You have a free Saturday coming up. What's your move?",
        "options": {
            "Hit the streets — talk to 20 restaurant owners this Saturday and gauge real interest before anything else": {
                "scores": {"mindset": 3, "skills": 2, "resources": 1, "acumen": 2},
                "archetype_weights": {"Builder": 2, "Connector": 3, "Resilient Adapter": 1},
                "feedback": "**Customer-first instinct.** You're prioritizing real market signal over assumptions — a hallmark of founders who build things people actually want. This bias toward primary research over desk research is what separates builders from planners."
            },
            "Draft a one-page business model and rough financial projection to see if the numbers even work": {
                "scores": {"mindset": 2, "skills": 2, "resources": 2, "acumen": 3},
                "archetype_weights": {"Analyst": 3, "Builder": 1, "Visionary": 1},
                "feedback": "**Analytical foundation.** You want to validate the economics before investing time — smart. The risk is that spreadsheets can become a hiding place from the messiness of real customer feedback. Your instinct for financial rigor is strong; pair it with market testing."
            },
            "Create a compelling pitch deck and start recruiting more people who could help make this real": {
                "scores": {"mindset": 3, "skills": 1, "resources": 2, "acumen": 1},
                "archetype_weights": {"Visionary": 3, "Connector": 2},
                "feedback": "**Vision-led approach.** You're thinking about storytelling and team-building first — you instinctively know that great ventures need great people. Watch that you're not recruiting for a vision that hasn't been validated yet."
            },
            "Research the competitor thoroughly — sign up for their service, read their reviews, map their strategy": {
                "scores": {"mindset": 1, "skills": 2, "resources": 1, "acumen": 3},
                "archetype_weights": {"Analyst": 3, "Resilient Adapter": 1},
                "feedback": "**Strategic intelligence.** Studying the competition is wise — but it can become a form of productive procrastination. The best founders learn from competitors AND talk to customers simultaneously. Your analytical instinct is an asset if you set a time limit on research."
            },
        },
    },
    {
        "title": "ð° Scene 2: The Reality Check",
        "narrative": "It's two weeks later. You've made some progress, but now you're facing a hard truth: to do a proper pilot, you need about $3,000 for packaging, a basic website, and initial food inventory. Between the three of you, you can scrape together $800. How do you handle this?",
        "options": {
            "Bootstrap it — strip the pilot down to the absolute minimum that still tests the core idea with real customers": {
                "scores": {"mindset": 3, "skills": 2, "resources": 3, "acumen": 2},
                "archetype_weights": {"Builder": 3, "Resilient Adapter": 2},
                "feedback": "**Lean startup mentality.** You're willing to test ugly and learn fast rather than wait for perfect conditions. This scrappiness is one of the strongest predictors of startup survival. The founders who launch with duct tape and spreadsheets often outperform those who wait for funding."
            },
            "Pitch local businesses for sponsorship — offer them featured placement in exchange for covering costs": {
                "scores": {"mindset": 2, "skills": 3, "resources": 2, "acumen": 2},
                "archetype_weights": {"Connector": 3, "Visionary": 1, "Builder": 1},
                "feedback": "**Creative deal-making.** You see partnerships where others see obstacles. This ability to create value exchanges (not just ask for money) is a powerful entrepreneurial skill. It also pre-validates demand — if businesses won't sponsor you, that's data."
            },
            "Apply for a small business grant or pitch a local angel investor / entrepreneurship competition": {
                "scores": {"mindset": 2, "skills": 1, "resources": 2, "acumen": 2},
                "archetype_weights": {"Visionary": 2, "Analyst": 2},
                "feedback": "**External validation path.** Seeking formal funding forces you to articulate your value proposition clearly, which is valuable. The risk is timeline — grants and competitions take weeks or months, and your competitor isn't waiting."
            },
            "Put the idea on hold until you can save up enough to do it properly — you don't want to launch something half-baked": {
                "scores": {"mindset": 0, "skills": 1, "resources": 1, "acumen": 1},
                "archetype_weights": {"Analyst": 1},
                "feedback": "**Perfectionism risk.** The instinct to \"do it right\" is understandable, but in entrepreneurship, waiting for perfect conditions is often the biggest risk of all. Most successful startups launched with far less than they thought they needed. The market won't wait for you to be ready."
            },
        },
    },
    {
        "title": "ð§ Scene 3: The First Failure",
        "narrative": "You launched a small pilot! But the first week is rough. Only 4 out of 30 meal kits sold. Your Instagram campaign got barely any engagement. Maya is frustrated and talking about quitting. Jordan says the whole concept might be flawed. You're sitting at your kitchen table on Sunday night staring at the numbers. What do you do?",
        "options": {
            "Call every single person who DID buy and ask them why — then call people who didn't and ask what would change their mind": {
                "scores": {"mindset": 3, "skills": 3, "resources": 1, "acumen": 3},
                "archetype_weights": {"Builder": 2, "Analyst": 2, "Resilient Adapter": 2},
                "feedback": "**Learn-from-failure reflex.** This is the response of someone who treats setbacks as data, not verdicts. Talking to actual customers (both buyers and non-buyers) is the fastest path to understanding what's broken. This instinct alone separates founders who iterate from founders who spiral."
            },
            "Reframe the narrative for the team — remind everyone that most startups fail on their first try and this is just iteration": {
                "scores": {"mindset": 3, "skills": 1, "resources": 1, "acumen": 1},
                "archetype_weights": {"Visionary": 2, "Resilient Adapter": 2, "Connector": 1},
                "feedback": "**Emotional leadership.** You instinctively protect team morale and reframe setbacks as learning. This is critical — most startups die from co-founder conflict, not bad ideas. But be careful that optimism doesn't substitute for diagnosis. Your team needs hope AND a concrete plan."
            },
            "Dig into the data — analyze who saw the campaign, map the drop-off points, A/B test different messaging this week": {
                "scores": {"mindset": 2, "skills": 3, "resources": 1, "acumen": 3},
                "archetype_weights": {"Analyst": 3, "Builder": 1},
                "feedback": "**Data-driven pivot.** You go to the metrics first, which is smart. Understanding WHERE the funnel breaks is essential to fixing it. The risk is getting lost in dashboards instead of having real conversations with real humans about why they didn't buy."
            },
            "Pivot the model — maybe meal kits aren't right, but the food rescue relationships are valuable. Brainstorm completely different approaches": {
                "scores": {"mindset": 2, "skills": 1, "resources": 2, "acumen": 2},
                "archetype_weights": {"Visionary": 3, "Resilient Adapter": 2},
                "feedback": "**Pivot instinct.** You're willing to let go of the original form while keeping the core value. This is a powerful entrepreneurial trait — but be cautious about pivoting too fast. One bad week isn't always a signal to change direction entirely. Sometimes the idea is right but the execution needs tuning."
            },
        },
    },
    {
        "title": "ð¥ Scene 4: The Team Fracture",
        "narrative": "After three months of grinding, things are picking up — you're now selling 50+ kits per week. But tension is rising. Maya has been doing most of the delivery logistics and feels overworked. Jordan has been handling social media but wants to focus on strategy. You've been managing restaurant relationships. Nobody formally agreed on roles, equity, or decision-making authority. A big argument erupts over whether to hire a part-time driver. How do you handle this?",
        "options": {
            "Call a formal meeting — put roles, equity, and decision-making process in writing before making any more operational decisions": {
                "scores": {"mindset": 2, "skills": 3, "resources": 2, "acumen": 3},
                "archetype_weights": {"Analyst": 2, "Builder": 2, "Connector": 1},
                "feedback": "**Structural maturity.** You recognize that the informal startup phase needs to evolve into something more structured. Getting roles and equity in writing now — while relationships are strained but not broken — is exactly the right instinct. Most co-founder blowups happen because this conversation was delayed too long."
            },
            "Focus on Maya's burnout first — she's the most at risk of leaving, and without her the logistics fall apart": {
                "scores": {"mindset": 3, "skills": 2, "resources": 1, "acumen": 2},
                "archetype_weights": {"Connector": 3, "Resilient Adapter": 2},
                "feedback": "**People-first leadership.** You triage the human problem before the structural one. Retaining Maya is existentially important, and you see that. The risk is that fixing one person's frustration without addressing the systemic issue means you'll be putting out fires forever."
            },
            "Just hire the driver — the argument is really about everyone being overworked, and reducing the workload will reduce the tension": {
                "scores": {"mindset": 1, "skills": 1, "resources": 2, "acumen": 1},
                "archetype_weights": {"Builder": 2, "Resilient Adapter": 1},
                "feedback": "**Action bias.** You want to solve the symptom quickly and keep moving. Sometimes this works — but the argument about the driver is really about power, equity, and roles. Hiring without resolving those deeper issues just adds another person to an unclear structure."
            },
            "Bring in an outside mentor or advisor to mediate — you're too close to this to be objective": {
                "scores": {"mindset": 2, "skills": 2, "resources": 3, "acumen": 2},
                "archetype_weights": {"Analyst": 1, "Connector": 2, "Visionary": 1},
                "feedback": "**Self-awareness and resourcefulness.** Knowing when you're too close to a problem and need outside perspective is a sign of maturity. Mentors can see patterns you can't. The key is finding someone who's navigated co-founder dynamics before, not just a general business advisor."
            },
        },
    },
    {
        "title": "ð Scene 5: The Big Opportunity",
        "narrative": "Six months in, FreshLoop is growing steadily. Then a regional grocery chain approaches you: they want to partner exclusively — they'll give you all their unsold food for free, but you can't work with any other grocers in the area. They also want you to use their branding on the meal kits. It would 3x your supply instantly but fundamentally change the business. Your team is split.",
        "options": {
            "Take the deal but negotiate hard — remove the exclusivity clause and the branding requirement, even if it means less supply": {
                "scores": {"mindset": 3, "skills": 3, "resources": 2, "acumen": 3},
                "archetype_weights": {"Analyst": 2, "Connector": 2, "Builder": 1},
                "feedback": "**Strategic negotiation.** You see the value but refuse to give up independence. Negotiating to keep your brand and supplier diversity shows you're thinking about long-term positioning, not just short-term growth. This is the instinct that separates businesses that scale from ones that get absorbed."
            },
            "Take it as-is — this kind of opportunity doesn't come twice, and you can always renegotiate later when you have more leverage": {
                "scores": {"mindset": 2, "skills": 1, "resources": 3, "acumen": 1},
                "archetype_weights": {"Builder": 2, "Resilient Adapter": 2},
                "feedback": "**Growth-at-all-costs instinct.** Speed and scale are tempting, but exclusivity and branding concessions are extremely hard to undo later. 'We'll renegotiate when we're bigger' rarely works — the power dynamic often gets worse, not better. Your boldness is an asset, but this needs more guardrails."
            },
            "Decline — your independence and brand are more valuable than free supply. Find a way to grow on your own terms": {
                "scores": {"mindset": 2, "skills": 1, "resources": 1, "acumen": 2},
                "archetype_weights": {"Visionary": 3, "Resilient Adapter": 1},
                "feedback": "**Brand-protective instinct.** You value autonomy and long-term brand equity over short-term growth. This can be the right call — but walking away from free supply when you're still early-stage is a significant risk. Consider whether your principles are well-timed or premature."
            },
            "Ask for a 90-day trial period — test the partnership with clear metrics before committing to anything long-term": {
                "scores": {"mindset": 2, "skills": 2, "resources": 2, "acumen": 3},
                "archetype_weights": {"Analyst": 3, "Builder": 1, "Resilient Adapter": 1},
                "feedback": "**Test-and-learn approach.** You want data before committing, which reduces risk. A trial period is a genuinely creative middle path. The question is whether the grocery chain will agree — big companies often want commitment, not experiments. But it's worth asking."
            },
        },
    },
]


# ══════════════════ REFLECTION PROMPTS & AI ANALYSIS ══════════════════

REFLECTIONS = {
    "motivation": {
        "prompt": "What draws you to entrepreneurship? What's the deeper reason you'd want to build something of your own — beyond money?",
        "analysis_map": {
            "impact|change|difference|help|community|world|better|social|people": {
                "trait": "Impact-Driven",
                "insight": "Your motivation is rooted in making a difference. Impact-driven founders often build the most enduring companies because their 'why' sustains them through the inevitable hard times. Channel this into a clear mission statement early — it becomes your north star when decisions get tough.",
                "archetype_boost": {"Visionary": 2, "Connector": 1},
            },
            "freedom|independence|autonomy|own boss|control|flexibility|schedule": {
                "trait": "Autonomy-Seeking",
                "insight": "You crave independence and self-determination. This is a powerful motivator, but be aware: early-stage entrepreneurship often means LESS freedom, not more — you answer to customers, investors, partners, and deadlines. The freedom comes later. Founders who understand this paradox persevere longer.",
                "archetype_boost": {"Builder": 1, "Resilient Adapter": 1},
            },
            "create|build|make|invent|design|product|ship|solve": {
                "trait": "Creator-Builder",
                "insight": "You're driven by the act of creation itself. This builder energy is one of the most reliable entrepreneurial motivators because the reward is intrinsic — you'll keep going even when external validation is scarce. Make sure you balance building what excites you with building what the market wants.",
                "archetype_boost": {"Builder": 2, "Visionary": 1},
            },
            "learn|grow|challenge|push|stretch|develop|skill|master": {
                "trait": "Growth-Oriented",
                "insight": "You see entrepreneurship as a vehicle for personal growth. This learning orientation is correlated with resilience — founders who frame setbacks as learning opportunities recover faster. Your growth mindset is an asset; pair it with a specific domain you want to master.",
                "archetype_boost": {"Resilient Adapter": 2, "Analyst": 1},
            },
            "opportunity|gap|market|problem|need|inefficiency|broken|fix": {
                "trait": "Opportunity-Spotter",
                "insight": "You see gaps and inefficiencies that others miss — and you want to fix them. This problem-solution orientation is classic entrepreneurial thinking. The key is validating that others experience the problem as acutely as you do. Your instinct for market gaps is strong; pair it with customer evidence.",
                "archetype_boost": {"Analyst": 2, "Visionary": 1},
            },
            "team|together|people|collaborate|lead|culture|hire": {
                "trait": "Team-Builder",
                "insight": "You're drawn to the human side of building — assembling and leading a team. This relational motivation is especially valuable because most startups succeed or fail based on the founding team, not the idea. Your instinct to think about people first is a genuine competitive advantage.",
                "archetype_boost": {"Connector": 2, "Builder": 1},
            },
        },
    },
    "failure_response": {
        "prompt": "Describe a time you faced a significant setback or failure. How did you respond, and what did you take away from it?",
        "analysis_map": {
            "learned|lesson|realized|understood|discovered|takeaway|insight": {
                "trait": "Reflective Learner",
                "insight": "You extract lessons from adversity — that's the hallmark of a resilient founder. Research shows that entrepreneurs who reflect on failures (rather than just powering through them) make better decisions in subsequent ventures. Your reflective capacity is a genuine strength.",
                "archetype_boost": {"Analyst": 1, "Resilient Adapter": 2},
            },
            "pivot|change|adapt|adjust|different|new approach|shifted|tried again": {
                "trait": "Adaptive Responder",
                "insight": "You respond to setbacks by changing course rather than doubling down on what isn't working. This adaptability is crucial in entrepreneurship where the original plan almost never survives contact with reality. Your flexibility is a superpower — just make sure pivots are driven by data, not just discomfort.",
                "archetype_boost": {"Resilient Adapter": 2, "Builder": 1},
            },
            "kept going|persisted|didn't give up|pushed through|stayed|committed|persevered|grit": {
                "trait": "Persistent Grinder",
                "insight": "Your instinct is to persist through difficulty — to outlast the problem. This grit is one of the most studied and validated entrepreneurial traits. The nuance is knowing when persistence becomes stubbornness. The best founders combine your persistence with strategic flexibility.",
                "archetype_boost": {"Builder": 2, "Resilient Adapter": 1},
            },
            "help|support|talked|mentor|advice|team|friend|family|asked": {
                "trait": "Support-Seeker",
                "insight": "You reach out to others when you're struggling — this is actually a sign of strength, not weakness. Founders who build support networks recover from setbacks faster and make better decisions under stress. Your willingness to be vulnerable and ask for help is a genuine competitive advantage.",
                "archetype_boost": {"Connector": 2, "Resilient Adapter": 1},
            },
            "plan|strategy|analyze|figured|research|understand|studied|systematic": {
                "trait": "Strategic Processor",
                "insight": "You respond to setbacks by stepping back and analyzing what went wrong. This systematic approach to failure is valuable — it means you're less likely to repeat mistakes. Pair this analytical response with speed; the best founders analyze quickly and act on their findings immediately.",
                "archetype_boost": {"Analyst": 2, "Visionary": 1},
            },
        },
    },
    "vision": {
        "prompt": "Imagine your ideal entrepreneurial life 5 years from now. What does your day look like? What kind of company are you running? Who's around you?",
        "analysis_map": {
            "team|employees|hire|culture|office|people|staff|co-founder": {
                "trait": "Organization Builder",
                "insight": "Your vision centers on people and team — you're building a company, not just a product. Founders who think about culture and team from day one tend to build more sustainable organizations. Your instinct for the human side of business is a genuine differentiator.",
                "archetype_boost": {"Connector": 2, "Builder": 1},
            },
            "product|customers|users|build|ship|create|platform|technology|app": {
                "trait": "Product Visionary",
                "insight": "Your future revolves around what you're building and who's using it. This product-centric vision is the engine of most successful startups. Make sure the people who use your product stay at the center of your vision — the best products come from deep empathy, not just technical ambition.",
                "archetype_boost": {"Builder": 2, "Visionary": 1},
            },
            "impact|community|social|change|better|mission|purpose|meaningful": {
                "trait": "Mission-Driven Leader",
                "insight": "Your 5-year vision is anchored in impact and meaning. Mission-driven founders attract purpose-driven talent and loyal customers. Your challenge will be balancing mission with financial sustainability — the most impactful companies find where purpose and profit overlap.",
                "archetype_boost": {"Visionary": 2, "Connector": 1},
            },
            "freedom|travel|flexible|lifestyle|balance|remote|family|enjoy": {
                "trait": "Lifestyle Designer",
                "insight": "You're building a business that serves your life, not the other way around. This clarity about what you actually want is surprisingly rare and valuable. Just know that lifestyle-optimized businesses usually require intense upfront investment of time before they deliver the freedom you envision.",
                "archetype_boost": {"Resilient Adapter": 1, "Builder": 1},
            },
            "revenue|profit|scale|grow|expand|million|funding|investor|IPO|exit": {
                "trait": "Scale-Oriented",
                "insight": "Your vision is ambitious — you're thinking about scale, growth, and significant financial outcomes. This ambition is the fuel that drives high-growth companies. Pair it with deep customer empathy so that your growth is built on real value, not just metrics.",
                "archetype_boost": {"Visionary": 1, "Analyst": 2},
            },
            "learn|expert|master|known for|thought leader|speak|write|teach": {
                "trait": "Expertise Builder",
                "insight": "Your vision includes becoming a recognized expert in your domain. This reputation-building instinct can be a powerful flywheel — expertise attracts opportunities, talent, and customers. Many successful founders built their company on the back of personal credibility in their field.",
                "archetype_boost": {"Analyst": 1, "Visionary": 1, "Connector": 1},
            },
        },
    },
}


# ══════════════════ SELF-ASSESSMENT DIMENSIONS ══════════════════

SELF_ASSESS_DIMS = [
    {"key": "risk_tolerance", "label": "Risk Tolerance", "low": "I prefer certainty and proven paths", "high": "I'm comfortable betting on uncertain outcomes", "category": "mindset"},
    {"key": "resourcefulness", "label": "Resourcefulness", "low": "I need proper resources before starting", "high": "I can make something from almost nothing", "category": "skills"},
    {"key": "persuasion", "label": "Selling & Persuasion", "low": "I find it hard to pitch or sell ideas", "high": "I can get almost anyone excited about my ideas", "category": "skills"},
    {"key": "financial_intuition", "label": "Financial Intuition", "low": "Numbers and finances stress me out", "high": "I naturally think in terms of costs, margins, and ROI", "category": "acumen"},
    {"key": "resilience", "label": "Resilience", "low": "Setbacks shake my confidence significantly", "high": "I bounce back quickly and use setbacks as fuel", "category": "mindset"},
    {"key": "leadership", "label": "Leadership", "low": "I prefer to follow or contribute individually", "high": "I naturally step into leadership roles", "category": "skills"},
    {"key": "adaptability", "label": "Adaptability", "low": "I like sticking to the plan once it's set", "high": "I thrive when plans change and I need to improvise", "category": "mindset"},
    {"key": "customer_empathy", "label": "Customer Empathy", "low": "I build what I think is best", "high": "I obsess over understanding what people actually need", "category": "acumen"},
]


# ══════════════════ ANALYSIS & SCORING FUNCTIONS ══════════════════

def analyze_text(text, analysis_map):
    """Analyze free-text response against keyword patterns and return matched traits."""
    if not text or len(text.strip()) < 10:
        return []
    text_lower = text.lower()
    matches = []
    for pattern, data in analysis_map.items():
        keywords = pattern.split("|")
        match_count = sum(1 for kw in keywords if kw in text_lower)
        if match_count > 0:
            matches.append({**data, "match_strength": match_count})
    matches.sort(key=lambda x: x["match_strength"], reverse=True)
    return matches[:3]  # Top 3 matches


def compute_archetype(scene_choices, reflection_matches, self_assess_values):
    """Compute primary and secondary archetypes from all inputs."""
    scores = {a: 0 for a in ARCHETYPES}

    # From scenario choices (40% weight)
    for choice_data in scene_choices:
        if choice_data:
            for arch, weight in choice_data.get("archetype_weights", {}).items():
                scores[arch] += weight * 1.5

    # From reflection analysis (35% weight)
    for matches in reflection_matches:
        for m in matches:
            for arch, boost in m.get("archetype_boost", {}).items():
                scores[arch] += boost * 1.2

    # From self-assessment (25% weight)
    if self_assess_values:
        # Map slider values to archetype tendencies
        sa = self_assess_values
        scores["Builder"] += sa.get("resourcefulness", 5) * 0.15 + sa.get("leadership", 5) * 0.1
        scores["Visionary"] += sa.get("risk_tolerance", 5) * 0.15 + sa.get("persuasion", 5) * 0.1
        scores["Analyst"] += sa.get("financial_intuition", 5) * 0.15 + sa.get("customer_empathy", 5) * 0.1
        scores["Connector"] += sa.get("persuasion", 5) * 0.15 + sa.get("leadership", 5) * 0.1
        scores["Resilient Adapter"] += sa.get("resilience", 5) * 0.15 + sa.get("adaptability", 5) * 0.1

    sorted_archs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_archs[0][0]
    secondary = sorted_archs[1][0] if len(sorted_archs) > 1 else None
    return primary, secondary, scores


def compute_dimension_scores(scene_choices, self_assess_values):
    """Compute scores across the 4 dimensions."""
    dims = {"mindset": 0, "skills": 0, "resources": 0, "acumen": 0}
    max_per_dim = {"mindset": 0, "skills": 0, "resources": 0, "acumen": 0}

    # Scene contributions
    for choice_data in scene_choices:
        if choice_data:
            for dim in dims:
                dims[dim] += choice_data["scores"].get(dim, 0)
                max_per_dim[dim] += 3

    # Self-assessment contributions
    if self_assess_values:
        for item in SELF_ASSESS_DIMS:
            cat = item["category"]
            val = self_assess_values.get(item["key"], 5)
            dims[cat] += val * 0.3
            max_per_dim[cat] += 3

    # Normalize to 0-100
    result = {}
    for dim in dims:
        mx = max(max_per_dim[dim], 1)
        result[dim] = min(100, int((dims[dim] / mx) * 100))

    return result


def overall_readiness(dim_scores):
    """Weighted overall readiness score."""
    weights = {"mindset": 0.30, "skills": 0.25, "resources": 0.20, "acumen": 0.25}
    total = sum(dim_scores.get(d, 0) * w for d, w in weights.items())
    return int(total)


def readiness_label(score):
    if score >= 80:
        return "Ready to Launch", "#22c55e", "You have strong entrepreneurial foundations across the board. You're not just ready — you're likely already acting like a founder."
    elif score >= 60:
        return "Almost There", "#f59e0b", "You have solid foundations with some specific areas to develop. Targeted growth in your gap areas could make a significant difference."
    elif score >= 40:
        return "Building Momentum", "#f97316", "You're developing real entrepreneurial instincts. Focus on your strengths while actively building skills in your gap areas."
    else:
        return "Early Explorer", "#3b82f6", "You're at the beginning of your entrepreneurial journey — and that's a great place to be. Everyone starts here. Your awareness of where you stand is itself a strength."


def generate_coaching(primary_arch, dim_scores, overall):
    """Generate personalized coaching recommendations."""
    arch_data = ARCHETYPES[primary_arch]
    recs = []

    # Based on lowest dimension
    sorted_dims = sorted(dim_scores.items(), key=lambda x: x[1])
    weakest = sorted_dims[0]

    dim_coaching = {
        "mindset": "**Strengthen your entrepreneurial mindset** by putting yourself in low-stakes situations that require tolerating ambiguity — like volunteering to lead an unfamiliar project or making small bets on uncertain outcomes. Mindset is a muscle, not a trait.",
        "skills": "**Build your skill toolkit** by focusing on the skill you use least: if it's selling, practice pitching one idea per week to a friend. If it's building, try shipping a tiny project in a weekend. Skills compound faster than you think.",
        "resources": "**Expand your resource network** by mapping the assets you already have access to (people, skills, spaces, tools) and the gaps. Often the resources exist — they're just not yet connected to your goal. Start by telling 10 people what you're building.",
        "acumen": "**Sharpen your business acumen** by studying one business model per week — not just what companies do, but HOW they make money. Understanding unit economics and customer acquisition costs will transform your decision-making.",
    }

    recs.append(dim_coaching.get(weakest[0], ""))

    # Based on archetype gaps
    if arch_data["gaps"]:
        top_gaps = arch_data["gaps"][:2]
        recs.append(f"**As a {primary_arch}, watch for:** {' and '.join(top_gaps).lower()}. These are your natural blind spots. You don't need to become great at them — but you need someone on your team who is.")

    return recs


# ══════════════════ SESSION STATE ══════════════════

if "page" not in st.session_state:
    st.session_state.page = 0

if "scene_choices" not in st.session_state:
    st.session_state.scene_choices = [None] * 5

if "self_assess" not in st.session_state:
    st.session_state.self_assess = {}

if "reflections" not in st.session_state:
    st.session_state.reflections = {"motivation": "", "failure_response": "", "vision": ""}

def go_to(p):
    st.session_state.page = p


# ══════════════════ PROGRESS INDICATOR ══════════════════

def render_progress(current, total=4):
    labels = ["Welcome", "Scenario", "About You", "Results"]
    dots_html = ""
    for i in range(total):
        cls = "done" if i < current else ("active" if i == current else "")
        dots_html += f'<div class="dot {cls}" title="{labels[i]}"></div>'
    st.markdown(f'<div class="progress-dots">{dots_html}</div>', unsafe_allow_html=True)


# ══════════════════ PAGE RENDERING ══════════════════

page = st.session_state.page


# ── PAGE 0: WELCOME ──
if page == 0:
    st.markdown("""
    <div class="hero-card">
        <h1>Entrepreneurial Readiness Simulation</h1>
        <p>An interactive experience that reveals your entrepreneurial strengths, your natural founder archetype, and who you need around you to succeed.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="content-card">
        <p class="section-header">What You'll Discover</p>
        <p style="color: #374151; line-height: 1.8;">
        This isn't a quiz — it's a simulation. You'll navigate a realistic startup story, making decisions that reveal
        your natural instincts as a founder. Along the way, you'll reflect on your motivations and assess your skills.
        At the end, you'll get a personalized profile including:</p>
        <p style="color: #374151; line-height: 1.8; margin-top: 0.75rem;">
        <strong style="color: #6366f1;">&#9670;</strong> Your <strong>Entrepreneurial Archetype</strong> — which of 5 founder types fits you best<br>
        <strong style="color: #22c55e;">&#9670;</strong> Your <strong>Readiness Score</strong> across 4 dimensions<br>
        <strong style="color: #f59e0b;">&#9670;</strong> <strong>AI-powered analysis</strong> of your written reflections<br>
        <strong style="color: #3b82f6;">&#9670;</strong> Your <strong>complementary profile</strong> — who you need on your team
        </p>
        <p style="color: #6b7280; margin-top: 1rem; font-size: 0.9rem;"><em>Takes about 10-12 minutes. There are no right answers — only YOUR answers.</em></p>
    </div>
    """, unsafe_allow_html=True)

    render_progress(0)

    if st.button("Begin the Simulation", key="start"):
        go_to(1)
        st.rerun()


# ── PAGE 1: THE FRESHLOOP SCENARIO (all 5 scenes on one scrolling page) ──
elif page == 1:
    render_progress(1)

    st.markdown("""
    <div class="content-card">
        <p class="section-header">The FreshLoop Story</p>
        <p style="color: #374151; line-height: 1.7;">""" + STORY_INTRO + """</p>
    </div>
    """, unsafe_allow_html=True)

    all_answered = True

    for i, scene in enumerate(SCENES):
        st.markdown(f"""
        <div class="scenario-card">
            <h3>{scene['title']}</h3>
            <p>{scene['narrative']}</p>
        </div>
        """, unsafe_allow_html=True)

        options = list(scene["options"].keys())
        choice = st.radio(
            f"Your decision:",
            options=options,
            key=f"scene_{i}",
            index=None,
            label_visibility="collapsed",
        )

        if choice:
            choice_data = scene["options"][choice]
            st.session_state.scene_choices[i] = choice_data
            st.markdown(f"""
            <div class="insight-box">
                <p>{choice_data['feedback']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            all_answered = False

        st.markdown("---")

    if all_answered:
        if st.button("Continue to Self-Assessment", key="to_assess"):
            go_to(2)
            st.rerun()
    else:
        st.info("Make a choice for each scene to continue")


# ── PAGE 2: SELF-ASSESSMENT + REFLECTIONS (combined) ──
elif page == 2:
    render_progress(2)

    st.markdown("""
    <div class="content-card">
        <p class="section-header">Quick Self-Assessment</p>
        <p style="color: #6b7280;">Rate yourself on each dimension. Be honest — this isn't about scoring high, it's about accuracy.</p>
    </div>
    """, unsafe_allow_html=True)

    for item in SELF_ASSESS_DIMS:
        val = st.slider(
            item["label"],
            min_value=1, max_value=10, value=st.session_state.self_assess.get(item["key"], 5),
            help=f"1 = {item['low']}  |  10 = {item['high']}",
            key=f"sa_{item['key']}",
        )
        st.session_state.self_assess[item["key"]] = val

    st.markdown("---")

    st.markdown("""
    <div class="content-card">
        <p class="section-header">Reflections</p>
        <p style="color: #6b7280;">Share your thoughts in a few sentences. The more you write, the richer your analysis will be.</p>
    </div>
    """, unsafe_allow_html=True)

    for key, ref_data in REFLECTIONS.items():
        st.markdown(f"**{ref_data['prompt']}**")
        text = st.text_area(
            "Your response:",
            value=st.session_state.reflections.get(key, ""),
            height=120,
            key=f"ref_{key}",
            label_visibility="collapsed",
        )
        st.session_state.reflections[key] = text

        # Show live analysis preview if they've written enough
        if text and len(text.strip()) > 20:
            matches = analyze_text(text, ref_data["analysis_map"])
            if matches:
                top = matches[0]
                st.markdown(f"""
                <div class="analysis-card">
                    <p style="color: #6366f1; font-weight: 600; margin-bottom: 0.25rem;">Detected pattern: {top['trait']}</p>
                    <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">{top['insight'][:150]}...</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")

    can_continue = all(len(st.session_state.reflections.get(k, "").strip()) > 10 for k in REFLECTIONS)

    if can_continue:
        if st.button("See My Results", key="to_results"):
            go_to(3)
            st.rerun()
    else:
        st.info("Write at least a sentence or two for each reflection to continue")


# ── PAGE 3: RESULTS DASHBOARD ──
elif page == 3:
    render_progress(3)

    # Compute everything
    reflection_matches = []
    for key, ref_data in REFLECTIONS.items():
        text = st.session_state.reflections.get(key, "")
        matches = analyze_text(text, ref_data["analysis_map"])
        reflection_matches.append(matches)

    primary, secondary, arch_scores = compute_archetype(
        st.session_state.scene_choices, reflection_matches, st.session_state.self_assess
    )
    dim_scores = compute_dimension_scores(st.session_state.scene_choices, st.session_state.self_assess)
    overall = overall_readiness(dim_scores)
    label, color, label_desc = readiness_label(overall)

    # ── Overall Score ──
    st.markdown(f"""
    <div class="content-card" style="text-align: center;">
        <p class="section-header" style="justify-content: center;">Your Entrepreneurial Readiness</p>
        <div class="score-ring" style="background: linear-gradient(135deg, {color}, {color}dd);">
            {overall}
        </div>
        <h3 style="color: {color}; margin: 0.5rem 0;">{label}</h3>
        <p style="color: #6b7280; max-width: 500px; margin: 0 auto; line-height: 1.6;">{label_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Archetype ──
    arch_data = ARCHETYPES[primary]
    st.markdown(f"""
    <div class="archetype-badge">
        <h2>{arch_data['icon']} The {primary}</h2>
        <p style="font-size: 1.1rem; font-weight: 500; margin-bottom: 0.5rem;">{arch_data['tagline']}</p>
        <p>{arch_data['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    if secondary:
        sec_data = ARCHETYPES[secondary]
        st.markdown(f"""
        <div class="content-card" style="text-align: center;">
            <p style="color: #6b7280;">With strong secondary traits of <strong style="color: #6366f1;">{sec_data['icon']} The {secondary}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # ── Dimension Scores ──
    st.markdown('<p class="section-header">Your Four Dimensions</p>', unsafe_allow_html=True)

    dim_labels = {
        "mindset": ("Entrepreneurial Mindset", "#8b5cf6"),
        "skills": ("Skills & Competencies", "#3b82f6"),
        "resources": ("Resources & Network", "#22c55e"),
        "acumen": ("Business Acumen", "#f59e0b"),
    }

    for dim, (label_text, bar_color) in dim_labels.items():
        score = dim_scores.get(dim, 0)
        st.markdown(f"""
        <div class="dim-bar-container">
            <div class="dim-bar-label">
                <span>{label_text}</span>
                <span style="color: {bar_color}; font-weight: 600;">{score}%</span>
            </div>
            <div class="dim-bar-track">
                <div class="dim-bar-fill" style="width: {score}%; background: linear-gradient(90deg, {bar_color}, {bar_color}bb);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Strengths & Gaps ──
    col1, col2 = st.columns(2)
    with col1:
        strengths_html = "<br>".join("&#8226; " + s for s in arch_data['strengths'])
        st.markdown(f"""
        <div class="insight-box">
            <p style="font-weight: 600; color: #166534; margin-bottom: 0.5rem;">Your Strengths</p>
            <p>{strengths_html}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        gaps_html = "<br>".join("&#8226; " + g for g in arch_data['gaps'])
        st.markdown(f"""
        <div class="coaching-box">
            <p style="font-weight: 600; color: #92400e; margin-bottom: 0.5rem;">Growth Areas</p>
            <p>{gaps_html}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Who You Need Around You ──
    complement = arch_data["complement"]
    comp_data = ARCHETYPES[complement.replace("The ", "")]
    st.markdown(f"""
    <div class="complement-box">
        <p style="font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">{comp_data['icon']} Who You Need Around You: {complement}</p>
        <p>{arch_data['complement_why']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Self-Assessment Radar ──
    st.markdown('<p class="section-header">Self-Assessment Profile</p>', unsafe_allow_html=True)

    sa_data = pd.DataFrame([
        {"Dimension": item["label"], "Score": st.session_state.self_assess.get(item["key"], 5)}
        for item in SELF_ASSESS_DIMS
    ])

    chart = alt.Chart(sa_data).mark_bar(
        cornerRadiusTopRight=8,
        cornerRadiusBottomRight=8,
    ).encode(
        x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 10]), title="Your Rating"),
        y=alt.Y("Dimension:N", sort="-x", title=""),
        color=alt.condition(
            alt.datum.Score >= 7,
            alt.value("#22c55e"),
            alt.condition(alt.datum.Score >= 4, alt.value("#6366f1"), alt.value("#f59e0b"))
        ),
    ).properties(height=300).configure_axis(
        labelFontSize=12, titleFontSize=13
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)

    # ── Reflection Insights Recap ──
    st.markdown('<p class="section-header">What Your Reflections Reveal</p>', unsafe_allow_html=True)

    ref_labels = {"motivation": "Motivation", "failure_response": "Failure Response", "vision": "Future Vision"}

    for idx, (key, ref_data) in enumerate(REFLECTIONS.items()):
        text = st.session_state.reflections.get(key, "")
        matches = reflection_matches[idx]
        if matches:
            st.markdown(f"""
            <div class="content-card">
                <p style="font-weight: 600; color: #1e1b4b; margin-bottom: 0.5rem;">
                    {ref_labels[key]}
                </p>
            """, unsafe_allow_html=True)
            for m in matches:
                st.markdown(f"""
                <div class="analysis-card">
                    <p style="color: #6366f1; font-weight: 600; margin-bottom: 0.25rem;">{m['trait']}</p>
                    <p style="color: #374151; font-size: 0.95rem; line-height: 1.6; margin: 0;">{m['insight']}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        elif text.strip():
            st.markdown(f"""
            <div class="content-card">
                <p style="font-weight: 600; color: #1e1b4b; margin-bottom: 0.5rem;">{ref_labels[key]}</p>
                <p style="color: #6b7280;">Your response was unique — it didn't match common patterns, which may indicate a distinctive perspective. Consider discussing your entrepreneurial motivations with a mentor to uncover insights that automated analysis might miss.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Coaching Recommendations ──
    st.markdown('<p class="section-header">Your Next Steps</p>', unsafe_allow_html=True)
    coaching = generate_coaching(primary, dim_scores, overall)
    for rec in coaching:
        if rec:
            st.markdown(f"""
            <div class="coaching-box">
                <p>{rec}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Archetype Breakdown Chart ──
    st.markdown('<p class="section-header">Archetype Breakdown</p>', unsafe_allow_html=True)

    arch_df = pd.DataFrame([
        {"Archetype": f"{ARCHETYPES[a]['icon']} {a}", "Score": round(s, 1)}
        for a, s in sorted(arch_scores.items(), key=lambda x: x[1], reverse=True)
    ])

    arch_chart = alt.Chart(arch_df).mark_bar(
        cornerRadiusTopRight=8,
        cornerRadiusBottomRight=8,
    ).encode(
        x=alt.X("Score:Q", title="Archetype Affinity"),
        y=alt.Y("Archetype:N", sort="-x", title=""),
        color=alt.condition(
            alt.datum.Score == alt.expr.max("Score"),
            alt.value("#6366f1"),
            alt.value("#c7d2fe")
        ),
    ).properties(height=220).configure_axis(
        labelFontSize=12, titleFontSize=13
    ).configure_view(strokeWidth=0)

    st.altair_chart(arch_chart, use_container_width=True)

    st.markdown("""
    <div class="content-card" style="text-align: center; margin-top: 2rem;">
        <p style="color: #6b7280; font-size: 0.9rem;">
            This simulation is designed for educational exploration, not definitive assessment.
            Your entrepreneurial potential is shaped by many factors beyond what any simulation can measure.
            Use these insights as a starting point for deeper self-reflection and conversation with mentors.
        </p>
    </div>
    """, unsafe_allow_html=True)
