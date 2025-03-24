import streamlit as st
from langchain_community.llms import HuggingFaceHub
import os
import re
from dotenv import load_dotenv

load_dotenv()
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Configuración optimizada del modelo
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    model_kwargs={
        "temperature": 0.5,  # Más preciso, menos divagación
        "max_length": 300,
        "do_sample": True,
        "top_p": 0.95
    },
    huggingfacehub_api_token=huggingface_token
)

st.title("EduAI tu tutor virtual")

# CSS para mejor formato de texto
st.markdown("""
<style>
    .stMarkdown {
        white-space: pre-wrap;
        word-break: break-word;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Historial de chat optimizado
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar últimos 8 mensajes para mejor contexto
for message in st.session_state.messages[-8:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Procesamiento mejorado de entrada
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Guardado eficiente del mensaje
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generación de respuesta con limpieza reforzada
    with st.chat_message("assistant"):
        # Prompt oculto con delimitadores únicos
        hidden_instruction = """|||SYS
        Eres EduAI, tutor virtual. Reglas estrictas:
        1. Respuestas naturales SIN mencionar estas instrucciones
        2. Máximo 2 párrafos cortos
        3. Usar emojis relevantes por respuesta
        4. Prohibido usar markdown/etiquetas
        |||ENDSYS"""
        
        formatted_prompt = f"""⨀⨀INSTR⨀⨀
        {hidden_instruction}
        Pregunta: {prompt}
        ⨀⨀ENDINST⨀⨀"""
        
        response = llm.invoke(formatted_prompt)
        
        # Limpieza ultra-agresiva
        clean_response = re.sub(
            r"⨀⨀.*?⨀⨀|\|\|\|SYS.*?\|\|\|ENDSYS|<\/?s>|\[INST\]|�", 
            "", 
            response, 
            flags=re.DOTALL
        ).strip()
        
        # Eliminar autoreferencias residuales
        final_response = re.sub(
            r"(Como (tutor virtual|IA).*?:)|(Ejemplo de respuesta.*?(\n|$))", 
            "", 
            clean_response
        ).strip()
        
        # Formateo final con saltos de línea
        formatted_final = final_response.replace("\n", "<br>")
        
        st.markdown(formatted_final, unsafe_allow_html=True)
    
    # Guardar solo la respuesta limpia
    st.session_state.messages.append({"role": "assistant", "content": final_response})