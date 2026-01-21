import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import base64

# 设置页面配置
st.set_page_config(
    page_title="心桥",
    page_icon="❤️",
    layout="wide"
)

# 添加蓝色和橙色主题样式
st.markdown("""
<style>
    .stApp {
        background-color: #e6f2ff;
    }
    .stSidebar {
        background-color: #1E90FF;
    }
    .stSidebar>div>div>div>div>div {
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1E90FF;
    }
    .stButton>button {
        background-color: #FF8C00;
        color: white;
    }
    .stRadio>div>label>div[data-testid="stRadio"]>div {
        color: #1E90FF;
    }
</style>
""", unsafe_allow_html=True)

# 创建必要的目录
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("avatars"):
    os.makedirs("avatars")

# 数据文件路径
USERS_FILE = "data/users.csv"
POSTS_FILE = "data/posts.csv"
COMMENTS_FILE = "data/comments.csv"
LIKES_FILE = "data/likes.csv"
ADMIN_REQUESTS_FILE = "data/admin_requests.csv"

# 初始化数据文件
def init_data_files():
    # 初始化用户文件
    if not os.path.exists(USERS_FILE):
        users_df = pd.DataFrame({
            "nickname": [],
            "password": [],
            "role": [],  # parent or child
            "avatar": [],
            "is_admin": []  # 是否为管理员
        })
        users_df.to_csv(USERS_FILE, index=False)
    
    # 初始化帖子文件
    if not os.path.exists(POSTS_FILE):
        posts_df = pd.DataFrame({
            "post_id": [],
            "nickname": [],
            "content": [],
            "created_at": []
        })
        posts_df.to_csv(POSTS_FILE, index=False)
    
    # 初始化评论文件
    if not os.path.exists(COMMENTS_FILE):
        comments_df = pd.DataFrame({
            "comment_id": [],
            "post_id": [],
            "nickname": [],
            "content": [],
            "created_at": []
        })
        comments_df.to_csv(COMMENTS_FILE, index=False)
    
    # 初始化点赞文件
    if not os.path.exists(LIKES_FILE):
        likes_df = pd.DataFrame({
            "like_id": [],
            "post_id": [],
            "nickname": [],
            "created_at": []
        })
        likes_df.to_csv(LIKES_FILE, index=False)
    
    # 初始化管理员请求文件
    if not os.path.exists(ADMIN_REQUESTS_FILE):
        admin_requests_df = pd.DataFrame({
            "request_id": [],
            "nickname": [],
            "status": [],  # pending, approved, rejected
            "created_at": []
        })
        admin_requests_df.to_csv(ADMIN_REQUESTS_FILE, index=False)

# 加载数据
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

# 保存数据
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# 密码加密
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 检查昵称是否存在
def nickname_exists(nickname):
    users_df = load_data(USERS_FILE)
    return nickname in users_df["nickname"].values

# 获取用户角色
def get_user_role(nickname):
    users_df = load_data(USERS_FILE)
    user = users_df[users_df["nickname"] == nickname]
    if not user.empty:
        return user.iloc[0]["role"]
    return None

# 获取用户头像
def get_user_avatar(nickname):
    users_df = load_data(USERS_FILE)
    user = users_df[users_df["nickname"] == nickname]
    if not user.empty:
        return user.iloc[0]["avatar"]
    return None

# 验证用户登录
def verify_login(nickname, password):
    users_df = load_data(USERS_FILE)
    user = users_df[users_df["nickname"] == nickname]
    if user.empty:
        return False
    hashed_pw = hash_password(password)
    return user.iloc[0]["password"] == hashed_pw

# 获取角色对应的颜色
def get_role_color(role):
    if role == "parent":
        return "#1E90FF"  # 蓝色
    elif role == "child":
        return "#FF8C00"  # 橙色
    return "#000000"  # 默认黑色

# 检查用户是否点赞了帖子
def has_liked(post_id, nickname):
    likes_df = load_data(LIKES_FILE)
    return not likes_df[(likes_df["post_id"] == post_id) & (likes_df["nickname"] == nickname)].empty

