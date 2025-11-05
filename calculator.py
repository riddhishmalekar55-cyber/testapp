# app.py
import streamlit as st
import random
import time

st.set_page_config(page_title="Tiny Fight Game", page_icon="⚔️", layout="wide")

# ---------- Helper functions ----------
def new_game():
    st.session_state.player = {
        "name": st.session_state.get("player_name", "Hero"),
        "class": st.session_state.get("player_class", "Warrior"),
        "max_hp": 120,
        "hp": 120,
        "atk": 18,
        "def": 6,
        "special_ready": True,
        "potions": 2,
    }
    cls = st.session_state.player["class"]
    if cls == "Warrior":
        st.session_state.player.update({"max_hp": 140, "hp": 140, "atk": 16, "def": 9})
    elif cls == "Mage":
        st.session_state.player.update({"max_hp": 100, "hp": 100, "atk": 24, "def": 4})
    elif cls == "Rogue":
        st.session_state.player.update({"max_hp": 110, "hp": 110, "atk": 20, "def": 5})
    # enemy
    st.session_state.enemy = {
        "name": random.choice(["Goblin", "Orc", "Bandit", "Warlock"]),
        "max_hp": random.randint(90, 150),
        "hp": 0,
        "atk": random.randint(12, 22),
        "def": random.randint(3, 8),
        "special_ready": True
    }
    st.session_state.enemy["hp"] = st.session_state.enemy["max_hp"]
    st.session_state.turn = "player"
    st.session_state.log = [
        f"🌟 New game started! You are a {st.session_state.player['class']}. Enemy: {st.session_state.enemy['name']} (HP {st.session_state.enemy['max_hp']})."
    ]
    st.session_state.game_over = False

def push_log(msg):
    st.session_state.log.insert(0, msg)  # newest first
    # Keep log to reasonable size
    if len(st.session_state.log) > 40:
        st.session_state.log = st.session_state.log[:40]

def damage(attacker_atk, defender_def, multiplier=1.0, guaranteed=False):
    base = max(1, int(attacker_atk * multiplier) - defender_def)
    var = random.randint(0, int(base * 0.35))
    dmg = base + var
    if guaranteed:
        return max(1, dmg)
    return dmg

def enemy_decision():
    # Very simple AI: prefer attack, sometimes use special or heal (if implemented)
    e = st.session_state.enemy
    p = st.session_state.player
    if e["hp"] < e["max_hp"] * 0.25 and random.random() < 0.45:
        return "defend"
    if e["special_ready"] and random.random() < 0.22:
        return "special"
    return "attack"

def check_end():
    p = st.session_state.player
    e = st.session_state.enemy
    if p["hp"] <= 0:
        st.session_state.game_over = True
        push_log(f"💀 You were defeated by the {e['name']}...")
        return True
    if e["hp"] <= 0:
        st.session_state.game_over = True
        push_log(f"🏆 You defeated the {e['name']}! Congratulations!")
        return True
    return False

def do_player_action(action):
    if st.session_state.game_over:
        return
    p = st.session_state.player
    e = st.session_state.enemy

    if action == "attack":
        dmg = damage(p["atk"], e["def"])
        e["hp"] -= dmg
        push_log(f"🗡️ {p['name']} attacks {e['name']} for {dmg} damage.")
    elif action == "defend":
        # defend reduces incoming damage this turn
        st.session_state.player_defending = True
        push_log(f"🛡️ {p['name']} assumes a defensive stance (less damage incoming this turn).")
    elif action == "special":
        if not p["special_ready"]:
            push_log("✨ Special not ready!")
        else:
            cls = p["class"]
            if cls == "Warrior":
                dmg = damage(p["atk"], e["def"], multiplier=2.0, guaranteed=True)
                e["hp"] -= dmg
                push_log(f"💥 {p['name']} (Warrior) performs a mighty strike for {dmg} damage!")
            elif cls == "Mage":
                dmg = damage(p["atk"] + 6, e["def"], multiplier=2.2)
                e["hp"] -= dmg
                push_log(f"🔥 {p['name']} (Mage) casts Fire Blast for {dmg} damage!")
            elif cls == "Rogue":
                dmg = damage(p["atk"], e["def"], multiplier=2.0)
                e["hp"] -= dmg
                push_log(f"🎯 {p['name']} (Rogue) lands a precision critical for {dmg} damage!")
            p["special_ready"] = False
    elif action == "heal":
        if p["potions"] <= 0:
            push_log("🍶 No potions left!")
        else:
            heal_amt = int(p["max_hp"] * 0.28) + random.randint(0, 8)
            p["hp"] = min(p["max_hp"], p["hp"] + heal_amt)
            p["potions"] -= 1
            push_log(f"🍶 {p['name']} drinks a potion and recovers {heal_amt} HP.")
    # after player action, check
    if check_end():
        return
    # enemy turn happens immediately after player's action
    st.session_state.turn = "enemy"
    time.sleep(0.18)
    do_enemy_turn()

