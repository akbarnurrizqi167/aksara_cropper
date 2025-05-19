import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64
import os
os.system('pip install --upgrade pip')

# Konfigurasi layout
st.set_page_config(layout="wide")

# Fungsi konversi gambar ke Base64 untuk Streamlit Cloud
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Sidebar kiri untuk upload dan pengaturan
st.sidebar.header("Menu Utama")
uploaded_file = st.sidebar.file_uploader("Upload Gambar", type=["png", "jpg", "jpeg"])
start_crop = st.sidebar.button("Mulai Crop Baru")
preview_merge = st.sidebar.button("Preview Gabungan")
merge_and_save = st.sidebar.button("Gabung & Simpan")

# Variabel untuk menyimpan state
if "crops" not in st.session_state:
    st.session_state.crops = []
if "history" not in st.session_state:
    st.session_state.history = []
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []

# Fungsi untuk membersihkan koordinat jika terjadi perubahan pada canvas
def clear_crops():
    st.session_state.crops.clear()
    st.session_state.history.clear()
    st.session_state.redo_stack.clear()

# Tampilan Canvas
if uploaded_file:
    image = Image.open(uploaded_file)
    background_image_url = "data:image/png;base64," + image_to_base64(image)

    st.write("### Area Gambar")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=1.5,
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="rect",
        display_toolbar=True,
        key="canvas",
    )

    # Jika terjadi perubahan pada canvas
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]

        # Jika jumlah objek lebih sedikit, berarti ada penghapusan
        if len(objects) < len(st.session_state.crops):
            clear_crops()

        # Tangkap koordinat cropping terbaru
        if len(objects) > 0:
            obj = objects[-1]
            x0, y0 = int(obj["left"]), int(obj["top"])
            x1, y1 = x0 + int(obj["width"]), y0 + int(obj["height"])

            new_crop = image.crop((x0, y0, x1, y1))
            if new_crop not in st.session_state.crops:
                st.session_state.crops.append(new_crop)
                st.session_state.history.append((x0, y0, x1, y1))
                st.session_state.redo_stack.clear()  # Clear redo stack setelah aksi baru

# Tombol Undo, Redo, dan Reset di sidebar kanan
st.sidebar.header("Opsi Edit")
if st.sidebar.button("Undo"):
    if st.session_state.history:
        last_crop = st.session_state.history.pop()
        st.session_state.redo_stack.append(last_crop)
        st.session_state.crops.pop()

if st.sidebar.button("Redo"):
    if st.session_state.redo_stack:
        redo_crop = st.session_state.redo_stack.pop()
        x0, y0, x1, y1 = redo_crop
        cropped_img = image.crop((x0, y0, x1, y1))
        st.session_state.crops.append(cropped_img)
        st.session_state.history.append(redo_crop)

if st.sidebar.button("Reset"):
    clear_crops()

# Preview hasil crop
if preview_merge and st.session_state.crops:
    total_width = sum(c.width for c in st.session_state.crops)
    max_height = max(c.height for c in st.session_state.crops)
    merged_image = Image.new('RGB', (total_width, max_height), color='white')

    x_offset = 0
    for im in st.session_state.crops:
        merged_image.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    st.write("### Hasil Gabungan")
    st.image(merged_image)

# Save hasil gabungan
if merge_and_save and st.session_state.crops:
    total_width = sum(c.width for c in st.session_state.crops)
    max_height = max(c.height for c in st.session_state.crops)
    merged_image = Image.new('RGB', (total_width, max_height), color='white')
    
    x_offset = 0
    for im in st.session_state.crops:
        merged_image.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    buf = io.BytesIO()
    merged_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(label="Download Hasil Gabungan", data=byte_im, file_name="hasil_gabungan.png", mime="image/png")
