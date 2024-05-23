import streamlit as st
import requests
import time
import re
import pandas as pd

sample_prompts = {
    "Gene": [
        "Several 7SL RNA encoding sequences and various intergenic spacers were amplified from the individual Hind III fragments of about 13 and 28 kb.",
        "Phosphorylation of myosin binding subunit MBS of myosin phosphatase by Rho kinase in vivo",
        "Previously we showed that the APRE is a cytokine tumor necrosis factor alpha TNFalpha inducible enhancer by binding the heterodimeric nuclear factor kappaB NF kappaB complex Rel A x NF kappaB1"
    ],
    "Disease": [
        "FLA-63 , a dopamine-beta-oxidase inhibitor , did not have any effect on the hypotension , bradycardia or reflex-enhancing effect of L-dopa",
        "Microangiopathic hemolytic anemia complicating FK506 (tacrolimus) therapy.",
        "Lithium-associated cognitive and functional deficits reduced by a switch to divalproex sodium: a case series.",
        "Six epidemiologic studies in the United States and Europe indicate that habitual use of phenacetin is associated with the development of chronic renal failure and end - stage renal disease ( ESRD ) , with a relative risk in the range of 4 to 19."
    ],
    "Chemical": [
        "Effects of acetylsalicylic acid , dipyridamole , and hydrocortisone on epinephrine - induced myocardial injury in dogs.",
        "The antinociceptive effect of 3 alpha-tropyl 2-(p-bromophenyl) propionate[ (+/-)-PG-9 ] (10-40 mg kg-1s).",
        "Acetylsalicylic acid, dipyridamole, and hydrocortisone all appear to have cardioprotective effects when tested in this model"
    ],
    "Species": [
        "Aureus SA113 wild type and its isogenic graRS deletion mutant by the human cathelicidin LL-37 or human neutrophil granulocytes in vitro , and the ability to cause infection in vivo.",
        "We show here that graRS deletion considerably alters bacterial surface charge , increases susceptibility to killing by human neutrophils or the defense peptide LL-37 , and attenuates virulence of S type.",
        "Background Staphylococcus aureus , a frequent cause of human infections, is highly resistant to antimicrobial factors of the innate immune system such as cationic antimicrobial peptides (CAMPs) [1, 2] which are produced by epithelial cells and neutrophils [3, 4]"
    ]
}

# API configurations for both Bloom and Gemma models based on the entity type
model_paths = {
    "Gene": {
        "Bloom": "MayankD/bloom3b_bc2gm_gene_5epochs",
        "Gemma": "MayankD/gemma-ft-bc2gm_gene_5epochs"
    },
    "Disease": {
        "Bloom": "MayankD/bloom3b_bc5cdr_disease_5epochs",
        "Gemma": "MayankD/gemma-ft-bc5cdr_disease_5epochs"
    },
    "Chemical": {
        "Bloom": "MayankD/bloom3b_bc5cdr_chemical_5epochs",
        "Gemma": "MayankD/gemma-ft-bc5cdr_chemical_5epochs"
    },
    "Species": {
        "Bloom": "MayankD/bloom3b_BioNLP11ID_species_5epochs",
        "Gemma": "MayankD/gemma-ft-BioNLP11ID_species_5epochs"
    }
}

# API base URL
API_BASE_URL = "https://api-inference.huggingface.co/models"
headers = {f"Authorization": "Bearer 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"}

def query_model(model_name, payload):
    try:
        response = requests.post(f"{API_BASE_URL}/{model_name}", headers=headers, json=payload, timeout=600)
    except Exception as e:
        st.warning(e, response.json())
    return response.json()

def process_response(model_name, prompt):
    # Determine entity type based on model name (assuming model names are descriptive)
    if 'disease' in model_name.lower():
        entity_type = 'Disease'
    elif 'gene' in model_name.lower():
        entity_type = 'GENE'
    elif 'chemical' in model_name.lower():
        entity_type = 'Chemical'
    elif 'species' in model_name.lower():
        entity_type = 'Organism'
    else:
        entity_type = 'Unknown'  # Fallback if model name doesn't contain entity indicator

    output = query_model(model_name, {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200}
    })

    try:
        o_list = output[0]['generated_text'].split("Response:\n")[-1].strip("[").strip("]").replace("'", "").split(", ")
        response = {
            f"B-{entity_type}": [],
            f"I-{entity_type}": [],
            f"E-{entity_type}": [],
            f"S-{entity_type}": []
        }
        for item in o_list:
            key, value = item.split(":")
            response[key].append(value.strip())
        print(response)
        return response
    except Exception as e:
        # Log error or handle it appropriately
        # st.warning(f"An error occurred: {str(e)}")
        return {}


