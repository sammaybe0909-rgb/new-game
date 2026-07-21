
import copy
import html
import random

import streamlit as st


st.set_page_config(
    page_title="BioCard Game",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GAME DATA
# =========================================================

STATIONS = ['Farm', 'Stage 1', 'Stage 2', 'Harvest', 'Transportation', 'Biorefinery']

FARMS = {'Pacific Northwest Farm': {'resists': ['Wildfire'],
                            'description': 'Reduces wildfire losses by 2 trees.'},
 'Midwest Farm': {'resists': ['Tornado', 'Blizzard'],
                  'description': 'Reduces tornado and blizzard losses by 2 trees.'},
 'Western Farm': {'resists': ['Drought', 'Heat Wave'],
                  'description': 'Reduces drought and heat-wave losses by 2 trees.'},
 'Southern Farm': {'resists': ['Flood', 'Hurricane'],
                   'description': 'Reduces flood and hurricane losses by 2 trees.'}}

DIFFICULTIES = {'Easy': {'starting_trees': 10,
          'turn_limit': 18,
          'required_trees': 20,
          'failed_turn_limit': 4,
          'event_every': 2,
          'event_count': 1,
          'description': '10 starting trees. One major dilemma every two turns. 18-turn limit. '
                         'Lower tree requirements for advancement.'},
 'Medium': {'starting_trees': 8,
            'turn_limit': 14,
            'required_trees': 24,
            'failed_turn_limit': 3,
            'event_every': 1,
            'event_count': 1,
            'description': '8 starting trees. One dilemma every turn. 14-turn limit. Moderate tree '
                           'requirements for advancement.'},
 'Hard': {'starting_trees': 7,
          'turn_limit': 11,
          'required_trees': 28,
          'failed_turn_limit': 2,
          'event_every': 1,
          'event_count': 2,
          'description': '7 starting trees. Two dilemmas every turn. 11-turn limit. High tree '
                         'requirements for advancement.'}}

ADVANCE_REQUIREMENTS = {'Easy': {'Farm': 10,
          'Stage 1': 12,
          'Stage 2': 14,
          'Harvest': 16,
          'Transportation': 18,
          'Biorefinery': 20},
 'Medium': {'Farm': 10,
            'Stage 1': 13,
            'Stage 2': 16,
            'Harvest': 19,
            'Transportation': 22,
            'Biorefinery': 24},
 'Hard': {'Farm': 10,
          'Stage 1': 14,
          'Stage 2': 18,
          'Harvest': 22,
          'Transportation': 26,
          'Biorefinery': 28}}

DICE_YIELDS = {'Switchgrass': {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2},
 'Poplar Trees': {1: -2, 2: -1, 3: 1, 4: 1, 5: 3, 6: 4},
 'Corn Stover': {1: -2, 2: 0, 3: 2, 4: 2, 5: 3, 6: 3}}

PLANTS = {'Switchgrass': {'icon': 'SW',
                 'summary': 'Reliable and resilient',
                 'details': 'Reduces negative results by 1 tree.'},
 'Poplar Trees': {'icon': 'PT',
                  'summary': 'Slow start, stronger later',
                  'details': 'First use gets -1; later uses earn a growing bonus.'},
 'Corn Stover': {'icon': 'CS',
                 'summary': 'Strong early, weaker later',
                 'details': 'First use gets +2, second +1, then repeated use declines.'}}

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

SUIT_SYMBOLS = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}

RANKS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

NORMAL_CONDITIONS = {'name': 'Normal Growing Conditions',
 'description': 'No major disaster occurs this turn. Choose which feedstock you want to develop '
                'while conditions are stable.',
 'outcomes': {'Switchgrass': 2, 'Poplar Trees': 2, 'Corn Stover': 3},
 'lesson': 'Different biomass feedstocks balance reliability, establishment time, and short-term '
           'availability.'}

