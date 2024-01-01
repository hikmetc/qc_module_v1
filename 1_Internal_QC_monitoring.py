# Developed by Hikmet Can Çubukçu

import streamlit as st
st.set_page_config(layout="wide", page_title="QC Module", page_icon="📈")
from datetime import datetime
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


with st.sidebar:
    st.header("QC Module")
    with open('./template/template_IQC.xlsx', "rb") as template_file:
        template_byte = template_file.read()
    # download template excel file
    st.download_button(label="Click to Download Template File",
                        data=template_byte,
                        file_name="template_IQC.xlsx",
                        mime='application/octet-stream')
      # upload file
    uploaded_file = st.file_uploader('#### **Upload your .xlsx (Excel) or .csv file:**', type=['csv','xlsx'], accept_multiple_files=False)
    
    def process_file(file):
        # data of analyte selection
        try:
            uploaded_file = pd.read_excel(file)
        except:
            uploaded_file = pd.read_csv(file, sep=None, engine='python')
        analyte_name_box = st.selectbox("**Select IQC result Column**", tuple(uploaded_file.columns))
        analyte_data = uploaded_file[analyte_name_box]
        analyte_data = analyte_data.dropna(axis=0).reset_index()
        analyte_data = analyte_data[analyte_name_box]
        return analyte_data, analyte_name_box

    # column name (data) selection
    if uploaded_file is not None:
        # data of analyte selection
        analyte_data, analyte_name_box = process_file(uploaded_file)
    st.info('*Developed by Hikmet Can Çubukçu, MD, EuSpLM* <hikmetcancubukcu@gmail.com>')
        

st.header("📉 Quality Control Module")

tab1, tab2, tab3 = st.tabs(["📖 **Instructions**", "📉 **:green[Levey-Jennings & Moving Averages Charts]**", 
                                "📈 **:blue[Sigmametric & Medical Decision Charts]**"
                                ],)
with tab1:
    instructions = """
    #### :blue[Instructions for Use]

    ##### :blue[Sidebar Features]

    **:blue[1. QC Module:]**
    - The sidebar contains a section titled "QC Module."
    - Users can download the "template_IQC.xlsx" Excel template file by clicking the "Click to Download Template File" button.
    - The sidebar also includes a file upload section where users can upload Excel (.xlsx) or CSV (.csv) files. Users can either drag and drop files or use the "Browse files" button to select files from their folders.
    - The application reads the uploaded file, processes both Excel and CSV formats, and prompts users to select a column representing IQC results.
    - The selected column is processed, removing missing values and resetting the index for further analysis.

    ##### :blue[Tabs]

    **:blue[1. Instructions Tab:]**
    - The "Instructions" tab provides guidance on effectively using the application.

    **:blue[2. Levey-Jennings & Moving Averages Graphs Tab:]**
    - This tab allows direct data entry through an editable table structure.
    - Users can input and modify data using a data editor widget, and they can dynamically increase the row count using the plus sign under the table.
    - Checkboxes in the right column allow users to include or exclude each data point.
    - Radio buttons below the table enable users to choose which data to use for graph plotting.
    - Another set of radio buttons allows users to decide whether to calculate the mean and standard deviation from the entered or loaded data or to use user-inputted mean and standard deviation.
    - Users can select Westgard rules (e.g., 1-2s, 1-3s) to highlight points deviating from control limits.
    - The Levey-Jennings control chart is visualized using Plotly Express, with out-of-control points highlighted in red.

    **:blue[3. Sigmametric & Medical Decision Graphs Tab:]**
    - In this tab, users can calculate sigma-metric values using two methods by entering allowed total error, bias, analytical coefficient of variation, and within-subject biological variation.
    - The Operational Specifications (OPSpecs) graph is drawn based on the entered data.
    - Below the OPSpec graph, the Normalized OPSpecs Graph section is collapsible. Users can input test-related data, including bias, imprecision, and allowed total error. Normalized values and sigma-metric values are calculated and displayed. The graph visualizes data for multiple analyses.

    """
    st.markdown(instructions)