# Function to highlight entities in the text with color coding based on entity type
def highlight_text(text, entities, entity_type):
    if text:
        # Define colors for different entity types
        color_map = {
            'Gene': {
                'B-GENE': 'lightblue',
                'I-GENE': 'deepskyblue',
                'E-GENE': 'dodgerblue',
                'S-GENE': 'blue'
            },
            'Disease': {
                'B-Disease': 'yellow',
                'I-Disease': 'khaki',
                'E-Disease': 'goldenrod',
                'S-Disease': 'darkgoldenrod'
            },
            'Chemical': {
                'B-Chemical': 'lavender',
                'I-Chemical': 'thistle',
                'E-Chemical': 'plum',
                'S-Chemical': 'orchid'
            },
            'Species': {
                'B-Organism': 'salmon',
                'I-Organism': 'lightcoral',
                'E-Organism': 'indianred',
                'S-Organism': 'red'
            }
        }

        # Use a default color if the entity type or specific tag is not found
        default_color = 'lightgray'
        colors = color_map.get(entity_type, {f'B-{entity_type}': default_color,
                                             f'I-{entity_type}': default_color,
                                             f'E-{entity_type}': default_color,
                                             f'S-{entity_type}': default_color})

        # Highlight the text for each entity found
        for tag_type in entities:
            color = colors.get(tag_type, default_color)
            for entity in entities[tag_type]:
                # Ensure that we only replace whole words to avoid partial text modifications
                pattern = re.compile(r'\b' + re.escape(entity.strip()) + r'\b', re.IGNORECASE)
                text = pattern.sub(f'<mark style="background-color: {color};">{entity}</mark>', text)
        return text
    else:
        return "Oops... Try a better prompt"


# st.title("BioNER Comparison: Bloom vs Gemma")

# if st.sidebar.text_input("Enter Passkey:", type='password')=="38289":
#     def gen(prompt, entity_type):
#         if colb2.button("Generate"):
#             st.toast("Generating...")
#             if prompt:
#                 col1, col2 = st.columns(2)

#                 # Bloom model processing
#                 start_time = time.time()
#                 response_bloom = process_response(model_paths[entity_type]["Bloom"], prompt)
#                 if  time.time() - start_time < 6:
#                     st.toast("Just few seconds more...")
#                     time.sleep(20)
#                     response_bloom = process_response(model_paths[entity_type]["Bloom"], prompt)
                    
#                 highlighted_text_bloom = highlight_text(prompt, response_bloom, entity_type)
#                 col1.write(f"### NER Tags from Bloom ({entity_type}):")
#                 col1.markdown(highlighted_text_bloom, unsafe_allow_html=True)
#                 processing_time1 = time.time() - start_time
#                 col1.success(f"Processed in {processing_time1:.2f} seconds")

#                 # Gemma model processing
#                 start_time = time.time()
#                 response_gemma = process_response(model_paths[entity_type]["Gemma"], prompt)
#                 if  time.time() - start_time < 6:
#                     st.toast("Just few seconds more...")
#                     time.sleep(20)
#                     response_bloom = process_response(model_paths[entity_type]["Gemma"], prompt)
                    
#                 highlighted_text_gemma = highlight_text(prompt, response_gemma, entity_type)
#                 col2.write(f"### NER Tags from Gemma ({entity_type}):")
#                 col2.markdown(highlighted_text_gemma, unsafe_allow_html=True)
#                 processing_time2 = time.time() - start_time
#                 col2.success(f"Processed in {processing_time2:.2f} seconds")
#             else:
#                 st.warning("Please enter a prompt.")
                
#     st.sidebar.success("Correct Passkey")
#     c1,c2 = st.columns([5,1])
#     entity_type = c2.selectbox("Select Entity Type", list(model_paths.keys()))
    
#      # If user has not clicked the "Try your prompt" button, show sample prompts
#     colb1,colb2=st.columns([3,1.05])
#     use_custom_prompt = colb1.button("Try your prompt")

#     if use_custom_prompt:
#         prompt = c1.text_area("Enter your prompt:", placeholder="Type here...", key="prompt_1", height=150).strip()
#         gen(prompt=prompt, entity_type=entity_type)
#     else:
#         prompt = c1.selectbox(label="Select one", options=sample_prompts[entity_type], key="sample_prompt")
#         gen(prompt=prompt, entity_type=entity_type)
# else:
#     st.warning("Wrong Passkey. Try again.")
def format_response_for_comparison(response):
    # Flatten the dictionary to a list of (Type, Entity)
    formatted_data = []
    for entity_type, entities in response.items():
        for entity in entities:
            formatted_data.append((entity_type, entity))
    return formatted_data

