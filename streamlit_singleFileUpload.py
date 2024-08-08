import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os


# Function to display a centered title with underline
def display_title(title):
    st.markdown(
        f"<div style='display: flex; align-items: center; justify-content: center; border-bottom: 2px solid #2f3947;'><h1>{title}</h1></div>",
        unsafe_allow_html=True,
    )

# Function to extract user profile information from JSON data
def extract_user_profile(data):
    user_profile = {
        "name": None,
        "age": None
    }
    
    try:
        # Extract user profile data from JSON
        if isinstance(data, dict):
            user_profile["name"] = data.get("UserProfile", {}).get("name")
            user_profile["age"] = data.get("UserProfile", {}).get("age")

    except Exception as e:
        st.error(f"Error extracting user profile information: {e}")
    
    return user_profile

# Function to plot Total Scores with enhanced aesthetics
def plot_total_scores(task_names, total_scores):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(task_names, total_scores, color='skyblue', edgecolor='black')
    plt.title('Total Scores for Different Tasks', fontsize=18)
    plt.xlabel('Task Name', fontsize=14)
    plt.ylabel('Total Score', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--')
    plt.ylim(0, max(total_scores) * 1.1)
    plt.legend([bars[0]], ['Total Score'], loc='upper right', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt)

# Function to plot Completion Times with enhanced aesthetics
def plot_completion_times(df_completion_times):
    plt.figure(figsize=(12, 6))
    df_completion_times.boxplot(patch_artist=True, boxprops=dict(facecolor='skyblue', edgecolor='black'))
    plt.title('Completion Times for Different Tasks', fontsize=18)
    plt.ylabel('Completion Time (ms)', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt)

# Function to plot Variance and Error Rates with enhanced aesthetics
def plot_variance_error_rates(task_names, variances, error_rates):
    plt.figure(figsize=(12, 12))

    # Plot variance
    plt.subplot(2, 1, 1)
    plt.bar(task_names, variances, color='skyblue', edgecolor='black')
    plt.title('Variances of Tasks with Multiple Trials', fontsize=18)
    plt.xlabel('Task Name', fontsize=14)
    plt.ylabel('Variance', fontsize=14)

    # Plot error rates
    plt.subplot(2, 1, 2)
    for i, rates in enumerate(error_rates):
        plt.plot(rates, label=task_names[i])
    plt.title('Error Rates of Tasks with Multiple Trials', fontsize=18)
    plt.xlabel('Trial', fontsize=14)
    plt.ylabel('Error Rate (%)', fontsize=14)
    plt.legend(fontsize=12)

    plt.subplots_adjust(hspace=0.5)
    plt.tight_layout()
    st.pyplot(plt)

# Function to plot Serial Position Effects with enhanced aesthetics
def plot_serial_position_effects(task_names, primacy_effects, middle_effects, recency_effects):
    plt.figure(figsize=(12, 6))
    bar_width = 0.35

    plt.bar(task_names, primacy_effects, bar_width, label='Primacy', color='r', edgecolor='black')
    plt.bar(task_names, middle_effects, bar_width, bottom=primacy_effects, label='Middle', color='g', edgecolor='black')
    plt.bar(task_names, recency_effects, bar_width, bottom=np.array(primacy_effects) + np.array(middle_effects),
            label='Recency', color='b', edgecolor='black')

    plt.xlabel('Task', fontsize=14)
    plt.ylabel('Effect Value', fontsize=14)
    plt.title('Serial Position Effects', fontsize=18)
    plt.xticks(rotation=45, fontsize=12)
    plt.legend(fontsize=12)

    plt.tight_layout()
    st.pyplot(plt)

# Function to plot histogram for total scores
def plot_histogram(total_scores, group_name):
    plt.figure(figsize=(10, 6))
    sns.histplot(total_scores, bins='auto', edgecolor='black', alpha=0.7, color='skyblue')
    plt.title(f'Histogram of Total Scores in {group_name}', fontsize=18)
    plt.xlabel('Total Score', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

# Function to plot KDE plot for total scores
def plot_kde(total_scores, group_names, colors):
    plt.figure(figsize=(10, 6))
    for scores, color, group_name in zip(total_scores, colors, group_names):
        sns.kdeplot(scores, shade=True, color=color, label=group_name)
    plt.title('KDE Plot of HC and MCI Comparisons', fontsize=18)
    plt.xlabel('Total Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def plot_kde(total_scores, group_names, colors):
    plt.figure(figsize=(10, 6))
    for scores, label, color in zip(total_scores, group_names, colors):
        sns.kdeplot(scores, shade=True, color=color, label=label)

    plt.title('KDE Plot', fontsize=18)
    plt.xlabel('Total Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def calculate_total_scores(data):
    keys_to_sum = [
        "FigureSelectAll", "FigureRecallAll", "VerbalRecallAll", "DigitSpanAll",
        "OrientationAll", "SemanticChoiceAll", "VerbalLearningAll", "ComputationAll",
        "StoryMemoryAll", "SemanticRelateAll"
    ]
    
    # Find the number of persons (based on the length of the first key)
    num_persons = len(data[keys_to_sum[0]])
    
    # Initialize total scores list for all persons
    total_scores = [0] * num_persons
    
    # Sum up the scores for each person across the specified keys
    for key in keys_to_sum:
        if key in data and isinstance(data[key], list):
            for i in range(num_persons):
                total_scores[i] += data[key][i]
    
    # Sum up non-list scores for each person
    for key, value in data.items():
        if key not in keys_to_sum and isinstance(value, (int, float)):
            for i in range(num_persons):
                total_scores[i] += value
    
    return total_scores

# Function to extract finalScore from JSON files
def extract_final_score(file_path):
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            if 'finalScore' in data:
                return data['finalScore']
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON from {os.path.basename(file_path)}: {e}")
    return None

# Function to plot HC and MCI comparisons
def plot_hc_mci_comparisons(all_total_scores, labels):
    plt.figure(figsize=(12, 6))
    for i, (total_scores, label) in enumerate(zip(all_total_scores, labels)):
        plt.hist(total_scores, bins='auto', alpha=0.7, label=label, edgecolor='black')
    plt.title('Histogram of Total Scores in HC and MCI', fontsize=18)
    plt.xlabel('Total Score', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.legend(loc='upper right', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)


# Function to read and extract finalScore from JSON files in rimcat
def extract_rimcat_final_score(file_path):
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            if 'finalScore' in data:
                return data['finalScore']
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {os.path.basename(file_path)}: {e}")
    return None
# File paths
file1 = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/scores_2024604/1717171773410.json'
file2 = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/scores_20240531/1717457009365.json'
file3 = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/scores_20240531/1717456424749.json'
file_hc = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/summaries_groups/HC.json'
file_mci = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/summaries_groups/MCI.json'

# Sidebar for navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to', ['Overview', 'HC Group Analysis', 'MCI Group Analysis', 'HC and MCI Comparisons','RIMCAT and rimcat Analysis', 'Custom File Analysis'])

# Initialize the data variable
data = None
user_profile = None

# Display the selected page
if page == 'Overview':
    display_title('Welcome to Report Analysis')
    st.write("""
        This application allows you to analyze and visualize the JSON data files from the Ecowear project.
        You can select different analysis options from the sidebar to explore the data.
        
    """)

# Display the selected page
elif page == 'HC Group Analysis':
    try:
        with open(file_hc, 'r') as f:
            data = json.load(f)
        
        # Initialize variables to hold total scores
        num_persons = len(data["FigureSelectAll"])
        total_scores = [0] * num_persons

        for key, value in data.items():
            if isinstance(value, list):
                # If value is a list, add each element to corresponding person's score
                for i in range(num_persons):
                    total_scores[i] += value[i]
            elif isinstance(value, (int, float)):
                # If value is a single number, add it to each person's score
                for i in range(num_persons):
                    total_scores[i] += value

        overall_total_score = sum(total_scores)
        group_name = 'HC'

        st.subheader(f'{group_name} Total Scores')
        st.write(f"Overall total score: {overall_total_score}")

        df = pd.DataFrame({
            'Person': [f'Person {i+1}' for i in range(num_persons)],
            'Total Score': total_scores
        })

        st.subheader(f'{group_name} Total Scores Data Table')
        st.write(df)

        st.subheader(f'Plot of Total Scores in {group_name}')
        plot_type = st.radio("Select plot type:", ("Histogram", "KDE"))
        if plot_type == "Histogram":
            plot_histogram(total_scores, group_name)
        elif plot_type == "KDE":
            colors = ['blue']  # Adjust colors as needed
            plot_kde([total_scores], [group_name], colors)
    
    except Exception as e:
        st.error(f"Error processing HC data: {e}")

elif page == 'MCI Group Analysis':
    try:
        with open(file_mci, 'r') as f:
            data = json.load(f)
        
        # Initialize variables to hold total scores
        num_persons = len(data["FigureSelectAll"])
        total_scores = [0] * num_persons

        for key, value in data.items():
            if isinstance(value, list):
                # If value is a list, add each element to corresponding person's score
                for i in range(num_persons):
                    total_scores[i] += value[i]
            elif isinstance(value, (int, float)):
                # If value is a single number, add it to each person's score
                for i in range(num_persons):
                    total_scores[i] += value

        overall_total_score = sum(total_scores)
        group_name = 'MCI'

        st.subheader(f'{group_name} Total Scores')
        st.write(f"Overall total score: {overall_total_score}")

        df = pd.DataFrame({
            'Person': [f'Person {i+1}' for i in range(num_persons)],
            'Total Score': total_scores
        })

        st.subheader(f'{group_name} Total Scores Data Table')
        st.write(df)

        st.subheader(f'Plot of Total Scores in {group_name}')
        plot_type = st.radio("Select plot type:", ("Histogram", "KDE"))
        if plot_type == "Histogram":
            plot_histogram(total_scores, group_name)
        elif plot_type == "KDE":
            colors = ['green']  # Adjust colors as needed
            plot_kde([total_scores], [group_name], colors)
    
    except Exception as e:
        st.error(f"Error processing MCI data: {e}")


elif page == 'HC and MCI Comparisons':
    try:
        import json
        # File paths for HC and MCI data
        json_files = [file_hc, file_mci]
        all_total_scores = []
        all_labels = ["HC", "MCI"]  # Labels for HC and MCI groups

        for json_file in json_files:
            with open(json_file) as f:
                data = json.load(f)  # Load JSON data from file
            total_scores = calculate_total_scores(data)  # Pass loaded JSON data
            all_total_scores.append(total_scores)
            st.write(f"Total scores from {json_file}: {total_scores}")

        st.subheader('HC and MCI Comparison Plot')
        plot_type = st.radio("Select plot type:", ("Histogram", "KDE"))

        if plot_type == "Histogram":
            plot_hc_mci_comparisons(all_total_scores, all_labels)
        elif plot_type == "KDE": 
            plt.figure(figsize=(12, 6))
            colors = ['blue', 'green']  # Colors for HC and MCI groups
            for scores, label, color in zip(all_total_scores, all_labels, colors):
                sns.kdeplot(scores, shade=True, label=label, color=color, alpha=0.4)
            plt.title('KDE Plots of Total Scores in HC and MCI')
            plt.xlabel('Total Score')
            plt.ylabel('Density')
            plt.legend()
            st.pyplot(plt)
    except Exception as e:
        st.error(f"Error processing HC and MCI comparison data: {e}")


elif page == 'RIMCAT and rimcat Analysis':
        # Directories and files
        RIMCAT_json_directory = '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/scores_2024604'
        rimcat_json_files = [
            '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/summaries_groups/HC.json',
            '/Users/sanjanamortha/Desktop/Desktop/Ecowear/Data_analysis/summaries_groups/MCI.json'
        ]
        
        RIMCAT_final_scores = []
        for filename in os.listdir(RIMCAT_json_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(RIMCAT_json_directory, filename)
                final_score = extract_final_score(file_path)
                if final_score is not None:
                    RIMCAT_final_scores.append(final_score)
        
        all_total_scores = []
        labels = ["HC", "MCI"]
        
        for json_file in rimcat_json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)  # Load JSON data from file
                total_scores = calculate_total_scores(data)  # Calculate total scores
                all_total_scores.append(total_scores)
            except FileNotFoundError:
                st.error(f"File {json_file} not found.")
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON in {json_file}: {e}")
        
        rimcat_total_scores = all_total_scores[0] + all_total_scores[1]
        
        # Plotting with Seaborn and Matplotlib
        st.title('KDE Plots of rimcat and RIMCAT Final Scores')
        
        sns.set(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if RIMCAT_final_scores:
            sns.kdeplot(RIMCAT_final_scores, shade=True, label='RIMCAT Final Scores', color='blue', ax=ax)
        
        if rimcat_total_scores:
            sns.kdeplot(rimcat_total_scores, shade=True, label='rimcat Total Scores', color='green', ax=ax)
        
        ax.set_title('KDE Plots of rimcat and RIMCAT Final Scores')
        ax.set_xlabel('Score')
        ax.set_ylabel('Density')
        ax.legend()
        
        # Display plot in Streamlit
        st.pyplot(fig)



elif page == 'Custom File Analysis':
    # Sidebar for file selection
    st.sidebar.title('File Selection')
    selected_file = st.sidebar.selectbox('Select a file', ('file1', 'file2', 'file3', 'Upload your own'))

    # Load the selected file
    if selected_file == 'Upload your own':
        uploaded_file = st.sidebar.file_uploader("Choose a JSON file", type="json")
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                user_profile = extract_user_profile(data)
            except json.JSONDecodeError:
                st.error("Uploaded file is not a valid JSON.")

    else:
        # Determine which file is selected and load its data
        if selected_file == 'file1':
            selected_filepath = file1
        elif selected_file == 'file2':
            selected_filepath = file2
        elif selected_file == 'file3':
            selected_filepath = file3

        try:
            with open(selected_filepath, 'r') as f:
                data = json.load(f)
                user_profile = extract_user_profile(data)
        except json.JSONDecodeError:
            st.error("Selected file is not a valid JSON.")
        except Exception as e:
            st.error(f"Error loading selected file: {e}")

    # Display user profile information in the sidebar if available
    if user_profile:
        st.sidebar.title('User Profile Information')
        st.sidebar.markdown(f"**Name:** {user_profile['name']}")
        st.sidebar.markdown(f"**Age:** {user_profile['age']}")

    # Ensure data is loaded before processing
    if data:
        try:
            task_names = []
            total_scores = []

            for task in data.values():
                if isinstance(task, dict) and 'totalScore' in task:
                    task_name = task['taskName'].replace('TaskName.', '')
                    task_names.append(task_name)
                    total_scores.append(task['totalScore'])

            df = pd.DataFrame({
                'Task Name': task_names,
                'Total Score': total_scores
            })

            display_title('SCORES REPORT')
            st.subheader('Data Table for Total Scores of Different Tasks')
            st.write(df)

            st.subheader('Total Scores for Different Tasks')
            plot_total_scores(task_names, total_scores)

            completion_times_data = {}
            for task, info in data.items():
                if isinstance(info, dict) and "analysisResult" in info:
                    analysis_result = info["analysisResult"]
                    if isinstance(analysis_result, dict) and "completionTimes" in analysis_result:
                        completion_times_data[task] = analysis_result["completionTimes"]
                    else:
                        completion_times_data[task] = [np.nan]

            max_length = max(len(times) for times in completion_times_data.values())

            for task in completion_times_data:
                completion_times_data[task] += [np.nan] * (max_length - len(completion_times_data[task]))

            df_completion_times = pd.DataFrame(completion_times_data)

            st.subheader('Completion Times for Different Tasks Data Table')
            st.write(df_completion_times)

            st.subheader('Completion Time Distribution')
            plot_completion_times(df_completion_times)

            task_names = []
            variances = []
            error_rates = []

            for task_name, task_data in data.items():
                if isinstance(task_data, dict):
                    analysis_result = task_data.get("analysisResult", {})
                    task_responses = task_data.get("taskResponses", {})

                    if len(task_responses) > 1:
                        task_names.append(task_name)
                        variances.append(analysis_result.get("variance", 0))
                        error_rates.append(analysis_result.get("errorRates", []))

            st.subheader('Variance and Error Rates for Tasks with Multiple Trials')
            plot_variance_error_rates(task_names, variances, error_rates)

            task_names = []
            primacy_effects = []
            middle_effects = []
            recency_effects = []

            for task_data in data.values():
                if isinstance(task_data, dict) and 'taskName' in task_data:
                    task_name = task_data['taskName'].split('.')[-1]
                    task_names.append(task_name)
                    serial_position_effect = task_data.get('serialPositionEffect', [{}])[0]
                    primacy_effects.append(serial_position_effect.get('PrimacyEffect', 0.0))
                    middle_effects.append(serial_position_effect.get('MiddleEffect', 0.0))
                    recency_effects.append(serial_position_effect.get('RecencyEffect', 0.0))

            st.subheader('Serial Position Effects per Task')
            plot_serial_position_effects(task_names, primacy_effects, middle_effects, recency_effects)

        except Exception as e:
            st.error(f"Error processing data: {e}")
    else:
        st.write("Please select a file to display the analysis.")