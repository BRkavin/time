import cv2
import pytesseract
import re
import os
import subprocess
import pandas as pd
import streamlit as st

# Ensure Tesseract is correctly set (Only needed for Windows)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_first_frame(video_path, output_image):
    """Extracts the first frame from the video."""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_image, frame)
    cap.release()


def extract_time_from_frame(image_path):
    """Extracts the time from the frame using OCR."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    match = re.search(r'(\d{2}:\d{2}:\d{2})', text)
    return match.group(1) if match else None


def repair_video(input_video, repaired_video):
    """Repairs the input video to ensure moov atom is properly written."""
    ffmpeg_path = "ffmpeg"
    command = [
        ffmpeg_path, '-y', '-i', input_video, '-c', 'copy',
        '-movflags', '+faststart', repaired_video
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        return None, result.stderr

    if not os.path.exists(repaired_video) or os.path.getsize(repaired_video) == 0:
        return None, "Repaired video file is empty or missing."

    return repaired_video, None


def extract_video_segment(input_video, output_video, start_time, end_time):
    """Extracts a segment of a video."""
    ffmpeg_path = "ffmpeg"
    command = [
        ffmpeg_path, '-y', '-i', input_video,
        '-ss', start_time, '-to', end_time, '-c:v', 'libx264',
        '-preset', 'fast', '-crf', '23', '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart', output_video
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        return None, result.stderr

    if not os.path.exists(output_video) or os.path.getsize(output_video) == 0:
        return None, "Output video is empty or missing."

    return output_video, None


def time_to_seconds(time_str):
    """Converts a time string (HH:MM:SS) to total seconds."""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def seconds_to_time(seconds):
    """Converts total seconds to a time string (HH:MM:SS)."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"


def add_time_to_timestamp(base_time, duration):
    """Adds video duration (HH:MM:SS) to a base timestamp (HH:MM:SS)."""
    base_seconds = time_to_seconds(base_time)
    duration_seconds = time_to_seconds(duration)
    total_seconds = base_seconds + duration_seconds
    return seconds_to_time(total_seconds)


def main():
    # st.title("🎥 CSV Filter & Video Segment Player")

    # Upload CSV for filtering
    uploaded_csv = st.file_uploader("📂 Upload CSV", type=["csv"])

    # Upload video
    uploaded_video = st.file_uploader("📤 Upload Video", type=["mp4", "avi", "mov", "m4a", "3gp", "3g2", "mj2"])

    if uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        # st.write("📌 **Preview of Uploaded CSV**:")
        # st.dataframe(df)

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                column_name = st.selectbox("🔍 Select a column to filter", df.columns)

            with col2:
                unique_values = df[column_name].unique()
                selected_value = st.selectbox(f"🎯 Select a value from `{column_name}`", unique_values)

            filtered_df = df[df[column_name] == selected_value]
            if not filtered_df.empty:
                st.markdown("### ✅ Filtered Data:")
                st.dataframe(filtered_df)
            else:
                st.warning("⚠️ No data found for the selected filter.")

    if uploaded_video:
        video_path = "./input_video.mp4"
        repaired_video_path = "./repaired_video.mp4"
        image_path = "./start_time_frame.png"

        with open(video_path, "wb") as vid:
            vid.write(uploaded_video.read())

        # Repair the video
        # st.info("🔄 Repairing the uploaded video...")
        repaired_video, repair_error = repair_video(video_path, repaired_video_path)

        if not repaired_video:
            st.error(f"⛔ Video repair failed: {repair_error}")
            return

        # st.success("✅ Video repaired successfully!")

        # Extract the first frame for OCR
        extract_first_frame(repaired_video, image_path)

        detected_start_time = extract_time_from_frame(image_path)

        if detected_start_time:
            cap = cv2.VideoCapture(repaired_video)
            video_duration_seconds = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
            video_duration = seconds_to_time(video_duration_seconds)
            cap.release()

            video_end_time = add_time_to_timestamp(detected_start_time, video_duration)
            # st.info(f"🎥 **Video Duration**: `{video_duration}`")
            # st.success(f"🕒 Detected Start Time: `{detected_start_time}`")
            # st.info(f"🕓 Computed End Time: `{video_end_time}`")

            start_time = st.text_input("⏳ Enter Start Time (HH:MM:SS)", value=detected_start_time)
            end_time = st.text_input("⏳ Enter End Time (HH:MM:SS)", value=video_end_time)

            if st.button("🎬 Extract and Download Video Segment"):
                detected_start_seconds = time_to_seconds(detected_start_time)
                video_end_seconds = time_to_seconds(video_end_time)
                start_seconds = time_to_seconds(start_time)
                end_seconds = time_to_seconds(end_time)

                relative_start_seconds = start_seconds - detected_start_seconds
                relative_end_seconds = end_seconds - detected_start_seconds

                if (
                    detected_start_seconds <= start_seconds < video_end_seconds
                    and detected_start_seconds < end_seconds <= video_end_seconds
                    and start_seconds < end_seconds
                ):
                    # st.info(f"📌 Extracting video from `{start_time}` to `{end_time}`...")
                    output_video_path = "./temp_segment.mp4"
                    extracted_video, error = extract_video_segment(
                        repaired_video, output_video_path,
                        seconds_to_time(relative_start_seconds),
                        seconds_to_time(relative_end_seconds)
                    )

                    if extracted_video:
                        st.success("✅ Video segment extracted successfully!")
                        with open(output_video_path, "rb") as video_file:
                            video_bytes = video_file.read()
                            st.download_button(
                                label="📥 Download Extracted Video Segment",
                                data=video_bytes,
                                file_name="video_segment.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"⛔ Video segment extraction failed: {error}")
                else:
                    st.error(
                        "⚠️ Invalid start or end time. Ensure times are within the range "
                        f"`{detected_start_time}` to `{video_end_time}`, and start is before end."
                    )
        else:
            st.error("⛔ Could not detect time in the video frame. Try a clearer timestamp!")


if __name__ == "__main__":
    main()