def compare_entities(response_bloom, response_gemma):
    try:
        # Flatten responses
        bloom_data = format_response_for_comparison(response_bloom)
        gemma_data = format_response_for_comparison(response_gemma)
        
        # Convert lists of tuples to DataFrames
        df_bloom = pd.DataFrame(bloom_data, columns=['Type', 'Entity'])
        df_gemma = pd.DataFrame(gemma_data, columns=['Type', 'Entity'])
        
        # Create a full outer join to compare entities
        df_comparison = pd.merge(df_bloom, df_gemma, on=['Entity', 'Type'], how='outer', indicator=True)
        df_comparison['Source'] = df_comparison['_merge'].replace({'left_only': 'Bloom', 'right_only': 'Gemma', 'both': 'Both'})
        df_comparison.drop('_merge', axis=1, inplace=True)

        st.write("### Comparative Analysis of Entity Recognition")
        st.dataframe(df_comparison)
        return df_comparison
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        
def display_model_inference(df_comparison):
    # Counts by source
    source_counts = df_comparison['Source'].value_counts()
    st.write("### Model Comparison Insights")

    # Displaying counts
    st.write("#### Entity Detection Counts:")
    st.write(f"- **Both Models Detected**: {source_counts.get('Both', 0)} entities")
    st.write(f"- **Only Bloom Detected**: {source_counts.get('Bloom', 0)} entities")
    st.write(f"- **Only Gemma Detected**: {source_counts.get('Gemma', 0)} entities")

    # Analyzing proportions
    total_entities = source_counts.sum()
    if total_entities > 0:
        both_pct = (source_counts.get('Both', 0) / total_entities) * 100
        bloom_only_pct = (source_counts.get('Bloom', 0) / total_entities) * 100
        gemma_only_pct = (source_counts.get('Gemma', 0) / total_entities) * 100
        
        st.write("#### Proportional Analysis of Entity Detections:")
        st.write(f"- **Entities Detected by Both Models**: {both_pct:.2f}% of total detections")
        st.write(f"- **Entities Detected Only by Bloom**: {bloom_only_pct:.2f}% of total detections")
        st.write(f"- **Entities Detected Only by Gemma**: {gemma_only_pct:.2f}% of total detections")
        
st.title("BioNER Comparison: Bloom vs Gemma")

# Toggle for demo mode
demo_mode = st.checkbox("Demo Mode")

if st.sidebar.text_input("Enter Passkey:", type='password') == "38289":
    st.sidebar.success("Correct Passkey")
    
    # Select entity type regardless of mode
    entity_type = st.sidebar.selectbox("Select Entity Type", list(model_paths.keys()))

    def generate_entities(prompt, entity_type):
        if prompt:
            col1, col2 = st.columns(2)
            def bloom():
                # Bloom model processing
                start_time = time.time()
                response_bloom = process_response(model_paths[entity_type]["Bloom"], prompt)
                if  time.time() - start_time < 6:
                        st.toast("Just few seconds more...")
                        time.sleep(20)
                        response_bloom = process_response(model_paths[entity_type]["Bloom"], prompt)
                highlighted_text_bloom = highlight_text(prompt, response_bloom, entity_type)
                col1.write(f"### NER Tags from Bloom ({entity_type}):")
                col1.markdown(highlighted_text_bloom, unsafe_allow_html=True)
                processing_time1 = time.time() - start_time
                col1.success(f"Processed in {processing_time1:.2f} seconds")
                return response_bloom
            def gemma():
                # Gemma model processing
                start_time = time.time()
                response_gemma = process_response(model_paths[entity_type]["Gemma"], prompt)
                if  time.time() - start_time < 6:
                        st.toast("Just few seconds more... for Gemma Model")
                        time.sleep(20)
                        response_bloom = process_response(model_paths[entity_type]["Gemma"], prompt)
                highlighted_text_gemma = highlight_text(prompt, response_gemma, entity_type)
                col2.write(f"### NER Tags from Gemma ({entity_type}):")
                col2.markdown(highlighted_text_gemma, unsafe_allow_html=True)
                processing_time2 = time.time() - start_time
                col2.success(f"Processed in {processing_time2:.2f} seconds")
                return response_gemma
            
            r_bloom=bloom()
            r_gemma=gemma()            
            
            st.write("---")
            if r_bloom!={} and r_bloom !={}:
                display_model_inference(compare_entities(r_bloom, r_gemma))
                
        else:
            st.warning("Please enter a prompt.")

        
    if demo_mode:
        # Show the dropdown for sample prompts if in demo mode
        prompt = st.selectbox("Select a sample prompt:", sample_prompts[entity_type])
        if st.button("Generate from Sample"):
            generate_entities(prompt, entity_type)
    else:
        # Allow users to enter their own prompt if not in demo mode
        user_prompt = st.text_area("Enter your prompt:", placeholder="Type here...", key="custom_prompt_", height=150).strip()
        if st.button("Generate from Text"):
            generate_entities(user_prompt, entity_type)
            
    
            
else:
    st.warning("Wrong Passkey. Try again.")