import streamlit as st

# Title of the page
st.title("Team Members")

# Create a dictionary of team members and their information
team_members = {
    "จิรวัฒน์ เขมสถิตย์อนันต์": {"id": "6610422024", "image": "member/image1.jpg"},
    "ธนวัฒน์ เหลืองวิโรจน์": {"id": "6610422005", "image": "member/image2.jpg"},
    "ตรีภพ เนตรภู่": {"id": "6610422011", "image": "member/image3.jpg"},
    "บุลวัชร์ เจริญยืนนาน": {"id": "6610422013", "image": "member/image4.jpg"},
    "ชยพล หมื่นแจ้ง": {"id": "6610412004", "image": "member/image5.jpg"},
    "บวรวิชญ์ ศรีมาศ": {"id": "6610424030", "image": "member/image6.jpg"},
    "ณัฏฐชัย ใจรักษ์": {"id": "6610422021", "image": "member/image7.jpg"}
}

# Display information about each team member in two-column layout
for name, info in team_members.items():
    col1, col2 = st.columns([1, 3])  # Column 1 is for images, Column 2 is for text
    
    # Column 1 - Image
    with col1:
        try:
            st.image(info['image'], width=200)
        except Exception as e:
            st.write(f"Error loading image: {e}")
    
    # Column 2 - Name and ID
    with col2:
        st.subheader(name)
        st.write(f"ID: {info['id']}")
    
    st.write("---")
