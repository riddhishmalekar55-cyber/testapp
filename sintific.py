import streamlit as st
import math

# --- Page Setup ---
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS for better visuals ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #e3f2fd, #ffffff);
            color: #000;
        }
        .main-title {
            text-align: center;
            color: #1e88e5;
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sub-title {
            text-align: center;
            color: #424242;
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        .result-box {
            background-color: #bbdefb;
            color: #0d47a1;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 1.3em;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<p class="main-title">🧮 Scientific Calculator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Perform arithmetic and scientific calculations easily</p>', unsafe_allow_html=True)

# --- Layout ---
col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("Enter first number:", value=0.0)
with col2:
    num2 = st.number_input("Enter second number (if needed):", value=0.0)

st.markdown("### ⚙️ Choose Operation")

# Operation grouping
basic_ops = ["Addition", "Subtraction", "Multiplication", "Division", "Power"]
sci_ops = [
    "Square Root", "Logarithm (base 10)",
    "Sine", "Cosine", "Tangent", "Factorial"
]

operation_type = st.radio("Select Category", ("Basic", "Scientific"), horizontal=True)
if operation_type == "Basic":
    operation = st.selectbox("Select Basic Operation:", basic_ops)
else:
    operation = st.selectbox("Select Scientific Operation:", sci_ops)

# --- Calculation ---
result = None

if st.button("🔢 Calculate", use_container_width=True):
    try:
        # BASIC OPERATIONS
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

        # SCIENTIFIC OPERATIONS
        elif operation == "Square Root":
            if num1 < 0:
                st.error("❌ Cannot take square root of negative number!")
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

        if result is not None:
            st.markdown(f"<div class='result-box'>✅ Result: {result}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- Footer ---
st.markdown("---")
st.caption("💡 Created with ❤️ using Streamlit | Enhanced Scientific Calculator")
