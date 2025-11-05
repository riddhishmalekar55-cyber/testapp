import streamlit as st
import random

st.set_page_config(page_title="Fight Game", page_icon="⚔️")

st.title("⚔️ Epic Mini Fight")

# Initialize state
if "player_hp" not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.enemy_hp = 100
    st.session_state.log = []

def log(message):
    st.session_state.log.insert(0, message)

# Display health bars (fixed ✅)
st.subheader("Your Health")
st.progress(max(0, min(1, st.session_state.player_hp / 100)))
st.write(f"❤️ {st.session_state.player_hp}/100")

st.subheader("Enemy Health")
st.progress(max(0, min(1, st.session_state.enemy_hp / 100)))
st.write(f"👹 {st.session_state.enemy_hp}/100")

st.write("---")

# Fight buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗡️ Attack"):
        dmg_to_enemy = random.randint(7, 15)
        dmg_to_player = random.randint(5, 12)

        st.session_state.enemy_hp -= dmg_to_enemy
        st.session_state.player_hp -= dmg_to_player

        log(f"🗡️ You dealt **{dmg_to_enemy} damage**.")
        log(f"👹 Enemy hit back for **{dmg_to_player} damage**.")

with col2:
    if st.button("🛡️ Defend"):
        dmg_to_player = random.randint(1, 6)
        st.session_state.player_hp -= dmg_to_player
        log(f"🛡️ You defended! Took only **{dmg_to_player}** damage.")

with col3:
    if st.button("💖 Heal +12"):
        st.session_state.player_hp = min(100, st.session_state.player_hp + 12)
        log(f"💖 You healed **12 HP**.")

st.write("---")

# Check win/lose
if st.session_state.player_hp <= 0 and st.session_state.enemy_hp <= 0:
    st.error("🤝 It's a draw!")
elif st.session_state.player_hp <= 0:
    st.error("💀 You Lost!")
elif st.session_state.enemy_hp <= 0:
    st.success("🏆 You Won!")

if st.session_state.player_hp <= 0 or st.session_state.enemy_hp <= 0:
    if st.button("🔄 Restart Game"):
        st.session_state.player_hp = 100
        st.session_state.enemy_hp = 100
        st.session_state.log = []
    st.stop()

# Battle Log
st.subheader("🎬 Battle Log")
for entry in st.session_state.log[:8]:
    st.write(entry)
