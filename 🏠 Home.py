import streamlit as st

# Title of the page
st.set_page_config(
    page_title="🏠 MADT8102 FINAL PROJECT END TO END ",
    page_icon="🏠",
    layout="wide" 
)

st.title(" 🤵‍♂️ Team Members")

# Create a dictionary of team members and their information
team_members = {
    "บวรวิชญ์ ศรีมาศ":      {"id": "6610424030", "image": "member/image6.jpg"},
    "ชยพล หมื่นแจ้ง":      {"id": "6610412004", "image": "member/image5.jpg"},
    "ธนวัฒน์ เหลืองวิโรจน์":  {"id": "6610422005", "image": "member/image2.jpg"},
    "ตรีภพ เนตรภู่":        {"id": "6610422011", "image": "member/image3.jpg"},
    "บุลวัชร์ เจริญยืนนาน":   {"id": "6610422013", "image": "member/image4.jpg"},
    "ณัฏฐชัย ใจรักษ์":       {"id": "6610422021", "image": "member/image7.jpg"},
    "จิรวัฒน์ เขมสถิตย์อนันต์": {"id": "6610422024", "image": "member/image1.jpg"}
}

# Display information about each team member in a 4-column layout
columns = st.columns(4)  # 4 columns for layout

# Loop through team members and display their information
for index, (name, info) in enumerate(team_members.items()):
    col_index = index % 4  # To cycle through the 4 columns
    
    # Display in the appropriate column
    with columns[col_index]:
        try:
            st.image(info['image'], width=200)  # Display image
            # Add space between the image and text
            st.markdown("<br>", unsafe_allow_html=True)  # This adds an empty line
            st.subheader(name)  # Display name
            st.write(f"ID: {info['id']}")  # Display ID
        except Exception as e:
            st.write(f"Error loading image: {e}")

    # Add some spacing after each member's info to make it visually separated
    if (index + 1) % 4 == 0:
        st.write("---")