with tab2:
    
    st.markdown("##### **:blue[Levey-Jennings & Moving Averages Charts]**")
    st.markdown(' ')
    
    # Enter the number of rows for the dataframe
    number_of_rows = st.number_input('**:blue[Enter Number of Rows of Your Data]**', min_value=3, max_value=999999999999999)

    # Initialize an empty dataframe with the specified number of rows
    df = pd.DataFrame(
        [{"Date": None, "Index": None, "IQC results": None, "include": True} for _ in range(number_of_rows)]
    )

    # Use st.data_editor to create an editable dataframe
    edited_df = st.data_editor(
        df,
        column_config={
            "Date": st.column_config.DatetimeColumn(
                "Date",
                min_value=datetime(1980, 1, 1),
                max_value=datetime(2175, 1, 1),
                format="D MMM YYYY, h:mm a",
                step=60,
            ),
            "Index": st.column_config.NumberColumn(
                "Index",
                help="Index of the IQC results",
                min_value=0,
                max_value=999999999999999999999999999999999999999,
                step=1,
                format="%i",
            ),
            "IQC results": st.column_config.NumberColumn(
                "IQC results",
                help="IQC results",
                min_value=0,
                max_value=999999999999999999999999999999999999999,
                # step=1,
                format="%g",
            ),
            "include": st.column_config.CheckboxColumn(
                "include",
                help="Select to include",
                default=True,
            ),
        },
        hide_index=True, num_rows="dynamic"
    )  # An editable dataframe
    edited_df = pd.DataFrame(edited_df)
    # data selection
    data_select = st.radio("**:blue[Select the data to be plotted]**",
        ["From entered data table","Uploaded data"])
    
    if data_select == "Uploaded data":
        try:
            data = analyte_data
        except NameError as error:
            print("NameError occurred:", error)
            st.error("Data wasn't uploaded")
    else:
        edited_df = edited_df[edited_df['include']==True] # select where include == True
        data = edited_df['IQC results']
    
    APC_select = st.radio("**:blue[Source of mean and standard deviation for L-J Control Chart]**",
        ["From the entered/uploaded data","Custom"])
    if APC_select == "Custom":
        st.markdown('**:blue[Enter custom mean/target and standard deviation]**')
        col1, col2 = st.columns([1,1])
        mean_input = col1.number_input('**Mean**',step = 0.00001)
        SD_input = col2.number_input('**Standard Deviation**',step = 0.00001)
        st.write(f'Custom mean: {mean_input}, Custom SD: {SD_input} ')
        mean= mean_input
        std_dev = SD_input
    else:
        if data_select == "Uploaded data":
            if uploaded_file is not None:
                mean = np.mean(data)
                std_dev = np.std(data)
            else:
                st.error("Data wasn't uploaded")
        else:
            mean = np.mean(data)
            std_dev = np.std(data)
    
    try:
        # Calculate control limits
        upper_limit_3sd = mean + 3 * std_dev
        lower_limit_3sd = mean - 3 * std_dev
        upper_limit_2sd = mean + 2 * std_dev
        lower_limit_2sd = mean - 2 * std_dev
        upper_limit_1sd = mean + 1 * std_dev
        lower_limit_1sd = mean - 1 * std_dev
        
        # Select rules   
        st.markdown('**:blue[Select your IQC rules]**')
        col1, col2, col3, col4 ,col5, col6 = st.columns([1,1,1,1,1,1])
        rule_1_2s = col1.checkbox('**1-2s**')
        rule_1_3s = col2.checkbox('**1-3s**')
        rule_2_2s = col3.checkbox('**2-2s**')
        rule_R_4s = col4.checkbox('**R-4s**')
        rule_4_1s = col5.checkbox('**4-1s**')
        rule_10x = col6.checkbox('**10x**')


        # Create a dataframe for the plotly express function
        df = pd.DataFrame({'Data': data, 'Mean': mean, '+3SD': upper_limit_3sd, '-3SD': lower_limit_3sd,
                        '+2SD': upper_limit_2sd, '-2SD': lower_limit_2sd, 
                        '+1SD':upper_limit_1sd, '-1SD':lower_limit_1sd})

        # Create a Shewhart Chart using Plotly
        fig = go.Figure()

        # Scatter plot for the data points
        fig.add_trace(go.Scatter(x=df.index, y=df['Data'], mode='markers', name='Data'))

        # Line plot for upper and lower control limits
        fig.add_trace(go.Scatter(x=df.index, y=df['+3SD'], mode='lines', line=dict(color='red'), name='+3SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['-3SD'], mode='lines', line=dict(color='red'), name='-3SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['+2SD'], mode='lines', line=dict(color='blue'), name='+2SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['-2SD'], mode='lines', line=dict(color='blue'), name='-2SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['+1SD'], mode='lines', line=dict(color='lightblue'), name='+1SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['-1SD'], mode='lines', line=dict(color='lightblue'), name='-1SD'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Mean'], mode='lines', line=dict(color='lightgreen'), name='Mean'))
                
        out_of_control_traces = []
        # Highlight points outside control limits
        if rule_1_3s:
            df['Out of Control 1-3s'] = ((df['Data'] >= upper_limit_3sd) | (df['Data'] <= lower_limit_3sd))
            out_of_control_points_1_3s = df[df['Out of Control 1-3s']]
            fig.add_trace(go.Scatter(x=out_of_control_points_1_3s.index, y=out_of_control_points_1_3s['Data'],
                                    mode='markers', marker=dict(color='red'), showlegend=False, 
                                    name='1-3s',text='Out of Control (1-3s)'))
                
        if rule_1_2s:
            df['Out of Control 1-2s'] = (df['Data'] >= upper_limit_2sd) | (df['Data'] <= lower_limit_2sd)
            out_of_control_points_1_2s = df[df['Out of Control 1-2s']]
            fig.add_trace(go.Scatter(x=out_of_control_points_1_2s.index, y=out_of_control_points_1_2s['Data'],
                                    mode='markers', marker=dict(color='red'), showlegend=False,
                                    name='1-2s',text='Out of Control (1-2s)'))

        if rule_2_2s:
            # Identify points outside the 2-SD limit
            df['Out of Control 2-2s'] = ((((df['Data'] >= upper_limit_2sd) & (df['Data'].shift(1) >= upper_limit_2sd)) |
                                        ((df['Data'] >= upper_limit_2sd) & (df['Data'].shift(-1) >= upper_limit_2sd))) |
                                        (((df['Data'] <= lower_limit_2sd) & (df['Data'].shift(1) <= lower_limit_2sd)) |
                                        ((df['Data'] <= lower_limit_2sd) & (df['Data'].shift(-1) <= lower_limit_2sd))))
            # Extract only the points that meet the 2-2s rule
            out_of_control_2_2s_points = df[df['Out of Control 2-2s']]

            # Scatter plot for the out of control points
            fig.add_trace(go.Scatter(x=out_of_control_2_2s_points.index, y=out_of_control_2_2s_points['Data'],
                                    mode='markers', marker=dict(color='red'), 
                                    showlegend=False, name='2-2s', text='Out of Control (2-2s)'))

        if rule_R_4s:
            df['Out of Control R-4s'] = ((((df['Data'] >= upper_limit_2sd) & (df['Data'].shift(1) <= lower_limit_2sd))|
                                        ((df['Data'] >= upper_limit_2sd) & (df['Data'].shift(-1) <= lower_limit_2sd))) |
                                        (((df['Data'] <= lower_limit_2sd) & (df['Data'].shift(1) >= upper_limit_2sd))|
                                        ((df['Data'] <= lower_limit_2sd) & (df['Data'].shift(-1) >= upper_limit_2sd))))
                    
            out_of_control_R_4s_points = df[df['Out of Control R-4s']]
            # Identify points outside
            fig.add_trace(go.Scatter(x=out_of_control_R_4s_points.index, y=out_of_control_R_4s_points['Data'],
                                    mode='markers', marker=dict(color='red'),showlegend=False,
                                    name='R-4s', text='Out of Control (R-4s)'))

        if rule_4_1s:
            df['Out of Control 4-1s'] = ((((df['Data'] >= upper_limit_1sd) & (df['Data'].shift(1) >= upper_limit_1sd) & (df['Data'].shift(2) >= upper_limit_1sd) & (df['Data'].shift(3) >= upper_limit_1sd)) |
                                        ((df['Data'] >= upper_limit_1sd) & (df['Data'].shift(-1) >= upper_limit_1sd) & (df['Data'].shift(-2) >= upper_limit_1sd) & (df['Data'].shift(-3) >= upper_limit_1sd)) |
                                        ((df['Data'].shift(1) >= upper_limit_1sd) & (df['Data'] >= upper_limit_1sd) & (df['Data'].shift(-1) >= upper_limit_1sd) & (df['Data'].shift(-2) >= upper_limit_1sd)) |
                                    ((df['Data'].shift(-1) >= upper_limit_1sd) & (df['Data'] >= upper_limit_1sd) & (df['Data'].shift(1) >= upper_limit_1sd) & (df['Data'].shift(2) >= upper_limit_1sd))) |
                                        (((df['Data'] <= lower_limit_1sd) & (df['Data'].shift(1) <= lower_limit_1sd) & (df['Data'].shift(2) <= lower_limit_1sd) & (df['Data'].shift(3) <= lower_limit_1sd)) |
                                        ((df['Data'].shift(1) <= lower_limit_1sd) & (df['Data'] <= lower_limit_1sd) & (df['Data'].shift(-1) <= lower_limit_1sd) & (df['Data'].shift(-2) <= lower_limit_1sd))|
                                        ((df['Data'] <= lower_limit_1sd) & (df['Data'].shift(-1) <= lower_limit_1sd) & (df['Data'].shift(-2) <= lower_limit_1sd) & (df['Data'].shift(-3) <= lower_limit_1sd)) |
                                        ((df['Data'].shift(-1) <= lower_limit_1sd) & (df['Data'] <= lower_limit_1sd) & (df['Data'].shift(1) <= lower_limit_1sd) & (df['Data'].shift(2) <= lower_limit_1sd))))
                    
            # Extract only the points that meet the 4-1s rule
            out_of_control_4_1s_points = df[df['Out of Control 4-1s']]
            fig.add_trace(go.Scatter(x=out_of_control_4_1s_points.index, y=out_of_control_4_1s_points['Data'],
                                    mode='markers', marker=dict(color='red'), showlegend=False, 
                                    name='4-1s',text='Out of Control (4-1s)'))     

        if rule_10x:
            # Identify points shifted
            df['Out of Control 10x'] = ((((df['Data'] >= mean) & (df['Data'].shift(1) > mean) & (df['Data'].shift(2) > mean) & (df['Data'].shift(3) > mean) & (df['Data'].shift(4) > mean) 
                                        & (df['Data'].shift(5) > mean) & (df['Data'].shift(6) > mean) & (df['Data'].shift(7) > mean)  & (df['Data'].shift(8) > mean)  & (df['Data'].shift(9) > mean)) |
                                        ((df['Data'].shift(-1) > mean) & (df['Data'] > mean) & (df['Data'].shift(1) > mean) & (df['Data'].shift(2) > mean) & (df['Data'].shift(3) > mean) 
                                        & (df['Data'].shift(4) > mean) & (df['Data'].shift(5) > mean) & (df['Data'].shift(6) > mean) & (df['Data'].shift(7) > mean)  & (df['Data'].shift(8) > mean)) |
                                        ((df['Data'].shift(-2) > mean) & (df['Data'].shift(-1) > mean) & (df['Data'] > mean) & (df['Data'].shift(1) > mean) & (df['Data'].shift(2) > mean) 
                                        & (df['Data'].shift(3) > mean) & (df['Data'].shift(4) > mean) & (df['Data'].shift(5) > mean) & (df['Data'].shift(6) > mean) & (df['Data'].shift(7) > mean)) |
                                        ((df['Data'].shift(-3) > mean) & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-1) > mean) & (df['Data'] > mean) & (df['Data'].shift(1) > mean) 
                                        & (df['Data'].shift(2) > mean) & (df['Data'].shift(3) > mean) & (df['Data'].shift(4) > mean) & (df['Data'].shift(5) > mean) & (df['Data'].shift(6) > mean)) |
                                        ((df['Data'].shift(-4) > mean) & (df['Data'].shift(-3) > mean) & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-1) > mean) & (df['Data'] > mean) 
                                        & (df['Data'].shift(1) > mean) & (df['Data'].shift(2) > mean) & (df['Data'].shift(3) > mean) & (df['Data'].shift(4) > mean) & (df['Data'].shift(5) > mean)) |
                                        ((df['Data'].shift(1) > mean) & (df['Data'] > mean) & (df['Data'].shift(-1) > mean) & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-3) > mean) 
                                        & (df['Data'].shift(-4) > mean) & (df['Data'].shift(-5) > mean) & (df['Data'].shift(-6) > mean) & (df['Data'].shift(-7) > mean) & (df['Data'].shift(-8) > mean))|
                                        ((df['Data'].shift(2) > mean) & (df['Data'].shift(1) > mean) & (df['Data'] > mean) & (df['Data'].shift(-1) > mean) & (df['Data'].shift(-2) > mean) 
                                        & (df['Data'].shift(-3) > mean) & (df['Data'].shift(-4) > mean) & (df['Data'].shift(-5) > mean) & (df['Data'].shift(-6) > mean) & (df['Data'].shift(-7) > mean))|
                                        ((df['Data'].shift(3) > mean) & (df['Data'].shift(2) > mean) & (df['Data'].shift(1) > mean) & (df['Data'] > mean) & (df['Data'].shift(-1) > mean) 
                                        & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-3) > mean) & (df['Data'].shift(-4) > mean) & (df['Data'].shift(-5) > mean) & (df['Data'].shift(-6) > mean))|
                                        ((df['Data'].shift(4) > mean) & (df['Data'].shift(3) > mean) & (df['Data'].shift(2) > mean) & (df['Data'].shift(1) > mean) & (df['Data'] > mean) 
                                        & (df['Data'].shift(-1) > mean) & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-3) > mean) & (df['Data'].shift(-4) > mean) & (df['Data'].shift(-5) > mean))|
                                        ((df['Data'] > mean) & (df['Data'].shift(-1) > mean) & (df['Data'].shift(-2) > mean) & (df['Data'].shift(-3) > mean) & (df['Data'].shift(-4) > mean) 
                                        & (df['Data'].shift(-5) > mean) & (df['Data'].shift(-6) > mean) & (df['Data'].shift(-7) > mean) & (df['Data'].shift(-8) > mean) & (df['Data'].shift(-9) > mean))) 
                                        |
                                        (((df['Data'] < mean) & (df['Data'].shift(1) < mean) & (df['Data'].shift(2) < mean) & (df['Data'].shift(3) < mean) & (df['Data'].shift(4) < mean) 
                                        & (df['Data'].shift(5) < mean) & (df['Data'].shift(6) < mean) & (df['Data'].shift(7) < mean)  & (df['Data'].shift(8) < mean)  & (df['Data'].shift(9) < mean)) |
                                        ((df['Data'].shift(-1) < mean) & (df['Data'] < mean) & (df['Data'].shift(1) < mean) & (df['Data'].shift(2) < mean) & (df['Data'].shift(3) < mean) 
                                        & (df['Data'].shift(4) < mean) & (df['Data'].shift(5) < mean) & (df['Data'].shift(6) < mean) & (df['Data'].shift(7) < mean)  & (df['Data'].shift(8) < mean)) |
                                        ((df['Data'].shift(-2) < mean) & (df['Data'].shift(-1) < mean) & (df['Data'] < mean) & (df['Data'].shift(1) < mean) & (df['Data'].shift(2) < mean) 
                                        & (df['Data'].shift(3) < mean) & (df['Data'].shift(4) < mean) & (df['Data'].shift(5) < mean) & (df['Data'].shift(6) < mean) & (df['Data'].shift(7) < mean)) |
                                        ((df['Data'].shift(-3) < mean) & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-1) < mean) & (df['Data'] < mean) & (df['Data'].shift(1) < mean) 
                                        & (df['Data'].shift(2) < mean) & (df['Data'].shift(3) < mean) & (df['Data'].shift(4) < mean) & (df['Data'].shift(5) < mean) & (df['Data'].shift(6) < mean)) |
                                        ((df['Data'].shift(-4) < mean) & (df['Data'].shift(-3) < mean) & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-1) < mean) & (df['Data'] < mean) 
                                        & (df['Data'].shift(1) < mean) & (df['Data'].shift(2) < mean) & (df['Data'].shift(3) < mean) & (df['Data'].shift(4) < mean) & (df['Data'].shift(5) < mean)) |
                                        ((df['Data'].shift(1) < mean) & (df['Data'] < mean) & (df['Data'].shift(-1) < mean) & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-3) < mean) 
                                        & (df['Data'].shift(-4) < mean) & (df['Data'].shift(-5) < mean) & (df['Data'].shift(-6) < mean) & (df['Data'].shift(-7) < mean) & (df['Data'].shift(-8) < mean))|
                                        ((df['Data'].shift(2) < mean) & (df['Data'].shift(1) < mean) & (df['Data'] < mean) & (df['Data'].shift(-1) < mean) & (df['Data'].shift(-2) < mean) 
                                        & (df['Data'].shift(-3) < mean) & (df['Data'].shift(-4) < mean) & (df['Data'].shift(-5) < mean) & (df['Data'].shift(-6) < mean) & (df['Data'].shift(-7) < mean))|
                                        ((df['Data'].shift(3) < mean) & (df['Data'].shift(2) < mean) & (df['Data'].shift(1) < mean) & (df['Data'] < mean) & (df['Data'].shift(-1) < mean) 
                                        & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-3) < mean) & (df['Data'].shift(-4) < mean) & (df['Data'].shift(-5) < mean) & (df['Data'].shift(-6) < mean))|
                                        ((df['Data'].shift(4) < mean) & (df['Data'].shift(3) < mean) & (df['Data'].shift(2) < mean) & (df['Data'].shift(1) < mean) & (df['Data'] < mean) 
                                        & (df['Data'].shift(-1) < mean) & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-3) < mean) & (df['Data'].shift(-4) < mean) & (df['Data'].shift(-5) < mean))|
                                        ((df['Data'] < mean) & (df['Data'].shift(-1) < mean) & (df['Data'].shift(-2) < mean) & (df['Data'].shift(-3) < mean) & (df['Data'].shift(-4) < mean) 
                                        & (df['Data'].shift(-5) < mean) & (df['Data'].shift(-6) < mean) & (df['Data'].shift(-7) < mean) & (df['Data'].shift(-8) < mean) & (df['Data'].shift(-9) < mean))))

            # Extract only the points that meet the 10x rule
            out_of_control_10x_points = df[df['Out of Control 10x']]
            fig.add_trace(go.Scatter(x=out_of_control_10x_points.index, y=out_of_control_10x_points['Data'],
                                    mode='markers', marker=dict(color='red'), showlegend=False, 
                                    name='10x',text='Out of Control (10x)'))

                # Layout settings
        fig.update_layout(title='Levey-Jennings Control Chart',
                    xaxis_title='Data Point',
                    yaxis_title='Value',
                    showlegend=True, title_font=dict(color='#cc0000'))

        # Show the plot
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
        st.write("---")        
        
        # EWMA PLOT
        lambda_value_choice = st.select_slider('**:blue[Select the lambda value (weighting factor) for EWMA chart]**',
                    options=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1], value = 0.2)
        
        lambda_value = lambda_value_choice
        if lambda_value == 0.05:
            L = 2.615
        elif lambda_value == 0.1:
            L = 2.814
        elif lambda_value == 0.2:
            L = 2.962
        elif lambda_value == 0.3:
            L = 3.023
        elif lambda_value == 0.4:
            L = 3.054
        elif lambda_value == 0.5:
            L = 3.071
        elif lambda_value == 0.75:
            L = 3.087
        elif lambda_value == 1:
            L = 3.090

        try:
        # Calculate Exponential Weighted Moving Average (EWMA)
            ewma = df['Data'].ewm(alpha= lambda_value, span=None, adjust=False).mean()
        except Exception as e:
            st.error("Your data contains inappropriate type of values. Please check your data.")

        # Calculate UCL and LCL
        results = range(1, len(ewma) + 1)
        UCL_values = []
        LCL_values = []

        for ind in results:
            UCL = mean + L * std_dev * (((lambda_value) * (1 - (1 - lambda_value)**(2 * ind)) / (2 - lambda_value))**(0.5))
            LCL = mean - L * std_dev * (((lambda_value) * (1 - (1 - lambda_value)**(2 * ind)) / (2 - lambda_value))**(0.5))
            
            UCL_values.append(UCL)
            LCL_values.append(LCL)

        # Create a Plotly figure
        fig2 = go.Figure()
        
        # Add EWMA data
        fig2.add_trace(go.Scatter(x=ewma.index, y=ewma, mode='lines', name='EWMA'))
        
        # Add markers for points above UCL
        fig2.add_trace(go.Scatter(x=ewma[ewma > UCL_values].index, y=ewma[ewma >= UCL_values], mode='markers',
                                marker=dict(color='red'), name='Above UCL'))

        # Add markers for points below LCL
        fig2.add_trace(go.Scatter(x=ewma[ewma < LCL_values].index, y=ewma[ewma <= LCL_values], mode='markers',
                                marker=dict(color='blue'), name='Below LCL'))


        # Add UCL and LCL
        fig2.add_trace(go.Scatter(x=ewma.index, y=UCL_values, mode='lines', name='UCL', line=dict(color='red')))
        fig2.add_trace(go.Scatter(x=ewma.index, y=LCL_values, mode='lines', name='LCL', line=dict(color='blue')))

        # Customize the layout
        fig2.update_layout(title=f'Exponentially Weighted Moving Average (EWMA) chart with weighting factor "{lambda_value}"',
                        xaxis_title='Data point',
                        yaxis_title='Value', title_font=dict(color='#cc0000'))
        
        st.plotly_chart(fig2, theme="streamlit", use_container_width=True) 
        df[f'EWMA (lambda={lambda_value}) higher than UCL'] = (ewma >= UCL_values)      
        df[f'EWMA (lambda={lambda_value}) lower than LCL'] = (ewma <= LCL_values)      

        st.write("---")
        
        # CUSUM PLOT
        def plot_cusum(cusum_np_arr, mu, sd, k=0.5, h=5):
            # Drop rows with None values in 'Data' column
            cusum_np_arr = cusum_np_arr.dropna().reset_index(drop=True)
            
            Cp = (cusum_np_arr * 0).copy()
            Cm = Cp.copy()

            for ii in np.arange(len(cusum_np_arr)):
                if ii == 0:
                    Cp[ii] = 0
                    Cm[ii] = 0
                else:
                    Cp[ii] = np.max([0, ((cusum_np_arr[ii] - mu) / sd) - k + Cp[ii - 1]])
                    Cm[ii] = np.max([0, -k - ((cusum_np_arr[ii] - mu) / sd) + Cm[ii - 1]])

            Cont_limit_arr = np.array(h * np.ones((len(cusum_np_arr), 1)))
            Cont_lim_df = pd.DataFrame(Cont_limit_arr, columns=["h"])
            cusum_df = pd.DataFrame({'Cp': Cp, 'Cn': Cm})

            # Create figure
            fig = go.Figure()

            # Add trace for Cp and Cn
            fig.add_trace(go.Scatter(x=np.arange(len(cusum_np_arr)), y=cusum_df['Cp'], mode='lines', name='Cp'))
            fig.add_trace(go.Scatter(x=np.arange(len(cusum_np_arr)), y=-cusum_df['Cn'], mode='lines', name='Cn'))

            # Add trace for Cont_limit
            fig.add_trace(go.Scatter(x=np.arange(len(cusum_np_arr)), y=Cont_lim_df['h'], mode='lines', name='UCL', line=dict(color='red')))

            # Add trace for Cont_limit
            fig.add_trace(go.Scatter(x=np.arange(len(cusum_np_arr)), y=-Cont_lim_df['h'], mode='lines', name='LCL', line=dict(color='blue')))

            # Add markers for points above UCL
            fig.add_trace(go.Scatter(x=cusum_df[cusum_df['Cp'] > h].index, y=cusum_df['Cp'][cusum_df['Cp'] > h],
                                    mode='markers', marker=dict(color='red'), name='Above UCL'))

            # Add markers for points below LCL
            fig.add_trace(go.Scatter(x=cusum_df[-cusum_df['Cn'] < -h].index, y=-cusum_df['Cn'][-cusum_df['Cn'] < -h],
                                    mode='markers', marker=dict(color='blue'), name='Below LCL'))

            # Update layout
            fig.update_layout(
                title="CUSUM Control Chart",
                xaxis_title="Data points",
                yaxis_title="Value",
                #legend=dict(x=0, y=1),
                showlegend=True,title_font=dict(color='#cc0000')
            )

            # Show figure
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        plot_cusum(df['Data'], mean, std_dev)
        
        # This part add cusum results to the dataframe
        cusum_np_arr = df['Data'].dropna().reset_index(drop=True)
        k=0.5
        h=5    
        mu = mean
        sd = std_dev
        Cp = (cusum_np_arr * 0).copy()
        Cm = Cp.copy()

        for ii in np.arange(len(cusum_np_arr)):
            if ii == 0:
                Cp[ii] = 0
                Cm[ii] = 0
            else:
                Cp[ii] = np.max([0, ((cusum_np_arr[ii] - mu) / sd) - k + Cp[ii - 1]])
                Cm[ii] = np.max([0, -k - ((cusum_np_arr[ii] - mu) / sd) + Cm[ii - 1]])

        Cont_limit_arr = np.array(h * np.ones((len(cusum_np_arr), 1)))
        Cont_lim_df = pd.DataFrame(Cont_limit_arr, columns=["h"])
        cusum_df = pd.DataFrame({'Cp': Cp, 'Cn': Cm})

        df[f'CUSUM higher than UCL'] = (Cp >= h)      
        df[f'CUSUM lower than LCL'] = (Cm >= h)      

        # show dataframe with out-of-control results notation
        with st.expander("**:blue[See the details of your data & download your data as .csv file]**"):
            st.dataframe(df)

        if not math.isnan(mean):
            st.markdown("**:blue[Analytical Performance Characteristics (Mean, standard deviation, and CV) of the data]**")
            def round_half_up(n, decimals=0):
                multiplier = 10**decimals
                return math.floor(n * multiplier + 0.5) / multiplier
            try:
                st.markdown(f"""
                            | *:green[Analytical Performance Characteristics]* | *:green[Value]* |
                            | ----------- | ----------- |
                            | **:black[Mean]** | **{round_half_up(mean,2)}** |
                            | **:black[Standard Deviation]** | **{round_half_up(std_dev,2)}** |
                            | **:black[Coefficient of Variation (CV)]** | **{round_half_up((std_dev*100/mean),2)}** |
                            """)
            except ZeroDivisionError as ze:
                st.error('Mean value can not be "0"') 
    except NameError as ne:
        if 'data' in str(ne):
            st.info("Please upload your data")
        else:
            # Handle other NameError cases if needed
            print("A NameError occurred, but it's not related to 'data'")    

