streamlit
import streamlit as st

# --- App Title ---
st.set_page_config(page_title="Normal Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Normal Calculator")
st.write("Perform basic arithmetic operations easily!")

# --- Input Fields ---
num1 = st.number_input("Enter first number:", value=0.0)
num2 = st.number_input("Enter second number:", value=0.0)

# --- Operation Selection ---
operation = st.selectbox(
    "Select Operation:",
    ("Addition", "Subtraction", "Multiplication", "Division")
)

# --- Calculation ---
result = None
if st.button("Calculate"):
    try:
        if operation == "Addition":
            result = num1 + num2
        elif operation == "Subtraction":
            result = num1 - num2
        elif operation == "Multiplication":
            result = num1 * num2
        elif operation == "Division":
            if num2 == 0:
                st.error("❌ Division by zero is not allowed!")
            else:
                result = num1 / num2

        if result is not None:
            st.success(f"✅ Result: {result}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Created with ❤️ using Streamlit")
