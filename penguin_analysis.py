import streamlit as st
from palmerpenguins import load_penguins
import pandas as pd
import plotly.express as px

st.title("펭귄 데이터 분석")

# 데이터 로드
penguins = load_penguins()

if penguins is None or penguins.empty:
    st.write("데이터 로드에 실패했습니다.")
else:
    # 수치형, 범주형 변수 구분
    numeric_vars = penguins.select_dtypes(include=['float64', 'int64']).columns.tolist()
    factor_vars = penguins.select_dtypes(include=['object', 'category']).columns.tolist()

    st.subheader("펭귄 데이터 개요")
    st.write(penguins.head())

    # 산점도 옵션
    st.subheader("산점도 옵션")
    col1, col2 = st.columns([1,3])
    with col1:
        xvar_scatter = st.selectbox("X축 변수 선택(숫자형):", numeric_vars, index=numeric_vars.index("bill_length_mm") if "bill_length_mm" in numeric_vars else 0)
        yvar_scatter = st.selectbox("Y축 변수 선택(숫자형):", numeric_vars, index=numeric_vars.index("bill_depth_mm") if "bill_depth_mm" in numeric_vars else 0)
        colorvar_scatter = st.selectbox("색상 변수 선택:", ["None"] + factor_vars, index=(["None"] + factor_vars).index("species") if "species" in factor_vars else 0)
        sizevar_scatter = st.selectbox("크기 변수 선택(숫자형):", ["None"] + numeric_vars, index=0)
    with col2:
        # 산점도 그리기
        df_scatter = penguins.dropna(subset=[xvar_scatter, yvar_scatter])
        plot_args = dict(x=xvar_scatter, y=yvar_scatter)
        if colorvar_scatter != "None":
            plot_args["color"] = colorvar_scatter
        if sizevar_scatter != "None":
            plot_args["size"] = sizevar_scatter
        
        fig_scatter = px.scatter(df_scatter, **plot_args, title="펭귄 데이터 산점도")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 박스플롯 옵션
    st.subheader("박스플롯 옵션")
    col3, col4 = st.columns([1,3])
    with col3:
        # 박스플롯: X축 범주형, Y축 수치형
        # 기본값 species, bill_length_mm
        if factor_vars:
            xvar_box = st.selectbox("X축 변수(범주형):", factor_vars, index=factor_vars.index("species") if "species" in factor_vars else 0)
        else:
            xvar_box = None
        yvar_box = st.selectbox("Y축 변수(숫자형):", numeric_vars, index=numeric_vars.index("bill_length_mm") if "bill_length_mm" in numeric_vars else 0)
    with col4:
        if xvar_box is not None:
            df_box = penguins.dropna(subset=[xvar_box, yvar_box])
            fig_box = px.box(df_box, x=xvar_box, y=yvar_box, title="펭귄 데이터 박스플롯", color=xvar_box)
            # legend.position='none' 대신 color_discrete_sequence 등으로 조정 가능
            # plotly는 legend 숨기려면 fig_box.update_layout(showlegend=False) 사용 가능
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.write("범주형 변수가 없습니다. 데이터셋을 확인하세요.")
