import streamlit as st
import os
import time
from audiorecorder import audiorecorder
from analyze_audio import analyze_audio
from image_utils import get_bird_image_url
import io
from pydub import AudioSegment

# Page configuration
st.set_page_config(
    page_title="移动版鸟叫声识别",
    page_icon="🐦",
    layout="wide"
)

# Title and introduction
st.title("🐦 移动版鸟叫声识别")
st.markdown("直接使用手机或电脑麦克风录制声音，识别身边的鸟类朋友。")
st.caption(f"运行环境: {os.uname().sysname} (Web Audio)")

# Sidebar for settings
with st.sidebar:
    st.header("设置")
    # Note: Duration is controlled by user clicking start/stop in this version
    
    # Lowered default confidence for better initial experience
    min_conf = st.slider("最低置信度", min_value=0.1, max_value=0.9, value=0.10, step=0.05)
    
    st.subheader("音频增强")
    gain_boost = st.slider("音量增强 (dB)", min_value=0, max_value=30, value=0, help="如果录音声音太小，可以尝试增加此值")
    
    st.subheader("位置信息 (可选)")
    use_location = st.checkbox("启用位置辅助", value=True)
    lat = st.number_input("纬度 (Latitude)", value=39.9, disabled=not use_location)
    lon = st.number_input("经度 (Longitude)", value=116.4, disabled=not use_location)

# Main interface
col1, col2 = st.columns([1, 2])

output_file = "bird_sound_mobile.wav"

with col1:
    st.subheader("1. 获取声音")
    
    # Tabs for input method
    tab1, tab2 = st.tabs(["🎙️ 在线录音", "📂 上传文件"])
    
    with tab1:
        st.info("点击下方按钮开始录音，再次点击结束。")
        # Browser-based audio recorder
        audio = audiorecorder("🎙️ 点击开始", "⏹️ 点击停止")

        if len(audio) > 0:
            # Apply gain if needed
            if gain_boost > 0:
                audio = audio + gain_boost
                st.info(f"已应用 {gain_boost}dB 音量增强")
            
            # Export to wav format using pydub
            audio.export(output_file, format="wav")
            
            st.success(f"录音完成! 时长: {audio.duration_seconds:.1f}秒")
            
            # Save state
            st.session_state['audio_file_mobile'] = output_file
            st.session_state['has_recording_mobile'] = True
            
            # Playback
            try:
                audio_bytes = audio.export(format="wav").read()
                st.audio(audio_bytes, format='audio/wav')
            except Exception as e:
                st.error(f"播放失败: {e}")

    with tab2:
        st.info("推荐使用手机自带的高质量录音机录制，然后在此上传。")
        uploaded_file = st.file_uploader("选择音频文件", type=['wav', 'mp3', 'm4a', 'ogg'])
        
        if uploaded_file is not None:
            with st.spinner("正在处理音频文件..."):
                try:
                    # Load audio with pydub
                    # pydub handles format conversion automatically if ffmpeg is installed
                    audio_segment = AudioSegment.from_file(uploaded_file)
                    
                    # Apply gain if needed
                    if gain_boost > 0:
                        audio_segment = audio_segment + gain_boost
                        st.info(f"已应用 {gain_boost}dB 音量增强")
                    
                    # Export to standardized wav
                    audio_segment.export(output_file, format="wav")
                    
                    st.success(f"文件上传成功! 时长: {audio_segment.duration_seconds:.1f}秒")
                    
                    # Save state
                    st.session_state['audio_file_mobile'] = output_file
                    st.session_state['has_recording_mobile'] = True
                    
                    # Playback
                    st.audio(uploaded_file)
                    
                except Exception as e:
                    st.error(f"处理文件失败: {e}")
                    st.error("提示: 确保服务器已安装 ffmpeg 以支持 mp3/m4a 格式。")

# Analysis section
if st.session_state.get('has_recording_mobile'):
    with col2:
        st.subheader("2. 识别结果")
        
        if st.button("🔍 开始识别", type="primary", use_container_width=True):
            audio_file = st.session_state['audio_file_mobile']
            
            with st.spinner("正在分析音频..."):
                current_lat = lat if use_location else None
                current_lon = lon if use_location else None
                
                detections = analyze_audio(audio_file, lat=current_lat, lon=current_lon, min_conf=min_conf)
            
            if not detections:
                st.warning(f"未检测到明显的鸟叫声 (阈值: {min_conf})。")
                st.markdown("建议：\n1. 尝试使用**“上传文件”**功能，上传手机原生录音机录制的高清音频。\n2. 增加左侧的**“音量增强”**滑块。\n3. 调低**“最低置信度”**。")
            else:
                st.success(f"检测到 {len(detections)} 个结果！")
                
                for detection in detections:
                    bird_name = detection['common_name']
                    scientific_name = detection['scientific_name']
                    confidence = detection['confidence']
                    start_time = detection['start_time']
                    end_time = detection['end_time']
                    
                    with st.expander(f"🐦 {bird_name} ({confidence:.0%})", expanded=True):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            with st.spinner(f"获取图片中..."):
                                img_url = get_bird_image_url(bird_name)
                                if img_url:
                                    st.image(img_url, caption=f"{bird_name}", use_container_width=True)
                                else:
                                    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_in_yellow_circle.svg/200px-Question_mark_in_yellow_circle.svg.png", 
                                             width=150)
                        with c2:
                            st.markdown(f"**中文名称**: {bird_name}")
                            st.markdown(f"**学名**: *{scientific_name}*")
                            st.markdown(f"**置信度**: {confidence:.2f}")
                            st.markdown(f"**时间**: {start_time}s - {end_time}s")
                            search_url = f"https://www.bing.com/search?q={bird_name}"
                            st.markdown(f"[🔎 搜索更多信息]({search_url})")

st.markdown("---")
st.caption("Powered by BirdNET-Analyzer & Streamlit Web Audio")
