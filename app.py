import streamlit as st
import random
import re
from transformers import pipeline, set_seed
import torch

st.set_page_config(page_title="AI Motivation Generator", page_icon="🤖")

@st.cache_resource
def load_model():
    try:
        generator = pipeline(
            'text-generation', 
            model='gpt2-medium',
            tokenizer='gpt2-medium',
            device=0 if torch.cuda.is_available() else -1
        )
        return generator
    except Exception as e:
        st.error(f"Failed to load GPT-2 medium, trying smaller model: {e}")
        try:
            generator = pipeline('text-generation', model='gpt2')
            return generator
        except Exception as e2:
            st.error(f"Failed to load any model: {e2}")
            return None

def create_motivational_prompt(mood):
    mood_contexts = {
        "anxious": "someone who is feeling overwhelmed by worry and needs reassurance",
        "tired": "someone who is physically and mentally exhausted and needs encouragement",
        "unmotivated": "someone who has lost their drive and needs inspiration to start again",
        "feeling down": "someone who is sad or depressed and needs uplifting words",
        "lacking confidence": "someone who doubts themselves and needs a confidence boost",
        "stressed": "someone who is under pressure and needs calming motivation",
        "need focus": "someone who is distracted and needs motivation to concentrate",
        "lonely": "someone who feels isolated and needs encouraging companionship"
    }
    
    context = mood_contexts.get(mood.lower(), "someone who needs motivation")
    
    prompt = f"""Here are some examples of great motivational quotes:

"The only way to do great work is to love what you do."
"Believe you can and you're halfway there."
"Success is not final, failure is not fatal: it is the courage to continue that counts."

Now write an inspiring motivational quote for {context}. Make it positive, encouraging, and uplifting:

"{mood.title()} Quote:"""
    
    return prompt

