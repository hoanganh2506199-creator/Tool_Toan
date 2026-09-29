import streamlit as st
import google.generativeai as genai
import pypandoc
import os
from dotenv import load_dotenv
from datetime import datetime

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(page_title="Thầy Hoàng Anh", page_icon="🎓", layout="wide")

# KHỞI TẠO BỘ NHỚ LỊCH SỬ & CHAT
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "latest_docx" not in st.session_state:
    st.session_state.latest_docx = None

# GIAO DIỆN GHIM TÊN THẦY (ĐÃ KHÓA HOÀN TOÀN LỖI ĐÈ CHỮ)
st.markdown("""
<style>
    /* Ẩn thanh header mặc định của Streamlit */
    header[data-testid="stHeader"] { display: none !important; }
    
    /* Đẩy khung nội dung xuống để không bị che */
    .block-container { padding-top: 100px !important; }
    
    /* Hộp chứa tên Thầy được ghim cố định độc lập */
    .ten-thay-hoang-anh {
        position: fixed; 
        top: 15px; 
        left: 50%;
        transform: translateX(-50%); 
        background-color: white;
        z-index: 999999; 
        padding: 10px 30px;
        border-radius: 10px; 
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        white-space: nowrap;
        font-size: 32px;
        font-weight: bold;
        color: #1f1f1f;
    }

    /* Đưa các tiêu đề do AI viết về trạng thái bình thường */
    h1, h2, h3, h4, h5, h6 {
        position: static !important;
        transform: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }
</style>

<div class="ten-thay-hoang-anh">
    🎓 Thầy Hoàng Anh 
</div>
""", unsafe_allow_html=True)

# 2. HÀM CHUYỂN ĐỔI WORD
def generate_word_file(text_content):
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        pypandoc.download_pandoc()
        
    temp_md = "temp.md"
    out_docx = "Tai_Lieu_Toan.docx"
    with open(temp_md, "w", encoding="utf-8") as f:
        f.write(text_content)
    pypandoc.convert_file(temp_md, 'docx', outputfile=out_docx)
    with open(out_docx, "rb") as f:
        return f.read()

# 3. CẤU HÌNH API GEMINI
load_dotenv()
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Báo lỗi: Chưa tìm thấy API Key.")
    st.stop()

genai.configure(api_key=api_key)

try:
    with open("prompts/system.txt", "r", encoding="utf-8") as f:
        system_instruction = f.read()
except FileNotFoundError:
    system_instruction = "Bạn là chuyên gia sư phạm Toán. Hãy trình bày nội dung bằng Markdown."

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=system_instruction
)

