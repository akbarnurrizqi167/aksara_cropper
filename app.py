import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import io

# Konfigurasi layout
st.set_page_config(layout="wide")

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
    image_np = np.array(image)

    st.write("### Area Gambar")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=1.5,
        background_image=Image.fromarray(image_np),
        update_streamlit=True,
        height=image_np.shape[0],
        width=image_np.shape[1],
        drawing_mode="rect",
        display_toolbar=True,
        key="canvas",
    )

    # Jika terjadi perubahan pada canvas (misal undo, redo, atau hapus semua)
    if canvas_result.json_data is not None:
        # Jika jumlah objek lebih sedikit dari sebelumnya, berarti ada penghapusan
        if len(canvas_result.json_data["objects"]) < len(st.session_state.crops):
            clear_crops()
        # Tangkap koordinat cropping terbaru
        elif len(canvas_result.json_data["objects"]) > 0:
            obj = canvas_result.json_data["objects"][-1]
            x0, y0 = int(obj["left"]), int(obj["top"])
            x1, y1 = x0 + int(obj["width"]), y0 + int(obj["height"])

            # Cek apakah koordinat sudah ada sebelumnya
            new_crop = image.crop((x0, y0, x1, y1))
            if new_crop not in st.session_state.crops:
                st.session_state.crops.append(new_crop)
                st.session_state.history.append((x0, y0, x1, y1))
                st.session_state.redo_stack.clear()  # Clear redo stack setelah aksi baru

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
