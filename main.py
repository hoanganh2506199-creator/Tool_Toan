import streamlit as st
import os
import subprocess
import glob
from config import model
import pypandoc
# 1. Hàm đọc file yêu cầu hệ thống (system.txt)
def doc_file_yeu_cau(filepath="prompts/system.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Bạn là chuyên gia biên soạn đề thi KHTN." # Dự phòng nếu mất file

# Hàm chuyển đổi Word tự động bằng pypandoc
def xuat_word_bang_pandoc(noi_dung_md, ten_file_docx="De_Thi_KHTN_Ban_Chuan.docx"):
    try:
        # Tự động kiểm tra và tải gói pypandoc nếu máy chưa có
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            pypandoc.download_pandoc()
            
        temp_md = "temp.md"
        with open(temp_md, "w", encoding="utf-8") as f:
            f.write(noi_dung_md)
            
        # Chuyển đổi trực tiếp từ Markdown sang docx
        pypandoc.convert_file(temp_md, 'docx', outputfile=ten_file_docx)
        return True
    except Exception as e:
        st.error(f"❌ Lỗi khi xuất file Word với pypandoc: {e}")
        return False
# --- 1. DỮ LIỆU PHẠM VI KIẾN THỨC CHI TIẾT (KẾT NỐI TRI THỨC) ---
DANH_MUC_KHTN = {
    "Lớp 6": {
        "Chương 1: Mở đầu về Khoa học tự nhiên": ["Bài 1: Giới thiệu về Khoa học tự nhiên", "Bài 2: An toàn trong phòng thực hành", "Bài 3: Sử dụng kính lúp", "Bài 4: Sử dụng kính hiển vi quang học", "Bài 5: Đo chiều dài", "Bài 6: Đo khối lượng", "Bài 7: Đo thời gian", "Bài 8: Đo nhiệt độ"],
        "Chương 2: Chất quanh ta": ["Bài 9: Sự đa dạng của chất", "Bài 10: Các thể của chất và sự chuyển thể", "Bài 11: Oxygen. Không khí"],
        "Chương 3: Một số vật liệu, nguyên liệu, nhiên liệu, lương thực - thực phẩm": ["Bài 12: Một số vật liệu", "Bài 13: Một số nguyên liệu", "Bài 14: Một số nhiên liệu", "Bài 15: Một số lương thực, thực phẩm"],
        "Chương 4: Hỗn hợp. Tách chất ra khỏi hỗn hợp": ["Bài 16: Hỗn hợp các chất", "Bài 17: Tách chất ra khỏi hỗn hợp"],
        "Chương 5: Tế bào": ["Bài 18: Tế bào – Đơn vị cơ bản của sự sống", "Bài 19: Cấu tạo và chức năng các thành phần của tế bào", "Bài 20: Sự lớn lên và sinh sản của tế bào", "Bài 21: Thực hành: Quan sát và phân biệt một số loại tế bào"],
        "Chương 6: Từ tế bào đến cơ thể": ["Bài 22: Cơ thể sinh vật", "Bài 23: Tổ chức cơ thể đa bào", "Bài 24: Thực hành: Quan sát hệ cơ quan của sinh vật"],
        "Chương 7: Đa dạng thế giới sống": ["Bài 25: Hệ thống phân loại sinh vật", "Bài 26: Khóa lưỡng phân", "Bài 27: Vi khuẩn", "Bài 28: Thực hành: Quan sát vi khuẩn, tìm hiểu các bước làm sữa chua", "Bài 29: Virus", "Bài 30: Nguyên sinh vật", "Bài 31: Thực hành: Quan sát nguyên sinh vật", "Bài 32: Nấm", "Bài 33: Thực hành: Quan sát các loại nấm", "Bài 34: Thực vật", "Bài 35: Thực hành: Quan sát và phân biệt các nhóm thực vật", "Bài 36: Động vật", "Bài 37: Thực hành: Quan sát và nhận biết một số nhóm động vật", "Bài 38: Đa dạng sinh học", "Bài 39: Tìm hiểu sinh vật ngoài thiên nhiên"],
        "Chương 8: Lực trong đời sống": ["Bài 40: Lực là gì?", "Bài 41: Biểu diễn lực", "Bài 42: Biến dạng của lò xo", "Bài 43: Trọng lượng, lực hấp dẫn", "Bài 44: Lực ma sát", "Bài 45: Lực cản của nước"],
        "Chương 9: Năng lượng": ["Bài 46: Năng lượng và sự truyền năng lượng", "Bài 47: Một số dạng năng lượng", "Bài 48: Sự chuyển hóa năng lượng", "Bài 49: Năng lượng hao phí", "Bài 50: Năng lượng tái tạo"],
        "Chương 10: Trái Đất và bầu trời": ["Bài 51: Hệ Mặt Trời", "Bài 52: Chuyển động nhìn thấy của Mặt Trời. Thiên thể", "Bài 53: Mặt Trăng", "Bài 54: Hệ Ngân Hà"]
    },
    "Lớp 7": {
        "Chương 1: Nguyên tử. Sơ lược về bảng tuần hoàn các nguyên tố hóa học": ["Bài 1: Phương pháp và kĩ năng học tập môn KHTN", "Bài 2: Nguyên tử", "Bài 3: Nguyên tố hóa học", "Bài 4: Sơ lược về bảng tuần hoàn các nguyên tố hóa học"],
        "Chương 2: Phân tử. Liên kết hóa học": ["Bài 5: Phân tử - Đơn chất - Hợp chất", "Bài 6: Giới thiệu về liên kết hóa học", "Bài 7: Hóa trị và công thức hóa học"],
        "Chương 3: Tốc độ": ["Bài 8: Tốc độ chuyển động", "Bài 9: Đo tốc độ", "Bài 10: Đồ thị quãng đường - thời gian", "Bài 11: Thảo luận về ảnh hưởng của tốc độ trong an toàn giao thông"],
        "Chương 4: Âm thanh": ["Bài 12: Sóng âm", "Bài 13: Độ to và độ cao của âm", "Bài 14: Phản xạ âm, chống ô nhiễm tiếng ồn"],
        "Chương 5: Ánh sáng": ["Bài 15: Năng lượng ánh sáng. Tia sáng, vùng tối", "Bài 16: Sự phản xạ ánh sáng", "Bài 17: Ảnh của vật qua gương phẳng"],
        "Chương 6: Từ": ["Bài 18: Nam châm", "Bài 19: Từ trường", "Bài 20: Chế tạo nam châm điện đơn giản"],
        "Chương 7: Trao đổi chất và chuyển hóa năng lượng ở sinh vật": ["Bài 21: Khái quát về trao đổi chất và chuyển hóa năng lượng", "Bài 22: Quang hợp ở thực vật", "Bài 23: Một số yếu tố ảnh hưởng đến quang hợp", "Bài 24: Thực hành: Chứng minh quang hợp ở cây xanh", "Bài 25: Hô hấp tế bào", "Bài 26: Một số yếu tố ảnh hưởng đến hô hấp tế bào", "Bài 27: Thực hành: Hô hấp ở thực vật", "Bài 28: Trao đổi khí ở sinh vật", "Bài 29: Vai trò của nước và chất dinh dưỡng đối với sinh vật", "Bài 30: Trao đổi nước và chất dinh dưỡng ở thực vật", "Bài 31: Trao đổi nước và chất dinh dưỡng ở động vật", "Bài 32: Thực hành: Chứng minh thân vận chuyển nước và lá thoát hơi nước"],
        "Chương 8: Cảm ứng ở sinh vật": ["Bài 33: Cảm ứng ở sinh vật và tập tính ở động vật", "Bài 34: Vận dụng hiện tượng cảm ứng ở sinh vật vào thực tiễn", "Bài 35: Thực hành: Cảm ứng ở sinh vật"],
        "Chương 9: Sinh trưởng và phát triển ở sinh vật": ["Bài 36: Khái quát về sinh trưởng và phát triển ở sinh vật", "Bài 37: Ứng dụng sinh trưởng và phát triển ở sinh vật vào thực tiễn", "Bài 38: Thực hành: Quan sát, mô tả sự sinh trưởng và phát triển ở một số sinh vật"],
        "Chương 10: Sinh sản ở sinh vật": ["Bài 39: Sinh sản vô tính ở sinh vật", "Bài 40: Sinh sản hữu tính ở sinh vật", "Bài 41: Một số yếu tố ảnh hưởng và điều hòa sinh sản ở sinh vật", "Bài 42: Cơ thể sinh vật là một thể thống nhất"]
    },
    "Lớp 8": {
        "Chương 1: Phản ứng hóa học": ["Bài 1: Sử dụng hóa chất, dụng cụ và thiết bị điện an toàn", "Bài 2: Biến đổi vật lí và biến đổi hóa học", "Bài 3: Phản ứng hóa học", "Bài 4: Mol và tỉ khối của chất khí", "Bài 5: Tính toán theo phương trình hóa học", "Bài 6: Nồng độ dung dịch", "Bài 7: Tốc độ phản ứng và chất xúc tác"],
        "Chương 2: Một số hợp chất thông dụng": ["Bài 8: Acid", "Bài 9: Base. Thang pH", "Bài 10: Oxide", "Bài 11: Muối", "Bài 12: Phân bón hóa học"],
        "Chương 3: Khối lượng riêng và Áp suất": ["Bài 13: Khối lượng riêng", "Bài 14: Thực hành: Xác định khối lượng riêng", "Bài 15: Áp suất trên một bề mặt", "Bài 16: Áp suất chất lỏng. Áp suất khí quyển", "Bài 17: Lực đẩy Archimedes"],
        "Chương 4: Tác dụng làm quay của lực": ["Bài 18: Tác dụng làm quay của lực. Moment lực", "Bài 19: Đòn bẩy và ứng dụng"],
        "Chương 5: Điện": ["Bài 20: Hiện tượng nhiễm điện do cọ xát", "Bài 21: Dòng điện, nguồn điện", "Bài 22: Mạch điện đơn giản", "Bài 23: Tác dụng của dòng điện"],
        "Chương 6: Nhiệt": ["Bài 24: Năng lượng nhiệt", "Bài 25: Sự truyền nhiệt lượng"],
        "Chương 7: Sinh học cơ thể người": ["Bài 26: Khái quát về cơ thể người", "Bài 27: Hệ vận động ở người", "Bài 28: Hệ tiêu hóa ở người", "Bài 29: Dinh dưỡng và tiêu hóa ở người", "Bài 30: Máu và hệ tuần hoàn ở người", "Bài 31: Thực hành về máu và hệ tuần hoàn", "Bài 32: Hệ hô hấp ở người", "Bài 33: Môi trường trong cơ thể và hệ bài tiết ở người", "Bài 34: Hệ thần kinh và các giác quan ở người", "Bài 35: Hệ nội tiết ở người", "Bài 36: Da và điều hòa thân nhiệt ở người", "Bài 37: Hệ sinh dục và sinh sản ở người"],
        "Chương 8: Sinh vật và môi trường": ["Bài 38: Môi trường và các nhân tố sinh thái", "Bài 39: Quần thể sinh vật", "Bài 40: Quần xã sinh vật", "Bài 41: Hệ sinh thái", "Bài 42: Sinh quyển"]
    },
    "Lớp 9": {
        "Chương 1: Năng lượng cơ học": ["Bài 1: Nhận biết một số dụng cụ, hóa chất. Thuyết trình một vấn đề KHTN", "Bài 2: Động năng. Thế năng", "Bài 3: Cơ năng"],
        "Chương 2: Ánh sáng": ["Bài 4: Khúc xạ ánh sáng", "Bài 5: Hiện tượng phản xạ toàn phần", "Bài 6: Lăng kính. Sự màu sắc ánh sáng", "Bài 7: Thấu kính. Ảnh của vật qua thấu kính", "Bài 8: Kính lúp. Mắt. Kính cận, kính viễn"],
        "Chương 3: Điện": ["Bài 9: Điện trở. Định luật Ohm", "Bài 10: Đoạn mạch nối tiếp, đoạn mạch song song", "Bài 11: Năng lượng điện. Công suất điện"],
        "Chương 4: Điện từ": ["Bài 12: Cảm ứng điện từ", "Bài 13: Dòng điện xoay chiều"],
        "Chương 5: Kim loại. Sự khác biệt cơ bản giữa phi kim và kim loại": ["Bài 14: Tính chất chung của kim loại", "Bài 15: Dãy hoạt động hóa học của kim loại", "Bài 16: Tách kim loại. Sử dụng hợp kim"],
        "Chương 6: Hợp chất hữu cơ": ["Bài 17: Hợp chất hữu cơ", "Bài 18: Alkane (Hydrocarbon)", "Bài 19: Ethylene (Alkene)", "Bài 20: Ethylic alcohol (Cồn)", "Bài 21: Acetic acid", "Bài 22: Lipid (Chất béo)", "Bài 23: Carbohydrate (Glucid)", "Bài 24: Protein", "Bài 25: Polymer"],
        "Chương 7: Di truyền": ["Bài 26: Gene và sự biểu hiện của gene", "Bài 27: DNA và RNA", "Bài 28: Nhiễm sắc thể", "Bài 29: Quá trình nguyên phân và giảm phân", "Bài 30: Định luật Mendel", "Bài 31: Đột biến gene và đột biến nhiễm sắc thể", "Bài 32: Di truyền y học"],
        "Chương 8: Tiến hóa": ["Bài 33: Bằng chứng tiến hóa", "Bài 34: Học thuyết tiến hóa tổng hợp hiện đại (Chọn lọc tự nhiên, nhân tạo)"],
        "Chương 9: Sinh thái và Môi trường": ["Bài 35: Biến đổi khí hậu", "Bài 36: Phát triển bền vững"]
    }
}

# Cấu hình trang
st.set_page_config(page_title="Thầy giáo Hoàng Anh", layout="wide")
st.title("📚 Thầy giáo Hoàng Anh")

# --- 2. THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🎯 Cấu trúc Đề (Chuẩn Form mới)")
    
    st.markdown("**📌 Phạm vi kiến thức**")
    khoi_lop = st.selectbox("Chọn Khối lớp:", list(DANH_MUC_KHTN.keys()))
    
    danh_sach_chuong = list(DANH_MUC_KHTN[khoi_lop].keys())
    chuong_duoc_chon = st.multiselect("Chọn Chương:", danh_sach_chuong, default=[danh_sach_chuong[0]])
    
    danh_sach_bai = []
    for chuong in chuong_duoc_chon:
        danh_sach_bai.extend(DANH_MUC_KHTN[khoi_lop][chuong])
        
    bai_duoc_chon = st.multiselect("Chọn Bài cụ thể (Tùy chọn):", danh_sach_bai, default=danh_sach_bai)
    
    st.markdown("---")
    
    st.markdown("**0. Tỉ lệ Phân môn (%)**")
    mon_duoc_chon = st.multiselect("Chọn các phân môn tham gia:", ["KHTN Lí", "KHTN Hóa", "Sinh học", "Vật Lí"], default=["KHTN Lí", "KHTN Hóa"])
    
    ti_le_mon = {}
    if mon_duoc_chon:
        cols_mon = st.columns(len(mon_duoc_chon))
        for i, mon in enumerate(mon_duoc_chon):
            with cols_mon[i]:
                ti_le_mon[mon] = st.number_input(f"{mon}", min_value=0, max_value=100, value=100 // len(mon_duoc_chon), key=f"tl_{mon}")
                
    st.markdown("---")
    
    st.markdown("**1. Phân bổ Mức độ nhận thức (%):**")
    col_md1, col_md2 = st.columns(2)
    with col_md1:
        nhan_biet = st.number_input("Nhận biết (%)", value=40)
        van_dung = st.number_input("Vận dụng (%)", value=20)
    with col_md2:
        thong_hieu = st.number_input("Thông hiểu (%)", value=30)
        vd_cao = st.number_input("VD cao (%)", value=10)

    st.markdown("**2. Phân bổ Số lượng câu hỏi:**")
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        sl_tn_nhieu = st.number_input("P1. TN Nhiều lựa chọn:", value=12)
        sl_tn_ds = st.number_input("P2. TN Đúng/Sai (x4 ý):", value=4)
    with col_sl2:
        sl_tl_ngan = st.number_input("P3. Trả lời ngắn:", value=6)
        sl_tu_luan = st.number_input("P4. Tự luận:", value=2)

# --- 3. MÀN HÌNH CHÍNH (MAIN AREA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def lam_moi_bai():
    st.session_state.messages = []

tab_tuong_tac, tab_lich_su = st.tabs(["🚀 Tương tác Trực tiếp", "🕰 Lịch sử đã tạo"])

with tab_tuong_tac:
    st.markdown("### 💡 1. Khởi tạo Nội dung")
    st.caption("Nhập tên bài hoặc chủ đề...")
    
    chu_de_nhap = st.text_area(
        label="Tên bài hoặc chủ đề",
        label_visibility="collapsed",
        placeholder="Ví dụ: Đề kiểm tra giữa kì 1 Toán 12...",
        height=100
    )
    
    col_btn1, col_btn2 = st.columns([1.5, 8.5])
    with col_btn1:
        btn_bat_dau = st.button("🚀 Bắt đầu tạo", type="primary", use_container_width=True)
    with col_btn2:
        btn_lam_moi = st.button("🧹 Làm mới / Bắt đầu bài mới", on_click=lam_moi_bai)
        
    st.markdown("---")
    
    # Hiển thị lịch sử tin nhắn
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Xử lý nút bắt đầu tạo đề
    if btn_bat_dau:
        if not chu_de_nhap:
            st.warning("Vui lòng nhập tên bài hoặc chủ đề cần tạo!")
        else:
            yeu_cau = f"**Chủ đề:** {chu_de_nhap}"
            st.session_state.messages.append({"role": "user", "content": yeu_cau})
            
            with st.chat_message("user"):
                st.markdown(yeu_cau)
                
            with st.chat_message("assistant"):
                with st.spinner("AI đang soạn đề dựa trên cấu hình và hệ thống luật... (Quá trình này mất khoảng 10-20 giây)"):
                    
                    chuoi_chuong = ", ".join(chuong_duoc_chon) if chuong_duoc_chon else "Toàn bộ"
                    chuoi_bai = ", ".join(bai_duoc_chon) if bai_duoc_chon else "Không giới hạn"
                    chuoi_ti_le_mon = ", ".join([f"{k} ({v}%)" for k, v in ti_le_mon.items()])
                    
                    # Gọi hàm đọc file system.txt
                    luat_he_thong = doc_file_yeu_cau("prompts/system.txt")
                    
                    prompt = f"""
                    {luat_he_thong}
                    
                    --- THÔNG SỐ ĐỀ BÀI LẦN NÀY ---
                    - Khối lớp: KHTN {khoi_lop}
                    - Chủ đề cụ thể: {chu_de_nhap}
                    - Phạm vi chương: {chuoi_chuong}
                    - Giới hạn bài: {chuoi_bai}
                    
                    CẤU TRÚC ĐỀ THI BẮT BUỘC:
                    - Tỉ lệ phân môn: {chuoi_ti_le_mon}.
                    - Tỉ lệ mức độ: Nhận biết {nhan_biet}%, Thông hiểu {thong_hieu}%, Vận dụng {van_dung}%, Vận dụng cao {vd_cao}%.
                    - Số lượng: {sl_tn_nhieu} câu TN nhiều lựa chọn, {sl_tn_ds} câu TN đúng/sai, {sl_tl_ngan} câu trả lời ngắn, {sl_tu_luan} câu tự luận.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        ket_qua_ai = response.text
                        st.markdown(ket_qua_ai)
                        st.session_state.messages.append({"role": "assistant", "content": ket_qua_ai})
                    except Exception as e:
                        st.error(f"❌ Lỗi kết nối đến AI: {e}")
                        
            st.rerun()
                    
    # Thanh chat để tương tác với kết quả
    yeu_cau_sua = st.chat_input("Nhập yêu cầu sửa thêm (VD: Đổi câu 3 thành mức độ Vận dụng cao...)")
    
    if yeu_cau_sua:
        st.session_state.messages.append({"role": "user", "content": yeu_cau_sua})
        with st.chat_message("user"):
            st.markdown(yeu_cau_sua)
            
        with st.chat_message("assistant"):
            with st.spinner("AI đang đọc lại đề cũ và tinh chỉnh theo yêu cầu..."):
                
                lich_su_hoi_thoai = "Dưới đây là bối cảnh trò chuyện hiện tại:\n"
                for msg in st.session_state.messages:
                    vai_tro = "Giáo viên yêu cầu" if msg['role'] == "user" else "AI đã tạo"
                    lich_su_hoi_thoai += f"--- {vai_tro} ---\n{msg['content']}\n\n"
                
                # Gọi lại hàm đọc file system.txt để nhắc AI không quên luật
                luat_he_thong = doc_file_yeu_cau("prompts/system.txt")
                
                prompt_hoan_chinh = f"{luat_he_thong}\n\n{lich_su_hoi_thoai}"
                
                try:
                    response = model.generate_content(prompt_hoan_chinh)
                    phan_hoi_sua = response.text
                    
                    st.markdown(phan_hoi_sua)
                    st.session_state.messages.append({"role": "assistant", "content": phan_hoi_sua})
                except Exception as e:
                    st.error(f"❌ Lỗi kết nối đến AI: {e}")
                    
        st.rerun()
    # --- PHẦN MỚI THÊM: NÚT TẢI XUỐNG FILE WORD ---
    # Kiểm tra xem AI đã tạo ra kết quả nào chưa
    tin_nhan_ai = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
    if tin_nhan_ai:
        st.markdown("---")
        st.markdown("### 📥 Tải Đề Thi Về Máy")
        
        # Lấy nội dung mới nhất AI vừa tạo hoặc vừa sửa
        noi_dung_moi_nhat = tin_nhan_ai[-1]["content"]
        ten_file_word = "De_Thi_KHTN_Ban_Chuan.docx"
        
        # Chạy ngầm Pandoc để tạo file
        thanh_cong = xuat_word_bang_pandoc(noi_dung_moi_nhat, ten_file_word)
        
        if thanh_cong:
            with open(ten_file_word, "rb") as file:
                st.download_button(
                    label="📥 TẢI FILE WORD (.docx) KHÔNG LỖI CÔNG THỨC",
                    data=file,
                    file_name=ten_file_word,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
with tab_lich_su:
    st.markdown("### 🕰 Danh sách đề thi đã lưu")
    st.info("Khu vực này hiển thị các file Word đã tạo trong các phiên làm việc trước.")