# 4. THANH BÊN (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Tùy chọn Biên soạn")
    phan_mon = st.selectbox("Phân môn:", ["Đại số", "Hình học", "Giải tích", "Thống kê & Xác suất"])
    khoi_lop = st.selectbox("Khối lớp:", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9", "Lớp 10", "Lớp 11", "Lớp 12"])
    
    st.markdown("---")
    loai_yeu_cau = st.radio("📝 Thầy/Cô muốn AI tạo gì?", ("Soạn Giáo án (Chuẩn CV 5512)", "Soạn Đề / Bài tập"))
    st.markdown("---")
    
    if loai_yeu_cau == "Soạn Giáo án (Chuẩn CV 5512)":
        st.subheader("📖 Chi tiết Giáo án")
        loai_bai_day = st.selectbox("Loại bài dạy:", ["Bài học mới", "Luyện tập", "Ôn tập chương", "Thực hành / Trải nghiệm"])
        phuong_phap = st.selectbox("Định hướng phương pháp:", ["Phát triển năng lực chung", "Tăng cường hoạt động nhóm", "Dạy học dự án / STEM", "Trọng tâm luyện giải toán"])
        chi_tiet_prompt = f"- Loại bài dạy: {loai_bai_day}\n- Phương pháp trọng tâm: {phuong_phap}"
        
    else:
        st.subheader("🎯 Cấu trúc Đề (Chuẩn Form mới)")
        st.markdown("**1. Phân bổ Mức độ nhận thức (%):**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            tl_nb = st.number_input("Nhận biết (%)", min_value=0, max_value=100, value=40, step=10)
            tl_vd = st.number_input("Vận dụng (%)", min_value=0, max_value=100, value=20, step=10)
        with col_m2:
            tl_th = st.number_input("Thông hiểu (%)", min_value=0, max_value=100, value=30, step=10)
            tl_vdc = st.number_input("VD cao (%)", min_value=0, max_value=100, value=10, step=10)
            
        if (tl_nb + tl_th + tl_vd + tl_vdc) != 100:
            st.warning("⚠️ Tổng tỉ lệ chưa đúng 100%.")

        st.markdown("**2. Phân bổ Số lượng câu hỏi:**")
        col1, col2 = st.columns(2)
        with col1:
            sl_phan_1 = st.number_input("P1. TN Nhiều lựa chọn:", min_value=0, max_value=50, value=12)
            sl_phan_2 = st.number_input("P2. TN Đúng/Sai (x4 ý):", min_value=0, max_value=20, value=4)
        with col2:
            sl_phan_3 = st.number_input("P3. Trả lời ngắn:", min_value=0, max_value=20, value=6)
            sl_phan_4 = st.number_input("P4. Tự luận:", min_value=0, max_value=10, value=2)
            
        chi_tiet_prompt = f"""
        - TỈ LỆ NHẬN THỨC: Nhận biết {tl_nb}%, Thông hiểu {tl_th}%, Vận dụng {tl_vd}%, VD cao {tl_vdc}%.
        - CẤU TRÚC ĐỀ KIỂM TRA:
          + Phần I (Nhiều lựa chọn): {sl_phan_1} câu.
          + Phần II (Đúng/Sai): {sl_phan_2} câu (mỗi câu bắt buộc 4 ý a, b, c, d trình bày theo đúng ví dụ mẫu).
          + Phần III (Trả lời ngắn): {sl_phan_3} câu (có chừa dòng kẻ chấm điền đáp án).
          + Phần IV (Tự luận): {sl_phan_4} câu (có chừa khoảng trống làm bài).
        * Bắt buộc có Bảng đáp án và Lời giải chi tiết ở cuối trang (ngăn cách bằng `---`).
        """

# 5. KHU VỰC TƯƠNG TÁC
tab1, tab2 = st.tabs(["🚀 Tương tác Trực tiếp", "🕰️ Lịch sử đã tạo"])

with tab1:
    st.subheader("💡 1. Khởi tạo Nội dung")
    user_input = st.text_area("Nhập tên bài hoặc chủ đề...", placeholder="Ví dụ: Đề kiểm tra giữa kì 1 Toán 12...", height=100)

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        btn_tao = st.button("🚀 Bắt đầu tạo", type="primary")
    with col_btn2:
        btn_moi = st.button("🧹 Làm mới / Bắt đầu bài mới", type="secondary")

    if btn_moi:
        st.session_state.chat_messages = []
        st.session_state.current_chat = None
        st.session_state.latest_docx = None
        st.rerun()

    if btn_tao:
        if user_input.strip() == "":
            st.warning("Vui lòng nhập chủ đề!")
        else:
            with st.spinner("⏳ Trợ lý của thầy Hoàng Anh đang làm việc hết công suất nên từ từ nhé..."):
                full_prompt = f"Phân môn: Toán {phan_mon} {khoi_lop}.\nYêu cầu chính: {loai_yeu_cau}.\nCấu trúc:\n{chi_tiet_prompt}\nNội dung: {user_input}"
                try:
                    st.session_state.current_chat = model.start_chat(history=[])
                    response = st.session_state.current_chat.send_message(full_prompt)
                    
                    st.session_state.chat_messages = [
                        {"role": "user", "content": f"**Yêu cầu ban đầu:** {user_input}"},
                        {"role": "assistant", "content": response.text}
                    ]
                    
                    docx_data = generate_word_file(response.text)
                    st.session_state.latest_docx = docx_data
                    
                    st.session_state.history.insert(0, {
                        "thoi_gian": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
                        "yeu_cau": user_input,
                        "loai": "Giáo án" if "Giáo án" in loai_yeu_cau else "Đề thi",
                        "ket_qua": response.text,
                        "file_word": docx_data
                    })
                    st.rerun() 
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")

    st.markdown("---")
    
    if st.session_state.chat_messages:
        st.subheader("💬 2. Nội dung & Chỉnh sửa")
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if st.session_state.latest_docx:
            st.download_button(
                label="📥 TẢI BẢN WORD CẬP NHẬT MỚI NHẤT (.docx)",
                data=st.session_state.latest_docx,
                file_name="Tai_Lieu_Toan_Cap_Nhat.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )

    if follow_up := st.chat_input("Nhập yêu cầu sửa thêm (VD: Thêm 2 câu khó, sửa câu 3 thành tự luận...)"):
        if st.session_state.current_chat:
            st.session_state.chat_messages.append({"role": "user", "content": follow_up})
            with st.chat_message("user"):
                st.markdown(follow_up)
                
            with st.chat_message("assistant"):
                with st.spinner("⏳ Trợ lý đang chỉnh sửa theo yêu cầu của Thầy..."):
                    try:
                        reply = st.session_state.current_chat.send_message(follow_up)
                        st.markdown(reply.text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply.text})
                        
                        new_docx = generate_word_file(reply.text)
                        st.session_state.latest_docx = new_docx
                        
                        st.session_state.history.insert(0, {
                            "thoi_gian": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
                            "yeu_cau": f"[Chỉnh sửa] {follow_up}",
                            "loai": "Bản sửa đổi",
                            "ket_qua": reply.text,
                            "file_word": new_docx
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi sửa: {e}")
        else:
            st.warning("⚠️ Thầy cần 'Bắt đầu tạo' nội dung gốc trước khi yêu cầu chỉnh sửa nhé!")

with tab2:
    st.subheader("Lịch sử các phiên làm việc")
    if len(st.session_state.history) == 0:
        st.info("Chưa có dữ liệu.")
    else:
        if st.button("🗑️ Xóa toàn bộ lịch sử"):
            st.session_state.history = []
            st.rerun()
            
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"🕒 {item['thoi_gian']} | {item['loai']}: {item['yeu_cau'][:40]}..."):
                st.download_button(
                    label="📥 Tải lại File Word này",
                    data=item["file_word"],
                    file_name=f"Lich_su_{i}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_{i}"
                )
                st.markdown("---")
                st.markdown(item["ket_qua"])