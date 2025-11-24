import streamlit as st
import asyncio
import edge_tts
import os
import tempfile
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip

# إعداد الصفحة
st.set_page_config(page_title="Free AI Video Maker", layout="centered")

async def generate_voice_edge(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "speech.mp3")
    await communicate.save(output_path)
    return output_path

st.title("🎬 صانع الفيديوهات المجاني")
st.info("هذا الموقع يعمل بمكتبات مجانية بالكامل (بدون API Keys).")

# المدخلات
script_text = st.text_area("1. اكتب النص هنا:", "Hello, this is a test video created for free.")
voice_option = st.selectbox("2. اختر الصوت:", ["en-US-ChristopherNeural", "ar-EG-ShakirNeural", "ar-SA-HamedNeural"])
uploaded_video = st.file_uploader("3. (اختياري) ارفع فيديو خلفية", type=["mp4"])

if st.button("إنشاء الفيديو"):
    if not script_text:
        st.error("الرجاء كتابة نص.")
    else:
        with st.spinner("جاري العمل... قد يستغرق دقيقة"):
            try:
                # 1. توليد الصوت
                audio_path = asyncio.run(generate_voice_edge(script_text, voice_option))
                
                # 2. تجهيز الخلفية
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration + 1
                
                if uploaded_video:
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
                    tfile.write(uploaded_video.read())
                    bg_clip = VideoFileClip(tfile.name)
                    # تكرار الفيديو ليغطي مدة الصوت
                    bg_clip = bg_clip.loop(duration=duration)
                    bg_clip = bg_clip.resize(height=720) # توحيد الجودة
                    # قص الفيديو ليكون بنفس مدة الصوت
                    bg_clip = bg_clip.subclip(0, duration)
                else:
                    # خلفية ملونة إذا لم يرفع فيديو
                    bg_clip = ColorClip(size=(1280, 720), color=(50, 50, 50), duration=duration)
                    bg_clip = bg_clip.set_fps(24)

                # 3. الدمج
                final_video = bg_clip.set_audio(audio_clip)
                
                output_path = "output_video.mp4"
                final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                st.success("تم!")
                st.video(output_path)
                
            except Exception as e:
                st.error(f"حدث خطأ: {e}")


