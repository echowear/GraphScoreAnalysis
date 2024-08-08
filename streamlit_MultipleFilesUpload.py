import streamlit as st
import pandas as pd
import json
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Function to extract user profile from JSON data
def extract_user_profile(data):
    return {
        'name': data.get('name', 'N/A'),
        'age': data.get('age', 'N/A')
    }

# Function to plot total scores
def plot_total_scores(df):
    fig = px.bar(df, y='Task Name', x='Total Score', color='File Name',
                orientation='h', title='Total Scores for Different Tasks',
                barmode='group', labels={'Total Score': 'Total Score', 'Task Name': 'Task Name'})
    st.plotly_chart(fig)

def plot_completion_times(df_completion_times):
    fig = px.box(df_completion_times, x='Task Name', y='Completion Time', color='File Name',
                 title='Completion Times for Different Tasks',
                 labels={'Completion Time': 'Completion Time (ms)', 'Task Name': 'Task Name'})
    st.plotly_chart(fig)

def plot_variance_error_rates(data_dict):
    task_names = list(data_dict.keys())
    variances = [data_dict[task]['variance'] for task in task_names]
    error_rates = [data_dict[task]['errorRates'] for task in task_names]
    file_names = [data_dict[task]['fileName'] for task in task_names]

    df_variance = pd.DataFrame({
        'Task Name': task_names,
        'Variance': variances,
        'File Name': file_names
    })

    fig_variance = px.bar(df_variance, x='Task Name', y='Variance', color='File Name',
                          title='Variances of Tasks with Multiple Trials',
                          labels={'Variance': 'Variance'})
    st.plotly_chart(fig_variance)

    fig_error_rates = go.Figure()
    for i, rates in enumerate(error_rates):
        if len(rates) > 0:  # Ensure there's data to plot
            fig_error_rates.add_trace(go.Scatter(y=rates, mode='lines', name=f'{task_names[i]} ({file_names[i]})'))

    fig_error_rates.update_layout(title='Error Rates of Tasks with Multiple Trials',
                                  xaxis_title='Trial',
                                  yaxis_title='Error Rate')
    st.plotly_chart(fig_error_rates)

def plot_serial_position_effects(task_names, primacy_effects, middle_effects, recency_effects, file_names):
    # Check if all lists are of the same length
    if len(task_names) != len(primacy_effects) or len(task_names) != len(middle_effects) or len(task_names) != len(recency_effects) or len(task_names) != len(file_names):
        st.error("Mismatch in lengths of lists for serial position effects.")
        return

    df = pd.DataFrame({
        'Task Name': task_names,
        'Primacy Effect': primacy_effects,
        'Middle Effect': middle_effects,
        'Recency Effect': recency_effects,
        'File Name': file_names
    })

    # Create separate bar charts for each file
    file_names_unique = df['File Name'].unique()
    for file_name in file_names_unique:
        file_df = df[df['File Name'] == file_name]
        
        # Melt data for Plotly Express
        file_df_melted = file_df.melt(id_vars=['Task Name'], value_vars=['Primacy Effect', 'Middle Effect', 'Recency Effect'],
                                      var_name='Effect Type', value_name='Effect Value')
        
        fig = px.bar(file_df_melted, x='Task Name', y='Effect Value', color='Effect Type',
                     color_discrete_map={'Primacy Effect': 'blue', 'Middle Effect': 'green', 'Recency Effect': 'red'},
                     title=f'Serial Position Effects for {file_name}',
                     labels={'Effect Value': 'Effect Value', 'Effect Type': 'Effect Type'})
        st.plotly_chart(fig)

    # Create radial lollipop chart for combined serial position effects
    df_melted = df.melt(id_vars=['Task Name', 'File Name'], value_vars=['Primacy Effect', 'Middle Effect', 'Recency Effect'],
                        var_name='Effect Type', value_name='Effect Value')

    fig = go.Figure()

    colors = {'Primacy Effect': 'blue', 'Middle Effect': 'green', 'Recency Effect': 'red'}

    for effect_type in df_melted['Effect Type'].unique():
        df_filtered = df_melted[df_melted['Effect Type'] == effect_type]
        fig.add_trace(go.Scatterpolar(
            r=df_filtered['Effect Value'],
            theta=df_filtered['Task Name'],
            mode='markers+lines',
            name=effect_type,
            text=df_filtered['File Name'],  # Add file name as text for hover information
            line=dict(color=colors[effect_type]),
            marker=dict(size=8, color=colors[effect_type])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
            angularaxis=dict(tickmode='array', tickvals=df['Task Name'].unique())
        ),
        title='Serial Position Effects Across Files',
        showlegend=True
    )

    st.plotly_chart(fig)

