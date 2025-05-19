import streamlit as st
from PIL import Image, ImageDraw
from utils import merge_crops

# Inisialisasi State
if "crops" not in st.session_state:
    st.session_state["crops"] = []
if "start_pos" not in st.session_state:
    st.session_state["start_pos"] = None
if "preview_image" not in st.session_state:
    st.session_state["preview_image"] = None

st.title("Crop Manual Aksara Jawa")

# Upload Image
uploaded_file = st.file_uploader("Upload Gambar", type=['png', 'jpg', 'jpeg'])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.session_state["preview_image"] = image.copy()
    st.image(image, caption="Gambar Asli", use_column_width=True)

# Tombol Mulai Crop Baru
if st.button("Mulai Crop Baru"):
    st.session_state["crops"] = []

# Canvas untuk cropping
if st.session_state["preview_image"]:
    st.write("Klik dan drag untuk crop:")

    canvas_result = st.image(st.session_state["preview_image"], use_column_width=True)

    # Koordinat cropping (disederhanakan untuk Streamlit)
    if st.button("Simpan Crop"):
        x0, y0, x1, y1 = st.slider("Pilih Koordinat", 0, st.session_state["preview_image"].width, (0, st.session_state["preview_image"].width)), \
                         st.slider("Pilih Koordinat", 0, st.session_state["preview_image"].height, (0, st.session_state["preview_image"].height))

        cropped = st.session_state["preview_image"].crop((x0[0], y0[0], x0[1], y0[1]))
        st.session_state["crops"].append(cropped)
        st.image(cropped, caption="Hasil Crop", use_column_width=True)

# Preview Gabungan
if st.button("Preview Gabungan"):
    if st.session_state["crops"]:
        merged_image = merge_crops(st.session_state["crops"])
        if merged_image:
            st.image(merged_image, caption="Preview Gabungan", use_column_width=True)

# Simpan Hasil Gabungan
if st.button("Gabung & Simpan"):
    if st.session_state["crops"]:
        merged_image = merge_crops(st.session_state["crops"])
        if merged_image:
            merged_image.save("outputs/merged.png")
            st.success("Gambar berhasil disimpan di folder 'outputs/merged.png'!")
            st.image(merged_image, caption="Gambar Gabungan", use_column_width=True)
