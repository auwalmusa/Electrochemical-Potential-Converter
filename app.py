import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Electrochemical Potential Converter",
    page_icon="⚡",
    layout="wide"
)

# Dictionary of reference electrode potentials vs. SHE at 25°C
REFERENCE_POTENTIALS = {
    'NHE (Normal Hydrogen)': 0.000,
    'SHE (Standard Hydrogen)': 0.000,
    'Calomel (Sat\'d KCl)': 0.241,
    'Calomel (3.5M KCl)': 0.250,
    'Calomel (1M KCl)': 0.280,
    'Calomel (0.1M KCl)': 0.334,
    'Ag/AgCl (Sat\'d KCl)': 0.197,
    'Ag/AgCl (3.5M KCl)': 0.205,
    'Ag/AgCl (3M KCl)': 0.210,
    'Ag/AgCl (0.1M KCl)': 0.288,
    'Mercury/Mercurous Sulfate (0.5M H₂SO₄)': 0.682,
    'Mercury/Mercurous Sulfate (1M H₂SO₄)': 0.674,
    'Mercury/Mercurous Sulfate (Sat\'d K₂SO₄)': 0.640,
    'Hg/HgO (1M NaOH)': 0.098,
    'Hg/HgO (20% KOH)': 0.095,
    'Silver/Silver Sulfate (Sat\'d K₂SO₄)': 0.654
}

# Function to convert potential between reference electrodes
def convert_potential(potential, from_ref, to_ref):
    """
    Convert a potential value from one reference electrode to another
    
    Parameters:
    -----------
    potential : float
        Potential value to convert (V)
    from_ref : str
        Original reference electrode
    to_ref : str
        Target reference electrode
        
    Returns:
    --------
    float
        Converted potential value (V)
    """
    # Convert to SHE first, then to the target reference
    potential_vs_she = potential + REFERENCE_POTENTIALS[from_ref]
    potential_vs_target = potential_vs_she - REFERENCE_POTENTIALS[to_ref]
    
    return potential_vs_target

# App title and description
st.title("Electrochemical Potential Converter")
st.markdown("""
This application converts potential values between different electrochemical reference electrodes.
Enter a potential value, select the original reference electrode and the target reference electrode, 
then click "Convert" to see the result.
""")

# Create columns for a cleaner layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Potential Conversion")
    
    # Input for potential value
    potential_value = st.number_input(
        "Potential Value (V)",
        value=0.350,
        format="%.3f",
        step=0.001
    )
    
    # Selection for reference electrodes
    from_ref = st.selectbox(
        "From Reference Electrode",
        options=list(REFERENCE_POTENTIALS.keys()),
        index=list(REFERENCE_POTENTIALS.keys()).index('Ag/AgCl (Sat\'d KCl)')
    )
    
    to_ref = st.selectbox(
        "To Reference Electrode",
        options=list(REFERENCE_POTENTIALS.keys()),
        index=list(REFERENCE_POTENTIALS.keys()).index('SHE (Standard Hydrogen)')
    )
    
    # Swap references button
    if st.button("Swap References"):
        # We can't directly swap the selectbox values in Streamlit,
        # but we can use session state as a workaround for next refresh
        st.session_state['from_ref'] = to_ref
        st.session_state['to_ref'] = from_ref
        st.experimental_rerun()
    
    # Apply session state if it exists
    if 'from_ref' in st.session_state:
        from_ref = st.session_state['from_ref']
        del st.session_state['from_ref']
    
    if 'to_ref' in st.session_state:
        to_ref = st.session_state['to_ref']
        del st.session_state['to_ref']
    
    # Convert button
    if st.button("Convert"):
        converted_value = convert_potential(potential_value, from_ref, to_ref)
        
        # Display result in a highlighted box
        st.success(f"""
        ### Conversion Result:
        **{potential_value:.3f} V vs. {from_ref}** = **{converted_value:.3f} V vs. {to_ref}**
        """)
        
        # Add to history if it doesn't exist yet
        if 'conversion_history' not in st.session_state:
            st.session_state['conversion_history'] = []
        
        # Add current conversion to history
        st.session_state['conversion_history'].append({
            'Input Potential': f"{potential_value:.3f} V",
            'From Reference': from_ref,
            'To Reference': to_ref,
            'Result': f"{converted_value:.3f} V",
            'Timestamp': pd.Timestamp.now().strftime("%H:%M:%S")
        })

# Sidebar with reference electrode data
with st.sidebar:
    st.header("Reference Electrode Potentials")
    st.markdown("Values vs. SHE at 25°C")
    
    # Create a dataframe for the reference potentials
    ref_data = pd.DataFrame({
        'Reference Electrode': list(REFERENCE_POTENTIALS.keys()),
        'Potential vs. SHE (V)': list(REFERENCE_POTENTIALS.values())
    })
    
    # Display as a table
    st.dataframe(ref_data.style.format({'Potential vs. SHE (V)': '{:.3f}'}))
    
    st.markdown("""
    ### About Reference Electrodes
    
    Reference electrodes are essential in electrochemistry to provide a stable 
    potential against which working electrode potentials are measured. Different 
    reference electrodes are commonly used in different research areas or with 
    specific electrolytes.
    
    The Standard Hydrogen Electrode (SHE) is defined as having a potential of 
    exactly 0.000 V and serves as the fundamental reference point in electrochemistry.
    """)

# Conversion history section
with col2:
    st.subheader("Conversion History")
    
    if 'conversion_history' in st.session_state and st.session_state['conversion_history']:
        history_df = pd.DataFrame(st.session_state['conversion_history'])
        st.dataframe(history_df, hide_index=True)
        
        if st.button("Clear History"):
            st.session_state['conversion_history'] = []
            st.experimental_rerun()
    else:
        st.info("No conversion history yet. Perform a conversion to see it here.")

# Information section at the bottom
st.markdown("""
---
### Why Reference Conversion Matters

Converting between reference electrodes is crucial in electrochemistry for:

1. **Comparing data from different studies** that use different reference electrodes
2. **Relating measured potentials to standard thermodynamic values** (often given vs. SHE)
3. **Ensuring proper interpretation** of electrochemical windows and reaction potentials
4. **Reproducing literature experiments** when using a different reference electrode

Without proper conversion, errors of hundreds of millivolts can occur, leading to significant misinterpretations of electrochemical data.
""")

# Footer
st.markdown("""
---
Made with Streamlit • Python for Electroanalysis • 2025
""")
