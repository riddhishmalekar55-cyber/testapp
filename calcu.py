import streamlit as st

st.title("🧮 Simple Calculator")

# Input numbers
a = st.number_input("Enter first number", value=0.0)
b = st.number_input("Enter second number", value=0.0)

# Select operation
option = st.radio("Choose operation", ("Add", "Subtract", "Multiply", "Divide"))

# Calculate result
if st.button("Calculate"):
    if option == "Add":
        st.success(f"Result: {a + b}")
    elif option == "Subtract":
        st.success(f"Result: {a - b}")
    elif option == "Multiply":
        st.success(f"Result: {a * b}")
    elif option == "Divide":
        if b == 0:
            st.error("Cannot divide by zero!")
        else:
            st.success(f"Result: {a / b}")
