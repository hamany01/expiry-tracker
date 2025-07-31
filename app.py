# app.py - صفحة الدخول الرئيسية
import streamlit as st
from auth_system import AuthSystem

# إعدادات أساسية للصفحة
st.set_page_config(
    page_title="نظام تتبع الانتهاء - تسجيل الدخول",
    page_icon="🔐",
    layout="centered"
)

# استدعاء نظام الصلاحيات
auth = AuthSystem()

# التحقق مما إذا كان المستخدم مسجلاً للدخول بالفعل
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# عرض واجهة تسجيل الدخول إذا لم يكن المستخدم مسجلاً
if not st.session_state['authenticated']:
    st.title("🔐 تسجيل الدخول إلى النظام")
    st.write("الرجاء إدخال اسم المستخدم وكلمة المرور.")

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")

        if submitted:
            user = auth.authenticate_user(username, password)
            if user:
                st.session_state['user_info'] = user
                st.session_state['authenticated'] = True
                st.session_state['user_permissions'] = auth.get_user_permissions(user['id'])
                st.rerun()  # إعادة تحميل الصفحة لإظهار المحتوى بعد الدخول
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

    st.info("💡 **معلومات الدخول الافتراضية للمدير:**\n\n- اسم المستخدم: `admin`\n- كلمة المرور: `admin123`")

    # إيقاف تنفيذ باقي الكود إذا لم يتم الدخول
    st.stop()

# هذا الجزء من الكود يعمل فقط بعد تسجيل الدخول بنجاح
st.success(f"أهلاً بك، {st.session_state['user_info']['full_name']}!")
st.write("لقد تم تسجيل دخولك بنجاح. يمكنك الآن تصفح الصفحات من الشريط الجانبي.")

if st.button("تسجيل الخروج"):
    st.session_state['authenticated'] = False
    st.session_state['user_info'] = None
    st.session_state['user_permissions'] = []
    st.rerun()
