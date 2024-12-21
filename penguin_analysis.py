import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.title("엑셀 데이터 분석 (Github data/ 폴더 연동)")

# data 폴더에 존재하는 xlsx 파일 목록 (예: penguins.xlsx, datafile2.xlsx, ...)
data_files = [
    "penguins_data.xlsx",     # 예시 파일
    # 필요하면 더 추가...
]

# GitHub 레포 주소: 실제 사용자/레포이름으로 수정
github_username = "dorororong"  
github_repo = "Streamlit"

# data_files 리스트 중에서 하나를 선택하게 함
selected_file = st.selectbox("불러올 Excel 파일 선택:", data_files)

# base URL (raw 버전) 
base_url = f"https://raw.githubusercontent.com/{github_username}/{github_repo}/main/data/"

# 선택한 파일의 raw URL
file_url = base_url + selected_file

st.write(f"**선택된 파일:** {selected_file}")
st.write("**Github Raw URL:**", file_url)

# 파일 읽기
try:
    response = requests.get(file_url)
    response.raise_for_status()  # URL 오류 시 예외 발생

    # xlsx 파일 바이너리를 메모리에 올려서 pandas로 읽기
    xlsx_data = BytesIO(response.content)
    df = pd.read_excel(xlsx_data)

    st.subheader("데이터 미리보기")
    st.write(df.head())

    # 수치형 컬럼 / 범주형 컬럼 자동 탐색
    numeric_vars = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    factor_vars = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if len(numeric_vars) == 0 and len(factor_vars) == 0:
        st.warning("이 데이터에는 수치형/범주형 변수가 충분하지 않을 수 있습니다.")
    else:
        # ========== 산점도 (Scatter Plot) ==========
        st.subheader("산점도 옵션")

        col1, col2 = st.columns([1,3])
        with col1:
            if numeric_vars:
                xvar_scatter = st.selectbox("X축(숫자형)", numeric_vars, index=0)
                yvar_scatter = st.selectbox("Y축(숫자형)", numeric_vars, index=min(len(numeric_vars)-1, 1))
            else:
                st.error("숫자형 변수가 없습니다.")
                xvar_scatter, yvar_scatter = None, None

            colorvar_scatter = st.selectbox("색상(범주형)", ["None"] + factor_vars, index=0)
            sizevar_scatter  = st.selectbox("크기(숫자형)", ["None"] + numeric_vars, index=0)

        with col2:
            if xvar_scatter and yvar_scatter:
                df_scatter = df.dropna(subset=[xvar_scatter, yvar_scatter])
                # plotly scatter
                scatter_args = dict(x=xvar_scatter, y=yvar_scatter, title="산점도")

                # 색상 지정
                if colorvar_scatter != "None":
                    scatter_args["color"] = colorvar_scatter

                # 사이즈 지정
                if sizevar_scatter != "None":
                    scatter_args["size"] = sizevar_scatter

                fig_scatter = px.scatter(df_scatter, **scatter_args)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("숫자형 변수가 없어서 산점도를 그릴 수 없습니다.")

        # ========== 박스플롯 (Box Plot) ==========
        st.subheader("박스플롯 옵션")

        col3, col4 = st.columns([1,3])
        with col3:
            if factor_vars:
                xvar_box = st.selectbox("X축(범주형)", factor_vars, index=0)
            else:
                xvar_box = None
                st.error("범주형 변수가 없습니다. 박스플롯은 범주형 X축이 필요합니다.")

            if numeric_vars:
                yvar_box = st.selectbox("Y축(숫자형)", numeric_vars, index=0)
            else:
                yvar_box = None
                st.error("숫자형 변수가 없습니다. 박스플롯은 숫자형 Y축이 필요합니다.")

        with col4:
            if xvar_box and yvar_box:
                df_box = df.dropna(subset=[xvar_box, yvar_box])
                fig_box = px.box(df_box, x=xvar_box, y=yvar_box, color=xvar_box, title="박스플롯")
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)

except requests.exceptions.RequestException as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
except Exception as e:
    st.error(f"예상치 못한 오류가 발생했습니다: {e}")
