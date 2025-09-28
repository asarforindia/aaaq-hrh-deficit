import streamlit as st
import constants as c


# Variable Selector
def variable_selector():
    st.write("Variable Selector")
    variable_groups = c.VARIABLE_GROUPS

    selection = st.segmented_control(
        "Choose Group of Variables:",
        variable_groups.keys(),
    )

    if selection is not None:
        groups = variable_groups[selection]
        selected_option = st.selectbox("Choose a Variable:", groups)

        # Exclude group headers
        if selected_option:
            st.write(f"You selected: {selected_option}")


# Main app
def main():
    st.title("Variable Selector")
    variable_selector()


# Run the app
if __name__ == "__main__":
    main()
