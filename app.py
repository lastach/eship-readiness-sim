import streamlit as st
import pandas as pd
import altair as alt
import random
import time
import re

st.set_page_config(
    page_title="ThermaLoop | Entrepreneurial Readiness Simulation",
    page_icon="🔥",
    layout="wide",
)

# ============== CUSTOM CSS FOR GAME-LIKE FEEL ==============
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(170deg, #0d1117 0%, #161b22 100%);
    color: #e6edf3;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #30363d;
}

/* ── Typography ── */
h1, h2, h3 { color: #58a6ff !important; }
h1 { font-size: 2.2rem !important; letter-spacing: -0.5px; }

/* ── Progress bar ── */
.progress-outer {
    background: #21262d; border-radius: 12px; height: 18px;
    margin: 0.8rem 0 1.6rem 0; overflow: hidden;
    border: 1px solid #30363d;
}
.progress-inner {
    height: 100%; border-radius: 12px;
    background: linear-gradient(90deg, #238636 0%, #2ea043 50%, #56d364 100%);
    transition: width 0.6s ease;
    display: flex; align-items: center; justify-content: flex-end;
    padding-right: 8px; font-size: 11px; color: #fff; font-weight: 600;
}

/* ── Narrative box ── */
.narrative-box {
    background: #161b22; border-left: 4px solid #58a6ff;
    border-radius: 8px; padding: 1.2rem 1.4rem; margin: 1rem 0 1.6rem 0;
    font-size: 1.05rem; line-height: 1.6; color: #c9d1d9;
}
.narrative-box em { color: #79c0ff; }

/* ── Consequence box (transition pages) ── */
.consequence-box {
    background: #161b22; border-left: 4px solid #f0883e;
    border-radius: 8px; padding: 1.2rem 1.4rem; margin: 1rem 0 1.6rem 0;
    font-size: 1rem; line-height: 1.6; color: #c9d1d9;
}

/* ── Character dialogue box ── */
.character-box {
    background: #161b22; border-left: 4px solid #f0883e;
    border-radius: 8px; padding: 1.2rem 1.4rem; margin: 1rem 0 1.2rem 0;
    font-size: 0.95rem; line-height: 1.5; color: #c9d1d9;
}
.char-name {
    font-weight: 600; color: #79c0ff; margin-bottom: 0.4rem;
}
.char-dialogue {
    font-style: italic; color: #c9d1d9;
}

/* ── Dashboard metric ── */
.dashboard-metric {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem; margin: 0.6rem 0;
    font-size: 0.9rem; color: #c9d1d9;
}
.metric-label {
    color: #8b949e; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;
}
.metric-value {
    font-weight: 600; color: #58a6ff; font-size: 1.1rem; margin-top: 0.2rem;
}

/* ── Scenario card ── */
.scenario-card {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
    font-size: 0.95rem; color: #c9d1d9;
}
.scenario-card strong { color: #58a6ff; }

/* ── Game header badge ── */
.game-badge {
    display: inline-block; background: #238636; color: #fff;
    font-weight: 700; font-size: 0.75rem; letter-spacing: 1.2px;
    padding: 4px 12px; border-radius: 20px; margin-bottom: 0.6rem;
    text-transform: uppercase;
}

/* ── Score card (results) ── */
.score-big {
    text-align: center; padding: 2rem;
    background: linear-gradient(135deg, #161b22, #0d1117);
    border: 2px solid #30363d; border-radius: 16px;
    margin-bottom: 1.5rem;
}
.score-big .number { font-size: 4rem; font-weight: 800; color: #58a6ff; }
.score-big .label { font-size: 1.1rem; color: #8b949e; margin-top: 0.4rem; }

/* ── Coaching box ── */
.coaching-box {
    background: #0d1117; border: 1px solid #238636;
    border-radius: 10px; padding: 1.2rem 1.4rem; margin: 1rem 0;
    font-size: 1rem; line-height: 1.6; color: #c9d1d9;
}
.coaching-box strong { color: #56d364; }

/* ── Button styling ── */
.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all 0.2s ease !important;
    color: #c9d1d9 !important;
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
}
.stButton > button:hover {
    background-color: #21262d !important;
    border-color: #58a6ff !important;
    color: #e6edf3 !important;
}

/* ── Step counter ── */
.step-counter {
    color: #8b949e; font-size: 0.85rem; margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)


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

# ============== NARRATIVE CONTEXT ==============
THERMALOOP_INTRO = """
You're **Alex**, the founder of **ThermaLoop** — a smart ventilation retrofit kit that cuts
building energy costs by up to 30% without ripping out existing HVAC systems.

You left your job six weeks ago. You have a working prototype, a handful of interested
building managers, and a shrinking savings account. Every decision from here shapes whether
ThermaLoop becomes a real business — or a good idea that never quite made it.

**This simulation puts you in the founder's seat.** You'll face real startup decisions across
five rounds, then assess your skills, resources, and business knowledge. At the end, you'll
get an honest readiness profile — not a grade, but a map of where you're strong and where
to focus next.
"""

GAME_NARRATIVES = {
    1: """*Week 3. Your inbox is full of mixed signals.* Building managers say different things.
Some love the concept. Others are polite but vague. A few are already hacking together their
own solutions. **Your job: separate real demand from noise.** Flag only the signals that
suggest genuine, actionable market opportunity.""",

    2: """*Week 5. Reality check.* You've got no budget for user research, no designer on call,
and limited engineering time. Welcome to startup life. **For each constraint, pick the move
you'd actually make** — not the textbook answer, the real one.""",

    3: """*Week 7. Time is ticking.* You've got limited runway and too many possible next steps.
The difference between founders who make it and those who don't often comes down to what they
do *next* — not what they plan. **Pick what you'd actually do in each situation.**""",

    4: """*Week 9. Things just went sideways.* A contractor missed a deadline. Your costs spiked.
A competitor made a move. Shocks like these are normal — how you respond defines your trajectory.
**Choose your real reaction, not the one that sounds best.**""",

    5: """*Week 11. Sprint planning.* You've got a budget of **{budget} cost units** and a list of
possible changes. Some are high-impact. Some feel productive but aren't. You can't do everything.
**Pick the features you'd actually ship this sprint** — stay within budget.""",

    6: """*Self-assessment checkpoint.* Before the next phase, rate yourself honestly on six core
startup skills. Then prove it — scenario rounds will test how you'd actually operate in each area.
**The gap between self-rating and scenario performance is often where the real insight lives.**""",

    7: """*Resource inventory.* Building a venture isn't just about hustle — it's about what you
can realistically tap into. Money, tools, people, connections, time, and support all matter.
**Answer based on what's actually available to you in the next 3–6 months.**""",

    8: """*Final round: Venture-building knowledge.* These questions test how you think about
problems, markets, business models, and growth. There are no trick questions — just real
tradeoffs that founders face every day.""",
}

# ============== GAME 1: CUSTOMER SIGNAL CARDS ==============
OPP_SCENARIOS = [
    {
        "key": "opp_1",
        "text": "20% of building managers export HVAC data weekly to fix errors via a manual spreadsheet workaround.",
        "is_opportunity": True,
    },
    {
        "key": "opp_2",
        "text": "Several building managers mention they'd like a mobile app dashboard 'someday.'",
        "is_opportunity": False,
    },
    {
        "key": "opp_3",
        "text": "40% of prospects start your demo workflow but never finish it.",
        "is_opportunity": True,
    },
    {
        "key": "opp_4",
        "text": "Your LinkedIn posts about smart ventilation get lots of likes but modest demo signups.",
        "is_opportunity": False,
    },
    {
        "key": "opp_5",
        "text": "Prospects say they'd 'maybe try a retrofit kit like this in the future.'",
        "is_opportunity": False,
    },
    {
        "key": "opp_6",
        "text": "Support emails repeatedly mention the same calibration bug that forces managers to redo setups.",
        "is_opportunity": True,
    },
    {
        "key": "opp_7",
        "text": "Several building managers have rigged their own sensor workarounds to get data ThermaLoop should provide.",
        "is_opportunity": True,
    },
    {
        "key": "opp_8",
        "text": "An industry blog post about smart ventilation trends gets traffic, but almost nobody requests a demo.",
        "is_opportunity": False,
    },
    {
        "key": "opp_9",
        "text": "You have a growing waitlist of building managers regularly following up asking when they can get access.",
        "is_opportunity": True,
    },
    {
        "key": "opp_10",
        "text": "Conference attendees say your booth was 'interesting,' but few accept a follow-up call.",
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


# ============== GAME 5: FEATURE BUDGET ==============
FEATURE_BUDGET = 20

Vu
y02_EATURE_ = [
    {
        "key": "oeatu_a,
        "iame : "oFx eacalibration bug tcasineg 25 of pnw ansial_l to gfilson wfirt oetups",
        "iost : "7
        "iseadl_oint.": "5
    },
    {
        "key": "oeatu_b,
        "iame : "oAd a deshboard 'olor:theye copion.",
    "   "iost : "3
        "iseadl_oint.": "1
    },
    {
        "key": "oeatu_c,
        "iame : "ouildia gruseadoetupswilzrd 'hat fwalk managers tohounghtheir ofirt oetrofit kn Onder o15min(te_s",
    "   "iost : "6
        "iseadl_oint.": "4
    },
    {
        "key": "oeatu_d,
        "iame : "oSip tn gxpoerientil b'ir aqulity cmod iing 'featureswith io desand fignals tyet",
    "   "iost : "5
        "iseadl_oint.": "1
    },
    {
        "key": "oeatu_e,
        "iame : "oRuna smarl mpilt whth i10idea  building managers ,incoluing monoard ng and sollow-up ",
    "   "iost : "6
        "iseadl_oint.": "4
    },
    {
        "key": "oeatu_f,
        "iame : "oPolsh iin(r:teshboard 'detils rhat fnly tpoer bser  ofccaion_lly anoicae",
    "   "iost : "2
        "iseadl_oint.": "2
    },
    {
        "key": "oeatu_g,
        "iame : "oAd ansiaruentilion tr carpureswiere aanagers tdro of f duing tetups",
        "iost : "4
        "iseadl_oint.": "5
    },
 


def compute_oalue _ceation score():
    telected = s[        "ffor s int u
y02_EATURE_ =f s[.session_state.get(sf"key"], False)
     ]    if tot telected:
         eturn 1.0
    relected:oalue = sum(1f"kseadl_oint.":]for s int elected:)    max_rossible c sum(1f"kseadl_oint.":]for s int u
y02_EATURE_ )    norm = max(0.0, min(1.0, relected:oalue =/max_rossible )
    return round(1 + 4 * norm, 2)


# ============== GINDSET_GAME S 2–4==============
FINDSET_DQUESIONS = {
    "# esourcefulness" –Game h2    ""ms_est_1: "
        "ksubdim: "oRsourcefulness",
    "   "krovmp": "You heedstr cnders tnd wheybuilding managers rdro ohermaLoop safer {nsial_l but ayu have azer budget for uesearch,. Wat fd you ictually do ifirt ?,
    "   "kopion.": "[        "   "kUseexisting Hignals t(upport aickits, bcnce lation tmails )and thalk dirctey to fafew achrn dstanagers ",
        "   "kWitlcndilaayu have audget for u folmal �study",
        "   "kAsk frinds ghat they phink about
achrn int gnergal",
        "   "kSarch,fnlyinefor u rickle about sVAC dustomersretuntion tefore ohalkng togandyne.""
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"ms_est_2: "
        "ksubdim: "oRsourcefulness",
    "   "krovmp": "You heedstr claunh arclaning magesfor uhermaLoop stoday but ayu rdesigner oust ruite.,
    "   "kopion.": "[        "   "kUseeanor-cod texmplte ioolsand suip tomedting boaiocthat cuommnitcte sthe salue =rovp",
        "   "kWitlcor u fnw aesigner osoit �look mpolsh ed",
        "   "kWrte bcop anowand whitlcor uesignetime, lte r",
        "   "kMockit �u inta smlseadecikand sued scereenshts or crospects ""
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"ms_est_3: "
        "ksubdim: "oRsourcefulness",
    "   "krovmp": "You hwat thotest h fnw a'preditive bmint,ennce ialert'featureswut aave ao dngineering time.this ionths.,
    "   "kopion.": "[        "   "kreatieeansiplet clckible maocku ir s ake-dor:thst ho geaugeintereste",
        "   "kWitlcndilaangineeri have rime.thobuildiit �rovperly",
        "   "kWrte brclng apectand suire nntere_lly aor s edsackg",
        "   "kLok an sidmilar IoTtools,and theatithe sdea tassaluidtedlif toey pave rte.,
    "   "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"ms_est_4: "
        "ksubdim: "oRsourcefulness",
    "   "krovmp": "You hnly tave a cess.thob10iuilding managers rfr eacly festing,of phermaLoop .,
    "   "kopion.": "[        "   "kRunadeepnntereview,and tober e the r astuallworkflow ,and tpint oint."",
        "   "kRuna sig .quldilttive bsu e  withitheye",
        "   "kDn't ohst hndilaayu have a sig ers audence ",
        "   "kReadindustry breort  about smart vuilding s{nsiaeadif phalkng togaheye",
        "]
    "   "kcore(": "[5,"3,"1
"2]
    },
    {# xecution Bbia" –Game h3    {"ms_eecu_1: "
        "ksubdim: "oxecution Bias",
    "   "krovmp": "You have ane tafer non tr cde-ris the fhermaLoop soncept.tefore oapotential vnvensor maeeing,. Wat fd you ictually do ?,
    "   "kopion.": "[        "   "kRuna5quicklcall.swithituilding managers rr s e �u iansiplet laning magesftste",
        "   "kWrte brc20-agesftraiteg do cmap ing ohe next 32tyeas ",
        "   "kBaintsor mproducti ame sand decignet fnw alogo",
        "   "kSarch,fnlyinefor uompetitor mexapletsand dsae the minto.a de cmithout rontrctiog andyne.""
        "]
    "   "kcore(": "[5,"1
"2
 2]
    },
    {"ms_eecu_2: "
        "ksubdim: "oxecution Bias",
    "   "krovmp": "You hwat thotest hnteresteinta s'multi-zne tontraol'�u rade,for uhermaLoop . Wat ' your text steps?,
    "   "kopion.": "[        "   "kAd a d'ompng Hion 'button {n the feshboard 'nd theaklcalcki mplusfollow-up cntereste",
        "   "kuildiahe futl faatureswnd liaunh auicetly",
        "   "kSu e  wfrinds gha don't oanagervuilding s",
        "   "kLok an sompetitor maatureswist ,and theatithea as senunghtaluidteon.",
    "   "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"ms_eecu_3: "
        "ksubdim: "oxecution Bias",
    "   "krovmp": "You re sor nbetween stargeing Hiarl mofic,rvuilding s vs.liargeuesedeatial vompletxs. SHowad you irovceds?,
    "   "kopion.": "[        "   "kRunatwotein festi in Oaratlle — hifferent tlaning mages — jnd tomplre nespondseeaites",
        "   "kick tne tased opresy on syur inbtuieon.",
    "   "   "kWitlcndilaayu han gd fafeul matket ostudy",
        "   "kAsk amentir wohih siegent counds bmre orovmisng and sgowithitheae.,
    "   "]
    "   "kcore(": "[5,"2,"1
"3]
    },
    {"ms_eecu_4: "
        "ksubdim: "oxecution Bias",
    "   "krovmp": "You hrata spilt whth i10iuilding s" esolts)are no isywut alea postiive . Wat fd you io ?,
    "   "kopion.": "[        "   "kMae a miarl mecision fn the feircteon fofthe signalsand skeepnesting,",
        "   "kIgnre ot and thitlcor uerfoctey tkleardata ",
        "   "kRetart yrom ncerath shth iatotal_l different tp irachi",
        "   "kAsk ata dvior wohther thei phink aou ihould ptrst rhe spilt wata ",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"ms_eecu_5: "
        "ksubdim: "oxecution Bias",
    "   "krovmp": "You  uom-ounder ouggest  a duicklchst hoat cuold pisplove iyu  uomeswnssumpion.about snergy cavings  Your cove.?,
    "   "kopion.": "[        "   "kRunathetest h d bu reald to fpivt wf ttlcoils ",
        "   "kAvoidathetest ;you io 't owat thotnder minerhe spithi",
        "   "kDely theyohst hndilaaafer {he futning mound.",
        "   "kAsk ata dvior wohther tt's aorkhithsting,oa all ",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {# esolience & Aaaptability" –Game h4    {"ms_estil_1: "
        "ksubdim: "oRsolience & Adaptability",
    "   "krovmp": "Y⚡ SHOCK:Your ciredwre nontractor mdely  a dcitizcl �snsor wuip ent cby 3weeks a�� jight:tefore oyu  upilt wiaunh .,
    "   "kopion.": "[        "   "kDotot hng and scipleyoprshrhe spilt wime.yinefackg",
        "   "kReplce ehe concractor matiaesy ",
        "   "kRe-corperhe spilt ,adjustimdepndeen worka,jnd tompmnitcte  irachively ahth ipilt wustomers,",
        "]
    "   "kcore(": "[1
"2
 5]
    },
    {"ms_estil_2: "
        "ksubdim: "oRsolience & Adaptability",
    "   "krovmp": "Y⚡ SHOCK:Your customersrcquirition post ujumps 0% ofvr nght:tafer {aplantolmachanges.tt' a  'nlgritihm.,
    "   "kopion.": "[        "   "kKeepncaplagnasrunwnng and sceeghat thp inso",
        "   "kKll trl mpaidahangnel impmedite ly",
        "   "kShiftapecd, yhst hnw aceativels,gxpolre otrgaitcahangnel  and recviewfutnnelaqulity ",
        "]
    "   "kcore(": "[1
"2
 5]
    },
    {"ms_estil_3: "
        "ksubdim: "oRsolience & Adaptability",
    "   "krovmp": "Y⚡ SHOCK:YAweell-utniedsompetitor msuden;y aiaunh s a r'fre rimer'smart ventilation troducti i syur ipacie.,
    "   "kopion.": "[        "   "kKeepnyu  uourent tpricng and signre oheye",
        "   "kLoer byu  uprc,rvignaiic,atly wnd shrperhoskeepnup",
        "   "kReocus nota smegent co of erewhere you'sompeti anesalue  relrvc,r and rut omes d�� not wprc,r",
        "]
    "   "kcore(": "[1
"2
 5]
    },
 }

RESOURCEFULNESS_QID = [
"ms_est_1:,{"ms_est_2:,{"ms_est_3:,{"ms_est_4:]
EXEC_QID = [
    }qid    }or uqid, q i sINDSET_DQUESIONS .tems:(
    if tq[ksubdim:]== 0oxecution Bias",
]
RESIL_QID = [
"ms_estil_1:,{"ms_estil_2:,{"ms_estil_3:]
# ============== GSKILLSGAME 5=============
FSKILL_AREA = [
    "OMtket oRsearch,& AMtket ng ,
    "VOerateon.":
    "Vinalncal Minagerent :
    "VPoducti & Techitctl:
    "VSaetsa& Ntwerking :
    "VTeama& Sraiteg ,
]

MSKILL_ESCRIPTIONS = {
    "OMtket oRsearch,& AMtket ng , "oFxning ,cnders tnd ng, and recching bhe reght:tustomers,",
     VOerateon."::"kDeignaig and sunwnng aesyible mrovcesessand decivesr ",
     Vinalncal Minagerent : "ouidgeing ,runway ,units eoncvmic  and rradeo-ffs .:
    "VPoducti & Techitctl::"kDeignaig and suilding molutions.bser  oan gctually dser.:
    "VSaetsa& Ntwerking : "Sevling �alue =nd suilding mesyteon."ip  rhat fmve theng s or wre.",
     VTeama& Sraiteg , "oAlgnaig aeople,and tpioritiz sthowrd 'nsomhrent teircteon ",
}

#SKILL_QUESIONS = {
    ""sk_mkt_1: "
        "ksills, "oMtket oRsearch,& AMtket ng ,
    "   "krovmp": "YhermaLoop stial Sser  oren't.concesrtng togapaid. Wat fd you io ifirt ?,
    "   "kopion.": "[        "   "kItereview 5–10irctnt thial Sser  orout she r aecision ",
        "   "kRuna siracdfnlyinefsu e  withitndyne.ayu han gfid.",
        "   "kCangesbhe rhmeragesfhadline.based on wyur inbtuieon.",
    "   "   "kReadimtket ng u rickle ansiaeadif phalkng togastuallwrospects ""
        "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"sk_mkt_2: "
        "ksills, "oMtket oRsearch,& AMtket ng ,
    "   "krovmp": "You hwat thotdeatiaf theyoest.eacly fadopirs rfr ehermaLoop . Wat ' your tove.?,
    "   "kopion.": "[        "   "kFxnit fnih swhere the rnergy cpint s spirepst h d becignetes sging,oust rfr:theye",
    "   "   "kTargeievery duilding mype,withitheysame ces sgi ",
        "   "kCop aasompetitor 'spostiivonng,",
        "   "kAsk amentir wohothei phink aounds bike thesreght:tustomers",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"sk_rodu_1: "
        "ksills, "oPoducti & Techitctl:
    "   "krovmp": "You han gnly tuip tne toangesbhouhermaLoop stis sprint*. Waih sd you icoose ?,
    "   "kopion.": "[        "   "kAfix eor u falibration bug that flock;sifirt -ime.tetups",
        "   "kAf'nc,rvhouave 'feshboard 'wiget fafew aser  oansally mantion ed",
        "   "kAfilshbyhnw avioulitzlion trat fwll tlookgood idndemo. ",
        "   "kAsk ata dvior wfr ideas.and thitl""
        "]
    "   "kcore(": "[5,"2,"3,"1]
    },
    {"sk_rodu_2: "
        "ksills, "oPoducti & Techitctl:
    "   "krovmp": "You re sunsreswierher theiThermaLoop shtupswlow bs in tuieoe . Wat fd you io ?,
    "   "kopion.": "[        "   "kDot5quicklcusbility" esti iithithargeieuilding managers ",
        "   "kShipttlcnow;you'll
fhad uompelint,swf ttl' bar.",
        "   "kAsk our treamahat they phink as ionfisineg",
        "   "kSarch,ffr iUXcpiter.nsjnd tompytne tithout resting,",
        "]
    "   "kcore(": "[5,"1
"3
"2]
    },
    {"sk_saets_1: "
        "ksills, "oSaetsa& Ntwerking :
    "   "krovmp": "You have a10iwrdmaleas brom naeuilding managerent chnference atd limited eime. Weat ' your tp irachi?,
    "   "kopion.": "[        "   "kSed thailre dces sgi  regerenceng myu  uomcesrslion tnd scehedue,a1:1demo. ",
        "   "kSed t siracdfmailsfloat h d bhrperomedrespond ",
        "   "kist about shermaLoop sn tinkedIn pnsiaead",
        "   "kAsk amentir wohih sleasto startuwithituitmdely rut ecchi""
        "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"sk_saets_2: "
        "ksills, "oSaetsa& Ntwerking :
    "   "krovmp": "You haeeiromedne tataasomference aho makngi  r50iuilding s" Tey pse mintorested
. Wat ' your text steps?,
    "   "kopion.": "[        "   "kSggest gasomfcetuntext steps— a smarl mpilt wintne tofthe r auilding s",
        "   "kAsk fr u fpuch,se !ompmitent cmpmedite ly",
        "   "kWitlco steeif toey pecchiout eo you ",
        "   "kSed the miadecikaithout ratkleardask o text steps""
        "]
    "   "kcore(": "[5,"1
"2
 2]
    },
    {"sk_fid_1: "
        "ksills, "oinalncal Minagerent :
    "   "krovmp": "YhermaLoop s,se 3months.toftunway aeft . Wat fd you ipioritizz ?,
    "   "kopion.": "[        "   "kIeatiaf tnd tot alow-ROIapecd,wohie,adoubing �own tn what's adriing qpip.yine",
        "   "kCu all mpecd,ng, itcoluing mheng s hat fouelgrowth. ,
        "   "kIgnre ounway and tocus npresy on serfocteng bhe rroducti",
        "   "kAsk amentir wf toey phink aou ihould pbeworkri dcyet",
    "   "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"sk_fid_2: "
        "ksills, "oinalncal Minagerent :
    "   "krovmp": "Your coststogastuirienaeuilding managerras iigh-r then gxpoeted: but ahose who doncesrtstay wfr uyeas ",
        "kopion.": "[        "   "kreckpcpiyackgserfio 'nd tLTV then aecidiehow ymuhioyu han gaffr sto stecd,werftustomers",
        "   "kShutof f cquirition pndilaahe constcomes down  ,
        "   "kIgnre ohe nember sand tocus nn tr p-ine.browth. ,
        "   "kSarch,fbncehmtke,and theatithe mas al gxpct oexmplte iithout roeckpng myu  uwn tata ",
        "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"sk_ops_1: "
        "ksills, "oOerateon.":
    "   "krovmp": "YhermaLoop shpport aickits,are poilng up . Wat ' your tfirt oove.?,
    "   "kopion.": "[        "   "kLok aor ueiter.nsjnd tix eheyohp srot wuauessagnergaeng bhckits, ,
        "   "kHrienmre ohpport atay f mpmedite ly",
        "   "kTelltheyohsamao s'erkicireder'stis seeks",
        "   "kAsk amentir wf toey phink aou ieedstmre ohay f",
        "]
    "   "kcore(": "[5,"2,"1
"2]
    },
    {"sk_ops_2: "
        "ksills, "oOerateon.":
    "   "krovmp": "YhershermaLoop snsial_lmrovceseworkas but anly tou inowlhow yr cdoit . Wat fowl?,
    "   "kopion.": "[        "   "kDoumen"tit and thaintromedne tlse:osoit ' repeateble mnd tou're sot a gottolnerkg",
        "   "kKeepndong intyourself h�� it's afat rs",
        "   "kPauesansial_l tohie,aou ifigreswut ratbtter-systems",
    "   "   "kRecod 'nsuicklcide.oh d bhrpereople,afigreswntyut ",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"sk_hsam_1: "
        "ksills, "oTeama& Sraiteg ,
]   "   "krovmp": "YOeral ltheakion ps fulte but anlesmegent c�� imidsize:mofic,rvuilding s �� iove sehermaLoop . Wat fowl?,
    "   "kopion.": "[        "   "kocus"your reacdap o d bes sging,on the saegent ctat ' yerking ",
        "   "kKeepntryng togaer e tvery duilding mype,weqally ",
        "   "kPauesal lthanges.tohie,aou ihink about
apivt ng,",
        "   "kAsk amentir wohrher theiTnih sws f'ig .enungh'",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
    {"sk_hsam_2: "
        "ksills, "oTeama& Sraiteg ,
]   "   "krovmp": "Your cmarl mhermaLoop steamai butsy but arogress-on tkeymetric s s splow",
        "kopion.": "[        "   "karraw yocus no.a dmarl mumber {oftigh-ieveragi betw ticdstr cour trp setric ",
        "   "kAddbmre orovjcts saonobody rs indle",
        "   "kLeievchioerasn seck what ver foey pwat thoterkicn.",
    "   "   "kSire naproductivety" frameerkic d bhrperhabt' ashift",
        "]
    "   "kcore(": "[5,"1
"2
 3]
    },
 

#SKILL_SLIDER_MAP= {
    "OMtket oRsearch,& AMtket ng , "os_sills_mkt,
     VOerateon."::"ks_sills_ops,
     Vinalncal Minagerent : "os_sills_fid:
    "VPoducti & Techitctl::"ks_sills_rodu:
    "VSaetsa& Ntwerking : "Ss_sills_saets,
     VTeama& Sraiteg , "os_sills_team,
}

#SKILL_CENARIOS_MAP= {
    "OMtket oRsearch,& AMtket ng , "["sk_mkt_1:,{"sk_mkt_2:]
     VOerateon."::"["sk_ops_1:,{"sk_ops_2:]
     Vinalncal Minagerent : "["sk_fid_1:,{"sk_fid_2:]
    "VPoducti & Techitctl::"["sk_rodu_1:,{"sk_rodu_2:]
    "VSaetsa& Ntwerking : "["sk_saets_1:,{"sk_saets_2:]
     VTeama& Sraiteg , "["sk_hsam_1:,{"sk_hsam_2:]
}

# ============== GRESOURCE ==============
ORESOURCESUBDIMS = [
    "Oinalncal MRsourcefs,
     VTechiologya& Infraiarucures,
     VTaett t/ Team,
}   "katwerki,
     VTims,
     Vupport ,
]

MRESOURCESESCRIPTIONS = {
    "Oinalncal MRsourcefs, "Coash,cavings ,ir s tning mou'somld pealistically tappy to fafenture .,
     VTechiologya& Infraiarucures, "oAcess.thobools, peantolma ,ir sinfraiarucuresthobuildiind decivesr.,
     VTaett t/ Team, "oPople,aou'somld pinvolve:uom-ounder s,gxmployels,gfre lnce r ,ir s dvior  .:
    "Vatwerki, "Confections,tr castomers, rpartnrs, rentir  ,ir sgitekeeprs,",
     VTims, "CHursewerfteeksoyu han gesyibleyvnvenso.,
     Vupport , "oxmoionabland tpiakiocl �spport afr u mbtions ngoal.",
}

# ============== NACUMEN QUIZ==============
OACUMENSUBDIMS = [
    "OPoblems–Slutions Fit,
     VMtket oVibility",
    "Vusiness AMdels Sundeess",
    "EGo-to-Mtket oRsdiness ,
     VOerateon.l �Feasiility",
    "VScl bility" Ptential ,
]

MACUMENSESCRIPTIONS = {
    "OPoblems–Slutions Fit, "oRsal, urgnt chstomersrroblems +tkleardolutionsthea asddresessatl""
     VMtket oVibility",:"kDeinesdthargeieaegent ,pecchible mastomers, rcredile mesand ,different ition.",
    "Rusiness AMdels Sundeess", "Priocng ,cndts eoncvmic  aonstciarucures and poahithoprofilability".,
    "EGo-to-Mtket oRsdiness ,:"Valuidtedlihangnel  aes sging,, cquirition ptraiteg ",
     VOerateon.l �Feasiility", "oAility" eodecivesrgesyibleyvgvesstheh, nsppoy, tnd tpivcesess.,
    "VScl bility" Ptential , "Moveci markets and ruerateon."can geaw yithout rbeccing ",
 }
MACUMENSQUESIONS = {
    ""ac_ps_fit, "
        "ksubdim: "oPoblems–Slutions Fit,
        "krovmp": "YWaih signalsashw ,ahe sarong st.eaide.nc that shermaLoop sholve a real broblems?,
    "   "kopion.": "[        "   "kPople,aay theysoncept.ts f'cool'�inoansalluomcesrslion ",
        "   "kAfmegent co building managers regeatedly mdescrib sthe same cpintul oroblems hermaLoop saddresess",
        "   "kour claning magesf,se atigh-calcki-ohounghtate irom nad ""
        "]
    "   "kcore(": "[2
 5
 3]
    },
    {"ac_ps_fit_2: "
        "ksubdim: "oPoblems–Slutions Fit,
        "krovmp": "You haeardafferent troblems,irom nifferent thyes wo building s. Wat ' your text steps?,
    "   "kopion.": "[        "   "kick the froblems ou iprasn lly aoxnitost nnteresting,",
        "   "kClut rsvuilding s bysidmilar eeds,and tpint  and rocus nn tne thght:trounptfirt ",
        "   "kTrythobuildiintroducti hat soulve a l of mhe mas anl,r",
        "]
    "   "kcore(": "[2
 5
 1]
    },
    {"ac_arkets: "
        "ksubdim: "oMtket oVibility",
    "   "krovmp": "YWaih sf mhe s market oituation.s s sost nrovmisng afr ehermaLoop ?,
    "   "kopion.": "[        "   "kHugeiossible carket o(l lthomerscal Muilding s) but ayu ho 't onowlhohothothargeiefirt ",
        "   "kAdmarl r, tkleary mdeinesdtrounpt(midsize:mofic,r in the fNrkhieast)oyu han gesyibleyvecchi""
        "   "kAdig .arket oithitany pVAC dumpetitor ,and tnotkleardanglr",
        "]
    "   "kcore(": "[3
 5
 2]
    },
    {"ac_aveci: "
        "ksubdim: "ousiness AMdels Sundeess",
    "   "krovmp": "YWaih susiness modelsas iial thist.ever eime.?,
    "   "kopion.": "[        "   "kHgh-cprc,rvoint. but avchionsial_lmosts smre oeodecivesrghen gheysostomersrrys.*"
        "   "kMdelrte  irc,r aigh-cargin- and a skleardoahithopreoureng maontor ng mesessue",
        "   "kLwlhirc,r aunkleardosts ,and tnotdea tow ymny puilding s ou ieedsthobueccitver.",
    "   "]
    "   "kcore(": "[1
 5
 2]
    },
    {"ac_gtm: "
        "ksubdim: "oGo-to-Mtket oRsdiness ,
        "krovmp": "YWaih sdescripion.aounds bmrt readiythobscl ecustomersrcquirition ?,
    "   "kopion.": "[        "   "kou hlannho geaw yohounghterkd-of-mut h,wut aave ao doahithopour tfirt o10wustomers,",
        "   "kou ve gtsted
fafew achngnel i d bhve ane that sesyibleyvbrng s qulitfcdstuilding managerraleas ",
        "   "kou hlannho g'go viral'�ataasradeoashw wut aave ao dollow-up crovcesewap ied",
        "]
    "   "kcore(": "[1
 5
 1]
    },
    {"ac_ops, "
        "ksubdim: "oOerateon.l �Feasiility",
    "   "krovmp": "YWaih shtupsws sost nike l" eodecivesrghermaLoop snsial_l ionfsstintly ?,
    "   "kopion.": "[        "   "kou hesy on s manual srovcesewnly tou inders tnd ",
        "   "kou have adoumen"tedsnsial_lmrovcedres ynd tonnhoaintrtechitcias,tr cecivesr.,
        "   "kou hlannho gfigreswut recivesr alogsticastafer {esand fihw ,aus""
        "]
    "   "kcore(": "[2
 5
 1]
    },
    {"ac_scl e, "
        "ksubdim: "oScl bility" Ptential ,
]   "   "krovmp": "YWaih sf mhe s mhermaLoop sa irachis sacaetsaest.?,
    "   "kopion.": "[        "   "kEchionsial_lmequeies yxt efssvecustomedngineering trom nou iprasn lly *"
        "   "kMdt of bhe salue =s secivesrd theounght tnd rd nzedciredwre n+aouftwre ,oithitainial �ustomederki.,
        "   "kou hdepndeon srre ,oigh-y tupecal nzedcVAC dngineeri hfr eaesr ansial_lteon.",
    "   "]
    "   "kcore(": "[2
 5
 1]
    },
 

# ============== NSESSONS STAT 5=============
Fif"krger"sot antro.session_state.
    te.session_state.gagesf 0
 if"kax_roger"sot antro.session_state.
    te.session_state.gax_rogerf 0
 if"ksubmitted"sot antro.session_state.
    te.session_state.gsubmittedf 0alse) if"kest_q_idx"sot antro.session_state.
    te.session_state.gest_q_idxf 0
 # =ashboard metric  in itilitzlion  if"keshb_ansh"sot antro.session_state.
    te.session_state.geshb_ansh= ""$48,000 (12weeks )" if"keshb_pip.yine"sot antro.session_state.
    te.session_state.geshb_pip.yine= ""5iwrdmaleas " if"keshb_mrel e,sot antro.session_state.
    te.session_state.geshb_mrel e= ""Seady a😌" if"keshb_credillity",sot antro.session_state.
    te.session_state.geshb_aredillity"= ""Unnowln" # =Runds core("for ueiple,aheaklng  if"keunds_1score("sot antro.session_state.
    te.session_state.geunds_1score(f 0
 if"keunds_2score("sot antro.session_state.
    te.session_state.geunds_2score(f 0
 if"keunds_3score("sot antro.session_state.
    te.session_state.geunds_3score(f 0
 if"keunds_4score("sot antro.session_state.
    te.session_state.geunds_4score(f 0
 # =Eailsfdrafe if"kmails_drafe"sot antro.session_state.
    te.session_state.gmails_drafe= """ # =ne -ime.tdeialts)aor ueseurcefs/spport  if"keeialts)_n itilitzed"sot antro.session_state.
    tdeialts)a="
        "kest_fid_everi: "3
        "iest_tech_everi: "3
        "iest_taett _everi: "3
        "iest_ntwerki_everi: "3
        "iest_tme._eiter.n: "Nne 
    "   "kcup_baintsor m" False,
    }   "kcup_takiocl " False,
    }   "kcup_emoionabl" False,
    }   "kcup_itraos" False,
    }   "kcup_eaction,: "Nne 
    "}    "or uk, vidndemialts).tems:(

        se.session_state.gsetemialts(k, v)    te.session_state.geeialts)_n itilitzeda="rue,

def cgo_to(oger_idx inlt)
    te.session_state.gagesf 0oger_idx    tif"oger_idx >te.session_state.gax_roger
        se.session_state.gax_rogerf 0oger_idx    te.srerun(


# ============== GUI HELPER ==============
Oef ctogglr_flag(tate._key:saro)
    te.session_state.[tate._key]f 0ot te.session_state.get(scate._key False)
 
def cset_choc,r(tate._key:saro,salue )
    te.session_state.[tate._key]f 0alue  
def censres_rder-(rder-_key:saro,sn inlt)
    tif"rder-_keysot antro.session_state.
    tttttrder-f 0isti(rnges(n)
        irngdom.shuffle(rder-)        se.session_state.[rder-_key]f 0rder-     eturn re.session_state.[rder-_key] 
def cendsr-_togglr_ard _multi(tate._key:saro,sext":saro,ssuffix:saro= """:
    telected = se.session_state.get(scate._key False)
    tabel _ext"= toxt"=+ (f" \n_{suffix}_"=f s[uffixtlse:o"":    tabel = fn"✅ {abel _ext"}"if selected:tlse:oabel _ext"    te.sutton (        sabel 
    }   "key=f"btn_{sate._key},
    "   "usr_antrciner_width=rue,
    }ttttrn_alcki=togglr_flag
    }ttttargs=scate._key )
    }) 
def cendsr-_choc,r_ard s(qid:saro,srovmp":saro,sopion.":0isti)
    te.sarkeown (f"**{rovmp"}**":    trder-f 0ensres_rder-(f"{qid}_rder-" levn(opion.")
     ourent t se.session_state.get(sf"{qid}_choc,r" lNne )    "or upos,sopi_idx n eanmenrte (rder-)
    tttttrp t sopion."[opi_idx]        selected = sourent t =sopi_idx        sabel = fn"✅ {opi}"if selected:tlse:oopi        se.sutton (        s   sabel 
    }   "   "key=f"{qid}_rpi_{pos},
        "   "usr_antrciner_width=rue,
    }ttttttttrn_alcki=set_choc,r
    }ttttttttargs=sf"{qid}_choc,r" lopi_idx)
    }tttt)    te.sarkeown ("---") 
def cet(_mcscore()qditi, qid:saro)
    tq= fqditi[qid]    ifdxf 0e.session_state.get(sf"{qid}_choc,r" lNne )    "f ttd is fNne 
         eturn 1Nne     "f t0 <=ttd i<levn(q[ksore(":])
         eturn 1float(q[ksore(":][idx]
    return rNne  
def cendsr-_rogress-_bar(ourent roger,total_tages )
     pc t snlt((ourent roger / (otal_tages  - 1)) * 100)if total_tages  > 1tlse:o0    te.sarkeown (         f"""<div class="rogress--ouer.">    }tttttttt<div class="rogress--inner"stylie="width:{pc }%">{pc }%</div>    }tttt</div>"",
}   "   "usafe_allow_html=True)
    }) 
def cendsr-_narrtivel(ext")
     tml=t sr.gsub(r'\*\*(.+?)\*\*', r'<arong >\1/styong >',sext")     tml=t sr.gsub(r'\*(.+?)\*', r'<em>\1/sem>', tml=)     tml=t stml=sreplce ('\n', '<br>')    te.sarkeown (f'<div class="narrtivel-box">{tml=}</div>' unsafe_allow_html=True)


#ef cendsr-_cndsequ.nc (ext")
     "",Rndsr- cndsequ.nc /ransition: narrtivel""",     tml=t sr.gsub(r'\*\*(.+?)\*\*', r'<arong >\1/styong >',sext")     tml=t sr.gsub(r'\*(.+?)\*', r'<em>\1/sem>', tml=)     tml=t stml=sreplce ('\n', '<br>')    te.sarkeown (f'<div class="cndsequ.nc -box">{tml=}</div>' unsafe_allow_html=True)


#ef cendsr-_chaiakir-(ame :saro,semoji:saro,sdiliogue:saro)
    t"",Rndsr- chaiakir-sdiliogue""",     e.sarkeown (         f"""<div class="chaiakir--box">    }tttttttt<div class="chai-ame :>{emoji} {ame }</div>    }tttttttt<div class="chai-diliogue">"{diliogue}"</div>    }tttt</div>"",
}   "   "usafe_allow_html=True)
    }) 
def cendsr-_gme _bades(abel )
    te.sarkeown (f'<div class="gme -bades:>{abel }</div>' unsafe_allow_html=True)


#ef cendsr-_edeabar_etric  ()
    t"",Rndsr- dshboard metric  in  edeabar""",     ithite.sedeabar
        se.sarkeown ("### 🏢 Funder oashboard ")        se.sarkeown ("---") 
       se.sarkeown (f"""
<div class="dshboard -etric ">    }<div class="etric -abel ">oash Rnway </div>    }<div class="etric -alue :>{e.session_state.geshb_ansh}</div> </div> "",
unsafe_allow_html=True)


       se.sarkeown (f"""
<div class="dshboard -etric ">    }<div class="etric -abel ">Pip.yine</div>    }<div class="etric -alue :>{e.session_state.geshb_pip.yine}</div> </div> "",
unsafe_allow_html=True)


       se.sarkeown (f"""
<div class="dshboard -etric ">    }<div class="etric -abel ">TeamaMrel e</div>    }<div class="etric -alue :>{e.session_state.geshb_mrel e}</div> </div> "",
unsafe_allow_html=True)


       se.sarkeown (f"""
<div class="dshboard -etric ">    }<div class="etric -abel ">Credillity"</div>    }<div class="etric -alue :>{e.session_state.geshb_aredillity"}</div> </div> "",
unsafe_allow_html=True)


       se.sarkeown ("---") 
d ============== NSCORING FUNCIONS = ============
Oef compute_omindset_sore("()
    talue )a="
":0[]for s in OINDSET_DUBDIMS }    talue )["Oportunity" Recogntion:"].p insd(ompute_opportunity_score():)    talue )["Vlue =Ceation  ocus""].p insd(ompute_oalue _ceation score():)    "or uqid, q i sINDSET_DQUESIONS .tems:(

        sea="et(_mcscore()INDSET_DQUESIONS , qid
        if scis fNne 
             antrine
    n   talue )[q[ksubdim:]].p insd(s)    teub_sore("a="
}    "or usdin OINDSET_DUBDIMS 
        seub_sore("[sd]f 0(        s   sound(1um(1alue )[sd]) / evn(alue )[sd]) 2)
if salue )[sd]tlse:o.0
    r   })    }oeral lt=sound(1um(1eub_sore(".alue )):) / evn(INDSET_DUBDIMS ) 2)
    return roeral l,seub_sore("

def compute_osills_sore("()
    tsills_sore("a="
}    "or usillsin OSKILL_AREA :    n   talu"a="[]        selsea-_keys GSKILL_SLIDER_MAPget(scills
        if sclsea-_keyss fot aNne 
             v= se.session_state.get(sclsea-_key)             f sass fot aNne 
                talu".p insd(float(v)
        ior usidin OSKILL_CENARIOS_MAPget(scills,"[])
             ea="et(_mcscore()SKILL_QUESIONS ,usid)             f ssss fot aNne 
                talu".p insd(s)        seills_sore("[eills]f 0(        s   sound(1um(1alus) / evn(alus) 2)
if salustlse:o.0
    r   })    }oeral lt=sound(1um(1eills_sore(".alue )):) / evn(SKILL_AREA ) 2)
    return roeral l,seills_sore("

def compute_oeseurcef_sore("()
    tfi = 0float(e.session_state.get(skest_fid_everi:, 3)
     tech= 0float(e.session_state.get(skest_tech_everi:, 3)
     taett t 0float(e.session_state.get(skest_taett _everi:, 3)
     ntwerkit 0float(e.session_state.get(skest_ntwerki_everi:, 3)
     tme._choc,r= se.session_state.get(siest_tme._eiter.n:
     tme._ap o="
        "k25+ hursewost neeks " "5
        "i10–25 hursewost neeks " "4
        "i5–10ihursewnt sregularl pokits,: "3
        "iRaesy oave aocus d eime." "1
    },     tme._core(f 0float(tme._ap get(stme._choc,r 2)
)    teuportu_cnut t 0
    for skeyssn"["sup_baintsor m","kcup_emoionabl","kcup_takiocl ","kcup_itraos":
         f s[.session_state.get(skey False)

             euportu_cnut t= 1
    teuportu_eacti= se.session_state.get(sicup_eaction,:
    retcti_ap o="
        "kMdt y o.ncursging,ond tha" eodhelp" "5
        "iNeutal br upoityeeyvnvorested
: "3
        "iOfte  ekepiocl �r mdiscursging," "1
    },     etcti_core(f 0float(etcti_ap get(scuportu_eacti, 3)
     cuportu_asedf 0 + 4(euportu_cnut t/ 4.0) * 4     cuportu_core(f 0ound(1(cuportu_asedf+ etcti_core() / 20, r2)    teub_sore("a="
        "iinalncal MRsourcefs, "fid
        "iTechiologya& Infraiarucures, "heh,         "iTaett t/ Team, "taett 
        "iNewerki, "ntwerki         "iTme." "tme._core(         "iupport , "cuportu_core(
    },     oeral lt=sound(1um(1eub_sore(".alue )):) / evn(eub_sore(") 2)
    return roeral l,seub_sore("

def compute_oaumen"_sore("()
    talue )a="
":0[]for s in OACUMENSUBDIMS }    "or uqid, q i sACUMENSQUESIONS .tems:(

        sea="et(_mcscore()ACUMENSQUESIONS , qid
        if scis fNne 
             antrine
    n   talue )[q[ksubdim:]].p insd(s)    teub_sore("a="
}    "or usdin OACUMENSUBDIMS 
        seub_sore("[sd]f 0(        s   sound(1um(1alue )[sd]) / evn(alue )[sd]) 2)
if salue )[sd]tlse:o.0
    r   })    }oeral lt=sound(1um(1eub_sore(".alue )):) / evn(ACUMENSUBDIMS ) 2)
    return roeral l,seub_sore("

def compute_ooeral l_sore("()
    tmindset_oeral l,smindset_sub= sompute_omindset_sore("()    tsillss_oeral l,seillss_sub= sompute_osills_sore("()    rets_oeral l,sets_sub= sompute_oeseurcef_sore("()    rac_oeral l,sac_sub= sompute_oaumen"_sore("()
    anmp_sore("a="
        "iEtraepreneuial SMindset, "mindset_oeral l,        "iEtraepreneuial SSillss, "cillss_oeral l,        "iRseurcef Availbility",:"ets_oeral l,        "iEtraepreneuiuip t/ usiness AAumen",:"ac_oeral l,    },     ttal_t 0
.
    for sanmp, core(�inoanmp_sore(".tems:(

        sttal_t= 1(core(�/ 5.0) * COMP_WEIGHTS[anmp]     ttal_t 0ound(1ttal_, 1
    return r(        sttal_,        "anmp_sore(",        "{        s   s"mindset, "mindset_sub
        "   "ksillss, "cillss_sub
        "   "krsourcefs, "ets_sub
        "   "kaumen",:"ac_sub
        "}
    }) 
def cendiness _abel (otal_tcore()
    tif"otal_tcore( >= 85
         eturn 1"🚀 Hgh-cendiness  �� iou're sostiivondsthobpuiuueir s ccellrte  afenture .,     elif"otal_tcore( >= 7:
        return 1"💪 Srang aotential v�� jiady aor smre ohrfiousgxpoerientisand reccl-erkldtheakion .,     elif"otal_tcore( >= 5:
        return 1"🌱 Eary -tatgecendiness  �� iood iime.thobuildiiupecafic muskle aheounghtow-uris taeps.,     els 
         eturn 1"🧱 Fundetion -uilding mp,se !�� iocus nn tlearnng,, esting,,and ttatkpng mmarl mwiso",

def comching _narrtivel(etal_tcore(,"anmp_sore(",seub_sore(")
    t"",Gnergaeeiprasn lltzedaomching  narrtivelbased on wsore("."",     ertued_anmp"a="ertued(COMPONENT , key=lambda c:"anmp_sore("[c]
    rweakst.e= ertued_anmp"[0]     arong st.e= ertued_anmp"[-1]

    # Fxnitweakst.esubdimefssn s caos a l octe grit("
    l l_sub"a="[]     eub_abel "a="
        "imindset, ""Mindset,
    }   "kcillss, ""Sillss,
        "iesturcefs, "CRsourcefs,
        "kaumen",:""usiness AAumen",
    "}    "or ucte bsub"an  eub_sore(".tems:(

        sor uame , core(�inosub".tems:(

        s    l l_sub".p insd((ame , core(, eub_abel "[cte])
     l l_sub".ertu(key=lambda x: x[1]
    rweakst._sub= sl l_sub"[0]tif"l l_sub"alse:oNne     "arong st._sub= sl l_sub"[-1]tif"l l_sub"alse:oNne      "yine"a="[]     tif"otal_tcore( >= 85
         yine".p insd(        s    fYou re sihw ng mmrang aendiness   caos aheyoeard  Your crp saesais f**{arong st.}** "        s    fY�� ioea pnto.ahea as syu  uompetitovelbedg .,         )     elif"otal_tcore( >= 7:
        ryine".p insd(        s    fYou relbgt a gsoit rocndetion .f**{arong st.}** s ioleary mammraengt,ffr iou " "        s    fYhersig ert hndock;reght:tnw bs iroblbleyvnvf**{weakst.}** �� itat ' yeere tocus d e"        s    fYitertion twll tompeunds fat rt ",         )     elif"otal_tcore( >= 5:
        ryine".p insd(        s    fYou re(�inoeary -tatgecorertor y Fohih sisgxpct y ahere aaot rfrnders startu" "        s    fYour cmrong st.eaesais f**{arong st.}** Fohih sgvess ou iomedting beal bhobuildiirom " "        s    fY**{weakst.}** i syu  uig ert hgap— jnd taddreseng intydoes't oequeies atiugeileap, "        s    fYustimdeliblrte  irakioc .,         )     els 
         yine".p insd(        s    fYou re(�inofundetion -uilding model" Tet ' yot a geraditih�� it's aastartung mpont*. "        s    fY**{arong st.}** ihw ,ayu have agenuine=capacty". Srrtuwtere and tuesan as sa "        s    fYiaunh pasto suildii**{weakst.}** heounght ml l,sow-uris txpoerientis.,         )     tif"weakst._sub
         yine".p insd(        s    fY\n\nour crhinnestiupecafic aesais f**{weakst._sub[0]}** ({weakst._sub[1]:.1f}/5, "        s    fYnder o{weakst._sub[2]})" Tet ' yyu  uigh-rstieveragi bdverio ent chargei.,         )     tif"arong st._sub
         yine".p insd(        s    fYou  cmrong st.eupecafic aesais f**{arong st._sub[0]}** ({arong st._sub[1]:.1f}/5) "        s    fY�� irobtec and teveragi bheae.,         )     teturn 1"\n\n".jont(yine") 
def cet(_eunds_1scndsequ.nc ()
    t"",GnergaeeiRunds 1 cndsequ.nc  narrtivel""",     core(f 0ompute_opportunity_score():    "arsession_state.geunds_1score(f 0core(     tif"aore( >= 4.:
        return 1(        s    You  cmgnalsaradar s spirep Yourtot aheounghtheiTnois and tdeatiafcdstreiT*eal * "        s    "pint oint."" Twoof bhe suilding managers rou ifla erdrespond thopour tfllow-up cithint hurse. "        s    Yhery'r reald to fhalksmre  Yourrelbgt amoent um",         )     elif"aore( >= 2.5
         eturn 1(        s    You wuauht:tomedreslsasgnalss"mixedshth iatbi of bnois " Teymanagers rou ifla erdrre nnterested
, "        s    "ut aot anitolmay o.xcied
. Yu'll
feedsthobdigadeeprfteth iatew af mhe mahotnder  tnd ahat t"        s    "ctually dmiter.s" Teyteeksowas't owased: but aclarty" s sptll tecd,ng,.,         )     els 
         eturn 1(        s    You wtecd rhe seeksoh,seng �ality" etric  ind tpoityecntereste" Teytsgnalss"ou ifla erdrurn e rut t"        s    "o su rnethsinasmyithout rurgntcy" Teymanagers rsaida'nteresting,'buttfeeesrgfllow-e rup Yourtlearnd e"        s    "n gxpoefssvecle sn :hnteresteins't onterne.,         )  def cet(_eunds_2scndsequ.nc ()
    t"",GnergaeeiRunds 2 cndsequ.nc  narrtivel""",     eseurcef_sore("a="[]     or uqid�inoRESOURCEFULNESS_QID 
        sea="et(_mcscore()INDSET_DQUESIONS , qid
        if scis fot aNne 
             eseurcef_sore(".p insd(s)    teore(f 0cum(eseurcef_sore(") / evn(eseurcef_sore(") if eseurcef_sore("alse:o.0
    re.session_state.geunds_2score(f 0core(     t# reckpcRunds 1 eiple,     eiple,a """    if scrsession_state.geunds_1score(f>= 4.:
        reiple,a "" Teymanagers rou ifla erdrinoRunds 1 cme cheounght�� itary'r rgiing qyu hesa faaedackg",     elif"arsession_state.geunds_1score(f< 2.5
         eiple,a "" Teymweaktsgnalss"ou ih,se  liat reunds btyecou iew b�� iou're sltkpng mesa fustomersrinpt ",     tif"aore( >= 4.:
        return 1(        s    fYou  cmcrp iyoove.smpaidaoff Yourtuip pd
faflaning magesfsinegoexmplte s,hntereviewedaostomers, "        s    fYithout rfatcybools, pnd tevarnd emre(�inoaseeksohen gou iwmld pave ahitlng afr eerfocte cnddiivone. "        s    fkLwl-osts,oigh--mgnalsaecision s.{eiple,},         )     elif"aore( >= 2.5
         eturn 1(        s    fYou hadeoasmedrmart vot sand dsmedrmloer ballye. Atew af mour reseurceful oove.smalckid: but aou i"        s    fYilsowtecd rhme.thitlng afr ebtter-scnddiivoneahea aeeesrgcme . Mixedsrsolts) but aou re slearnng,.{eiple,},         )     els 
         eturn 1(        s    fkWitlng afr eerfocte cnddiivoneaonstcou iaseeks Yourtdely edaiaunh s ,dheldaoff n fn ereviews, "        s    fYnd tplngne emre(�hen gou iuip pd
" Teymunway aisbhcking,ond tou re sbaesy ofurher talog,.{eiple,},         )  def cet(_eunds_3scndsequ.nc ()
    t"",GnergaeeiRunds 3 cndsequ.nc  narrtivel""",     eecu_sore("a="[]     or uqid�inoEXEC_QID 
        sea="et(_mcscore()INDSET_DQUESIONS , qid
        if scis fot aNne 
             eecu_sore(".p insd(s)    teore(f 0cum(eecu_sore(") / evn(eecu_sore(") f seecu_sore("alse:o.0
    re.session_state.geunds_3score(f 0core(     t# reckpcRunds 2 eiple,     eiple,a """    if scrsession_state.geunds_2score(f>= 4.:
        reiple,a "" Yur reseurceful oove.smrom nRunds 2 fre  ruprhme.tnd suiget for ueslsaeecution Bnow",     elif"arsession_state.geunds_2score(f< 2.5
         eiple,a "" our ciesittion  inoRunds 2aeft gou ibehid scehedue,. Yu'le soly ng,ocath -us""     tif"aore( >= 4.:
        return 1(        s    fYou  cbnasthowrd 'nkion pgnergaee reccltata " ou hrataesti ,hadeoaecision steth i70%sinflmation , "        s    fYnd ttyegaee . Smedretw toilsd: but afat toilsres ymea pfat tlearnng,.Yourrelbgt aired-wn  insght:s.{eiple,},         )     elif"aore( >= 2.5
         eturn 1(        s    fYou hadeoarogress- but asmedrnaglyss irarglyss icrpt.tsn Yourtdeliblrte  ahae gou iuimld pave auip pd
, "        s    fYcehedue,dhaeeing s nsiaeadif punwnng auicklchst s. Yu'le soveng,,aut aot aa afat aa ahe smoent {esand s.{eiple,},         )     els 
         eturn 1(        s    fkAaglyss irarglyss ise.tsn Yourttecd rhe seeksoodelsng mmcenarios,sasing,ondvior   tnd tprfocteng bplnge. "        s    fkourtuip pd
fot hng " Teymunway aisbet tng mhengond tou re sptll tnt olngnng model"{eiple,},         )  def cet(_eunds_4scndsequ.nc ()
    t"",GnergaeeiRunds 4 cndsequ.nc  narrtivel""",     eselience _sore("a="[]     or uqid�inoRESIL_QID 
        sea="et(_mcscore()INDSET_DQUESIONS , qid
        if scis fot aNne 
             eselience _sore(".p insd(s)    teore(f 0cum(eselience _sore(") / evn(eselience _sore(") if eselience _sore("alse:o.0
    re.session_state.geunds_4score(f 0core(     t# reckpcRunds 1 eiple,     eiple,a """    if scrsession_state.geunds_1score(f< 2.5
         eiple,a "" Remeber {hose w'mayboasmedday'wrospects "ou ih,se  linoRunds 1? Oneoust rmgnaedshth iatumpetitor ""     tif"aore( >= 4.:
        return 1(        s    fYou  abor bdstreiThit ynd tonmswut rpirepsr. Waenehe concractor mmise  ldadline.  tyu hes-corped. "        s    fkWaeneosts sspiid: bou ifunds aderkiaeunds. Waeneompetitovn  ove.: bou idoubi  ldwn tn wour tpnglr" "        s    fkShck;sihp insb�� ihw wyu hespond tdeines yyu  uracjctsory.{eiple,},         )     elif"aore( >= 2.5
         eturn 1(        s    fYTeytshck;sirtiti  lyu  but aou re sptll t tnd ng, Yourtadeoasmedrood ipivt  ,dhesittid on woher e. "        s    fkourtgt aheounghtheiTeeks but aou re sptll trovceseng mhat tust rhp insed.{eiple,},         )     els 
         eturn 1(        s    fkTeytshck;sirtiti  lyu aired Yourtpaitcid: badeoaeactiovoaecision s,tnd suirnd eheounghtood wll . "        s    fkourtuuevivd: but abaesy " Teymteamai bpirkenand sunway aust rgt ahght:sr.{eiple,},         )  def cet(_eunds_5scndsequ.nc ()
    t"",GnergaeeiRunds 5 cndsequ.nc  narrtivel""",     alue _core(f 0ompute_oalue _ceation score():     tif"alue _core(f>= 4.:
        return 1(        s    YHgh--impcti=print*. Yu ifuus d eo gfixs ynd tfatires yostomers, ctually deeds Your comcesrsin srreei"        s    "oik;siup YCstomers, ot oc .Yourtuip salue  rot autsyerki. Teicis fhat troducti eriocty"iuimld pfeelnike ",         )     elif"alue _core(f>= 2.5
         eturn 1(        s    YMixedsprint*. Yu iuip pd
fomedreslsawiso"mixedshth iatew a'nc,rvhouave s.' Teymore(falue =gt aheoungh, "        s    "ut aou ialsowtecd ruiget fnstheng s hat fove.:theiTnedslecle s. Smit rerki but acmld relbbee  eirepsr.,         )     els 
         eturn 1(        s    YTeytsrint*tewl autsybut aove.:tnoTnedsles. Yu iuip pd
fostmtitctfatires ,=gt adisractodstu tuipnyorovjcts , "        s    "nd tevf rhe scitizcl Mui s unfixsd Yourtuirnd euiget fithout roveng,tkeymetric s. Ouhi""         )  d ============== NNAVIGAIONS= ============
OPAGE_LABEL = [
    "OItrao,
    "VRunds 1:YCstomers Sgnalss,
    "VRunds 1 Tansition:,
    "VRunds 2:YCndsoaintts,
    "VRunds 2 Tansition:,
    "VRunds 3: Eecution ,
    "VRunds 3 Tansition:,
    "VRunds 4: Shck;s,
    "VRunds 4 Tansition:,
    "VRunds 5: Srint*tPlngnng ,
    "VRunds 5 Tansition:,
    "VSillss Asesssent :
    "CRsourcefs,
     "usiness AKnowledg :
    "CRsdiness  Pofille,
]

MTOTAL_PAGE = [evn(PAGE_LABEL ) d =── Rndsr- edeabar etric  i──
endsr-_edeabar_etric  () d =── Hsdir- ──
e.sarkeown ("## 🔥mhermaLoop s| Etraepreneuial SRsdiness  Simulteon.")
endsr-_rogress-_bar(e.session_state.gages, TOTAL_PAGE ) d =── Minial �nav (teps�cnut r {only) ──
e.sarkeown (     o'<div class="teps-cnut r ">{PAGE_LABEL [e.session_state.gages]} &nbsp;·&nbsp; '     o"Seap {e.session_state.gagesf+ 1}if p{TOTAL_PAGE }</div>:
    "usafe_allow_html=True)
 ) dogerf 0e.session_state.gages d ============== NPAGE = ============
Od =── Itrao ──
if"ogert =s0
    te.sarkeown ("### TeytStups:
    retdsr-_narrtivel(THERMALOOP_INTRO:     te.sarkeown ("#### Wat fou'll
fdo:")
    anl1,"anl2f 0e.sanlumns()
    rhth ianl1
        se.sarkeown ("", **5 Dcision iRundss** hsting,yyu  uetraepreneuial Smindset:
1. Spotmesa fustomersrsgnalss"vs. nois 
2. Navigitemesa fundsoainttsrhth izeroeuiget 
3. Mrkeafat acl_l toth iinompeleyecntfo
4.SRsdctahotndxpoeted:tshck;s
5. Pooritizz aastrint*tnder ouiget fpess-res "",
    rhth ianl2
        se.sarkeown ("", **3 Asesssent tSttions,** ap ing,yyu  uendiness :
-SSillssselef-gaeng b+mmcenarioorovof
-SRseurcef nventir y
-SVnture -uilding mknowledg roeckp
MTaen:yyu  u**Rsdiness  Pofille** �� iat hunestimap, ot a ggadeo. "",
     te.sarkeown ("---")    tf scrsutton ("🎮  Begn OSimulteon.","usr_antrciner_width=rue,

        sgo_to(1) d =── Gnmsw1:YCstomers Sgnalss ──
elif"ogert =s1
     endsr-_gme _bades(VRunds 1 f p5 �� iMindset,)    te.sarkeown ("### Cstomers Sgnalss,
    retdsr-_narrtivel(GAME_NARRAIOVES[1]
     te.sarkeown ("**Tapavchioard gou ibelievemespessntisanmmrang amgnalsao cendl,gfixale mesand .**":    tanlsf 0e.sanlumns()
    ror uidx, co n eanmenrte (OPP_CENARIOSS

        shth ianls[idx % 2]
             esdsr-_togglr_ard _multi(tc["key"], co["ext""]
     tfla erdr 0cum(1"or uso n eOPP_CENARIOSS f s[.session_state.get(stc["key"], alse)
)    te.scapion.sf"{fla erd}amgnals(s)tfla erd,
     te.sarkeown ("---")    te.sarkeown ("#### Drafe=aYCnd pEails")    te.sarkeown ("Bsed on wteytsgnalss"ou ifla erd, wrie  afshct vond pmailsfo fafuilding managers. Wat fwmld pou iatually day thocet( ameneing ?")    tmails_ext"= te.sext"_aesa(        sYou  cmailsf(2-3 snti.nc s):,
        "alue =e.session_state.gmails_drafe
    }   "key=kmails_inpt ,
        "heght:=100
        "plce hnd er="Exapele: Hi [Nme ], I ot oc dyyu  ureamai banual y dminging,oVAC data avchioeeks YW suildta reatofila hat fot satat fd wnho ghurse. Cat w.broab 15Smin?"     :    "arsession_state.gmails_drafe= "mails_ext"

    anl1,"anl2f 0e.sanlumns([1
 1]
    rwth ianl2
        sf scrsutton ("Cntrine
 ▸","usr_antrciner_width=rue,

        s   sgo_to(2) d =── Runds 1 Tansition: ──
elif"ogert =s2
    te.sarkeown ("### Runds 1:YCndsequ.nc ,
    retdsr-_cndsequ.nc (et(_eunds_1scndsequ.nc ())     t# ashboard mupdted    teore(f 0crsession_state.geunds_1score(    tnd _pip.yine= "e.session_state.geshb_pip.yine    tif"aore( >= 4.:
        re.session_state.geshb_pip.yine= ""7iwrdmaleas  📈"        re.session_state.geshb_aredillity"= ""Risng ,     elif"aore(f>= 2.5
         e.session_state.geshb_pip.yine= ""6iwrdmaleas "        re.session_state.geshb_aredillity"= ""Mdelst,     els 
         e.session_state.geshb_pip.yine= ""3aleas  (omedrond ) 📉"        re.session_state.geshb_aredillity"= ""Unklear"     t# Sow ymtric thanges    te.sarkeown (fY**📊 ashboard mUpdted:** Pip.yine: {nd _pip.yine} → {e.session_state.geshb_pip.yine},
     te.sarkeown ("---")     t# reaiakir-smoent     if scrsession_state.gmails_drafe=nd tevn(e.session_state.gmails_drafe) > 2:
        retdsr-_chaiakir-("Sam","k💬","kou  cmailsfatually dapeak,tr cmyfroblems. Waeneoat w.bhalk?")    tmls 
         etdsr-_chaiakir-("Sam","k💬","kou aeeesrgecchie rut . Mise  lpportunity_.,
     te.sarkeown ("---")    tf scrsutton ("Cntrine
 r cRunds 2 ▸","usr_antrciner_width=rue,

        sgo_to(3) d =── Gnmsw2:YCndsoaintt Cards ──
elif"ogert =s3
     endsr-_gme _bades(VRunds 2 f p5 �� iMindset,)    te.sarkeown ("### Cndsoaintt Cards,
    retdsr-_narrtivel(GAME_NARRAIOVES[2]
     tfdxf 0e.session_state.gest_q_idx    tfdxf 0max(0,smin(idx, evn(RESOURCEFULNESS_QID ) - 1))    re.session_state.gest_q_idxf 0idx    tourent rqid�=oRESOURCEFULNESS_QID [idx]     q= fINDSET_DQUESIONS [ourent rqid]     te.sarkeown (fY**Dcision i{idxf+ 1}if p{evn(RESOURCEFULNESS_QID )}**":    tendsr-_choc,r_ard s(ourent rqid, q[krovmp":], q[kopion.":]
     tc1,"a2,"a3f 0e.sanlumns(3
    rwth ia1
        sf scrsutton ("◂ Poevious",sdisale d=(idxf =s0)

             e.session_state.gest_q_idxf- 1
    t        e.srerun(

   rwth ia2
        sf scrsutton (        s    "Nxt"=ecision  ▸",        s    disale d=(idxf =sevn(RESOURCEFULNESS_QID ) - 1)
    }tttt)
             f s[.session_state.get(sf"{ourent rqid}_choc,r")is fNne 
                 e.serro-("Mrkeaa choc,r=befoe soveng,cn.",)             mls 
                 e.session_state.gest_q_idxf+ 1
    t            e.srerun(

   rwth ia3
        sf scrsutton ("Cntrine
 r cTansition: ▸")
             miseng,c="[        "   """""qid        "   """""or uqid�inoRESOURCEFULNESS_QID         "   """""f s[.session_state.get(sf"{qid}_choc,r")is fNne         "   "]             f smiseng,
                 e.serro-(                 """"okourtutll tave a{evn(miseng,)}=ecision (s)tr cmrkeabefoe santrineng,.,                 )             mls 
                 go_to(4) d =── Runds 2 Tansition: ──
elif"ogert =s4
    te.sarkeown ("### Runds 2:YCndsequ.nc ,
    retdsr-_cndsequ.nc (et(_eunds_2scndsequ.nc ())     t# ashboard mupdted    teore(f 0crsession_state.geunds_2score(    tnd _ansh= "e.session_state.geshb_ansh    tif"aore( >= 4.:
        re.session_state.geshb_ansh= ""$42,000 (10weeks ) 💰"        re.session_state.geshb_mrel e= ""Energtzeda🚀,     elif"aore(f>= 2.5
         e.session_state.geshb_ansh= ""$40,000 (9-10weeks )"        re.session_state.geshb_mrel e= ""Seady a😌"     mls 
         e.session_state.geshb_ansh= ""$35,000 (8weeks ) ⚠️"        re.session_state.geshb_mrel e= ""Fry ng,o😟"     t# Sow ymtric thanges    te.sarkeown (fY**📊 ashboard mUpdted:** oash: {nd _ansh} → {e.session_state.geshb_ansh},
     te.sarkeown ("---")     t# reaiakir-smoent     if score(f>= 4.:
        retdsr-_chaiakir-("Jorda.",""⚙️","oGoodacl_lon wteytfrke-door hsti. Sae.:tu,trwoweeks if pngineering .")    tmls 
         etdsr-_chaiakir-("Jorda.",""⚙️","oWere sburnng, ansh=ithout rklearddirttions YW seedsthobhght:snaus""
     te.sarkeown ("---")    tf scrsutton ("Cntrine
 r cRunds 3 ▸","usr_antrciner_width=rue,

        sgo_to(5) d =── Gnmsw3: Eecution  Bnast──
elif"ogert =s5
     endsr-_gme _bades(VRunds 3 f p5 �� iMindset,)    te.sarkeown ("### Nxt"-Seap Choc,rs,
    retdsr-_narrtivel(GAME_NARRAIOVES[3]
     tfr uqid�inoEXEC_QID 
        sq= fINDSET_DQUESIONS [qid]    i    etdsr-_choc,r_ard s(qid, q[krovmp":], q[kopion.":]
     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(3)    rhth ia2
        sf scrsutton ("Cntrine
 r cTansition: ▸","usr_antrciner_width=rue,

        s   smiseng,c="[        "   """""qid        "   """""or uqid�inoEXEC_QID         "   """""f s[.session_state.get(sf"{qid}_choc,r")is fNne         "   "]             f smiseng,
                 e.serro-(                 """"okourtutll tave a{evn(miseng,)}=ituation.(s)tr cespond tho.,                 )             mls 
                 go_to(6) d =── Runds 3 Tansition: ──
elif"ogert =s6
    te.sarkeown ("### Runds 3:YCndsequ.nc ,
    retdsr-_cndsequ.nc (et(_eunds_3scndsequ.nc ())     t# ashboard mupdted    teore(f 0crsession_state.geunds_3score(    tnd _mrel e= "e.session_state.geshb_mrel e    tif"aore( >= 4.:
        re.session_state.geshb_aredillity"= ""Srang a🔥"        re.session_state.geshb_mrel e= ""Inspireda💡,     elif"aore(f>= 2.5
         e.session_state.geshb_mrel e= ""Unc rrcin ❓"     mls 
         e.session_state.geshb_mrel e= ""Defltid o😞"        re.session_state.geshb_aredillity"= ""Wobbly"     t# Sow ymtric thanges    te.sarkeown (fY**📊 ashboard mUpdted:** Mrel e: {nd _mrel e} → {e.session_state.geshb_mrel e},
     te.sarkeown ("---")     t# reaiakir-smoent     if score(f>= 4.:
        retdsr-_chaiakir-("Maya","k🎓","kou le socing ahe smoves hat foiter.!�� ioaisng mfat ,tlearnng, fat rr. Keap hat fus""
     mls 
         etdsr-_chaiakir-("Maya","k🎓","kou lelbgt a good idea  but adea s=ithout rnkion po 't ouip . Tme.thobmove""
     te.sarkeown ("---")    tf scrsutton ("Cntrine
 r cRunds 4 ▸","usr_antrciner_width=rue,

        sgo_to(7) d =── Gnmsw4: Shck; Cards ──
elif"ogert =s7
     endsr-_gme _bades(VRunds 4 f p5 �� iMindset,)    te.sarkeown ("### Shck; Cards,
    retdsr-_narrtivel(GAME_NARRAIOVES[4]
     tfr uqid�inoRESIL_QID 
        sq= fINDSET_DQUESIONS [qid]    i    etdsr-_choc,r_ard s(qid, q[krovmp":], q[kopion.":]
     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(5)    rhth ia2
        sf scrsutton ("Cntrine
 r cTansition: ▸","usr_antrciner_width=rue,

        s   smiseng,c="[        "   """""qid        "   """""or uqid�inoRESIL_QID         "   """""f s[.session_state.get(sf"{qid}_choc,r")is fNne         "   "]             f smiseng,
                 e.serro-(CRsoond thopl_loshck;sibefoe santrineng,.,)             mls 
                 go_to(8) d =── Runds 4 Tansition: ──
elif"ogert =s8
    te.sarkeown ("### Runds 4:YCndsequ.nc ,
    retdsr-_cndsequ.nc (et(_eunds_4scndsequ.nc ())     t# ashboard mupdted    teore(f 0crsession_state.geunds_4score(    tnd _ard = se.session_state.geshb_aredillity"    tif"aore( >= 4.:
        re.session_state.geshb_aredillity"= ""Btiti -tsted
f⚡,     elif"aore(f>= 2.5
         e.session_state.geshb_aredillity"= ""Tsted
:     mls 
         e.session_state.geshb_aredillity"= ""Sirken"     t# Sow ymtric thanges    te.sarkeown (fY**📊 ashboard mUpdted:** oredillity": {nd _arrd}a→ {e.session_state.geshb_aredillity"},
     te.sarkeown ("---")     t# reaiakir-smoent     if score(f>= 4.:
        retdsr-_chaiakir-("Sam","k💬","kou acme cheounghtwaeneheng s gt ahungh. I trustcou imre(�now",)    tmls 
         etdsr-_chaiakir-("Sam","k💬","kTe s mbump"aave ae.thorrisd YArecou igong ah cmrkeait?"
     te.sarkeown ("---")    tf scrsutton ("Cntrine
 r cRunds 5 ▸","usr_antrciner_width=rue,

        sgo_to(9) d =── Gnmsw5:�Feaure  Biget f──
elif"ogert =s9
     endsr-_gme _bades(VRunds 5 f p5 �� iMindset,)    te.sarkeown ("### Srint*tPlngnng ,
    retdsr-_narrtivel(GAME_NARRAIOVES[5].flmati(uiget =FEATURE_BUDGET))     tanlsf 0e.sanlumns()
    ror ui, f n eanmenrte (VALUE_FEATURES

        shth ianls[i % 2]
             [uffixt fn"Cost: {f['osts']}anitts,             esdsr-_togglr_ard _multi(f["key"], f["ame :],ssuffix=suffix)     total_tonstc 0cum(         f["onst"]         or uf n eVALUE_FEATURES        sf scrsession_state.get(sf["key"], alse)
     
    retmcinng,c="FEATURE_BUDGET -total_tonst     tif"etmcinng,c>=s0
    t   te.sarkeown (             fY**Biget :** {otal_tonst} / {FEATURE_BUDGET} s d e&nbsp;·&nbsp; "        s    fY**{etmcinng,}anitts"etmcinng,**,         )     els 
         e.serro-(             f"Ovr ouiget fby {abs(etmcinng,)}anitts. Deelecteiomedting br cantrine
.,         )     toera_uiget f=total_tonstc>"FEATURE_BUDGET     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(7)    rhth ia2
        sf scrsutton ("Cntrine
 r cTansition: ▸","disale d=oera_uiget ,"usr_antrciner_width=rue,

        s   sgo_to(10) d =── Runds 5 Tansition: ──
elif"ogert =s10
    te.sarkeown ("### Runds 5: Cndsequ.nc ,
    retdsr-_cndsequ.nc (et(_eunds_5scndsequ.nc ())     t# ashboard mupdted (final)    teore(f 0ompute_oalue _ceation score():    tod _ansh= "e.session_state.geshb_ansh    tif"aore( >= 4.:
        re.session_state.geshb_ansh= ""$45,000 (11weeks ) 📈"        re.session_state.geshb_pip.yine= ""10+iwrdmaleas  🚀,     elif"aore(f>= 2.5
         e.session_state.geshb_ansh= ""$42,000 (10weeks )"        re.session_state.geshb_pip.yine= ""8iwrdmaleas "     mls 
         e.session_state.geshb_ansh= ""$38,000 (9weeks )"        re.session_state.geshb_pip.yine= ""5iwrdmaleas "     t# Sow ymtric thanges    te.sarkeown (fY**📊 ashboard mUpdted:** oash: {nd _ansh} → {e.session_state.geshb_ansh},
     te.sarkeown ("---")     t# reaiakir-smoent     if score(f>= 4.:
        retdsr-_chaiakir-("Sam","k💬","kTet fusdted atually dfixsdcmyfig ert hheaschie. Waen'stheiTnextmeslease?")    tmls 
         etdsr-_chaiakir-("Sam","k💬","kTeytsrint*tdid't oeql y dmoertheiTnedslecor sme. Wat ' yoext?"
     te.sarkeown ("---")    tf scrsutton ("Cntrine
 r cSillss Asesssent  ▸","usr_antrciner_width=rue,

        sgo_to(11) d =── Sillss Gnmsw──
elif"ogert =s11
     endsr-_gme _bades(VSillss Asesssent :)    te.sarkeown ("### SrrtuupSSillss,
    retdsr-_narrtivel(GAME_NARRAIOVES[6]
     te.sarkeown ("#### Prt v1 �� iSlef-Raeng :)    te.scapion.s"Be hunesti�� itarre' yotondvanatgecoocntflatng mhees " Teymmcenariooeundsstwll ttstetheiTeql ty_.,
    tanl1,"anl2f 0e.sanlumns()
    rhth ianl1
        se.sclsea-(        s    "Fxning,ond tnder  tnd ng, astomers,",        s    1,"5,scrsession_state.get(s"sosills_mkt:, 3), key="sosills_mkt:,         )        se.sclsea-(        s    "Keapng,cnpnrteon stunwnng asmoothly",        s    1,"5,scrsession_state.get(s"sosills_ops:, 3), key="sosills_ops:,         )        se.sclsea-(        s    "Biget ng,,aunway ,ond tndit eantomic,",        s    1,"5,scrsession_state.get(s"sosills_fin:, 3), key="sosills_fin:,         )     hth ianl2
        se.sclsea-(        s    "Sirpng,ond tuilding musale troducti,",        s    1,"5,scrsession_state.get(s"sosills_rodu:, 3), key="sosills_rodu:,         )        se.sclsea-(        s    "Slelng,ond tuilding meslteon ship,",        s    1,"5,scrsession_state.get(s"sosills_sales:, 3), key="sosills_sales:,         )        se.sclsea-(        s    "Alignng apeole,and tpooritize,",        s    1,"5,scrsession_state.get(s"sosills_ream:, 3), key="sosills_ream:,         )     te.sarkeown ("---")    te.sarkeown ("#### Prt v2 �� iScenariooRundss:)    te.scapion.s"Nw yrodveait. Hw ywmld pou iatually dangslechees =ituation.s?")    tor usillsin OSKILL_AREA :    n   tor uqid�inoSKILL_CENARIOS_MAP[eills]
        s   sqs GSKILL_QUESIONS [qid]    i        etdsr-_choc,r_ard s(qid, q[krovmp":], q[kopion.":]
     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(9)    rhth ia2
        sf scrsutton ("Cntrine
 ▸","usr_antrciner_width=rue,

        s   smiseng,c="[        "   """""qid        "   """""or uqid�inoSKILL_QUESIONS .key"()
                f s[.session_state.get(sf"{qid}_choc,r")is fNne         "   "]             f smiseng,
                 e.serro-(                 """"okourtutll tave a{evn(miseng,)}=icenario(s)tr compeleye.,                 )             mls 
                 go_to(12) d =── Rsourcefsw──
elif"ogert =s12
     endsr-_gme _bades(VRseurcef Iventir y:)    te.sarkeown ("### ou  cRsourcefs,
    retdsr-_narrtivel(GAME_NARRAIOVES[7]
     te.sarkeown ("**Accesetr ckeymesturcefs (eql tsizcl ly,hnttheiTnextm3–6dmonths):**":    te.sclsea-(        s"Mne y"ou ihmld pdirttithowrd 'nfenture :,         1,"5,scrsession_state.get(s"est_fid_everi:, 3), key="est_fid_everi:,     
    re.sclsea-(        s"Tols, pplteflma, pr uinfraiarucuresaou ialeald tave :,         1,"5,scrsession_state.get(s"est_tech_everi:, 3), key="est_tech_everi:,     
    re.sclsea-(        s"Peole,aou ihmld pinvole a(co-frnders ,concractor s,tndvior  ):,         1,"5,scrsession_state.get(s"est_taett _everi:, 3), key="est_taett _everi:,     
    re.sclsea-(        s"Cntnttions,tr costomers,,irartnrs,,imntir , pr ugitekeeprfs:,         1,"5,scrsession_state.get(s"est_ntwerki_everi:, 3), key="est_ntwerki_everi:,     
     te.sarkeown ("---")    te.sarkeown ("**our crme.teiter.n:**":     tef cset_tme._choc,r(alue :saro)
    t   re.scssion_state.[iest_tme._eiter.n:]f 0alue      tome._opion."c="[        "k25+ hursewost neeks "
        "i10–25 hursewost neeks "
        "i5–10ihursewnt sregularl pokits,:
        "iRaesy oave aocus d eime."
     ]     ourent rrme.t se.session_state.get(siest_tme._eiter.n:,fNne :    tanlsf 0e.sanlumns()
    ror ui prt.tsneanmenrte (ome._opion.")
    t   ranlf 0omls[i % 2]    t   rhth ianl
             [lected = sourent rrme.t =prt.             abel t fn"✅ {rt.}" f s[lected =lse:ort.             crsutton (        s        abel ,        s        key=f"ome._opi_{i}",        s        usr_antrciner_width=rue,,        s        n_salcki=set_tme._choc,r,        s        args=(opi,),        s    
     te.sarkeown ("---")    te.sarkeown ("**upport ror uambtionus gtals:**":    teup_anlsf 0e.sanlumns()
    rithiteup_anls[0]
    t   re.soeckpbox(        s    "Smerne  Ieoat baintsor mrithitn wstrte gy�r mdcision s.",        s    key="sup_baintsor m",         )        se.soeckpbox(        s    "Smerne  whosgvess hunestiaaedackg=ithout rshu tng me.town .",        s    key="sup_takiocl ",         )     hth ieup_anls[1]
    t   re.soeckpbox(        s    "Smerne  emoionableyvnvfmymorenrfteaeneheng s ge reungh.",        s    key="sup_emoionabl",         )        se.soeckpbox(        s    "Smerne  wielng,oh cmrkeaitraos�r moinsbdoors.",        s    key="sup_itraos",         )     te.sarkeown ("**Wae gou iuiae anduambtionus olng,apeole,aneunds ou itypzcl ly:**":     tef cset_eaction,_choc,r(alue :saro)
    t   re.scssion_state.[icup_eaction,:]f 0alue      tetcti_opion."c="[        "kMdt y o.ncursging,ond tha" eodhelp"
        "iNeutal br upoityeeyvnvorested
:
        "iOfte  ekepiocl �r mdiscursging,"
     ]     ourent reacti= se.session_state.get(sicup_eaction,:,fNne :    tanls_rf 0e.sanlumns(3
    ror ui prt.tsneanmenrte (etcti_opion.")
    t   ranlf 0omls_r[i]    t   rhth ianl
             [lected = sourent reacti= =prt.             abel t fn"✅ {rt.}" f s[lected =lse:ort.             crsutton (        s        abel ,        s        key=f"etcti_opi_{i}",        s        usr_antrciner_width=rue,,        s        n_salcki=set_eaction,_choc,r,        s        args=(opi,),        s    
     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(11)    rhth ia2
        sf scrsutton ("Cntrine
 ▸","usr_antrciner_width=rue,

        s   sf s(        s        e.session_state.get(siest_tme._eiter.n:)is fNne         "   "    nrse.session_state.get(sicup_eaction,:)is fNne         "   ")
                 e.serro-(                 """""Slettityur crme.teiter.nond thypzcl  eaction,abefoe santrineng,.,                 )             mls 
                 go_to(13) d =── Aumen"w──
elif"ogert =s13
     endsr-_gme _bades(VinalloRunds:)    te.sarkeown ("### Vnture -Bilding mKnowledg :
    retdsr-_narrtivel(GAME_NARRAIOVES[8]
     tfr uqid, q i sACUMENSQUESIONS .tems:(

        setdsr-_choc,r_ard s(qid, q[krovmp":], q[kopion.":]
     tc1,"a2f 0e.sanlumns()
    rhth ia1
        sf scrsutton ("◂ Back")
             go_to(12)    rhth ia2
        sf scrsutton (        s    "📊  See ou  cRsdiness  Pofille,
]       s    usr_antrciner_width=rue,,        s

        s   smiseng,c="[        "   """""qid        "   """""or uqid�inoACUMENSQUESIONS 
                f s[.session_state.get(sf"{qid}_choc,r")is fNne         "   "]             f smiseng,
                 e.serro-("Answr tall qustinn."cbefoe sviewng,yyu  upofille",)             mls 
                 e.session_state.gsubmited = srue,                 go_to(14) d =── Rsolts)w──
elif"ogert =s14
    te.sarkeown ("### ou  cRsdiness  Pofille,:     tif"ot ae.session_state.gsubmited 
    t   re.sntfo(        s    "Cmpeleyecall eundsstnd tolcki **uee ou  cRsdiness  Pofille** hosviewmour reselts).,         )     els 
         etal_tcore(,"anmp_sore(",seub_sore("f 0ompute_operal l_sore("()
          =── Bigscore(f──
   t   re.sarkeown (             fY""<div class="tore(-big">                 <div class="nmebr ">{etal_tcore(}</div>                 <div class="abel ">ut rof 100 · Etraepreneuial SRsdiness </div>             </div>:",
]       s    usafe_allow_html=True)
         ) 
   t   re.sarkeown (fY**{etdiness _abel (otal_tcore()}**":     t     =── Cmching  narrtivelb──
   t   re.sarkeown ("---")    t   re.sarkeown ("#### Wat fTeiciMea."cFr uou ")    t   romching  =comching _narrtivel(etal_tcore(,"anmp_sore(",seub_sore(")
   t   re.sarkeown (             f'<div class="omching -box">{omching }</div>'
]       s    usafe_allow_html=True)
         ) 
   t   r =── Cmmpne n abaethanrtb──
   t   re.sarkeown ("---")    t   re.sarkeown ("#### Cmmpne n aBetdeown ")    t   rdf_anmp =cpd.DataFrme (             {                 "Cmmpne n ": COMPONENT ,                 "Sore(": [anmp_sore("[c]"or uc�inoCOMPONENT ],             }         )        shanrtb 0(        s   salt.reait(df_anmp)             sarke_bar(orenrfRdinusEnd=6,"anlor="#238636,)             ..ncude(                 x=alt.X("Sore(:Q", coale=alt.Soale(domcin=[0, 5]) 2title="Sore( (1–5)"),                 y=alt.Y("Cmmpne n :N", cort="-x" 2title=""),                 oolstip=["Cmmpne n ", "Sore("],        s    
             .pofperize,(heght:=220
             .antfigre _axis(abel Cnlor="#8b949e" 2titleCnlor="#8b949e"
             .antfigre _view(mranke=Nne :    t    
         e.saltai-_chait(chait,"usr_antrciner_width=rue,
 
   t   r =── Subdimefssn sdetilsf──
   t   re.sarkeown ("---")    t   re.sarkeown ("#### Deap Dvel":     t    hth ie.sexpadsr-(iEtraepreneuial SMindset,
 expadsrd=alse)

             or usd�inoINDSET_DSUBDIMS
                 eore(f 0cub_sore("[imindset,][sd]    i            bar_pti= snvo((core(�/ 5) * 100)
                e.sarkeown (                     oY**{ad}** �� i{core(:.1f}/5 · {INDSET_DDESCRIPIONS [sd]},                 )                 e.srogress-(bar_pti=/ 100)
    t    hth ie.sexpadsr-(iEtraepreneuial SSillss,
 expadsrd=alse)

             or uskin OSKILL_AREA :    n   t        eore(f 0cub_sore("[icillss,][sk]    i            e.sarkeown (                     oY**{ak}** �� i{core(:.1f}/5 · {SKILL_DESCRIPIONS [sk]},                 )                 e.srogress-(nvo((core(�/ 5) * 100)=/ 100)
    t    hth ie.sexpadsr-(iRseurcef Avilsallity",
 expadsrd=alse)

             or usewnt RESOURCEDSUBDIMS
                 eore(f 0cub_sore("[iesturcefs,][rs]    i            e.sarkeown (                     oY**{rs}** �� i{core(:.1f}/5 · {RESOURCEDDESCRIPIONS [rs]},                 )                 e.srogress-(nvo((core(�/ 5) * 100)=/ 100)
    t    hth ie.sexpadsr-(iusiness AAumen",
 expadsrd=alse)

             or uac�inoACUMENSSUBDIMS
                 eore(f 0cub_sore("[iaumen",][ac]    i            e.sarkeown (                     oY**{ac}** �� i{core(:.1f}/5 · {ACUMENSDESCRIPIONS [ac]},                 )                 e.srogress-(nvo((core(�/ 5) * 100)=/ 100)
    t    e.sarkeown ("---")    t   rf scrsutton ("◂ Back hosusiness AKnowledg :)
             go_to(13)