# 获取帖子的点赞数
def get_like_count(post_id):
    likes_df = load_data(LIKES_FILE)
    return len(likes_df[likes_df["post_id"] == post_id])

# 切换点赞状态
def toggle_like(post_id, nickname):
    likes_df = load_data(LIKES_FILE)
    if has_liked(post_id, nickname):
        # 取消点赞
        likes_df = likes_df[~((likes_df["post_id"] == post_id) & (likes_df["nickname"] == nickname))]
    else:
        # 添加点赞
        new_like_id = len(likes_df) + 1
        new_like = pd.DataFrame({
            "like_id": [new_like_id],
            "post_id": [post_id],
            "nickname": [nickname],
            "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        likes_df = pd.concat([likes_df, new_like], ignore_index=True)
    save_data(likes_df, LIKES_FILE)

# 检查用户是否为管理员
def is_admin(nickname):
    users_df = load_data(USERS_FILE)
    user = users_df[users_df["nickname"] == nickname]
    if not user.empty:
        return user.iloc[0].get("is_admin", False)
    return False

# 申请管理员权限
def request_admin(nickname):
    admin_requests_df = load_data(ADMIN_REQUESTS_FILE)
    # 检查是否已有待处理的请求
    existing_request = admin_requests_df[(admin_requests_df["nickname"] == nickname) & (admin_requests_df["status"] == "pending")]
    if not existing_request.empty:
        return False
    
    # 创建新请求
    new_request_id = len(admin_requests_df) + 1
    new_request = pd.DataFrame({
        "request_id": [new_request_id],
        "nickname": [nickname],
        "status": ["pending"],
        "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    admin_requests_df = pd.concat([admin_requests_df, new_request], ignore_index=True)
    save_data(admin_requests_df, ADMIN_REQUESTS_FILE)
    return True

# 处理管理员请求
def process_admin_request(request_id, action):
    admin_requests_df = load_data(ADMIN_REQUESTS_FILE)
    request = admin_requests_df[admin_requests_df["request_id"] == request_id]
    if request.empty:
        return False
    
    nickname = request.iloc[0]["nickname"]
    admin_requests_df.loc[admin_requests_df["request_id"] == request_id, "status"] = action
    save_data(admin_requests_df, ADMIN_REQUESTS_FILE)
    
    if action == "approved":
        # 设置用户为管理员
        users_df = load_data(USERS_FILE)
        users_df.loc[users_df["nickname"] == nickname, "is_admin"] = True
        save_data(users_df, USERS_FILE)
    
    return True

# 主页
def main_page():
    # 设置页面样式
    st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .post-section {
        background-color: rgba(30, 144, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 2px 0;
    }
    .comment-card {
        background-color: rgba(255, 140, 0, 0.1);
        padding: 5px;
        border-radius: 8px;
        margin: 1px 0;
    }
    .horizontal-user-info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .comment-section {
        margin-top: 5px;
    }
    .nav-container {
        background-color: #1E90FF;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: white;
        width: 100%;
    }
    .nav-container .stButton>button {
        background-color: #FF8C00;
        color: white;
    }
    .nav-container .stRadio>div>label {
        color: white !important;
    }
    .nav-container .stRadio>div>label>div[data-testid="stRadio"]>div {
        color: white !important;
    }
    .nav-container p {
        color: white !important;
    }
    .nav-container div {
        color: white !important;
    }
    .nav-container span {
        color: white !important;
    }
    .nav-container .stImage {
        margin: 0;
    }
    .nav-container .stColumns {
        width: 100%;
    }
    .nav-container .stRadio > label {
        font-size: 5em !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 顶部导航
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # 导航容器
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    # 顶部用户信息和退出按钮
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.user:
            st.write(f"当前用户: {st.session_state.user}")
            # 显示用户头像
            avatar = get_user_avatar(st.session_state.user)
            if avatar and os.path.exists(f"avatars/{avatar}"):
                st.image(f"avatars/{avatar}", width=50)
    with col2:
        if st.session_state.user:
            if st.button("退出登录"):
                st.session_state.user = None
                st.rerun()
    
    # 顶部导航菜单
    if st.session_state.user:
        menu_options = ["我要发帖", "孩子的心声", "家长的困惑", "申请管理员"]
        if is_admin(st.session_state.user):
            menu_options.insert(4, "后台管理")
        menu = st.radio("导航", menu_options, horizontal=True)
    else:
        menu = st.radio("导航", ["首页", "注册", "登录"], horizontal=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("心桥 - 连接亲子的桥梁")
    
    # 首页
    if menu == "首页":
        st.subheader("分享你的故事")
        
        # 显示所有帖子
        posts_df = load_data(POSTS_FILE)
        if not posts_df.empty:
            # 按时间倒序排列
            posts_df = posts_df.sort_values("created_at", ascending=False)
            
            for _, post in posts_df.iterrows():
                st.markdown("---")
                
                # 稍透明的蓝色卡片
                st.markdown('<div class="post-section">', unsafe_allow_html=True)
                
                # 水平显示帖主信息
                st.markdown('<div class="horizontal-user-info">', unsafe_allow_html=True)
                avatar = get_user_avatar(post["nickname"])
                if avatar and os.path.exists(f"avatars/{avatar}"):
                    st.image(f"avatars/{avatar}", width=50)
                role = get_user_role(post["nickname"])
                role_suffix = "-家长" if role == "parent" else "-孩子" if role == "child" else ""
                st.markdown(f"<p style='color:black; font-weight:bold;'>{post['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 帖子内容
                st.write(f"**{post['content']}**")
                st.write(f"发布时间: {post['created_at']}")
                
                # 点赞和删除功能
                if st.session_state.user:
                    col3, col4 = st.columns([1, 1])
                    with col3:
                        like_count = get_like_count(post["post_id"])
                        liked = has_liked(post["post_id"], st.session_state.user)
                        if st.button(f"{'❤️' if liked else '🤍'} 点赞 ({like_count})", key=f"like_{post['post_id']}"):
                            toggle_like(post["post_id"], st.session_state.user)
                            st.rerun()
                    with col4:
                        if post["nickname"] == st.session_state.user:
                            if st.button("删除帖子", key=f"delete_post_{post['post_id']}"):
                                # 删除帖子
                                posts_df = load_data(POSTS_FILE)
                                posts_df = posts_df[posts_df["post_id"] != post["post_id"]]
                                save_data(posts_df, POSTS_FILE)
                                
                                # 删除相关评论
                                comments_df = load_data(COMMENTS_FILE)
                                comments_df = comments_df[comments_df["post_id"] != post["post_id"]]
                                save_data(comments_df, COMMENTS_FILE)
                                
                                # 删除相关点赞
                                likes_df = load_data(LIKES_FILE)
                                likes_df = likes_df[likes_df["post_id"] != post["post_id"]]
                                save_data(likes_df, LIKES_FILE)
                                
                                st.success("帖子已删除")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 手风琴功能 - 折叠/展开评论
                if f"expanded_{post['post_id']}" not in st.session_state:
                    st.session_state[f"expanded_{post['post_id']}"] = False
                
                # 评论部分
                st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                
                # 加载评论数据
                comments_df = load_data(COMMENTS_FILE)
                post_comments = comments_df[comments_df["post_id"] == post["post_id"]]
                comment_count = len(post_comments)
                
                # 显示评论标题和折叠/展开按钮（仅当有评论时显示按钮）
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown('<p style="font-size:16px; font-weight:bold;">评论:</p>', unsafe_allow_html=True)
                with col2:
                    if comment_count > 0:
                        # 小按钮，显示评论总数
                        toggle_key = f"toggle_comment_{post['post_id']}_{comment_count}"
                        if st.button(f"{'展开' if not st.session_state[f'expanded_{post['post_id']}'] else '折叠'}({comment_count})", key=toggle_key, help="展开/折叠评论"):
                            st.session_state[f"expanded_{post['post_id']}"] = not st.session_state[f"expanded_{post['post_id']}"]
                
                # 根据状态显示或隐藏评论
                if st.session_state[f"expanded_{post['post_id']}"] or comment_count == 0:
                    if not post_comments.empty:
                        for idx, comment in post_comments.iterrows():
                            # 稍透明的橙色卡片
                            st.markdown('<div class="comment-card">', unsafe_allow_html=True)
                            comment_role = get_user_role(comment["nickname"])
                            role_suffix = "-家长" if comment_role == "parent" else "-孩子" if comment_role == "child" else ""
                            st.markdown(f"<p style='color:black; font-weight:bold;'>{comment['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-weight:bold;'>{comment['content']}</p>", unsafe_allow_html=True)
                            st.write(f"评论时间: {comment['created_at']}")
                            
                            # 删除评论功能
                            if st.session_state.user and (comment["nickname"] == st.session_state.user):
                                delete_key = f"delete_comment_{comment['comment_id']}_{idx}"
                                if st.button(f"删除评论", key=delete_key):
                                    comments_df = load_data(COMMENTS_FILE)
                                    comments_df = comments_df[comments_df["comment_id"] != comment["comment_id"]]
                                    save_data(comments_df, COMMENTS_FILE)
                                    st.success("评论已删除")
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write("暂无评论")
                    
                    # 评论输入
                    if st.session_state.user:
                        comment_key = f"comment_{post['post_id']}_{comment_count}"
                        submit_key = f"submit_comment_{post['post_id']}_{comment_count}"
                        comment_content = st.text_area("写下你的评论...", key=comment_key)
                        if st.button("提交评论", key=submit_key):
                            if comment_content:
                                comments_df = load_data(COMMENTS_FILE)
                                new_comment_id = len(comments_df) + 1
                                new_comment = pd.DataFrame({
                                    "comment_id": [new_comment_id],
                                    "post_id": [post["post_id"]],
                                    "nickname": [st.session_state.user],
                                    "content": [comment_content],
                                    "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                                })
                                comments_df = pd.concat([comments_df, new_comment], ignore_index=True)
                                save_data(comments_df, COMMENTS_FILE)
                                st.success("发表成功！")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write("暂无帖子，快来发布第一条吧！")
    
    # 我要发帖
    elif menu == "我要发帖":
        if st.session_state.user:
            st.subheader("发布新帖子")
            content = st.text_area("分享你的故事或感受...", height=200)
            if st.button("发布"):
                if content:
                    posts_df = load_data(POSTS_FILE)
                    new_post_id = len(posts_df) + 1
                    new_post = pd.DataFrame({
                        "post_id": [new_post_id],
                        "nickname": [st.session_state.user],
                        "content": [content],
                        "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    })
                    posts_df = pd.concat([posts_df, new_post], ignore_index=True)
                    save_data(posts_df, POSTS_FILE)
                    st.success("发表成功！")
                else:
                    st.warning("请输入内容")
        else:
            st.warning("请先登录")
    
    # 孩子的心声
    elif menu == "孩子的心声":
        st.subheader("孩子的心声")
        
        # 显示孩子发布的帖子
        posts_df = load_data(POSTS_FILE)
        child_posts = []
        for _, post in posts_df.iterrows():
            if get_user_role(post["nickname"]) == "child":
                child_posts.append(post)
        
        if child_posts:
            # 按时间倒序排列
            child_posts_df = pd.DataFrame(child_posts).sort_values("created_at", ascending=False)
            
            for _, post in child_posts_df.iterrows():
                st.markdown("---")
                
                # 稍透明的蓝色卡片
                st.markdown('<div class="post-section">', unsafe_allow_html=True)
                
                # 水平显示帖主信息
                st.markdown('<div class="horizontal-user-info">', unsafe_allow_html=True)
                avatar = get_user_avatar(post["nickname"])
                if avatar and os.path.exists(f"avatars/{avatar}"):
                    st.image(f"avatars/{avatar}", width=50)
                role = get_user_role(post["nickname"])
                role_suffix = "-家长" if role == "parent" else "-孩子" if role == "child" else ""
                st.markdown(f"<p style='color:black; font-weight:bold;'>{post['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 帖子内容
                st.write(f"**{post['content']}**")
                st.write(f"发布时间: {post['created_at']}")
                
                # 点赞和删除功能
                if st.session_state.user:
                    col3, col4 = st.columns([1, 1])
                    with col3:
                        like_count = get_like_count(post["post_id"])
                        liked = has_liked(post["post_id"], st.session_state.user)
                        if st.button(f"{'❤️' if liked else '🤍'} 点赞 ({like_count})", key=f"like_child_{post['post_id']}"):
                            toggle_like(post["post_id"], st.session_state.user)
                            st.rerun()
                    with col4:
                        if post["nickname"] == st.session_state.user:
                            if st.button("删除帖子", key=f"delete_post_child_{post['post_id']}"):
                                # 删除帖子
                                posts_df = load_data(POSTS_FILE)
                                posts_df = posts_df[posts_df["post_id"] != post["post_id"]]
                                save_data(posts_df, POSTS_FILE)
                                
                                # 删除相关评论
                                comments_df = load_data(COMMENTS_FILE)
                                comments_df = comments_df[comments_df["post_id"] != post["post_id"]]
                                save_data(comments_df, COMMENTS_FILE)
                                
                                # 删除相关点赞
                                likes_df = load_data(LIKES_FILE)
                                likes_df = likes_df[likes_df["post_id"] != post["post_id"]]
                                save_data(likes_df, LIKES_FILE)
                                
                                st.success("帖子已删除")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 手风琴功能 - 折叠/展开评论
                if f"expanded_{post['post_id']}" not in st.session_state:
                    st.session_state[f"expanded_{post['post_id']}"] = False
                
                # 评论部分
                st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                
                # 加载评论数据
                comments_df = load_data(COMMENTS_FILE)
                post_comments = comments_df[comments_df["post_id"] == post["post_id"]]
                comment_count = len(post_comments)
                
                # 显示评论标题和折叠/展开按钮（仅当有评论时显示按钮）
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown('<p style="font-size:16px; font-weight:bold;">评论:</p>', unsafe_allow_html=True)
                with col2:
                    if comment_count > 0:
                        # 小按钮，显示评论总数
                        toggle_key = f"toggle_comment_child_{post['post_id']}_{comment_count}"
                        if st.button(f"{'展开' if not st.session_state[f'expanded_{post['post_id']}'] else '折叠'}({comment_count})", key=toggle_key, help="展开/折叠评论"):
                            st.session_state[f"expanded_{post['post_id']}"] = not st.session_state[f"expanded_{post['post_id']}"]
                
                # 根据状态显示或隐藏评论
                if st.session_state[f"expanded_{post['post_id']}"] or comment_count == 0:
                    if not post_comments.empty:
                        for idx, comment in post_comments.iterrows():
                            # 稍透明的橙色卡片
                            st.markdown('<div class="comment-card">', unsafe_allow_html=True)
                            comment_role = get_user_role(comment["nickname"])
                            role_suffix = "-家长" if comment_role == "parent" else "-孩子" if comment_role == "child" else ""
                            st.markdown(f"<p style='color:black; font-weight:bold;'>{comment['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-weight:bold;'>{comment['content']}</p>", unsafe_allow_html=True)
                            st.write(f"评论时间: {comment['created_at']}")
                            
                            # 删除评论功能
                            if st.session_state.user and (comment["nickname"] == st.session_state.user):
                                delete_key = f"delete_comment_child_{comment['comment_id']}_{idx}"
                                if st.button(f"删除评论", key=delete_key):
                                    comments_df = load_data(COMMENTS_FILE)
                                    comments_df = comments_df[comments_df["comment_id"] != comment["comment_id"]]
                                    save_data(comments_df, COMMENTS_FILE)
                                    st.success("评论已删除")
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write("暂无评论")
                    
                    # 评论输入
                    if st.session_state.user:
                        comment_key = f"comment_child_{post['post_id']}_{comment_count}"
                        submit_key = f"submit_comment_child_{post['post_id']}_{comment_count}"
                        comment_content = st.text_area("写下你的评论...", key=comment_key)
                        if st.button("提交评论", key=submit_key):
                            if comment_content:
                                comments_df = load_data(COMMENTS_FILE)
                                new_comment_id = len(comments_df) + 1
                                new_comment = pd.DataFrame({
                                    "comment_id": [new_comment_id],
                                    "post_id": [post["post_id"]],
                                    "nickname": [st.session_state.user],
                                    "content": [comment_content],
                                    "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                                })
                                comments_df = pd.concat([comments_df, new_comment], ignore_index=True)
                                save_data(comments_df, COMMENTS_FILE)
                                st.success("发表成功！")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write("暂无孩子的帖子")
    
    # 家长的困惑
    elif menu == "家长的困惑":
        st.subheader("家长的困惑")
        
        # 显示家长发布的帖子
        posts_df = load_data(POSTS_FILE)
        parent_posts = []
        for _, post in posts_df.iterrows():
            if get_user_role(post["nickname"]) == "parent":
                parent_posts.append(post)
        
        if parent_posts:
            # 按时间倒序排列
            parent_posts_df = pd.DataFrame(parent_posts).sort_values("created_at", ascending=False)
            
            for _, post in parent_posts_df.iterrows():
                st.markdown("---")
                
                # 稍透明的蓝色卡片
                st.markdown('<div class="post-section">', unsafe_allow_html=True)
                
                # 水平显示帖主信息
                st.markdown('<div class="horizontal-user-info">', unsafe_allow_html=True)
                avatar = get_user_avatar(post["nickname"])
                if avatar and os.path.exists(f"avatars/{avatar}"):
                    st.image(f"avatars/{avatar}", width=50)
                role = get_user_role(post["nickname"])
                role_suffix = "-家长" if role == "parent" else "-孩子" if role == "child" else ""
                st.markdown(f"<p style='color:black; font-weight:bold;'>{post['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 帖子内容
                st.write(f"**{post['content']}**")
                st.write(f"发布时间: {post['created_at']}")
                
                # 点赞和删除功能
                if st.session_state.user:
                    col3, col4 = st.columns([1, 1])
                    with col3:
                        like_count = get_like_count(post["post_id"])
                        liked = has_liked(post["post_id"], st.session_state.user)
                        if st.button(f"{'❤️' if liked else '🤍'} 点赞 ({like_count})", key=f"like_parent_{post['post_id']}"):
                            toggle_like(post["post_id"], st.session_state.user)
                            st.rerun()
                    with col4:
                        if post["nickname"] == st.session_state.user:
                            if st.button("删除帖子", key=f"delete_post_parent_{post['post_id']}"):
                                # 删除帖子
                                posts_df = load_data(POSTS_FILE)
                                posts_df = posts_df[posts_df["post_id"] != post["post_id"]]
                                save_data(posts_df, POSTS_FILE)
                                
                                # 删除相关评论
                                comments_df = load_data(COMMENTS_FILE)
                                comments_df = comments_df[comments_df["post_id"] != post["post_id"]]
                                save_data(comments_df, COMMENTS_FILE)
                                
                                # 删除相关点赞
                                likes_df = load_data(LIKES_FILE)
                                likes_df = likes_df[likes_df["post_id"] != post["post_id"]]
                                save_data(likes_df, LIKES_FILE)
                                
                                st.success("帖子已删除")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 手风琴功能 - 折叠/展开评论
                if f"expanded_{post['post_id']}" not in st.session_state:
                    st.session_state[f"expanded_{post['post_id']}"] = False
                
                # 评论部分
                st.markdown('<div class="comment-section">', unsafe_allow_html=True)
                
                # 加载评论数据
                comments_df = load_data(COMMENTS_FILE)
                post_comments = comments_df[comments_df["post_id"] == post["post_id"]]
                comment_count = len(post_comments)
                
                # 显示评论标题和折叠/展开按钮（仅当有评论时显示按钮）
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown('<p style="font-size:16px; font-weight:bold;">评论:</p>', unsafe_allow_html=True)
                with col2:
                    if comment_count > 0:
                        # 小按钮，显示评论总数
                        toggle_key = f"toggle_comment_parent_{post['post_id']}_{comment_count}"
                        if st.button(f"{'展开' if not st.session_state[f'expanded_{post['post_id']}'] else '折叠'}({comment_count})", key=toggle_key, help="展开/折叠评论"):
                            st.session_state[f"expanded_{post['post_id']}"] = not st.session_state[f"expanded_{post['post_id']}"]
                
                # 根据状态显示或隐藏评论
                if st.session_state[f"expanded_{post['post_id']}"] or comment_count == 0:
                    if not post_comments.empty:
                        for idx, comment in post_comments.iterrows():
                            # 稍透明的橙色卡片
                            st.markdown('<div class="comment-card">', unsafe_allow_html=True)
                            comment_role = get_user_role(comment["nickname"])
                            role_suffix = "-家长" if comment_role == "parent" else "-孩子" if comment_role == "child" else ""
                            st.markdown(f"<p style='color:black; font-weight:bold;'>{comment['nickname']}{role_suffix}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-weight:bold;'>{comment['content']}</p>", unsafe_allow_html=True)
                            st.write(f"评论时间: {comment['created_at']}")
                            
                            # 删除评论功能
                            if st.session_state.user and (comment["nickname"] == st.session_state.user):
                                delete_key = f"delete_comment_parent_{comment['comment_id']}_{idx}"
                                if st.button(f"删除评论", key=delete_key):
                                    comments_df = load_data(COMMENTS_FILE)
                                    comments_df = comments_df[comments_df["comment_id"] != comment["comment_id"]]
                                    save_data(comments_df, COMMENTS_FILE)
                                    st.success("评论已删除")
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write("暂无评论")
                    
                    # 评论输入
                    if st.session_state.user:
                        comment_key = f"comment_parent_{post['post_id']}_{comment_count}"
                        submit_key = f"submit_comment_parent_{post['post_id']}_{comment_count}"
                        comment_content = st.text_area("写下你的评论...", key=comment_key)
                        if st.button("提交评论", key=submit_key):
                            if comment_content:
                                comments_df = load_data(COMMENTS_FILE)
                                new_comment_id = len(comments_df) + 1
                                new_comment = pd.DataFrame({
                                    "comment_id": [new_comment_id],
                                    "post_id": [post["post_id"]],
                                    "nickname": [st.session_state.user],
                                    "content": [comment_content],
                                    "created_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                                })
                                comments_df = pd.concat([comments_df, new_comment], ignore_index=True)
                                save_data(comments_df, COMMENTS_FILE)
                                st.success("发表成功！")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write("暂无家长的帖子")
    
    # 申请管理员
    elif menu == "申请管理员":
        st.subheader("申请管理员权限")
        if st.session_state.user:
            if st.button("提交申请"):
                if request_admin(st.session_state.user):
                    st.success("申请已提交，等待审核！")
                else:
                    st.warning("您已有待处理的申请，请耐心等待！")
        else:
            st.warning("请先登录")
    
    
    
    # 注册
    elif menu == "注册":
        st.subheader("用户注册")
        
        nickname = st.text_input("昵称")
        password = st.text_input("密码", type="password")
        confirm_password = st.text_input("确认密码", type="password")
        role = st.radio("身份", ["家长", "孩子"])
        
        # 头像上传
        avatar = st.file_uploader("上传头像", type=["jpg", "jpeg", "png"])
        
        if st.button("注册"):
            # 验证输入
            if not nickname:
                st.warning("请输入昵称")
            elif nickname_exists(nickname):
                st.warning("昵称已存在")
            elif not password:
                st.warning("请输入密码")
            elif password != confirm_password:
                st.warning("两次输入的密码不一致")
            else:
                # 处理头像
                avatar_filename = None
                if avatar:
                    avatar_filename = f"{nickname}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{avatar.name.split('.')[-1]}"
                    with open(f"avatars/{avatar_filename}", "wb") as f:
                        f.write(avatar.getbuffer())
                
                # 保存用户信息
                users_df = load_data(USERS_FILE)
                new_user = pd.DataFrame({
                    "nickname": [nickname],
                    "password": [hash_password(password)],
                    "role": ["parent" if role == "家长" else "child"],
                    "avatar": [avatar_filename],
                    "is_admin": [False]
                })
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_data(users_df, USERS_FILE)
                
                st.success("注册成功！")
                st.session_state.user = nickname
                st.rerun()
    
    # 登录
    elif menu == "登录":
        st.subheader("用户登录")
        
        nickname = st.text_input("昵称")
        password = st.text_input("密码", type="password")
        
        if st.button("登录"):
            if verify_login(nickname, password):
                st.session_state.user = nickname
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("昵称或密码错误")
    
    # 后台管理
    elif menu == "后台管理":
        if is_admin(st.session_state.user):
            st.subheader("后台管理")
            
            # 统计数据
            st.write("## 统计数据")
            users_df = load_data(USERS_FILE)
            posts_df = load_data(POSTS_FILE)
            comments_df = load_data(COMMENTS_FILE)
            
            likes_df = load_data(LIKES_FILE)
            st.write(f"总用户数: {len(users_df)}")
            st.write(f"总帖子数: {len(posts_df)}")
            st.write(f"总评论数: {len(comments_df)}")
            st.write(f"总点赞数: {len(likes_df)}")
            
            # 处理管理员申请
            st.write("## 管理员申请管理")
            admin_requests_df = load_data(ADMIN_REQUESTS_FILE)
            pending_requests = admin_requests_df[admin_requests_df["status"] == "pending"]
            
            if not pending_requests.empty:
                for _, request in pending_requests.iterrows():
                    st.markdown("---")
                    st.write(f"**申请ID: {request['request_id']}**")
                    st.write(f"申请人: {request['nickname']}")
                    st.write(f"申请时间: {request['created_at']}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"批准申请 {request['request_id']}", key=f"approve_{request['request_id']}"):
                            process_admin_request(request['request_id'], "approved")
                            st.success("申请已批准")
                            st.rerun()
                    with col2:
                        if st.button(f"拒绝申请 {request['request_id']}", key=f"reject_{request['request_id']}"):
                            process_admin_request(request['request_id'], "rejected")
                            st.success("申请已拒绝")
                            st.rerun()
            else:
                st.write("暂无待处理的管理员申请")
        
        # 管理帖子
        st.write("## 管理帖子")
        if not posts_df.empty:
            for _, post in posts_df.iterrows():
                st.markdown("---")
                st.write(f"**帖子ID: {post['post_id']}**")
                st.write(f"发布人: {post['nickname']}")
                st.write(f"内容: {post['content']}")
                st.write(f"发布时间: {post['created_at']}")
                if st.button(f"删除帖子 {post['post_id']}", key=f"delete_post_{post['post_id']}"):
                    # 删除帖子
                    posts_df = posts_df[posts_df["post_id"] != post["post_id"]]
                    save_data(posts_df, POSTS_FILE)
                    
                    # 删除相关评论
                    comments_df = comments_df[comments_df["post_id"] != post["post_id"]]
                    save_data(comments_df, COMMENTS_FILE)
                    
                    st.success("帖子已删除")
                    st.rerun()
        else:
            st.write("暂无帖子")
        
        # 管理评论
        st.write("## 管理评论")
        if not comments_df.empty:
            for _, comment in comments_df.iterrows():
                st.markdown("---")
                st.write(f"**评论ID: {comment['comment_id']}**")
                st.write(f"评论人: {comment['nickname']}")
                st.write(f"内容: {comment['content']}")
                st.write(f"评论时间: {comment['created_at']}")
                if st.button(f"删除评论 {comment['comment_id']}", key=f"delete_comment_{comment['comment_id']}"):
                    comments_df = comments_df[comments_df["comment_id"] != comment["comment_id"]]
                    save_data(comments_df, COMMENTS_FILE)
                    st.success("评论已删除")
                    st.rerun()
        else:
            st.write("暂无评论")

# 初始化数据文件
init_data_files()

# 运行主页面
if __name__ == "__main__":
    main_page()