DILEMMAS = {'Farm': [{'name': 'Drought',
           'description': 'Low rainfall threatens establishment of the first crop.',
           'outcomes': {'Switchgrass': 1, 'Poplar Trees': -2, 'Corn Stover': -2},
           'lesson': 'Perennial grasses can tolerate dry conditions better than newly established '
                     'trees or annual-crop systems.'},
          {'name': 'Flood',
           'description': 'Heavy rain saturates the fields and delays planting.',
           'outcomes': {'Switchgrass': 0, 'Poplar Trees': 1, 'Corn Stover': -2},
           'lesson': 'Flooding can delay field operations and reduce annual crop yield.'},
          {'name': 'Tornado',
           'description': 'A tornado damages newly prepared farm areas.',
           'outcomes': {'Switchgrass': -1, 'Poplar Trees': -2, 'Corn Stover': -2},
           'lesson': 'Extreme weather can damage standing biomass and farm infrastructure.'}],
 'Stage 1': [{'name': 'Heat Wave',
              'description': 'Extreme temperatures stress the growing feedstock.',
              'outcomes': {'Switchgrass': 1, 'Poplar Trees': -1, 'Corn Stover': -2},
              'lesson': 'Heat stress affects crops differently depending on species and growth '
                        'stage.'},
             {'name': 'Invasive Species',
              'description': 'A pest begins damaging the biomass crop.',
              'outcomes': {'Switchgrass': 0, 'Poplar Trees': -2, 'Corn Stover': -1},
              'lesson': 'Feedstock diversity reduces the chance that one pest harms the entire '
                        'biomass supply.'},
             {'name': 'Excellent Rainfall',
              'description': 'Moderate temperatures and steady rainfall improve growth.',
              'outcomes': {'Switchgrass': 2, 'Poplar Trees': 3, 'Corn Stover': 3},
              'lesson': 'Favorable weather can improve biomass yield across several feedstocks.'}],
 'Stage 2': [{'name': 'Wildfire',
              'description': 'A wildfire threatens the available biomass.',
              'outcomes': {'Switchgrass': -1, 'Poplar Trees': -4, 'Corn Stover': -2},
              'lesson': 'Woody feedstocks may store more standing biomass, but that biomass can '
                        'also be exposed to wildfire.'},
             {'name': 'Blizzard',
              'description': 'Freezing temperatures interrupt growth and field access.',
              'outcomes': {'Switchgrass': 0, 'Poplar Trees': -1, 'Corn Stover': -2},
              'lesson': 'Cold weather affects harvest timing, access, and moisture conditions.'},
             {'name': 'Soil Nutrient Decline',
              'description': 'Repeated biomass removal begins reducing soil quality.',
              'outcomes': {'Switchgrass': 1, 'Poplar Trees': 2, 'Corn Stover': -2},
              'lesson': 'Removing too much crop residue can reduce soil cover and nutrient '
                        'recycling.'}],
 'Harvest': [{'name': 'Early Frost',
              'description': 'An early frost arrives before the planned harvest.',
              'outcomes': {'Switchgrass': 1, 'Poplar Trees': -1, 'Corn Stover': 0},
              'lesson': 'Harvest timing affects yield, moisture, and feedstock quality.'},
             {'name': 'Labor Shortage',
              'description': 'Too few workers and machines are available for harvest.',
              'outcomes': {'Switchgrass': 0, 'Poplar Trees': 1, 'Corn Stover': -2},
              'lesson': 'Feedstocks have different harvest windows and equipment requirements.'},
             {'name': 'Ideal Harvest Conditions',
              'description': 'Dry weather creates an excellent harvest window.',
              'outcomes': {'Switchgrass': 3, 'Poplar Trees': 4, 'Corn Stover': 3},
              'lesson': 'Good harvest conditions reduce losses and preserve usable biomass.'}],
 'Transportation': [{'name': 'Road Closure',
                     'description': 'A major route to the biorefinery is unavailable.',
                     'outcomes': {'Switchgrass': -1, 'Poplar Trees': 0, 'Corn Stover': -2},
                     'lesson': 'Low-density biomass can become expensive to move over long '
                               'distances.'},
                    {'name': 'Wet Feedstock',
                     'description': 'Rain increases feedstock moisture and hauling weight.',
                     'outcomes': {'Switchgrass': 0, 'Poplar Trees': -1, 'Corn Stover': -2},
                     'lesson': 'Moisture increases transportation weight and can lower conversion '
                               'efficiency.'},
                    {'name': 'Efficient Rail Access',
                     'description': 'A nearby rail route lowers transportation losses.',
                     'outcomes': {'Switchgrass': 2, 'Poplar Trees': 2, 'Corn Stover': 3},
                     'lesson': 'Transportation infrastructure can improve the value of biomass '
                               'feedstocks.'}],
 'Biorefinery': [{'name': 'Equipment Failure',
                  'description': 'A processing unit fails during biomass conversion.',
                  'outcomes': {'Switchgrass': -1, 'Poplar Trees': -2, 'Corn Stover': -1},
                  'lesson': 'Reliable conversion equipment is necessary to turn biomass into '
                            'energy.'},
                 {'name': 'Feedstock Quality Problem',
                  'description': 'Moisture and particle size vary more than expected.',
                  'outcomes': {'Switchgrass': 1, 'Poplar Trees': 0, 'Corn Stover': 1},
                  'lesson': 'Consistent feedstock quality helps a biorefinery operate '
                            'efficiently.'},
                 {'name': 'High Bioenergy Demand',
                  'description': 'Demand for renewable energy increases sharply.',
                  'outcomes': {'Switchgrass': 3, 'Poplar Trees': 3, 'Corn Stover': 4},
                  'lesson': 'Market demand can increase the value of multiple biomass '
                            'feedstocks.'}]}


# =========================================================
# APPEARANCE
# =========================================================