# Main Streamlit app
st.title('Score Analysis Dashboard')

# Sidebar for file selection
st.sidebar.title('File Selection')
uploaded_files = st.sidebar.file_uploader("Choose JSON files", type="json", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    user_profiles = []
    for uploaded_file in uploaded_files:
        try:
            data = json.load(uploaded_file)
            all_data.append((uploaded_file.name, data))
            user_profiles.append((uploaded_file.name, extract_user_profile(data)))
        except json.JSONDecodeError:
            st.error(f"File {uploaded_file.name} is not a valid JSON.")
    
    st.sidebar.title('User Profile Information')
    for i, (filename, user_profile) in enumerate(user_profiles):
        st.sidebar.markdown(f"**File {i+1}:** {filename}")
        st.sidebar.markdown(f"**Name:** {user_profile['name']}")
        st.sidebar.markdown(f"**Age:** {user_profile['age']}")

    if all_data:
        try:
            df_list = []
            completion_times_list = []
            task_data_dict = {}
            task_names = []
            primacy_effects = []
            middle_effects = []
            recency_effects = []
            file_names = []

            for filename, data in all_data:
                for task_name, task in data.items():
                    if isinstance(task, dict) and 'totalScore' in task:
                        task_clean_name = task_name.replace('TaskName.', '')
                        df_list.append({
                            'File Name': filename,
                            'Task Name': task_clean_name,
                            'Total Score': task['totalScore']
                        })
                    
                    if isinstance(task, dict) and 'analysisResult' in task:
                        analysis_result = task["analysisResult"]
                        if isinstance(analysis_result, dict) and "completionTimes" in analysis_result:
                            task_clean_name = task_name.replace('TaskName.', '')
                            for time in analysis_result["completionTimes"]:
                                completion_times_list.append({
                                    'File Name': filename,
                                    'Task Name': task_clean_name,
                                    'Completion Time': time
                                })
                        else:
                            completion_times_list.append({
                                'File Name': filename,
                                'Task Name': task_name.replace('TaskName.', ''),
                                'Completion Time': np.nan
                            })

                    if isinstance(task, dict):
                        serial_position_effects = task.get("serialPositionEffect", [])
                        for effect in serial_position_effects:
                            primacy_effects.append(effect.get("PrimacyEffect", 0))
                            middle_effects.append(effect.get("MiddleEffect", 0))
                            recency_effects.append(effect.get("RecencyEffect", 0))
                            task_clean_name = task_name.replace('TaskName.', '')
                            task_names.append(task_clean_name)
                            file_names.append(filename)
                            # For variance and error rates
                            if task_clean_name not in task_data_dict:
                                task_data_dict[task_clean_name] = {
                                    'variance': task.get("analysisResult", {}).get("variance", 0),
                                    'errorRates': task.get("analysisResult", {}).get("errorRates", []),
                                    'fileName': filename
                                }
                            task_data_dict[task_clean_name]['fileName'] = filename

            combined_df = pd.DataFrame(df_list)
            pivot_df = combined_df.pivot(index='Task Name', columns='File Name', values='Total Score')

            st.subheader('Data Table for Total Scores of Different Tasks')
            st.write(pivot_df)

            st.subheader('Total Scores for Different Tasks')
            plot_total_scores(combined_df)
            
            df_completion_times = pd.DataFrame(completion_times_list)
            st.subheader('Completion Times for Different Tasks')
            plot_completion_times(df_completion_times)

            st.subheader('Variance and Error Rates for Tasks with Multiple Trials')
            plot_variance_error_rates(task_data_dict)

            st.subheader('Serial Position Effects')
            plot_serial_position_effects(task_names, primacy_effects, middle_effects, recency_effects, file_names)

        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")