def do_enemy_turn():
    e = st.session_state.enemy
    p = st.session_state.player
    if st.session_state.game_over:
        return
    choice = enemy_decision()
    if choice == "attack":
        # check if player is defending
        if st.session_state.get("player_defending", False):
            effective_def = p["def"] + 6
        else:
            effective_def = p["def"]
        dmg = damage(e["atk"], effective_def)
        p["hp"] -= dmg
        push_log(f"👹 {e['name']} attacks {p['name']} for {dmg} damage.")
    elif choice == "defend":
        st.session_state.enemy_defending = True
        push_log(f"👹 {e['name']} takes a defensive stance.")
    elif choice == "special":
        # enemy special: heavy hit or buff
        if random.random() < 0.55:
            dmg = damage(e["atk"] + 8, p["def"])
            p["hp"] -= dmg
            push_log(f"💢 {e['name']} uses a dark rush for {dmg} damage!")
        else:
            e["atk"] += 4
            push_log(f"💪 {e['name']} powered up (attack increased).")
        e["special_ready"] = False

    # reset defending status (only for one enemy->player cycle)
    st.session_state.player_defending = False
    st.session_state.enemy_defending = False

    if check_end():
        return
    st.session_state.turn = "player"

# ---------- Initialize session state ----------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.player_name = "Hero"
    st.session_state.player_class = "Warrior"
    st.session_state.player_defending = False
    st.session_state.enemy_defending = False
    new_game()

# ---------- Layout ----------
col1, col2 = st.columns([2, 1])

with col1:
    st.title("⚔️ Tiny Fight: Streamlit Edition")
    st.markdown("A tiny turn-based fight game. Choose your class, then use actions to defeat the enemy!")

    # Top: Player + Enemy status cards
    status_cols = st.columns(2)
    with status_cols[0]:
        p = st.session_state.player
        st.subheader(f"Player — {p['name']} ({p['class']})")
        st.progress(min(1.0, max(0.0, p["hp"] / p["max_hp"])))
        st.write(f"HP: {p['hp']} / {p['max_hp']}")
        st.write(f"ATK: {p['atk']}  |  DEF: {p['def']}")
        st.write(f"Potions: {p['potions']}")
        st.write(f"Special Ready: {'✅' if p['special_ready'] else '⌛'}")

    with status_cols[1]:
        e = st.session_state.enemy
        st.subheader(f"Enemy — {e['name']}")
        st.progress(min(1.0, max(0.0, e["hp"] / e["max_hp"])))
        st.write(f"HP: {e['hp']} / {e['max_hp']}")
        st.write(f"ATK: {e['atk']}  |  DEF: {e['def']}")
        st.write(f"Special Ready: {'✅' if e['special_ready'] else '⌛'}")

    st.markdown("---")

    # Action buttons
    if st.session_state.game_over:
        st.info("Game over. Use the 'Restart' button in the sidebar to play again.")
    else:
        action_cols = st.columns(4)
        if action_cols[0].button("Attack"):
            do_player_action("attack")
        if action_cols[1].button("Defend"):
            do_player_action("defend")
        if action_cols[2].button("Special"):
            do_player_action("special")
        if action_cols[3].button("Heal"):
            do_player_action("heal")

    st.markdown("---")
    # Turn log
    st.subheader("Battle Log")
    for entry in st.session_state.log[:12]:
        st.write(entry)

with col2:
    st.sidebar.title("Game Controls")
    st.sidebar.text_input("Player name", key="player_name")
    st.sidebar.selectbox("Choose class", options=["Warrior", "Mage", "Rogue"], key="player_class")
    if st.sidebar.button("Start / Restart Game"):
        new_game()

    st.sidebar.markdown("---")
    st.sidebar.write("⚙️ Advanced")
    st.sidebar.write("- Enemy difficulty is randomized each game.")
    st.sidebar.write("- Specials are single-use per game for both sides.")

    st.sidebar.markdown("---")
    st.sidebar.write("Tips:")
    st.sidebar.markdown("""
    - Warriors are tanky; use Special for big guaranteed damage.  
    - Mages deal high damage but have low HP.  
    - Rogues rely on burst criticals.  
    - Use Heal when HP is low (potions are limited).
    """)

st.markdown("---")
st.caption("Made with ❤️ using Streamlit. Feel free to fork and expand!")

# Auto-save changes to session (optional)
