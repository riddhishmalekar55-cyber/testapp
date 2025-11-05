import streamlit as st
import random

st.title("⚔️ Simple Fight Game")

# Initialize the game state
if "player_hp" not in st.session_state:
    st.session_state.player_hp = 100
    st.session_state.enemy_hp = 100

# Show HP
st.write(f"**Your HP:** {st.session_state.player_hp}")
st.write(f"**Enemy HP:** {st.session_state.enemy_hp}")

# Fight buttons
if st.button("Attack"):
    player_damage = random.randint(5, 15)
    enemy_damage = random.randint(3, 12)

    st.session_state.enemy_hp -= player_damage
    st.session_state.player_hp -= enemy_damage

    st.write(f"🗡️ You dealt **{player_damage}** damage!")
    st.write(f"👹 Enemy dealt **{enemy_damage}** damage back!")

# Heal button
if st.button("Heal +10"):
    st.session_state.player_hp += 10
    st.write("💖 You healed **10 HP**!")

# Check winner
if st.session_state.player_hp <= 0 and st.session_state.enemy_hp <= 0:
    st.write("🤝 It's a draw!")
    st.button("Play Again", on_click=lambda: st.session_state.update(player_hp=100, enemy_hp=100))

elif st.session_state.player_hp <= 0:
    st.write("💀 You Lost!")
    st.button("Try Again", on_click=lambda: st.session_state.update(player_hp=100, enemy_hp=100))

elif st.session_state.enemy_hp <= 0:
    st.write("🏆 You Won!")
    st.button("Play Again", on_click=lambda: st.session_state.update(player_hp=100, enemy_hp=100))
