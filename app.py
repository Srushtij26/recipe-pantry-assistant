import streamlit as st
from dotenv import load_dotenv

from pantry.llm import suggest_swaps
from pantry.matcher import load_recipes, parse_pantry, rank

load_dotenv()
st.title("🥕 Recipe Pantry Assistant")
text = st.text_area("What's in your fridge? (comma-separated)", "egg, tomato, onion, butter")
allergies = set(st.multiselect("Allergies", ["dairy", "egg", "gluten", "nuts", "soy"]))

if st.button("Find recipes"):
    pantry = parse_pantry(text)
    for m in rank(pantry, load_recipes())[:5]:
        with st.expander(f"{m.name} — {len(m.have)}/{len(m.have)+len(m.missing)} ingredients"):
            st.write("✅ Have:", ", ".join(m.have))
            st.write("🛒 Missing:", ", ".join(m.missing) or "nothing!")
            if "safety_critical" in m.tags:
                st.warning("Food-safety-critical recipe: no substitutions suggested.")
            for s in suggest_swaps(m.name, m.missing, pantry, allergies, m.tags):
                st.info(f"Swap **{s.missing}** → **{s.use}**. {s.note}")
