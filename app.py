import streamlit as st
import tempfile
import os
from bass_generator import process_midi

# Настройка страницы
st.set_page_config(
    page_title="AI Bass Generator",
    page_icon="🎸",
    layout="wide"
)

# Заголовок
st.title("🎸 AI Bass Generator")
st.markdown("Загрузите MIDI-файл с аккордами, и AI создаст басовую партию")

# Боковая панель с настройками
with st.sidebar:
    st.header("⚙️ Настройки")
    
    style = st.selectbox(
        "Стиль баса",
        ["simple", "rock", "funk"],
        format_func=lambda x: {
            "simple": "🎵 Простой (только корни)",
            "rock": "🎸 Рок (корни + квинты)",
            "funk": "🕺 Фанк (синкопы + октавы)"
        }[x]
    )
    
    complexity = st.slider(
        "Сложность (нот на аккорд)",
        min_value=2,
        max_value=8,
        value=4,
        help="Больше нот = более детальная партия"
    )
    
    tempo = st.number_input(
        "Темп (BPM)",
        min_value=60,
        max_value=180,
        value=120
    )
    
    st.markdown("---")
    st.markdown("### Как использовать")
    st.markdown("""
    1. Загрузите MIDI-файл
    2. Выберите стиль баса
    3. Настройте сложность
    4. Нажмите «Сгенерировать»
    5. Скачайте результат
    """)

# Основная область
col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Загрузка")
    uploaded_file = st.file_uploader(
        "Выберите MIDI-файл",
        type=["mid", "midi"],
        help="Файл должен содержать аккордовую последовательность"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Файл загружен: {uploaded_file.name}")
        
        if st.button("🎸 Сгенерировать бас", type="primary"):
            with st.spinner("Анализирую аккорды и генерирую бас..."):
                # Сохраняем загруженный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                try:
                    # Генерируем бас
                    output_path, message = process_midi(
                        input_path, 
                        style=style, 
                        complexity=complexity,
                        tempo=tempo
                    )
                    
                    if output_path:
                        st.session_state['output_path'] = output_path
                        st.session_state['message'] = message
                        st.success(message)
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    os.unlink(input_path)

with col2:
    st.subheader("🎵 Результат")
    
    if 'message' in st.session_state:
        st.info(st.session_state['message'])
        
        if 'output_path' in st.session_state and os.path.exists(st.session_state['output_path']):
            with open(st.session_state['output_path'], "rb") as f:
                st.download_button(
                    label="💾 Скачать MIDI-файл",
                    data=f,
                    file_name="bass_generated.mid",
                    mime="audio/midi"
                )
            
            # Показываем превью нот (простое текстовое)
            st.markdown("---")
            st.markdown("### 📝 Информация")
            st.markdown("""
            **Совет:** Импортируйте оба файла в вашу DAW:
            1. Исходный файл с аккордами
            2. Сгенерированный бас
            """)

# Footer
st.markdown("---")
st.markdown(
    "<center>Сделано с ❤️ для музыкантов | AI Bass Generator v1.0</center>",
    unsafe_allow_html=True
)