with tab3:
    def round_half_up(n, decimals=0):
                multiplier = 10**decimals
                return math.floor(n * multiplier + 0.5) / multiplier
    col1, col2 = st.columns([1,1])
    col1.markdown('**:blue[Conventional Sigmametric]**')
    col1.latex(r'''\frac{{\text{{TEa(\%) - Bias(\%)}}}}{{\text{{Imprecision(\%CV)}}}}''')
    TEa_input = col1.number_input('**Total Allowable Error (TEa%)**', min_value=0.0,step = 0.00001)
    bias_input = col1.number_input('**Bias (%)**', min_value=0.0, step = 0.00001)
    CV_input = col1.number_input('**Imprecision (Analytical Coefficient of Variation %)**', min_value=0.0, step = 0.00001)
    # alternative sigmametric
    col2.markdown('**:blue[Alternative Sigmametric (Oosterhuis & Coskun 2018)]**')
    col2.latex(r'''\frac{{\text{{Within-subject biological variation}}(\%CV_{I})}}{{\text{{Imprecision}}(\%\text{CV})}}''')
    CVI_input = col2.number_input('**Within-subject biological variation(%CVI)**', min_value=0.0, step = 0.00001)
    #CV2_input = col2.number_input('**Analytical Coefficient of Variation**', min_value=0.0, step = 0.00001)
    # Calculate button "Simulate & Calculate"
    calc_button = st.button('**:green[Calculate & Plot OPSpecs Chart]**')
    if calc_button:
        if not CV_input==0:
            if bias_input < TEa_input:
                sigmametric_result_v1 = (TEa_input-bias_input)/CV_input
                col1.info(f""" **:green[Sigmametric value (conventional)]** : 
                            **{round_half_up((sigmametric_result_v1),2)}** 
                                """)
            else:
                col1.error("""**:red[Attention: Bias ≥ TEa]**""")
        else:
            col1.error("""**:red[Imprecision (%CV) value can not be zero]**""")
        
        
        if not CV_input==0:
            col2.info(f"""
                    **:green[Sigmametric value (alternative)]** : **{round_half_up((CVI_input/CV_input),2)}**
                        """)
        else:
            col2.error("""**:red[Imprecision (%CV) value can not be zero]**""")
            
        if not TEa_input == 0:
            y_limit_min = 0
            y_limit_max = TEa_input
            x_limit_min = 0
            x_limit_max = TEa_input/2
            
            sigma_2 = TEa_input/2
            sigma_3 = TEa_input/3
            sigma_4 = TEa_input/4
            sigma_5 = TEa_input/5
            sigma_6 = TEa_input/6
            
            # Create a DataFrame with the data point
            data = {'Imprecision (%CV)': [CV_input], 'Bias (%)': [bias_input]}  # Assuming y=0 for simplicity
            df = pd.DataFrame(data)

            # Create a scatter plot using plotly express
            fig = px.scatter(df, x='Imprecision (%CV)', y='Bias (%)', title='OPSpecs Chart')

            # Add lines for sigma_2, sigma_3, sigma_4, sigma_5, and sigma_6
            fig.add_trace(px.line(x=[sigma_2, 0], y=[0, y_limit_max], line_shape='linear').data[0].update(line=dict(color='red',width=1)))
            fig.add_trace(px.line(x=[sigma_3, 0], y=[0, y_limit_max], line_shape='linear').data[0].update(line=dict(color='orange', width=1)))
            fig.add_trace(px.line(x=[sigma_4, 0], y=[0, y_limit_max], line_shape='linear').data[0].update(line=dict(color='purple', width=1)))
            fig.add_trace(px.line(x=[sigma_5, 0], y=[0, y_limit_max], line_shape='linear').data[0].update(line=dict(color='blue', width=1)))
            fig.add_trace(px.line(x=[sigma_6, 0], y=[0, y_limit_max], line_shape='linear').data[0].update(line=dict(color='green', width=1)))
            
            # Add annotations directly on the lines with adjusted angle
            fig.add_annotation(x=sigma_2/2+sigma_2/20, y=y_limit_max/2, text='2', showarrow=False, font=dict(color='red'), textangle=0)
            fig.add_annotation(x=sigma_3/2+sigma_3/20, y=y_limit_max/2, text='3', showarrow=False, font=dict(color='orange'), textangle=0)
            fig.add_annotation(x=sigma_4/2+sigma_4/20, y=y_limit_max/2, text='4', showarrow=False, font=dict(color='purple'), textangle=0)
            fig.add_annotation(x=sigma_5/2+sigma_5/20, y=y_limit_max/2, text='5', showarrow=False, font=dict(color='blue'), textangle=0)
            fig.add_annotation(x=sigma_6/2+sigma_6/20, y=y_limit_max/2, text='6', showarrow=False, font=dict(color='green'), textangle=0)
                    
            # Set x and y axis limits
            fig.update_xaxes(range=[x_limit_min, x_limit_max + x_limit_max*0.2], title_text='Allowable Imprecision (%CV)')
            fig.update_yaxes(range=[y_limit_min, y_limit_max + y_limit_max*0.1], title_text='Allowable Bias (%Bias)')
            # Set title color
            fig.update_layout(title=dict(text='OPSpecs Chart', font=dict(color='#cc0000')))
                    
            # Show the plot
            st.plotly_chart(fig, use_container_width=True)
            
    with st.expander("**:blue[Normalized OPSpecs chart for comparison of multliple test performances]**"):
        # Initialize an empty dataframe with the specified number of rows
        df_v2 = pd.DataFrame(
            [{"Test": None, "Bias (%)": None, "Imprecision (%CV)": None, "Total Allowable Error (TEa%)": None} for _ in range(number_of_rows)]
        )

        # Use st.data_editor to create an editable dataframe
        edited_df_v2 = st.data_editor(
            df_v2,
            column_config={
                "Test": st.column_config.TextColumn(
                    "Test",
                    max_chars=50,
                ),
                "Bias (%)": st.column_config.NumberColumn(
                    "Bias (%)",
                    help="Bias (%)",
                    min_value=0,
                    max_value=999999999999999999999999999999999999999,
                    format="%g",
                ),
                "Imprecision (%CV)": st.column_config.NumberColumn(
                    "Imprecision (%CV)",
                    help="Imprecision (%CV)",
                    min_value=0.0000000000001,
                    max_value=999999999999999999999999999999999999999,
                    format="%g",
                ),
                "Total Allowable Error (TEa%)": st.column_config.NumberColumn(
                    "Total Allowable Error (TEa%)",
                    help="Total Allowable Error (TEa%)",
                    min_value=0,
                    max_value=999999999999999999999999999999999999999,
                    format="%g",
                ),
            },
            hide_index=True, num_rows="dynamic"
        )  # An editable dataframe
        edited_df_v2 = pd.DataFrame(edited_df_v2)
        
        # Calculate normalized values
        edited_df_v2['Normalized Bias'] = 100 * edited_df_v2['Bias (%)'] / edited_df_v2['Total Allowable Error (TEa%)']
        edited_df_v2['Normalized CV'] = 100 * edited_df_v2['Imprecision (%CV)'] / edited_df_v2['Total Allowable Error (TEa%)']
        edited_df_v2['Sigmametric'] = (edited_df_v2['Total Allowable Error (TEa%)']-edited_df_v2['Bias (%)'])/edited_df_v2['Imprecision (%CV)']
        # Set plot limits
        x_limit_min_2, x_limit_max_2 = 0, 100  # Assuming CV is a percentage
        y_limit_min_2, y_limit_max_2 = 0, 100  # Assuming Bias is a percentage
        sigma_22 = x_limit_max_2/2
        sigma_33 = x_limit_max_2/3
        sigma_44 = x_limit_max_2/4
        sigma_55 = x_limit_max_2/5
        sigma_66 = x_limit_max_2/6

        # Create a scatter plot using plotly express
        fig = px.scatter(edited_df_v2, x='Normalized CV', y='Normalized Bias', text = 'Test', title='Normalized OPSpecs Chart')
        # Adjust text position
        fig.update_traces(textposition='top center')
        
        # Add lines for sigma_2, sigma_3, sigma_4, sigma_5, and sigma_6
        fig.add_trace(px.line(x=[x_limit_max_2/2, 0], y=[0, y_limit_max_2], line_shape='linear').data[0].update(line=dict(color='red',width=1)))
        fig.add_trace(px.line(x=[x_limit_max_2/3, 0], y=[0, y_limit_max_2], line_shape='linear').data[0].update(line=dict(color='orange', width=1)))
        fig.add_trace(px.line(x=[x_limit_max_2/4, 0], y=[0, y_limit_max_2], line_shape='linear').data[0].update(line=dict(color='purple', width=1)))
        fig.add_trace(px.line(x=[x_limit_max_2/5, 0], y=[0, y_limit_max_2], line_shape='linear').data[0].update(line=dict(color='blue', width=1)))
        fig.add_trace(px.line(x=[x_limit_max_2/6, 0], y=[0, y_limit_max_2], line_shape='linear').data[0].update(line=dict(color='green', width=1)))
            
        # Add annotations directly on the lines with adjusted angle
        fig.add_annotation(x=sigma_22/2+sigma_22/20, y=y_limit_max_2/2, text='2', showarrow=False, font=dict(color='red'), textangle=0)
        fig.add_annotation(x=sigma_33/2+sigma_33/20, y=y_limit_max_2/2, text='3', showarrow=False, font=dict(color='orange'), textangle=0)
        fig.add_annotation(x=sigma_44/2+sigma_44/20, y=y_limit_max_2/2, text='4', showarrow=False, font=dict(color='purple'), textangle=0)
        fig.add_annotation(x=sigma_55/2+sigma_55/20, y=y_limit_max_2/2, text='5', showarrow=False, font=dict(color='blue'), textangle=0)
        fig.add_annotation(x=sigma_66/2+sigma_66/20, y=y_limit_max_2/2, text='6', showarrow=False, font=dict(color='green'), textangle=0)
            
        # Set x and y axis limits
        fig.update_xaxes(range=[x_limit_min_2, x_limit_max_2/2 + x_limit_max_2*0.2/2], title_text='Normalized Imprecision (Normalized %CV)')
        fig.update_yaxes(range=[y_limit_min_2, y_limit_max_2  + y_limit_max_2*0.1], title_text='Normalized Bias (Normalized %Bias)')

        # Set title color
        fig.update_layout(title=dict(text='Normalized OPSpecs Chart', font=dict(color='#cc0000')))

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(edited_df_v2[['Test','Sigmametric']],hide_index=True)
    
    
