import openai
import streamlit as st
from streamlit_chat import message

### set org id and api key
#model_engine = "gpt-3.5-turbo"
#klarity api key
openai.api_key = "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"

### Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []

### Cost state variables
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

### marketing state variables
if 'base_knowledge' not in st.session_state:
    st.session_state['base_knowledge'] = {}
    st.session_state['messages'] = [{"role": "system", "content": "You're a helpful assistant."}]

    #####################
    ### base info ###
    #####################
    st.session_state['base_knowledge']['scenario'] = "My company is working on a SaaS platform to help independent telehealth and hybrid clinics manage their non medical operations, including billing, finding new patients, building a website, managing their calendar, providing a virtual personal assistant, and much more. I am working on creating ads for this company to attract new users"

    st.session_state['base_knowledge']['target_user'] = "nurse practitioners and physicians assistants operating independent clinics"
    st.session_state['base_knowledge']['brand_logo'] = "kiwi fruit"

    #st.session_state['base knowledge']['painpoints'] = "Known painpoints are building a practice website, managing patient billing, and organizing a website"
    #print('rerunning initial states')

    for key in st.session_state['base_knowledge'].keys():
        content = ''
        if key == 'target_user': content = "the target user is "
        if key == 'painpoints': content = "known painpoints are "
        if key == 'brand_logo': content = "our logo symbol is "

        content += st.session_state['base_knowledge'][key]
        st.session_state['messages'].append({"role": "assistant", "content": content})

#if 'message' not in st.session_state:
#    st.session_state['messages'] = [{"role": "system", "content": "You're a helpful assistant."}]

###############
### Sidebar ###
###############

st.sidebar.title("Sidebar")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
art_style = st.sidebar.radio("Choose your ad style:", ("hyper-realistic", "cartoon", "watercolor", "ukiyo-e"))


# map model to openai mode
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"


# reset everything button
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [{"role": "system", "content": "You're a helpful assistant."}]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []

    ### Cost state variables
    st.session_state['cost'] = []
    st.session_state['total_tokens'] = []
    st.session_state['total_cost'] = 0.0
    #counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


#########################
### Generate response ###
#########################

def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    #print(st.session_state['messages'])

    completion = openai.ChatCompletion.create(
            model=model
            ,messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

def generate_image(prompt):

    response = openai.Image.create(
    prompt=prompt,
    n=1,
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url

### target user

with st.sidebar.form("Marketing Criteria"):
    st.write("Marketing Criteria")

    st.session_state['base_knowledge']['scenario'] = st.text_area('Company Description', st.session_state['base_knowledge']['scenario'])
    st.session_state['base_knowledge']['target_user'] = st.text_area('Target user input', st.session_state['base_knowledge']['target_user'])
    st.session_state['base_knowledge']['brand_logo'] = st.text_input('Brand Logo Input', st.session_state['base_knowledge']['brand_logo'])

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")

    if submitted:
        ## reset messages
        st.session_state['messages'] = st.session_state['messages'][:1]

        ### target user update
        st.write(st.session_state['base_knowledge']['scenario'])
        content = st.session_state['base_knowledge']['scenario']
        st.session_state['messages'].append({"role": "assistant", "content": content})

        st.write('Current target user:', st.session_state['base_knowledge']['target_user'])
        content = f"our target users are {st.session_state['base_knowledge']['target_user']}"
        st.session_state['messages'].append({"role": "assistant", "content": content})

        st.write('Current logo set: ', st.session_state['base_knowledge']['brand_logo'])
        content += f"our logo symbol is {st.session_state['base_knowledge']['brand_logo']}"

        st.session_state['messages'].append({"role": "assistant", "content": content})

        #print(st.session_state['messages'])

##############################
### chat history container ###
##############################

response_container = st.container()

# text box container
container = st.container()

with container:

    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        #print('in form')
        #print(st.session_state['messages'])

        if user_input == "generate an image description to fit with the ad copy":
            user_input += "... only describe it in 2-3 sentences and use " + art_style
            output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
            image_url = generate_image(output)
            st.session_state['past'].append(output)
            st.session_state['generated'].append(image_url)
            st.session_state['model_name'].append('dalle')
            st.session_state['total_tokens'].append(0)
        else:
            output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
            st.session_state['model_name'].append(model_name)
            st.session_state['total_tokens'].append(total_tokens)

        if "generate ad copy with " in user_input:
            st.session_state['ad copy'] = output

        if model_name == 'GPT-3.5':
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

#print('outside container')
#print(st.session_state['messages'])

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            if st.session_state['model_name'][i] != 'dalle':
                #print(st.session_state["past"][i])
                #print(st.session_state["generated"][i])
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
                message(st.session_state["generated"][i], key=str(i))

                #print(st.session_state["messages"])

            else:
                message(st.session_state["past"][i], key=str(i))
                st.session_state['img_url'] = st.session_state["generated"][i]
                st.image(st.session_state['img_url'], caption=st.session_state['ad copy'])
