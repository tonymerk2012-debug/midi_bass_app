import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
import numpy as np
from bass_generator import process_midi

# Настройка страницы
st.set_page_config(
    page_title="AI Bass Generator",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для улучшения внешнего вида
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

# Боковая панель с настройками
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
        help="Больше нот = более детальная и насыщенная басовая партия"
    )
    
    tempo = st.number_input(
        "⏱️ Темп (BPM)",
        min_value=60,
        max_value=200,
        value=120,
        step=5,
        help="Скорость воспроизведения MIDI-файла"
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
    
    st.markdown("---")
    st.markdown("### 💡 Советы")
    st.markdown("""
    - **Простой стиль** — для легкой музыки
    - **Рок стиль** — для энергичных треков
    - **Фанк стиль** — для танцевальной музыки
    - Импортируйте оба MIDI-файла в DAW
    """)

# Функция для визуализации аккордов
def visualize_chords(chords):
    """Создает визуализацию аккордов в виде нотного графика"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Создаем словарь для цветов разных аккордов
    colors = plt.cm.tab10(np.linspace(0, 1, len(chords)))
    
    for i, chord in enumerate(chords):
        for note in chord:
            # Рисуем каждую ноту аккорда
            ax.scatter(i, note, s=150, c=[colors[i]], alpha=0.7, 
                      edgecolors='black', linewidth=1, zorder=3)
    
    # Настройка графика
    ax.set_xlabel("Номер аккорда", fontsize=12, fontweight='bold')
    ax.set_ylabel("MIDI номер ноты", fontsize=12, fontweight='bold')
    ax.set_title("Визуализация аккордовой последовательности", fontsize=14, fontweight='bold', pad=20)
    
    # Настройка сетки
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_xlim(-0.5, len(chords) - 0.5)
    
    # Добавляем подписи аккордов
    ax.set_xticks(range(len(chords)))
    ax.set_xticklabels([f"{i+1}" for i in range(len(chords))], fontsize=10)
    
    # Добавляем легенду
    legend_elements = []
    for i, chord in enumerate(chords):
        # Пытаемся определить название аккорда (упрощенно)
        chord_name = f"Аккорд {i+1}"
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                          markerfacecolor=colors[i], 
                                          markersize=10, label=chord_name))
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Добавляем информацию о количестве нот
    total_notes = sum(len(chord) for chord in chords)
    ax.text(0.02, 0.98, f"Всего нот: {total_notes}", transform=ax.transAxes, 
            fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig

# Функция для отображения информации о MIDI-файле
def display_midi_info(midi_file):
    """Отображает информацию о загруженном MIDI-файле"""
    try:
        import pretty_midi
        midi_data = pretty_midi.PrettyMIDI(midi_file)
        
        # Подсчет инструментов и нот
        num_instruments = len(midi_data.instruments)
        total_notes = sum(len(instr.notes) for instr in midi_data.instruments)
        
        # Получение темпа
        tempo = midi_data.estimate_tempo()
        
        # Длительность
        duration = midi_data.get_end_time()
        
        st.markdown("### 📊 Информация о MIDI-файле")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Инструментов", num_instruments)
        with col2:
            st.metric("Всего нот", total_notes)
        with col3:
            st.metric("Темп", f"{tempo:.0f} BPM")
        with col4:
            st.metric("Длительность", f"{duration:.1f} сек")
            
    except Exception as e:
        st.warning(f"Не удалось получить информацию о файле: {str(e)}")

# Основная область с двумя колонками
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📁 Загрузка MIDI-файла")
    
    uploaded_file = st.file_uploader(
        "Выберите MIDI-файл с аккордами",
        type=["mid", "midi"],
        help="Поддерживаются стандартные MIDI-файлы (Type 0 и Type 1)"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Файл загружен: {uploaded_file.name}")
        
        # Отображаем информацию о файле
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_info:
            tmp_info.write(uploaded_file.getvalue())
            display_midi_info(tmp_info.name)
            os.unlink(tmp_info.name)
        
        st.markdown("---")
        
        # Кнопка генерации
        if st.button("🎸 Сгенерировать басовую партию", type="primary", use_container_width=True):
            with st.spinner("🔄 Анализирую аккорды и генерирую бас..."):
                # Сохраняем загруженный файл во временный файл
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
                        st.session_state['input_file'] = input_path
                        
                        # Показываем сообщение об успехе
                        st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"❌ {message}")
                        
                except Exception as e:
                    st.error(f"❌ Ошибка при генерации: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                finally:
                    # Чистим временный файл
                    if os.path.exists(input_path) and 'output_path' not in st.session_state:
                        os.unlink(input_path)

with col2:
    st.markdown("### 🎵 Результат")
    
    # Отображаем результат, если он есть
    if 'message' in st.session_state and 'output_path' in st.session_state:
        st.markdown(f'<div class="info-box">ℹ️ {st.session_state["message"]}</div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state['output_path']):
            # Кнопка скачивания
            with open(st.session_state['output_path'], "rb") as f:
                st.download_button(
                    label="💾 Скачать сгенерированный MIDI-файл",
                    data=f,
                    file_name="bass_generated.mid",
                    mime="audio/midi",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Показываем дополнительную информацию
            st.markdown("### 📝 Инструкция по использованию")
            st.markdown("""
            1. **Импортируйте оба файла в вашу DAW** (Ableton, FL Studio, REAPER, Logic Pro и др.)
            2. **Разместите треки**:
               - Исходный MIDI-файл → дорожка с аккордами (пианино, гитара)
               - Сгенерированный бас → басовая дорожка
            3. **Назначьте VST-инструменты** на каждую дорожку
            4. **Наслаждайтесь** результатом!
            """)
            
            # Если есть информация об аккордах из process_midi, визуализируем
            if 'chords_data' in st.session_state:
                st.markdown("### 🎼 Визуализация аккордов")
                fig = visualize_chords(st.session_state['chords_data'])
                st.pyplot(fig)
                plt.close(fig)

# Футер
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎸 AI Bass Generator v2.0 | Сделано с ❤️ для музыкантов</p>
        <p style="font-size: 0.8rem;">Генерация басовых партий на основе анализа аккордовой последовательности</p>
    </div>
    """,
    unsafe_allow_html=True
)