def clean_ai_quote(generated_text, original_prompt):
    text = generated_text.replace(original_prompt, "").strip()
    
    quote_match = re.search(r'"([^"]+)"', text)
    if quote_match:
        quote = quote_match.group(1).strip()
        if len(quote) > 10:
            return quote
    
    sentences = re.split(r'[.!?]\s+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        sentence = re.sub(r'^["\'\-\s]*', '', sentence)
        sentence = re.sub(r'["\'\s]*$', '', sentence)
        
        if (len(sentence) > 15 and 
            len(sentence) < 200 and
            not sentence.lower().startswith(('here', 'this', 'quote', 'motivation')) and
            any(word in sentence.lower() for word in ['you', 'your', 'can', 'will', 'strength', 'believe', 'success', 'achieve', 'overcome', 'courage', 'hope', 'dream', 'grow', 'strong'])):
            
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            return sentence
    
    return None

def get_fallback_quote(mood):
    quotes = {
        "anxious": [
            "Your anxiety is not your identity. You are brave, you are strong, and this feeling will pass.",
            "Breathe deeply and remember: you have survived 100% of your difficult days so far."
        ],
        "tired": [
            "Rest is not a reward for work completed, it's a requirement for work to continue.",
            "Your exhaustion today is building your resilience for tomorrow."
        ],
        "unmotivated": [
            "You don't have to be great to get started, but you have to get started to be great.",
            "Motivation gets you started, but habit is what keeps you going."
        ],
        "feeling down": [
            "This feeling is temporary, but your strength is permanent.",
            "Even the darkest night will end and the sun will rise again."
        ],
        "lacking confidence": [
            "You are braver than you believe, stronger than you seem, and smarter than you think.",
            "Confidence comes not from always being right, but from not fearing to be wrong."
        ],
        "stressed": [
            "You can't control everything that happens to you, but you can control how you respond.",
            "Stress is like a wave - you can't stop it from coming, but you can choose how to surf it."
        ],
        "need focus": [
            "Focus is not about doing more things, it's about doing the right things with full attention.",
            "Where attention goes, energy flows and results show."
        ],
        "lonely": [
            "The greatest thing in the world is to know how to belong to yourself.",
            "You are never alone when you like the person you're alone with."
        ]
    }
    
    mood_key = mood.lower().replace(" ", "_")
    if mood_key in quotes:
        return random.choice(quotes[mood_key])
    return "Every challenge is an opportunity to discover your inner strength."

with st.spinner(" Loading AI model... This may take a moment..."):
    generator = load_model()
    if generator:
        set_seed(42)
        model_loaded = True
        st.success("✅ AI model loaded successfully!")
    else:
        model_loaded = False
        st.warning("⚠️ AI model failed to load. Using fallback quotes.")

st.title("AI Motivation Generator")
st.write("Powered by GPT-2 AI model to generate personalized motivational quotes!")

if model_loaded:
    st.info(" **AI Status**: Model loaded and ready to generate custom quotes")
else:
    st.error("🔧 **AI Status**: Model unavailable, using curated quotes")

st.markdown("""
<style>
.quote-display {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 15px;
    color: white;
    margin: 20px 0;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}
.ai-badge {
    background-color: #4CAF50;
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    display: inline-block;
    margin-bottom: 10px;
}
.fallback-badge {
    background-color: #FF9800;
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    display: inline-block;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

moods = [
    "Anxious",
    "Tired", 
    "Unmotivated",
    "Feeling Down",
    "Lacking Confidence",
    "Stressed",
    "Need Focus",
    "Lonely"
]

selected_mood = st.selectbox("🎭 How are you feeling today?", moods)

mood_descriptions = {
    "Anxious": "When worry feels overwhelming 😰",
    "Tired": "When energy feels depleted 😴",
    "Unmotivated": "When drive seems missing 😑",
    "Feeling Down": "When spirits need lifting 😔",
    "Lacking Confidence": "When self-doubt creeps in 😕",
    "Stressed": "When pressure feels intense 😖",
    "Need Focus": "When attention feels scattered 🤯",
    "Lonely": "When connection feels distant 😞"
}

st.write(f"*{mood_descriptions.get(selected_mood, '')}*")

if model_loaded:
    with st.expander("🔧 AI Settings (Advanced)"):
        temperature = st.slider("Creativity Level", 0.1, 1.0, 0.8, 0.1)
        max_length = st.slider("Quote Length", 30, 100, 60, 10)
        st.caption("Higher creativity = more unique quotes, Lower = more predictable")

generate_button = st.button(" Generate AI Motivation", type="primary", use_container_width=True)

if generate_button:
    with st.spinner("🧠 AI is crafting your personalized quote..."):
        quote = None
        used_ai = False
        
        if model_loaded:
            try:
                prompt = create_motivational_prompt(selected_mood)
                
                result = generator(
                    prompt,
                    max_length=len(prompt.split()) + (max_length if model_loaded else 40),
                    num_return_sequences=1,
                    do_sample=True,
                    temperature=temperature if model_loaded else 0.8,
                    top_p=0.9,
                    pad_token_id=generator.tokenizer.eos_token_id,
                    eos_token_id=generator.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
                
                generated_text = result[0]['generated_text']
                ai_quote = clean_ai_quote(generated_text, prompt)
                
                if ai_quote:
                    quote = ai_quote
                    used_ai = True
                else:
                    quote = get_fallback_quote(selected_mood)
                    
            except Exception as e:
                st.error(f"AI generation failed: {str(e)}")
                quote = get_fallback_quote(selected_mood)
        else:
            quote = get_fallback_quote(selected_mood)
        
        st.success("✨ Your motivation is ready!")
        
        badge_html = '<div class="ai-badge"> AI Generated</div>' if used_ai else '<div class="fallback-badge">📚 Curated Quote</div>'
        
        st.markdown(f"""
        <div class="quote-display">
            {badge_html}
            <h3 style="margin-bottom: 15px;">💫 Your Personal Motivation</h3>
            <p style="font-size: 20px; font-style: italic; line-height: 1.6; margin: 0;">
                "{quote}"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if used_ai and model_loaded:
            st.info("🎯 This quote was uniquely generated by AI based on your mood!")
        elif not used_ai and model_loaded:
            st.warning("🔄 AI output wasn't suitable, showing curated quote instead. Try again!")
        
        st.write("🌱 **Remember**: You have the power to change your day!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Generate Another"):
                st.rerun()
        with col2:
            if st.button("📋 Copy Quote"):
                st.code(f'"{quote}"', language=None)

with st.expander("ℹ️ About the AI"):
    if model_loaded:
        st.write("""
        **Model**: GPT-2 (Generative Pre-trained Transformer 2)
        **Purpose**: Generates contextual motivational quotes based on your mood
        **Training**: Trained on diverse text to understand human language patterns
        **Customization**: Each quote is uniquely generated for your specific emotional state
        """)
    else:
        st.write("AI model is currently unavailable. Using high-quality curated quotes instead.")

st.markdown("---")
st.markdown("*🤖 Powered by AI • Made with 💙 for your wellbeing*")