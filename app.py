import streamlit as st
import tempfile
import os
import numpy as np
from bass_generator import process_midi

# Настройка страницы
st.set_page_config(
    page_title="AI Bass Generator",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #e7f3ff;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<div class="main-header">🎸 AI Bass Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Загрузите MIDI-файл с аккордами, и искусственный интеллект создаст басовую партию</div>', unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки генерации")
    
    style = st.selectbox(
        "🎵 Стиль баса",
        ["simple", "rock", "funk"],
        format_func=lambda x: {
            "simple": "🎵 Простой (только корневые ноты)",
            "rock": "🎸 Рок (корни + квинты, драйвовый)",
            "funk": "🕺 Фанк (синкопы, октавы, грувовый)"
        }[x]
    )
    
    complexity = st.slider(
        "📊 Сложность (нот на аккорд)",
        min_value=2,
        max_value=12,
        value=4,
        help="Больше нот = более детальная басовая партия"
    )
    
    tempo = st.number_input(
        "⏱️ Темп (BPM)",
        min_value=60,
        max_value=200,
        value=120,
        step=5
    )
    
    st.markdown("---")
    st.markdown("### 📖 Как использовать")
    st.markdown("""
    1. Загрузите MIDI-файл
    2. Выберите стиль баса
    3. Настройте сложность
    4. Нажмите «Сгенерировать»
    5. Скачайте результат
    """)

# Функция для отображения информации о MIDI-файле (упрощенная, без ошибок)
def display_midi_info(midi_file):
    try:
        import pretty_midi
        midi_data = pretty_midi.PrettyMIDI(midi_file)
        
        num_instruments = len(midi_data.instruments)
        total_notes = sum(len(instr.notes) for instr in midi_data.instruments)
        
        # Безопасное получение темпа
        try:
            tempo_est = midi_data.estimate_tempo()
            tempo_text = f"{tempo_est:.0f} BPM"
        except:
            tempo_text = "Не определен"
        
        duration = midi_data.get_end_time()
        
        st.markdown("### 📊 Информация о MIDI-файле")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Инструментов", num_instruments)
        with col2:
            st.metric("Всего нот", total_notes)
        with col3:
            st.metric("Темп", tempo_text)
        with col4:
            st.metric("Длительность", f"{duration:.1f} сек")
            
    except Exception as e:
        # Просто пропускаем отображение информации, это не критично
        st.info("ℹ️ MIDI-файл загружен (информация о файле не отображается, но генерация работает)")

# Основная область
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📁 Загрузка MIDI-файла")
    
    uploaded_file = st.file_uploader(
        "Выберите MIDI-файл с аккордами",
        type=["mid", "midi"]
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Файл загружен: {uploaded_file.name}")
        
        # Показываем информацию о файле (если получится)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_info:
            tmp_info.write(uploaded_file.getvalue())
            display_midi_info(tmp_info.name)
            os.unlink(tmp_info.name)
        
        st.markdown("---")
        
        if st.button("🎸 Сгенерировать басовую партию", type="primary", use_container_width=True):
            with st.spinner("🔄 Анализирую аккорды и генерирую бас..."):
                # Сохраняем загруженный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                try:
                    # ВЫЗОВ ФУНКЦИИ - ИСПРАВЛЕННЫЙ БЛОК
                    result = process_midi(input_path, style=style, complexity=complexity, tempo=tempo)
                    
                    # Обрабатываем разные варианты возврата
                    if len(result) == 3:
                        output_path, message, chords = result
                        st.session_state['chords_data'] = chords
                    else:
                        output_path, message = result
                        st.session_state['chords_data'] = None
                    
                    if output_path:
                        st.session_state['output_path'] = output_path
                        st.session_state['message'] = message
                        st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"❌ Ошибка при генерации: {str(e)}")
                    import traceback
                    with st.expander("Подробности ошибки"):
                        st.code(traceback.format_exc())
                finally:
                    if os.path.exists(input_path):
                        os.unlink(input_path)

with col2:
    st.markdown("### 🎵 Результат")
    
    if 'message' in st.session_state and 'output_path' in st.session_state:
        st.markdown(f'<div class="info-box">ℹ️ {st.session_state["message"]}</div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state['output_path']):
            with open(st.session_state['output_path'], "rb") as f:
                st.download_button(
                    label="💾 Скачать сгенерированный MIDI-файл",
                    data=f,
                    file_name="bass_generated.mid",
                    mime="audio/midi",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("### 📝 Инструкция")
            st.markdown("""
            1. **Импортируйте оба файла в вашу DAW**
            2. **Разместите треки**:
               - Исходный MIDI → аккорды
               - Сгенерированный бас → бас
            3. **Назначьте VST-инструменты**
            4. **Наслаждайтесь результатом!**
            """)

# Футер
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎸 AI Bass Generator v2.0 | Сделано с ❤️ для музыкантов</p>
    </div>
    """,
    unsafe_allow_html=True
)
