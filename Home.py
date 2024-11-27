import streamlit as st

# Title of the page
st.title("Team Members")

# Create a dictionary of team members and their information
team_members = {
    "จิรวัฒน์ เขมสถิตย์อนันต์": {"id": "6610422024", "image": "member/image1.jpg"},
    "ธนวัฒน์ เหลืองวิโรจน์": {"id": "6610422005", "image": "/workspaces/MADT-8102-CHATBOT/member/image2.jpg"},
    "ตรีภพ เนตรภู่": {"id": "6610422011", "image": "/workspaces/MADT-8102-CHATBOT/member/image3.jpg"},
    "บุลวัชร์ เจริญยืนนาน": {"id": "6610422013", "image": "/workspaces/MADT-8102-CHATBOT/member/image4.jpg"},
    "ชยพล หมื่นแจ้ง": {"id": "6610412004", "image": "/workspaces/MADT-8102-CHATBOT/member/image5.jpg"},
    "บวรวิชญ์ ศรีมาศ": {"id": "6610424030", "image": "/workspaces/MADT-8102-CHATBOT/member/image6.jpg"},
    "ณัฏฐชัย ใจรักษ์": {"id": "6610422021", "image": "/workspaces/MADT-8102-CHATBOT/member/image7.jpg"}
}

# Display information about each team member
for name, info in team_members.items():
    st.subheader(name)
    st.write(f"ID: {info['id']}")
    
    try:
        st.image(info['image'], width=200)
    except Exception as e:
        st.write(f"Error loading image: {e}")
    
    st.write("---")
