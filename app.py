import streamlit as st
import face_recognition
import os
import shutil
import pickle

# Paths to folders and files
main_folder = "imgs"  # Folder containing the images
encodings_file = "encodings.pkl"  # File where the pre-computed encodings are stored

# Create encodings if needed
def save_encodings():
    encodings = []
    for file_name in os.listdir(main_folder):
        image_path = os.path.join(main_folder, file_name)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            encodings.append((file_name, face_encodings[0]))
    with open(encodings_file, 'wb') as f:
        pickle.dump(encodings, f)
    print(f"Encodings saved for {len(encodings)} images.")

# Load precomputed encodings and compare with user input image
def load_and_compare(user_face_encoding, user_folder, tolerance=0.5):
    # Load pre-computed encodings from the file
    with open(encodings_file, 'rb') as f:
        known_encodings = pickle.load(f)

    photos_found = False
    for file_name, encoding in known_encodings:
        results = face_recognition.compare_faces([encoding], user_face_encoding, tolerance=tolerance)
        if results[0]:
            shutil.copy(os.path.join(main_folder, file_name), os.path.join(user_folder, file_name))
            photos_found = True

    return photos_found



st.set_page_config(page_title="findphoto", 
                    page_icon="None")


# load_dotenv()
st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

html = f"""
<style>
    .custom-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient( #4181fa, #5f96fc);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.27);
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0px;
    }}

    .custom-navbar p {{
        font-size: 35px;
        margin-left: 65px;
        margin-top: 8px;
        color: #fff;
    }}

</style>

<nav class="custom-navbar">
    <p><b>findphoto.ai</b></p>
</nav>

"""

st.markdown(html, unsafe_allow_html=True)



hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# Streamlit app
st.title("Find your photos with just one click!")

# Add padding from the top for the sidebar
sidebar_css = """
<style>
    section[data-testid="stSidebar"] {
        z-index:1;"
        position: fixed;
    }

.st-emotion-cache-1629p8f {
    color: #4181fa; /* Change the color of the heading */
    line-height: 0;
}
.st-emotion-cache-17b17hr {
    color: #333333;
    padding: 10px;
}
</style>
"""

# Render the sidebar below the navbar
st.markdown(sidebar_css, unsafe_allow_html=True)

# Sidebar for input
with st.sidebar:
    # Input for user name
    st.subheader("Enter your name:")
    user_name = st.text_input("Enter your name:",placeholder="Enter your name here",label_visibility='collapsed')

    # File uploader for user's image
    st.subheader("Upload your photo:")
    uploaded_file = st.file_uploader("Upload your photo:", type=["jpg", "jpeg", "png"],label_visibility='collapsed')

# Process the user's image
if st.sidebar.button("Find Photos"):
    if user_name and uploaded_file:
        # Create a folder for the user
        user_folder = os.path.join("user_photos", user_name)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Load and encode the uploaded user's image
        user_image = face_recognition.load_image_file(uploaded_file)
        user_face_encoding = face_recognition.face_encodings(user_image)

        # Check if any face was detected
        if user_face_encoding:
            user_face_encoding = user_face_encoding[0]

            # Compare the user's face with pre-computed encodings
            if load_and_compare(user_face_encoding, user_folder):
                st.success(f"Photos of {user_name} have been found!")
                
                # Display the copied images
                for file_name in os.listdir(user_folder):
                    image_path = os.path.join(user_folder, file_name)
                    st.image(image_path, caption=file_name)

                # Sidebar for downloading the photos
                with st.sidebar:
                    zip_file = shutil.make_archive(user_folder, 'zip', user_folder)
                    with open(zip_file, 'rb') as f:
                        st.download_button('Download all photos', f, file_name=f"{user_name}_photos.zip")

                folder = user_folder.split("/")
                shutil.rmtree(folder[0])
                    
            else:
                st.error("No matching photos found.")
        else:
            st.error("No face detected in the uploaded image.")
    else:
        st.error("Please provide both your name and an image.")
