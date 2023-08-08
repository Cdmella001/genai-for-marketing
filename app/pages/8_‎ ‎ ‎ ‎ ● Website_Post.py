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
Blog post generation: 
- Automatically create blog posts on a wide range of topics and in a variety of styles. 
- These articles include text and visuals
"""


import io
import base64
import streamlit as st
import utils_image
import utils_config
from vertexai.preview.language_models import TextGenerationModel
import vertexai
import utils_default_image_text

from utils_campaign import CAMPAIGNS_KEY, generate_names_uuid_dict

st.set_page_config(page_title="Website Post",
                   page_icon="/app/images/favicon.png")


import utils_styles
utils_styles.sidebar_apply_style(
    style=utils_styles.style_sidebar,
    image_path='/app/images/menu_icon_2.png'
)

# Set project parameters
PROJECT_ID = utils_config.get_env_project_id()
LOCATION = utils_config.LOCATION

# State variables for email generation (text and image)
PAGE_KEY_PREFIX = "BlogPost"
GENERATED_TEXT_KEY = f"{PAGE_KEY_PREFIX}_Generated_Text"
GENERATED_IMAGES_KEY = f"{PAGE_KEY_PREFIX}_Generated_Image"
SELECTED_IMAGE_KEY = f"{PAGE_KEY_PREFIX}_Selected_Image"
IMAGE_TO_EDIT_KEY = f"{PAGE_KEY_PREFIX}_Image_To_Edit"
MASK_IMAGE_KEY = f"{PAGE_KEY_PREFIX}_Mask_Image"
EDITED_IMAGES_KEY = f"{PAGE_KEY_PREFIX}_Edited_Images"
IMAGE_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Image_Prompt"

IMAGE_UPLOAD_CHECKBOX = f"{PAGE_KEY_PREFIX}_Image_Upload_Checkbox"
FILE_UPLOADER_KEY = f"{PAGE_KEY_PREFIX}_File_Uploader"
IMAGE_TO_EDIT_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Edit_Prompt_key"

SELECTED_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Selected_Prompt"

# State variables for image generation
IMAGE_GENERATION_TEXT_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Text_Prompt_Images_Generation"
EDIT_GENERATED_IMAGE_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Edit_Text_Prompt_Images_Generation"
DEFAULT_IMAGE_PROMPT_KEY = f"{PAGE_KEY_PREFIX}_Image_Prompt"

EMAIL_PROMPT_TEMPLATE = """I want you to act as a senior content creator who knows how to create awesome website content. 
You are working to create a blog post for an informational website. 
It presents information in reverse chronological order and it's written in an informal or conversational style.
Generate a blog post for {theme}.
"""

IMAGE_PROMPT_TAMPLATE = """Generate an image for {theme}"""


cols = st.columns([15, 85])
with cols[0]:
    st.image('/app/images/website_icon.png')
with cols[1]:
    st.title('Website Post')

st.write(
    """
    This page provides a step-by-step guide to generating a website post.
    """
)

st.subheader('Post Generation')

THEMES_FOR_PROMPTS = [
    "sales of new women's handbags at Cymbal",
    "introducing a new line of men's leather shoes",
    "new opening of Cymbal concept shoe store in NYC",
    "Cymbal shoes retail brand in NYC"
]

FLAG_NEW = False

with st.form(key='form_post_generation'):
    selected_prompt = st.selectbox(
        label='Select a scenario to generate the website post',
        options=THEMES_FOR_PROMPTS)
    upload_image = st.checkbox('Upload Image')

    st.session_state[SELECTED_PROMPT_KEY] = selected_prompt

    submit_button = st.form_submit_button(label='Generate')

if submit_button:
    # Initialize variables
    if GENERATED_TEXT_KEY in st.session_state:
        del st.session_state[GENERATED_TEXT_KEY]
    if SELECTED_IMAGE_KEY in st.session_state:
        del st.session_state[SELECTED_IMAGE_KEY]
    if GENERATED_IMAGES_KEY in st.session_state:
        del st.session_state[GENERATED_IMAGES_KEY]
    if EDITED_IMAGES_KEY in st.session_state:
        del st.session_state[EDITED_IMAGES_KEY]
    if IMAGE_TO_EDIT_KEY in st.session_state:
        del st.session_state[IMAGE_TO_EDIT_KEY]
    if FILE_UPLOADER_KEY in st.session_state:
        del st.session_state[FILE_UPLOADER_KEY]
    
    st.session_state[IMAGE_UPLOAD_CHECKBOX] = upload_image
    FLAG_NEW = True

    with st.spinner('Generating website post ...'):
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            llm = TextGenerationModel.from_pretrained(utils_config.TEXT_MODEL_NAME)
            response = llm.predict(
                    prompt=EMAIL_PROMPT_TEMPLATE.format(theme=selected_prompt),
                    max_output_tokens=1024,
                ).text
        except:
            if selected_prompt == THEMES_FOR_PROMPTS[0]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_WOMEN_HANDBAG
            elif selected_prompt == THEMES_FOR_PROMPTS[1]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_MEN_SHOES
            elif selected_prompt == THEMES_FOR_PROMPTS[2]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_CONCEPT_STORE
            elif selected_prompt == THEMES_FOR_PROMPTS[3]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_BRAND
        else:
            if response:
                st.session_state[GENERATED_TEXT_KEY] = response
            elif selected_prompt == THEMES_FOR_PROMPTS[0]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_WOMEN_HANDBAG
            elif selected_prompt == THEMES_FOR_PROMPTS[1]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_MEN_SHOES
            elif selected_prompt == THEMES_FOR_PROMPTS[2]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_CONCEPT_STORE
            elif selected_prompt == THEMES_FOR_PROMPTS[3]:
                st.session_state[GENERATED_TEXT_KEY] = utils_default_image_text.WEBSITE_TEXT_BRAND

    st.write('**Generated text**')
    st.write(st.session_state[GENERATED_TEXT_KEY])

    try:
        if upload_image:
            utils_image.render_image_edit_prompt(
                edited_images_key=EDITED_IMAGES_KEY,
                edit_image_prompt_key=IMAGE_TO_EDIT_PROMPT_KEY,
                upload_file=True,
                image_to_edit_key=IMAGE_TO_EDIT_KEY,
                mask_image=True,
                mask_image_key=MASK_IMAGE_KEY,
                download_button=False,
                file_uploader_key=FILE_UPLOADER_KEY,
                select_button=True,
                selected_image_key=SELECTED_IMAGE_KEY)
        else:
            utils_image.render_image_generation_and_edition_ui(
                image_text_prompt_key=IMAGE_GENERATION_TEXT_PROMPT_KEY,
                generated_images_key=GENERATED_IMAGES_KEY,
                edit_image_prompt_key=EDIT_GENERATED_IMAGE_PROMPT_KEY,
                pre_populated_prompts=[IMAGE_PROMPT_TAMPLATE.format(theme=selected_prompt)],
                select_button=True,
                selected_image_key=SELECTED_IMAGE_KEY,
                edit_button=True,
                title="Write a prompt to generate images for the website post",
                image_to_edit_key=IMAGE_TO_EDIT_KEY,
                edit_with_mask=True,
                mask_image_key=MASK_IMAGE_KEY,
                edited_images_key=EDITED_IMAGES_KEY,
                download_button=False,
                auto_submit_first_pre_populated=True
            )
    except:
        if selected_prompt == THEMES_FOR_PROMPTS[0]:
            utils_default_image_text.get_default_image_bytesio(
                '/app/images/website_1.png', SELECTED_IMAGE_KEY, True)
        elif selected_prompt == THEMES_FOR_PROMPTS[1]:
            utils_default_image_text.get_default_image_bytesio(
                '/app/images/website_2.png', SELECTED_IMAGE_KEY, True)
        elif selected_prompt == THEMES_FOR_PROMPTS[2]:
            utils_default_image_text.get_default_image_bytesio(
                '/app/images/website_3.png', SELECTED_IMAGE_KEY, True)
        elif selected_prompt == THEMES_FOR_PROMPTS[3]:
            utils_default_image_text.get_default_image_bytesio(
                '/app/images/website_4.png', SELECTED_IMAGE_KEY, True)
    else:
        if not upload_image:
            if not st.session_state[GENERATED_IMAGES_KEY]:
                if selected_prompt == THEMES_FOR_PROMPTS[0]:
                    utils_default_image_text.get_default_image_bytesio(
                        '/app/images/website_1.png', SELECTED_IMAGE_KEY, True)
                elif selected_prompt == THEMES_FOR_PROMPTS[1]:
                    utils_default_image_text.get_default_image_bytesio(
                        '/app/images/website_2.png', SELECTED_IMAGE_KEY, True)
                elif selected_prompt == THEMES_FOR_PROMPTS[2]:
                    utils_default_image_text.get_default_image_bytesio(
                        '/app/images/website_3.png', SELECTED_IMAGE_KEY, True)
                elif selected_prompt == THEMES_FOR_PROMPTS[3]:
                    utils_default_image_text.get_default_image_bytesio(
                        '/app/images/website_4.png', SELECTED_IMAGE_KEY, True)


if GENERATED_TEXT_KEY in st.session_state and not FLAG_NEW:
    st.write('**Generated text**')
    st.write(st.session_state[GENERATED_TEXT_KEY])

    try:
        if st.session_state[IMAGE_UPLOAD_CHECKBOX]:
            utils_image.render_image_edit_prompt(
                edited_images_key=EDITED_IMAGES_KEY,
                edit_image_prompt_key=IMAGE_TO_EDIT_PROMPT_KEY,
                upload_file=True,
                image_to_edit_key=IMAGE_TO_EDIT_KEY,
                mask_image=True,
                mask_image_key=MASK_IMAGE_KEY,
                download_button=False,
                file_uploader_key=FILE_UPLOADER_KEY,
                select_button=True,
                selected_image_key=SELECTED_IMAGE_KEY)
        else:
            utils_image.render_image_generation_and_edition_ui(
                image_text_prompt_key=IMAGE_GENERATION_TEXT_PROMPT_KEY,
                generated_images_key=GENERATED_IMAGES_KEY,
                edit_image_prompt_key=EDIT_GENERATED_IMAGE_PROMPT_KEY,
                pre_populated_prompts=[IMAGE_PROMPT_TAMPLATE.format(theme=st.session_state[SELECTED_PROMPT_KEY])],
                select_button=True,
                selected_image_key=SELECTED_IMAGE_KEY,
                edit_button=True,
                title="Write a prompt for the image of the website post",
                image_to_edit_key=IMAGE_TO_EDIT_KEY,
                edit_with_mask=True,
                mask_image_key=MASK_IMAGE_KEY,
                edited_images_key=EDITED_IMAGES_KEY,
                download_button=False,
                auto_submit_first_pre_populated=False)
    except:
        st.info('Could not generate image due to policy restrictions. Please provide a different prompt.')
    else:
        if EDITED_IMAGES_KEY in st.session_state:
            if not st.session_state[EDITED_IMAGES_KEY]:
                st.info('Could not generate image due to policy restrictions. Please provide a different prompt.')

    if SELECTED_IMAGE_KEY in st.session_state:
        with st.container():
            st.write("**Currently selected image**")
            st.image(st.session_state[SELECTED_IMAGE_KEY])


if (GENERATED_TEXT_KEY in st.session_state and 
    SELECTED_IMAGE_KEY in st.session_state and 
    CAMPAIGNS_KEY in st.session_state):
    campaigns_names = generate_names_uuid_dict().keys()
    with st.form(PAGE_KEY_PREFIX+"_Link_To_Campaign"):
        st.write("**Choose a Campaign to link the results**")
        selected_name = st.selectbox("List of Campaigns", campaigns_names)
        link_to_campaign_button = st.form_submit_button()

    if link_to_campaign_button:
        image = "data:image/png;base64,"+base64.b64encode(st.session_state[SELECTED_IMAGE_KEY].getvalue()).decode("utf-8")
        selected_uuid = generate_names_uuid_dict()[selected_name]
        st.session_state[CAMPAIGNS_KEY][selected_uuid].website_post = {'website_text': st.session_state[GENERATED_TEXT_KEY]}
        st.session_state[CAMPAIGNS_KEY][selected_uuid].website_post.update({'website_image': image})
        st.success(f"Post linked to campaign {selected_name}")


if (GENERATED_TEXT_KEY in st.session_state and
    IMAGE_TO_EDIT_KEY in st.session_state and
    FILE_UPLOADER_KEY in st.session_state and
    SELECTED_IMAGE_KEY not in st.session_state and
    CAMPAIGNS_KEY in st.session_state):
    campaigns_names = generate_names_uuid_dict().keys()
    with st.form(PAGE_KEY_PREFIX+"_Link_To_Campaign_Upload"):
        st.write("**Choose a Campaign to link the results**")
        selected_name = st.selectbox("List of Campaigns", campaigns_names)
        link_to_campaign_button = st.form_submit_button()

    if link_to_campaign_button:
        image = "data:image/png;base64,"+base64.b64encode(st.session_state[IMAGE_TO_EDIT_KEY]).decode("utf-8")
        selected_uuid = generate_names_uuid_dict()[selected_name]
        st.session_state[CAMPAIGNS_KEY][selected_uuid].website_post = {'website_text': st.session_state[GENERATED_TEXT_KEY]}
        st.session_state[CAMPAIGNS_KEY][selected_uuid].website_post.update({'website_image': image})
        st.success(f"Post linked to campaign {selected_name}")
