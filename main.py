import streamlit as st
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL

# ==============================
# KHỞI TẠO AI
# ==============================
genai.configure(api_key=GEMINI_API_KEY)

# ==============================
# ĐỌC PROMPT
# ==============================
def load_prompt(filename):
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("system.txt")
LATEX_PROMPT = load_prompt("latex_bt.txt")

# ==============================
# GỌI AI (Đã nâng cấp hỗ trợ Chat)
# ==============================
def ask_ai(history, user_prompt, current_instruction):
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=current_instruction
    )
    
    # Chuyển lịch sử trên giao diện thành định dạng mà Google Gemini hiểu
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    
    # Nối thêm yêu cầu mới nhất (đã tự động kẹp cấu hình ở Thanh bên)
    gemini_history.append({"role": "user", "parts": [user_prompt]})
    
    response = model.generate_content(gemini_history)
    return response.text

# ==============================
# GIAO DIỆN
# ==============================
st.set_page_config(
    page_title="Hoàng Anh ",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Thầy Hoàng Anh - MAPSTUDY HẠ LONG")
st.caption("Trợ lý AI của Hoàng Anhhh")
st.markdown("""
<style>
/* 1. Ghim cố định tiêu đề (thẻ h1) lên mép trên, căn giữa tuyệt đối */
h1 {
    position: fixed !important;
    top: 25px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background-color: rgba(255, 255, 255, 0.95) !important; /* Nền trắng đục để che chữ cuộn bên dưới */
    z-index: 999999 !important;
    padding: 12px 40px !important;
    border-radius: 0 0 15px 15px !important; /* Bo cong 2 góc dưới tạo độ mềm mại */
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.08) !important;
    white-space: nowrap !important; /* Chống rớt dòng khi màn hình nhỏ */
}

/* 2. Đẩy toàn bộ phần nội dung chính của trang web tụt xuống để không bị tiêu đề che lấp */
.block-container {
    padding-top: 100px !important; 
}

/* 3. Ẩn dải khoảng trắng mặc định của Streamlit trên cùng */
header[data-testid="stHeader"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Đảm bảo khối code không bị giấu phần tử khi tràn viền */
div[data-testid="stCodeBlock"] {
    overflow: visible !important;
}

/* Ép thanh công cụ chứa nút Copy phải bám dính vào màn hình */
div[data-testid="stCodeBlock"] div[data-testid="stElementToolbar"] {
    position: sticky !important;
    top: 65px !important; /* Cách mép trên 65px để không bị thanh tiêu đề web che mất */
    z-index: 99999 !important;
    opacity: 1 !important; /* Luôn luôn hiện nút Copy, không cần di chuột vào khối code */
    visibility: visible !important;
    display: flex !important;
}

/* Đổ màu nền và viền cho nút Copy để dễ nhìn hơn trên nền code trôi */
div[data-testid="stCodeBlock"] div[data-testid="stElementToolbar"] button {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}
</style>
""", unsafe_allow_html=True)
# ==============================
# THANH BÊN
# ==============================
with st.sidebar:
    st.header("⚙️ Cấu hình")
    
    subject = st.selectbox(
        "Môn học", 
        ["Vật Lí", "KHTN Lí", "KHTN Hóa"]
    )
    
    grade = st.selectbox(
        "Lớp", 
        ["6", "7", "8", "9", "10", "11", "12"]
    )
    
    task = st.selectbox(
        "Chức năng",
        ["Tạo câu hỏi đi kèm đáp án", "Tạo đề kiểm tra kèm theo đáp án"]
    )
    
    time_limit = st.text_input(
        "Thời gian làm bài", 
        placeholder="Ví dụ: 15 phút, 45 phút..."
    )
    
    st.markdown("**Tỉ lệ mức độ (số câu hoặc %)**")
    col1, col2 = st.columns(2)
    with col1:
        nb = st.text_input("Nhận biết", value="40%")
        vd = st.text_input("Vận dụng", value="20%")
    with col2:
        th = st.text_input("Thông hiểu", value="30%")
        vdc = st.text_input("Vận dụng cao", value="10%")
    st.markdown("**Cấu trúc đề (số câu)**")
    col3, col4 = st.columns(2)
    with col3:
        tn_nhieu = st.text_input("Nhiều lựa chọn", value="0")
        tl_ngan = st.text_input("Trả lời ngắn", value="0")
    with col4:
        tn_dungsai = st.text_input("Đúng/Sai", value="0")
        tu_luan = st.text_input("Tự luận", value="0")

# ==============================
# KHÔNG GIAN LÀM VIỆC & LỊCH SỬ CHAT
# ==============================
st.subheader("📝 Không gian làm việc")

# 1. Khởi tạo bộ nhớ tạm
if "messages" not in st.session_state:
    st.session_state.messages = []

# Nút dọn dẹp để làm đề bài mới
if st.button("🗑️ Làm mới / Xóa lịch sử"):
    st.session_state.messages = []
    st.rerun()

# 2. In lại lịch sử tin nhắn và kết quả cũ lên màn hình
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            st.code(msg["content"], language="latex" if task == "Chuyển sang LaTeX #bt" else "text")

# 3. Khung nhập liệu Chat (Tự động ghim dưới đáy màn hình)
if user_input := st.chat_input("Nhập yêu cầu tại đây (Ví dụ: Tạo 10 câu trắc nghiệm... hoặc Sửa câu 2...)"):
    
    # In ngay câu hỏi của thầy lên màn hình
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Gom cấu hình từ Thanh bên
    current_instruction = LATEX_PROMPT if task == "Chuyển sang LaTeX #bt" else SYSTEM_PROMPT
    full_prompt = f"""
Môn học: {subject}
Khối: {grade}
Chức năng: {task}
Thời gian làm bài: {time_limit}
Cấu trúc mức độ: Nhận biết ({nb}), Thông hiểu ({th}), Vận dụng ({vd}), Vận dụng cao ({vdc})
Cấu trúc đề kiểm tra: {tn_nhieu} câu Trắc nghiệm nhiều lựa chọn, {tn_dungsai} câu Trắc nghiệm đúng sai, {tl_ngan} câu Trả lời ngắn, {tu_luan} câu Tự luận.

YÊU CẦU CỦA GIÁO VIÊN:\n{user_input}
"""
    
    # Xử lý bằng AI
    with st.chat_message("assistant"):
        with st.spinner("Thầy Hoàng Anh đang nhờ người thân trợ giúp... hehehe"):
            try:
                # Gọi AI và truyền theo lịch sử tin nhắn cũ
                result = ask_ai(st.session_state.messages, full_prompt, current_instruction)
                
                # Dọn rác markdown
                result = result.replace("```latex\n", "").replace("```latex", "").replace("```text\n", "").replace("```", "").strip()
                
                # Hiển thị kết quả mới
                st.code(result, language="latex" if task == "Chuyển sang LaTeX #bt" else "text")
                
                # Nút tải về cho kết quả mới (Mỗi nút có một key riêng để chống lỗi trùng lặp)
                st.download_button(
                    label="⬇️ Nhặt thôi chứ sao nữa nhểy", 
                    data=result, 
                    file_name="ket_qua.txt", 
                    key=f"dl_{len(st.session_state.messages)}"
                )
                
                # Lưu toàn bộ vào bộ nhớ để AI nhớ cho lần nhắn tiếp theo
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": result})
                
            except Exception as e:
                st.error(f"Lỗi: {e}")