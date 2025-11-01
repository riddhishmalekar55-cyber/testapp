import streamlit as st
import math

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

st.title("🧮 Scientific Calculator")
st.write("Perform scientific and arithmetic calculations easily!")

# --- Number Inputs ---
num1 = st.number_input("Enter first number:", value=0.0)
num2 = st.number_input("Enter second number (if needed):", value=0.0)

# --- Operation Selection ---
operation = st.selectbox(
    "Select Operation:",
    (
        "Addition", "Subtraction", "Multiplication", "Division",
        "Power", "Square Root", "Logarithm (base 10)",
        "Sine", "Cosine", "Tangent",
        "Factorial"
    )
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
        elif operation == "Power":
            result = math.pow(num1, num2)
        elif operation == "Square Root":
            if num1 < 0:
                st.error("❌ Cannot take square root of a negative number!")
            else:
                result = math.sqrt(num1)
        elif operation == "Logarithm (base 10)":
            if num1 <= 0:
                st.error("❌ Logarithm undefined for zero or negative numbers!")
            else:
                result = math.log10(num1)
        elif operation == "Sine":
            result = math.sin(math.radians(num1))
        elif operation == "Cosine":
            result = math.cos(math.radians(num1))
        elif operation == "Tangent":
            result = math.tan(math.radians(num1))
        elif operation == "Factorial":
            if num1 < 0 or not float(num1).is_integer():
                st.error("❌ Factorial is only defined for non-negative integers!")
            else:
                result = math.factorial(int(num1))

        # Show result if available
        if result is not None:
            st.success(f"✅ Result: {result}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- Footer ---
st.markdown("---")
st.caption("Created with ❤️ using Streamlit | Scientific Calculator")
