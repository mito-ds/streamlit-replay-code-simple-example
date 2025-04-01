import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet, RunnableAnalysis
import os
import uuid

st.set_page_config(layout='wide')
st.title("Automation Hub Example")

st.markdown("This app demonstrates how to use the Mito Spreadsheet component to create an automation, and then rerun the analysis on a new dataset.")

tabs = st.tabs(["Create New Automation", "Rerun Existing Automation"])

with tabs[0]:

    st.markdown("""To create a new automation, follow these steps:
1. Use the input field below to name your script. 
2. Click on the `Import Files` button in the Mito spreadsheet and import `data/performance.csv`.
3. Make a few edits to the data.
4. Click the `Save Automation` button below the spreadsheet.
5. Find the generated code located at `/scripts/{script_name}.json`.
    """)

    st.markdown("""Notice that the generated code is a function. This is the result of setting the `code_options` parameter to the spreadsheet component.""")

    script_name = st.text_input('Script Name:', value='Automation Script')
    script_name_cleaned = script_name.replace(' ', '_').lower()

    if 'mito_key' not in st.session_state:
        st.session_state['mito_key'] = str(uuid.uuid4())

    # Create the Mito Spreadsheet component. Configure it to return an analysis object 
    # so we can use the Mito analysis utilities to save the analysis and replay it on a different
    # dataset later. Learn more here: https://docs.trymito.io/mito-for-streamlit/api-reference/runnableanalysis-class
    analysis = spreadsheet(
        import_folder = './data',
        return_type='analysis',
        key=st.session_state['mito_key'] 
    )

    if st.button("Save automation"):
        # When the user clicks the button, save the generated_code returned by the spreadsheet 
        # component to a .py file in the /scripts directory.
        file_path = os.path.join(os.getcwd(), 'scripts', script_name + '.json')
        with open(file_path, 'w') as f:
            f.write(analysis.to_json())
            st.success(f"""
                Saved the following automation to {script_name}.py. 
            
                If you're happy with the automation, switch to the "**Rerun Existing Automation**" tab to apply the analysis to a new dataset. Otherwise, make edits to the code and press the "**Save automation**" button again.
            """)
            with st.expander("View Generated Python Code", expanded=False):
                st.code(analysis.fully_parameterized_function)

    if st.button("Create new automation"):
        # Update the mito_key and then rerun the app to reset
        # the spreadsheet component 
        st.session_state['mito_key'] = str(uuid.uuid4())
        st.rerun()
        
with tabs[1]:
    st.markdown("""To rerun an existing automation on a new dataset, follow these steps:     
1. Select the automation you want to rerun from the dropdown menu below. 
2. Upload a new version of the dataset you want to apply the automation to. 
3. Click the `Run` button to rerun the automation.
    """)

    # Read the scripts from the /scripts directory so the user can select one
    analysis_names = os.listdir(os.path.join(os.getcwd(), 'scripts'))
    analysis_names = [name for name in analysis_names if name.endswith('.json')]
    
    if len(analysis_names) == 0:
        st.error("There are no existing automations. Create an automation first and then use this tab to rerun it on a new dataset.")
        st.stop()
    
    selected_analysis_name = st.selectbox("Select an automation", analysis_names)
        
    # Load JSON representation of the analysis and parse it back into a RunnableAnalysis object
    # so we can use the Mito analysis utilities to replay the analysis on a different dataset.
    with open(os.path.join(os.getcwd(), 'scripts', selected_analysis_name), 'r') as f:
        analysis_json = f.read()
    
        analysis = RunnableAnalysis.from_json(analysis_json)
    
    # Loop through the imports used in the analysis so the user can upload a new version of each file
    # Learn more about the get_param_metadata method here: https://docs.trymito.io/mito-for-streamlit/api-reference/runnableanalysis-class#get_param_metadata-param_type-literal-import-export
    updated_metadata = {}
    analysis_metadata = analysis.get_param_metadata()
    for idx, param in enumerate(analysis_metadata):
        new_param = None
            
        # For imports that are file imports, display a file uploader
        if param['subtype'] in ['file_name_import_excel', 'file_name_import_csv']:
            
            file_name = param['original_value'].split('/')[-1]
            new_param = st.file_uploader(f"Upload a new version of the file: `{file_name}`", key=idx)
        
        if new_param is not None:
            updated_metadata[param['name']] = new_param

    # Show a button to trigger re-running the analysis with the updated_metadata
    run = st.button('Run')
    if run:
        result = analysis.run(**updated_metadata)
        for sheet in result:
            st.write(sheet)
    
