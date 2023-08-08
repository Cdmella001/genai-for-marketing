# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Audience and Insight finder: 
- Create a conversational interface with data by translating from natural language to SQL queries.
"""

import streamlit as st

from google.cloud import bigquery

import utils_codey
import utils_config
from vertexai.preview.language_models import TextGenerationModel
import vertexai
import utils_default_image_text


# Set project parameters
PROJECT_ID = utils_config.get_env_project_id()
LOCATION = utils_config.LOCATION
MODEL_NAME = utils_config.CODE_MODEL_NAME

DATASET_ID = 'cdp_dataset'
TAG_NAME = 'llmcdptemplate'

TAG_TEMPLATE_NAME = f'projects/{PROJECT_ID}/locations/{LOCATION}/tagTemplates/{TAG_NAME}'
QUERY = f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.TABLES` WHERE table_name NOT LIKE "%metadata%"'

bqclient = bigquery.Client(project=PROJECT_ID)
vertexai.init(project=PROJECT_ID, location=LOCATION)
llm = TextGenerationModel.from_pretrained(utils_config.TEXT_MODEL_NAME)

# State variables for code generation and data preview
PAGE_KEY_PREFIX = "TalkToData"
PREVIEW_TABLES_KEY = f"{PAGE_KEY_PREFIX}_Preview_Tables"
RESULT_PREVIEW_QUERY_KEY = f"{PAGE_KEY_PREFIX}_Result_Preview_Query"
RESULT_FINAL_QUERY_KEY = f"{PAGE_KEY_PREFIX}_Result_Final_Query"
GENCODE_KEY = f"{PAGE_KEY_PREFIX}_Gen_Code"
PROMPT_TEMPLATE_KEY = f"{PAGE_KEY_PREFIX}_Prompt_Template"
DATASET_METADATA_KEY = f"{PAGE_KEY_PREFIX}_Dataset_Metadata"

st.set_page_config(page_title="Audiences", 
                   page_icon='/app/images/favicon.png')

import utils_styles
utils_styles.sidebar_apply_style(
    style=utils_styles.style_sidebar,
    image_path='/app/images/menu_icon_2.png'
)

cols = st.columns([15, 85])
with cols[0]:
    st.image('/app/images/audience_icon.png')
with cols[1]:
    st.title('Audiences')

st.write(
    """
    This page provides instructions on how to extract data from BigQuery using natural language and the PaLM API. 
    PaLM is a large language model from Google AI that can understand and respond to natural language queries. 
    By using PaLM, you can ask questions about your data in plain English, and PaLM will generate the 
    SQL queries necessary to retrieve the data.
    """
)

# =========================== Data preview =====================================

st.subheader('Data preview')
st.write('Click to preview the CDP dataset tables')
preview_button = st.button('Preview tables')

if preview_button:
    if PREVIEW_TABLES_KEY in st.session_state:
        del st.session_state[PREVIEW_TABLES_KEY]
    else:
        st.session_state[PREVIEW_TABLES_KEY] = [
            {'query': f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.customers` LIMIT 3', 'name': 'customers'},
            {'query': f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.events` LIMIT 3', 'name': 'events'},
            {'query': f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.transactions` LIMIT 3', 'name': 'transactions'}]

if PREVIEW_TABLES_KEY in st.session_state:
    if RESULT_PREVIEW_QUERY_KEY not in st.session_state:
        result_query = []
        with st.spinner('Querying BigQuery...'):
            for preview_table in st.session_state[PREVIEW_TABLES_KEY]:
                result_query.append({
                    "name": preview_table['name'],
                    "dataframe": bqclient.query(preview_table['query']).to_dataframe()
                })
        st.session_state[RESULT_PREVIEW_QUERY_KEY] = result_query
    
    for result in st.session_state[RESULT_PREVIEW_QUERY_KEY]:
        st.write(f'Preview for table: {result["name"]}')
        st.dataframe(result['dataframe'])

st.subheader('Audience and Insight Finder')

# Natural Language to GoogleSQL code generation
insight_tab, audience_tab, followup_tab = st.tabs(
    ["Insight Finder", "Audience Finder", "Purchase Follow Up"])

with insight_tab:
    utils_codey.generate_sql_and_query(
        state_key=f"{PAGE_KEY_PREFIX}_insight",
        title="Ask you data",
        query=QUERY,
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        tag_template_name=TAG_TEMPLATE_NAME,
        bqclient=bqclient,
        prompt_example="What are the customer emails ordered by the sum of transactions value by customers in New York City?",
        fallback_query=utils_default_image_text.AUDIENCE_QUERY_0
    )

with audience_tab:
    query_result = utils_codey.generate_sql_and_query(
        state_key=f"{PAGE_KEY_PREFIX}_audience",
        title="Find your audience",
        query=QUERY,
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        tag_template_name=TAG_TEMPLATE_NAME,
        bqclient=bqclient,
        prompt_example="What is the city and state with the most quantity of customers transactions?",
        fallback_query=utils_default_image_text.AUDIENCE_QUERY_1
    )

with followup_tab:
    utils_codey.generate_sql_and_query(
        state_key=f"{PAGE_KEY_PREFIX}_followup",
        title="Follow up purchases",
        query=QUERY,
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        tag_template_name=TAG_TEMPLATE_NAME,
        bqclient=bqclient,
        prompt_example="What are the top 50 customer emails ordered by loyalty score?",
        text_model=llm,
        fallback_query=utils_default_image_text.AUDIENCE_QUERY_2
    )