CSS = """
<style>
    html, body, [data-testid="stAppViewContainer"] {
        color-scheme: light !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, rgba(164, 210, 155, 0.22), transparent 28rem),
            linear-gradient(180deg, #fbfaf3 0%, #f3f7ec 100%);
        color: #263d23 !important;
    }

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp div[data-testid="stMarkdownContainer"] {
        color: #263d23;
    }

    .hero,
    .hero p,
    .hero h1,
    .hero h2,
    .hero h3,
    .hero span {
        color: white !important;
    }

    section[data-testid="stSidebar"] {
        background: #f4f1df !important;
    }

    section[data-testid="stSidebar"] * {
        color: #263d23;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input,
    textarea {
        background: white !important;
        color: #263d23 !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color: #263d23 !important;
    }

    div[data-testid="stNotification"] p,
    div[data-testid="stNotification"] span,
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: #263d23 !important;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #31572c 0%, #4f772d 55%, #90a955 100%);
        color: white;
        border-radius: 24px;
        padding: 2.3rem 2rem;
        text-align: center;
        box-shadow: 0 18px 45px rgba(49, 87, 44, 0.20);
        margin-bottom: 1.3rem;
    }

    .hero h1 {
        font-family: Georgia, serif;
        font-size: clamp(2.5rem, 6vw, 4.8rem);
        margin: 0;
        letter-spacing: 0.03em;
    }

    .hero p {
        font-size: 1.15rem;
        margin: 0.65rem 0 0;
        opacity: 0.94;
    }

    .panel {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #d8e2cc;
        border-radius: 18px;
        padding: 1.2rem 1.35rem;
        box-shadow: 0 10px 30px rgba(60, 90, 50, 0.08);
        margin-bottom: 1rem;
    }

    .dilemma {
        background: #fff8dc;
        border: 2px solid #e6ca77;
        border-radius: 18px;
        padding: 1.15rem 1.35rem;
        text-align: center;
        box-shadow: 0 10px 24px rgba(120, 91, 20, 0.08);
        margin: 0.9rem 0 1rem;
    }

    .dilemma .eyebrow {
        color: #7a5c00;
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .dilemma h2 {
        color: #654321;
        font-family: Georgia, serif;
        margin: 0.25rem 0 0.4rem;
    }

    .stage-card {
        min-height: 112px;
        padding: 0.8rem 0.4rem;
        border-radius: 14px;
        border: 2px solid #d5ddcf;
        background: #ffffff;
        text-align: center;
        box-shadow: 0 6px 16px rgba(50, 80, 45, 0.06);
    }

    .stage-card.active {
        background: #dff0d8;
        border-color: #4f772d;
        box-shadow: 0 8px 22px rgba(79, 119, 45, 0.18);
    }

    .stage-card.complete {
        background: #edf5e8;
        border-color: #90a955;
    }

    .stage-index {
        width: 28px;
        height: 28px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        background: #31572c;
        color: white;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .stage-name {
        font-weight: 800;
        color: #263d23 !important;
        line-height: 1.1;
        font-size: 0.82rem;
        white-space: nowrap;
        letter-spacing: -0.02em;
    }

    .stage-name.long-stage {
        font-size: 0.68rem;
        letter-spacing: -0.045em;
    }

    .status-card {
        min-height: 76px;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #cfdcc8;
        border-radius: 14px;
        padding: 0.65rem 0.45rem;
        text-align: center;
        box-shadow: 0 6px 16px rgba(49, 87, 44, 0.07);
        margin-bottom: 0.65rem;
    }

    .status-label {
        color: #60705b !important;
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.045em;
        line-height: 1.15;
        margin-bottom: 0.25rem;
    }

    .status-value {
        color: #263d23 !important;
        font-size: 0.98rem;
        font-weight: 850;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .stage-need {
        color: #62715e;
        font-size: 0.78rem;
        margin-top: 0.4rem;
    }

    .playing-card {
        width: min(100%, 420px);
        min-height: 180px;
        margin: 0.5rem auto 1rem;
        background: white;
        border: 4px solid #263238;
        border-radius: 18px;
        padding: 1rem 1.25rem;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.12);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .playing-card.placeholder {
        border-style: dashed;
        border-color: #a9b4a5;
        color: #778273;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.15rem;
    }

    .card-rank {
        font-family: Georgia, serif;
        font-weight: 900;
        font-size: 1.4rem;
    }

    .card-suit {
        text-align: center;
        font-size: 4rem;
        line-height: 1;
    }

    .card-name {
        text-align: center;
        font-weight: 800;
        font-size: 1.1rem;
    }

    .red-card {
        color: #b3261e;
    }

    .black-card {
        color: #171717;
    }

    .plant-card {
        min-height: 245px;
        background: white;
        border: 2px solid #d8e2cc;
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 10px 24px rgba(49, 87, 44, 0.08);
        margin-bottom: 0.6rem;
    }

    .plant-icon {
        width: 58px;
        height: 58px;
        margin: 0 auto 0.65rem;
        border-radius: 16px;
        background: #31572c;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 1.1rem;
    }

    .plant-card h3 {
        font-family: Georgia, serif;
        margin: 0.2rem 0;
        color: #31572c;
    }

    .plant-card .summary {
        font-weight: 700;
        color: #596a54;
    }

    .plant-card .details {
        color: #657260;
        font-size: 0.92rem;
        min-height: 4.2rem;
    }

    .die-face {
        width: 190px;
        height: 190px;
        margin: 0.8rem auto;
        border: 5px solid #202020;
        border-radius: 28px;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 8.3rem;
        line-height: 1;
        box-shadow: 0 16px 35px rgba(0, 0, 0, 0.15);
    }

    .flow-row {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
        margin: 0.7rem 0 1rem;
    }

    .flow-step {
        border-radius: 14px;
        background: #eef5e8;
        border: 1px solid #ccd9c5;
        padding: 0.7rem 0.35rem;
        text-align: center;
        min-height: 95px;
    }

    .flow-step .icon {
        font-size: 1.55rem;
    }

    .flow-step strong {
        display: block;
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }

    .result-box {
        border-radius: 18px;
        padding: 1.25rem;
        white-space: pre-line;
        background: #eef5e8;
        border: 2px solid #a9c99d;
        font-weight: 700;
        font-size: 1.08rem;
        text-align: center;
    }

    @media (max-width: 800px) {
        .flow-row {
            grid-template-columns: 1fr;
        }

        .stage-card {
            min-height: 96px;
        }

        .stage-name {
            font-size: 0.72rem;
        }

        .stage-name.long-stage {
            font-size: 0.58rem;
        }

        .status-label {
            font-size: 0.64rem;
        }

        .status-value {
            font-size: 0.86rem;
        }
    }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# STATE AND CORE LOGIC
# =========================================================

def create_deck():
    cards = [
        {"rank": rank, "suit": suit}
        for suit in SUITS
        for rank in RANKS
    ]
    random.shuffle(cards)
    return cards


def fresh_player():
    return {
        "name": "",
        "farm": "",
        "station": 0,
        "trees": 8,
        "plant_uses": {
            "Switchgrass": 0,
            "Poplar Trees": 0,
            "Corn Stover": 0,
        },
    }


def fresh_game():
    return {
        "difficulty": "Medium",
        "turn": 0,
        "failed_turns": 0,
        "current_dilemmas": [],
        "dilemma_index": 0,
        "current_card": None,
        "last_plant": None,
        "turn_tree_change": 0,
        "last_result": "",
        "last_lesson": "",
        "die_roll": None,
        "die_change": 0,
        "die_message": "",
        "gate_message": "",
        "lose_reason": "",
    }


def initialize_state():
    defaults = {
        "screen": "menu",
        "player": fresh_player(),
        "game": fresh_game(),
        "deck": create_deck(),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(value)


def restart_to_menu():
    st.session_state.screen = "menu"
    st.session_state.player = fresh_player()
    st.session_state.game = fresh_game()
    st.session_state.deck = create_deck()
    st.rerun()


def current_stage():
    return STATIONS[st.session_state.player["station"]]


def current_settings():
    difficulty = st.session_state.game["difficulty"]
    return DIFFICULTIES[difficulty]


def required_trees_for_current_stage():
    difficulty = st.session_state.game["difficulty"]
    return ADVANCE_REQUIREMENTS[difficulty][current_stage()]


def draw_playing_card():
    if not st.session_state.deck:
        st.session_state.deck = create_deck()

    return st.session_state.deck.pop()


def card_strength(rank):
    if rank in ["Ace", "2", "3", "4", "5"]:
        return 1
    if rank in ["6", "7", "8", "9", "10"]:
        return 2
    return 3


def card_modifier(card):
    strength = card_strength(card["rank"])

    if card["suit"] == "Hearts":
        return strength
    if card["suit"] == "Diamonds":
        return max(1, strength - 1)
    if card["suit"] == "Clubs":
        return -strength
    return -(strength + 1)


def plant_modifier(plant_name, base_result):
    player = st.session_state.player
    uses = player["plant_uses"][plant_name]
    result = base_result
    note = ""

    if plant_name == "Switchgrass":
        if result < 0:
            result += 1
            note = "Switchgrass resilience reduced the loss by 1 tree."

    elif plant_name == "Poplar Trees":
        if uses == 0:
            result -= 1
            note = "New poplar needed time to establish: -1 tree."
        else:
            bonus = min(2, uses)
            result += bonus
            note = f"Established poplar added a +{bonus} tree bonus."

    elif plant_name == "Corn Stover":
        if uses == 0:
            result += 2
            note = "First corn-stover use received a +2 tree bonus."
        elif uses == 1:
            result += 1
            note = "Second corn-stover use received a +1 tree bonus."
        else:
            penalty = min(2, uses - 1)
            result -= penalty
            note = f"Repeated residue removal caused a -{penalty} tree penalty."

    return result, note


def farm_resistance_bonus(dilemma_name, result):
    player = st.session_state.player
    farm_data = FARMS[player["farm"]]

    if dilemma_name in farm_data["resists"] and result < 0:
        improved = min(0, result + 2)
        prevented = improved - result
        return improved, f"{player['farm']} prevented {prevented} tree loss."

    return result, ""


def get_current_dilemma():
    game = st.session_state.game
    return game["current_dilemmas"][game["dilemma_index"]]


def production_die_change(plant_name, roll):
    return DICE_YIELDS[plant_name][roll]


def set_loss(reason):
    st.session_state.game["lose_reason"] = reason
    st.session_state.screen = "lose"


def prepare_turn():
    game = st.session_state.game
    settings = current_settings()

    if game["turn"] >= settings["turn_limit"]:
        set_loss("You ran out of time before reaching the biorefinery.")
        return

    game["turn"] += 1
    game["dilemma_index"] = 0
    game["current_card"] = None
    game["last_plant"] = None
    game["turn_tree_change"] = 0
    game["die_roll"] = None
    game["die_change"] = 0
    game["die_message"] = ""
    game["gate_message"] = ""

    if (
        game["difficulty"] == "Easy"
        and game["turn"] % settings["event_every"] != 0
    ):
        selected = [NORMAL_CONDITIONS]
    else:
        available = DILEMMAS[current_stage()]
        count = min(settings["event_count"], len(available))
        selected = random.sample(available, count)

    game["current_dilemmas"] = selected
    st.session_state.screen = "dilemma"


def start_game(name, farm, difficulty):
    cleaned_name = name.strip()
    if not cleaned_name:
        st.warning("Please enter a player name.")
        return

    settings = DIFFICULTIES[difficulty]

    st.session_state.player = {
        "name": cleaned_name,
        "farm": farm,
        "station": 0,
        "trees": settings["starting_trees"],
        "plant_uses": {
            "Switchgrass": 0,
            "Poplar Trees": 0,
            "Corn Stover": 0,
        },
    }
    st.session_state.game = fresh_game()
    st.session_state.game["difficulty"] = difficulty
    st.session_state.deck = create_deck()
    prepare_turn()
    st.rerun()


def resolve_plant_choice(plant_name):
    player = st.session_state.player
    game = st.session_state.game
    dilemma = get_current_dilemma()
    card = game["current_card"]

    if card is None:
        return

    base_result = dilemma["outcomes"][plant_name]
    plant_result, plant_note = plant_modifier(plant_name, base_result)
    farm_result, farm_note = farm_resistance_bonus(
        dilemma["name"],
        plant_result,
    )
    card_change = card_modifier(card)
    final_change = farm_result + card_change

    player["plant_uses"][plant_name] += 1
    game["last_plant"] = plant_name
    player["trees"] = max(0, player["trees"] + final_change)
    game["turn_tree_change"] += final_change

    if final_change > 0:
        change_text = f"Gain {final_change} trees."
    elif final_change < 0:
        change_text = f"Lose {abs(final_change)} trees."
    else:
        change_text = "No trees gained or lost."

    result_lines = [
        f"You chose {plant_name}.",
        f"Playing card: {card['rank']} of {card['suit']} ({card_change:+d})",
        change_text,
    ]
    if plant_note:
        result_lines.append(plant_note)
    if farm_note:
        result_lines.append(farm_note)

    game["last_result"] = "\n".join(result_lines)
    game["last_lesson"] = dilemma["lesson"]
    game["current_card"] = None

    if player["trees"] <= 0:
        set_loss("Your biomass supply collapsed to zero trees.")
    else:
        st.session_state.screen = "choice_result"

    st.rerun()


def continue_after_choice():
    game = st.session_state.game
    game["dilemma_index"] += 1

    if game["dilemma_index"] < len(game["current_dilemmas"]):
        game["current_card"] = None
        st.session_state.screen = "dilemma"
    else:
        if game["last_plant"] is None:
            set_loss("No plant was selected for the production die.")
        else:
            game["die_roll"] = None
            game["die_change"] = 0
            game["die_message"] = ""
            game["gate_message"] = ""
            st.session_state.screen = "dice"

    st.rerun()


def roll_production_die():
    player = st.session_state.player
    game = st.session_state.game
    plant_name = game["last_plant"]
    required = required_trees_for_current_stage()

    roll = random.randint(1, 6)
    change = production_die_change(plant_name, roll)

    player["trees"] = max(0, player["trees"] + change)
    game["turn_tree_change"] += change
    game["die_roll"] = roll
    game["die_change"] = change

    if change > 0:
        game["die_message"] = f"{plant_name} produced +{change} trees."
    elif change < 0:
        game["die_message"] = f"{plant_name} lost {abs(change)} trees."
    else:
        game["die_message"] = f"{plant_name} produced no additional trees."

    if current_stage() == "Biorefinery":
        if player["trees"] >= required:
            game["gate_message"] = (
                f"You have {player['trees']} trees, enough to operate the biorefinery."
            )
        else:
            game["gate_message"] = (
                f"You have {player['trees']} trees, but the biorefinery requires {required}."
            )
    elif player["trees"] >= required:
        next_stage = STATIONS[player["station"] + 1]
        game["gate_message"] = (
            f"Requirement met: {player['trees']}/{required}. "
            f"You will advance to {next_stage}."
        )
    else:
        game["gate_message"] = (
            f"Requirement not met: {player['trees']}/{required}. "
            f"You will remain at {current_stage()}."
        )

    st.rerun()


def finalize_turn():
    player = st.session_state.player
    game = st.session_state.game
    settings = current_settings()
    required = required_trees_for_current_stage()

    if player["trees"] <= 0:
        set_loss("Your biomass supply collapsed to zero trees.")
        st.rerun()

    if game["turn_tree_change"] < 0:
        game["failed_turns"] += 1
    else:
        game["failed_turns"] = 0

    if game["failed_turns"] >= settings["failed_turn_limit"]:
        set_loss(
            f"You suffered {settings['failed_turn_limit']} losing turns in a row."
        )
        st.rerun()

    if current_stage() == "Biorefinery":
        if player["trees"] >= required:
            st.session_state.screen = "win"
        else:
            set_loss(
                "The biorefinery could not operate because you finished with "
                f"fewer than {required} trees."
            )
        st.rerun()

    if player["trees"] >= required:
        player["station"] += 1

    if game["turn"] >= settings["turn_limit"]:
        set_loss("You reached the turn limit before completing the journey.")
        st.rerun()

    prepare_turn()
    st.rerun()


# =========================================================
# SHARED UI
# =========================================================

def render_hero():
    st.markdown(
        """
        <div class="hero">
            <h1>BIOCARD GAME</h1>
            <p>Draw a card. Choose a plant. Roll the production die.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rules_sidebar():
    with st.sidebar:
        st.title("📖 Quick Rules")
        st.caption("These rules stay open while you play.")

        st.markdown(
            """
            <div class="flow-row">
                <div class="flow-step"><div class="icon">❓</div><strong>Dilemma</strong></div>
                <div class="flow-step"><div class="icon">♥♣</div><strong>Draw card</strong></div>
                <div class="flow-step"><div class="icon">🌱</div><strong>Choose plant</strong></div>
                <div class="flow-step"><div class="icon">🎲</div><strong>Roll die</strong></div>
                <div class="flow-step"><div class="icon">🌳</div><strong>Check trees</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Turn order", expanded=True):
            st.markdown(
                """
                1. Read the stage dilemma.
                2. Draw from the 52-card deck.
                3. Choose a plant card.
                4. Apply the dilemma, farm, plant, and card effects.
                5. Roll the production die.
                6. Meet the tree requirement to advance.
                """
            )

        with st.expander("Playing cards"):
            st.markdown(
                """
                - **♥ Hearts** and **♦ Diamonds** usually help.
                - **♣ Clubs** and **♠ Spades** usually hurt.
                - Higher ranks create stronger effects.
                """
            )

        with st.expander("Plant cards"):
            st.markdown(
                """
                - **Switchgrass:** reduces negative results.
                - **Poplar Trees:** weak first use, stronger later.
                - **Corn Stover:** strong early, declines with repetition.
                """
            )

        with st.expander("Production die"):
            st.markdown(
                """
                **Switchgrass:** 1–2 = 0, 3–4 = +1, 5–6 = +2  
                **Poplar:** 1 = −2, 2 = −1, 3–4 = +1, 5 = +3, 6 = +4  
                **Corn Stover:** 1 = −2, 2 = 0, 3–4 = +2, 5–6 = +3
                """
            )

        with st.expander("Difficulty"):
            st.markdown(
                """
                - **Easy:** major dilemma every two turns.
                - **Medium:** one dilemma each turn.
                - **Hard:** two dilemmas each turn.
                """
            )

        with st.expander("Ways to lose"):
            st.markdown(
                """
                - Trees reach zero.
                - The turn limit is exceeded.
                - Too many losing turns happen in a row.
                - The biorefinery requirement is not met.
                """
            )

        st.divider()
        if st.button("↻ Restart game", use_container_width=True):
            restart_to_menu()


def render_status():
    player = st.session_state.player
    game = st.session_state.game
    settings = current_settings()

    status_items = [
        ("Current stage", current_stage()),
        ("Trees available", player["trees"]),
        ("Trees required", required_trees_for_current_stage()),
        ("Turn number", f"{game['turn']} of {settings['turn_limit']}"),
        (
            "Losing turns",
            f"{game['failed_turns']} of {settings['failed_turn_limit']}",
        ),
    ]

    columns = st.columns(len(status_items))

    for column, (label, value) in zip(columns, status_items):
        column.markdown(
            f"""
            <div class="status-card">
                <div class="status-label">{html.escape(str(label))}</div>
                <div class="status-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_progress():
    player = st.session_state.player
    difficulty = st.session_state.game["difficulty"]
    columns = st.columns(len(STATIONS))

    for index, (column, stage) in enumerate(zip(columns, STATIONS)):
        if index == player["station"]:
            state_class = "active"
        elif index < player["station"]:
            state_class = "complete"
        else:
            state_class = ""

        requirement = ADVANCE_REQUIREMENTS[difficulty][stage]
        stage_name_class = (
            "stage-name long-stage"
            if stage == "Transportation"
            else "stage-name"
        )

        column.markdown(
            f"""
            <div class="stage-card {state_class}">
                <div class="stage-index">{index + 1}</div>
                <div class="{stage_name_class}">{html.escape(stage)}</div>
                <div class="stage-need">Need {requirement} trees</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_playing_card(card):
    if card is None:
        st.markdown(
            """
            <div class="playing-card placeholder">
                Draw a playing card
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    suit = card["suit"]
    symbol = SUIT_SYMBOLS[suit]
    color_class = "red-card" if suit in ["Hearts", "Diamonds"] else "black-card"

    st.markdown(
        f"""
        <div class="playing-card {color_class}">
            <div class="card-rank">{html.escape(card['rank'])}</div>
            <div class="card-suit">{symbol}</div>
            <div class="card-name">{html.escape(suit)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rules_content():
    st.header("How to Play")
    st.markdown(
        """
        ### One turn at a glance

        **❓ Dilemma → ♥ Draw card → 🌱 Choose plant → 🎲 Roll die → 🌳 Check trees**

        ### Turn order

        1. Read the current stage-based dilemma.
        2. Draw one card from the shuffled 52-card deck.
        3. Choose Switchgrass, Poplar Trees, or Corn Stover.
        4. Combine the dilemma, farm resistance, plant ability, and playing card.
        5. Roll the production die.
        6. Meet the current stage's tree requirement to advance.

        ### Difficulty

        - **Easy:** one major dilemma every two turns.
        - **Medium:** one dilemma every turn.
        - **Hard:** two dilemmas every turn.

        ### Ways to lose

        - Your trees reach zero.
        - You exceed the turn limit.
        - You have too many losing turns in a row.
        - You cannot meet the biorefinery requirement.
        """
    )

    st.subheader("Tree requirements")
    header = "| Difficulty | " + " | ".join(STATIONS) + " |"
    divider = "|---" * (len(STATIONS) + 1) + "|"
    rows = []
    for difficulty in ["Easy", "Medium", "Hard"]:
        values = [
            str(ADVANCE_REQUIREMENTS[difficulty][stage])
            for stage in STATIONS
        ]
        rows.append(
            f"| {difficulty} | " + " | ".join(values) + " |"
        )
    st.markdown("\n".join([header, divider, *rows]))


# =========================================================
# SCREENS
# =========================================================

def screen_menu():
    render_hero()

    st.markdown(
        """
        <div class="panel">
            <h3 style="margin-top:0;color:#31572c;">Build a resilient bioenergy supply</h3>
            <p>
                Travel from the farm to the biorefinery. Every turn combines a
                stage dilemma, a standard playing card, a strategic plant choice,
                and a production die.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([1, 1, 1])

    with middle:
        if st.button(
            "▶ Start game",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.screen = "setup"
            st.rerun()

        if st.button(
            "📖 Full rules",
            use_container_width=True,
        ):
            st.session_state.screen = "rules"
            st.rerun()


def screen_rules():
    rules_content()
    if st.button("← Back to menu"):
        st.session_state.screen = "menu"
        st.rerun()


def screen_setup():
    st.header("Create Your Farm")

    st.markdown(
        """
        <div class="panel">
            Choose a farm and difficulty. The information below updates
            immediately when you change either option.
        </div>
        """,
        unsafe_allow_html=True,
    )

    name = st.text_input(
        "Player name",
        placeholder="Enter your name",
        key="setup_player_name",
    )

    farm = st.selectbox(
        "Choose your farm",
        options=list(FARMS.keys()),
        key="setup_farm",
    )

    farm_data = FARMS[farm]
    resisted_events = ", ".join(farm_data["resists"])
    st.success(
        f"**{farm}**\n\n"
        f"{farm_data['description']}\n\n"
        f"Resists: **{resisted_events}**"
    )

    difficulty = st.selectbox(
        "Choose difficulty",
        options=list(DIFFICULTIES.keys()),
        index=1,
        key="setup_difficulty",
    )

    difficulty_data = DIFFICULTIES[difficulty]
    st.info(
        f"**{difficulty} mode**\n\n"
        f"{difficulty_data['description']}\n\n"
        f"Starting trees: **{difficulty_data['starting_trees']}**  \n"
        f"Turn limit: **{difficulty_data['turn_limit']}**  \n"
        f"Allowed losing turns: **{difficulty_data['failed_turn_limit']}**"
    )

    st.subheader(f"{difficulty} tree requirements")
    requirement_columns = st.columns(len(STATIONS))

    for column, stage in zip(requirement_columns, STATIONS):
        requirement = ADVANCE_REQUIREMENTS[difficulty][stage]
        stage_name_class = (
            "stage-name long-stage"
            if stage == "Transportation"
            else "stage-name"
        )

        column.markdown(
            f"""
            <div class="stage-card">
                <div class="{stage_name_class}">{html.escape(stage)}</div>
                <div class="stage-need">Need {requirement} trees</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button(
        "Begin journey",
        type="primary",
        use_container_width=True,
    ):
        start_game(name, farm, difficulty)

    if st.button("← Back to menu"):
        st.session_state.screen = "menu"
        st.rerun()


def screen_dilemma():
    player = st.session_state.player
    game = st.session_state.game
    dilemma = get_current_dilemma()

    render_status()
    render_progress()

    total = len(game["current_dilemmas"])
    number = game["dilemma_index"] + 1
    eyebrow = (
        f"Dilemma {number} of {total}"
        if total > 1
        else "This turn's dilemma"
    )

    st.markdown(
        f"""
        <div class="dilemma">
            <div class="eyebrow">{html.escape(eyebrow)}</div>
            <h2>{html.escape(dilemma['name'])}</h2>
            <div>{html.escape(dilemma['description'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_playing_card(game["current_card"])

    if game["current_card"] is None:
        if st.button(
            "Draw playing card",
            type="primary",
            use_container_width=True,
        ):
            game["current_card"] = draw_playing_card()
            st.rerun()
        st.caption(f"{len(st.session_state.deck)} cards remain in the deck.")
        return

    st.subheader("Choose one plant card")
    plant_columns = st.columns(3)

    for column, plant_name in zip(plant_columns, PLANTS):
        plant = PLANTS[plant_name]
        uses = player["plant_uses"][plant_name]

        with column:
            st.markdown(
                f"""
                <div class="plant-card">
                    <div class="plant-icon">{html.escape(plant['icon'])}</div>
                    <h3>{html.escape(plant_name)}</h3>
                    <div class="summary">{html.escape(plant['summary'])}</div>
                    <p class="details">{html.escape(plant['details'])}</p>
                    <strong>Used {uses} time(s)</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Play {plant_name}",
                key=f"plant_{game['turn']}_{game['dilemma_index']}_{plant_name}",
                use_container_width=True,
            ):
                resolve_plant_choice(plant_name)


def screen_choice_result():
    game = st.session_state.game
    player = st.session_state.player

    st.header("Dilemma Result")
    st.markdown(
        f"""
        <div class="result-box">{html.escape(game['last_result'])}</div>
        """,
        unsafe_allow_html=True,
    )

    st.metric("Current trees", player["trees"])

    st.info(f"**Bioeconomy note:** {game['last_lesson']}")

    more_dilemmas = (
        game["dilemma_index"] + 1
        < len(game["current_dilemmas"])
    )

    if more_dilemmas:
        label = "Next dilemma"
    else:
        label = "Roll production die"

    if st.button(label, type="primary", use_container_width=True):
        continue_after_choice()


def screen_dice():
    game = st.session_state.game
    player = st.session_state.player
    plant_name = game["last_plant"]
    required = required_trees_for_current_stage()

    render_status()
    render_progress()

    st.header("Roll the Production Die")
    st.write(
        f"**Production plant:** {plant_name}  \n"
        f"**Current trees:** {player['trees']}  \n"
        f"**Needed at {current_stage()}:** {required}"
    )

    profiles = {
        "Switchgrass": "1–2: +0 · 3–4: +1 · 5–6: +2",
        "Poplar Trees": "1: −2 · 2: −1 · 3–4: +1 · 5: +3 · 6: +4",
        "Corn Stover": "1: −2 · 2: +0 · 3–4: +2 · 5–6: +3",
    }
    st.caption(profiles[plant_name])

    die_symbols = {
        1: "⚀",
        2: "⚁",
        3: "⚂",
        4: "⚃",
        5: "⚄",
        6: "⚅",
    }

    die_display = die_symbols.get(game["die_roll"], "🎲")
    st.markdown(
        f'<div class="die-face">{die_display}</div>',
        unsafe_allow_html=True,
    )

    if game["die_roll"] is None:
        if st.button(
            "Roll production die",
            type="primary",
            use_container_width=True,
        ):
            roll_production_die()
    else:
        st.success(
            f"You rolled **{game['die_roll']}**. "
            f"{game['die_message']}"
        )
        st.info(game["gate_message"])

        if st.button(
            "Continue",
            type="primary",
            use_container_width=True,
        ):
            finalize_turn()


def screen_win():
    player = st.session_state.player
    game = st.session_state.game

    st.balloons()
    st.success("## You Win!")
    st.markdown(
        f"""
        <div class="panel" style="text-align:center;">
            <h2 style="color:#31572c;">The biorefinery is operating!</h2>
            <p><strong>{html.escape(player['name'])}</strong> completed the journey.</p>
            <h1>🌳 {player['trees']} trees</h1>
            <p>Difficulty: {html.escape(game['difficulty'])}<br>
            Turns used: {game['turn']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Play again",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.screen = "setup"
        st.session_state.player = fresh_player()
        st.session_state.game = fresh_game()
        st.session_state.deck = create_deck()
        st.rerun()

    if st.button("Main menu", use_container_width=True):
        restart_to_menu()


def screen_lose():
    player = st.session_state.player
    game = st.session_state.game

    st.error("## Game Over")
    st.markdown(
        f"""
        <div class="panel" style="text-align:center;">
            <h3 style="color:#8b2f2f;">{html.escape(game['lose_reason'])}</h3>
            <p>
                Trees remaining: <strong>{player['trees']}</strong><br>
                Stage reached: <strong>{html.escape(current_stage())}</strong><br>
                Turns used: <strong>{game['turn']}</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Try again",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.screen = "setup"
        st.session_state.player = fresh_player()
        st.session_state.game = fresh_game()
        st.session_state.deck = create_deck()
        st.rerun()

    if st.button("Main menu", use_container_width=True):
        restart_to_menu()


# =========================================================
# APP ROUTER
# =========================================================

initialize_state()
render_rules_sidebar()

SCREENS = {
    "menu": screen_menu,
    "rules": screen_rules,
    "setup": screen_setup,
    "dilemma": screen_dilemma,
    "choice_result": screen_choice_result,
    "dice": screen_dice,
    "win": screen_win,
    "lose": screen_lose,
}

screen_function = SCREENS.get(
    st.session_state.screen,
    screen_menu,
)
screen_function()
