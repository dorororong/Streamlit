import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from plotnine import (
    ggplot, aes, geom_histogram, geom_point, geom_bar,
    geom_boxplot, geom_col, geom_line, theme_minimal, theme, element_text
)
import matplotlib.font_manager as font_manager

# 1. (GitHub Actions 등 리눅스 환경) apt-get install fonts-nanum
# 2. Python 코드에서 폰트 설정:
font_path = 'font/NanumGothic-Bold.ttf'
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

def is_continuous(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)

def load_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    return None

def main():
    st.title("간단한 시각화 App (ggplot 방식)")

    # --- 1) 데이터 업로드 ---
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])
    df = load_data(uploaded_file)

    if df is not None:
        st.success("데이터 업로드 성공!")
        st.write("미리보기:")
        st.dataframe(df.head())
    else:
        st.info("엑셀 파일을 업로드해주세요.")

    st.markdown("---")

    # --- 2) 그래프 종류, X축, Y축 선택 ---
    col_graph_type, col_x, col_y = st.columns([1.3, 1, 1])
    with col_graph_type:
        graph_type = st.selectbox(
            "그래프 종류 선택",
            ["선택안함", "히스토그램", "산점도", "막대그래프", "상자그림", "선그래프"]
        )
    with col_x:
        x_col = st.selectbox("X축", options=["사용안함"] + (df.columns.tolist() if df is not None else []))
    with col_y:
        if df is not None:
            y_options = ["사용안함", "개수"] + df.columns.tolist()
        else:
            y_options = ["사용안함", "개수"]
        y_col = st.selectbox("Y축", options=y_options)

    st.markdown("---")

    # --- 3) 그래프별 옵션 ---
    st.markdown("### 그래프 옵션")

    bins = None
    color_col = None
    group_col = None
    agg_method = None  # 막대그래프용 (합계/평균)

    if df is not None and graph_type != "선택안함":
        if graph_type == "히스토그램":
            st.markdown("**히스토그램 옵션**")
            bins = st.slider("빈(bin) 개수", 5, 100, 20, 1)

            st.markdown("**그룹 옵션** (겹쳐진 히스토그램)")
            discrete_cols = [c for c in df.columns if not is_continuous(df[c])]
            group_col = st.selectbox("그룹(옵션)", ["없음"] + discrete_cols)

        elif graph_type == "산점도":
            st.markdown("**산점도 옵션**")
            discrete_cols = [c for c in df.columns if not is_continuous(df[c])]
            color_col = st.selectbox("색상(이산형 변수)", ["없음"] + discrete_cols)

        elif graph_type == "막대그래프":
            st.markdown("**막대그래프 옵션**")
            # x는 이산형
            # y = 개수 or 연속형(geom_col)
            discrete_cols_except_x = [
                c for c in df.columns
                if (not is_continuous(df[c])) and c != x_col
            ]
            group_col = st.selectbox("그룹(옵션)", ["없음"] + discrete_cols_except_x)

            # 집계 방식: y축이 개수가 아닐 때 '합계', '평균' 중 선택
            # (y 연속형인 경우)
            if y_col not in ["사용안함", "개수"] and is_continuous(df[y_col]):
                agg_method = st.selectbox("집계 방식", ["합계", "평균"])

        elif graph_type == "상자그림":
            st.markdown("**상자그림 옵션**")
            discrete_cols_except_x = [
                c for c in df.columns
                if (not is_continuous(df[c])) and c != x_col
            ]
            group_col = st.selectbox("그룹(옵션)", ["없음"] + discrete_cols_except_x)

        elif graph_type == "선그래프":
            st.markdown("**선그래프 옵션**")
            discrete_cols_all = [c for c in df.columns if not is_continuous(df[c])]
            color_col = st.selectbox("색상(이산형, 옵션)", ["없음"] + discrete_cols_all)

    st.markdown("---")

    # --- 4) 그래프 결과 ---
    st.markdown("### 그래프 결과")
    plot = None
    filtered_df = df.copy() if df is not None else None

    if df is not None and graph_type != "선택안함":
        # --- 5) 이산형 필터 ---
        discrete_filter_cols = []
        for c in [x_col, y_col, group_col, color_col]:
            if c and c not in ["사용안함", "없음", "개수"] and (not is_continuous(df[c])):
                discrete_filter_cols.append(c)
        discrete_filter_cols = list(dict.fromkeys(discrete_filter_cols))

        for col_name in discrete_filter_cols:
            raw_vals = filtered_df[col_name].dropna().unique()
            unique_vals_str = sorted(map(str, raw_vals))
            selected_vals_str = st.multiselect(
                f"'{col_name}' 필터 선택",
                unique_vals_str,
                default=unique_vals_str
            )
            # 필터 적용
            filtered_df = filtered_df[filtered_df[col_name].astype(str).isin(selected_vals_str)]

        # 그래프를 그리기 위한 타입 체크
        x_is_cont = (x_col != "사용안함") and is_continuous(filtered_df[x_col])
        y_is_cont = (y_col not in ["사용안함", "개수"]) and is_continuous(filtered_df[y_col])

        from plotnine import ggplot, aes, theme_minimal

        # --- 그래프별 로직 ---
        if graph_type == "히스토그램":
            if x_col != "사용안함" and x_is_cont:
                if group_col and group_col != "없음":
                    plot = (
                        ggplot(filtered_df, aes(x=x_col, fill=group_col))
                        + geom_histogram(
                            bins=bins,
                            color="white",
                            alpha=0.5,
                            position="identity"
                        )
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
                else:
                    plot = (
                        ggplot(filtered_df, aes(x=x_col))
                        + geom_histogram(bins=bins, fill="steelblue", color="white")
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
            else:
                st.error("히스토그램은 X축에 연속형 변수가 필요합니다.")

        elif graph_type == "산점도":
            if x_col != "사용안함" and y_col not in ["사용안함", "개수"] and x_is_cont and y_is_cont:
                if color_col and color_col != "없음":
                    plot = (
                        ggplot(filtered_df, aes(x=x_col, y=y_col, color=color_col))
                        + geom_point()
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
                else:
                    plot = (
                        ggplot(filtered_df, aes(x=x_col, y=y_col))
                        + geom_point(color="steelblue")
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
            else:
                st.error("산점도는 X, Y 모두 연속형 변수가 필요합니다.")

        elif graph_type == "막대그래프":
            # x = 이산형
            if x_col != "사용안함" and not x_is_cont:
                # (1) y_col = '개수' => geom_bar
                if y_col == "개수":
                    if group_col and group_col != "없음":
                        plot = (
                            ggplot(filtered_df, aes(x=x_col, fill=group_col))
                            + geom_bar(position="dodge")
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                    else:
                        plot = (
                            ggplot(filtered_df, aes(x=x_col))
                            + geom_bar(fill="steelblue")
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                else:
                    # (2) y_col = 연속형 => geom_col
                    if y_is_cont:
                        # 합계 / 평균 선택 => groupby
                        # group_col도 고려
                        if agg_method in ["합계", "평균"]:
                            if group_col and group_col != "없음":
                                if agg_method == "합계":
                                    aggregated_df = filtered_df.groupby([x_col, group_col], as_index=False)[y_col].sum()
                                else:
                                    aggregated_df = filtered_df.groupby([x_col, group_col], as_index=False)[y_col].mean()

                                plot = (
                                    ggplot(aggregated_df, aes(x=x_col, y=y_col, fill=group_col))
                                    + geom_col(position="dodge")
                                    + theme_minimal()
                                    + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                                )
                            else:
                                # group이 없음
                                if agg_method == "합계":
                                    aggregated_df = filtered_df.groupby(x_col, as_index=False)[y_col].sum()
                                else:
                                    aggregated_df = filtered_df.groupby(x_col, as_index=False)[y_col].mean()

                                plot = (
                                    ggplot(aggregated_df, aes(x=x_col, y=y_col))
                                    + geom_col(fill="steelblue")
                                    + theme_minimal()
                                    + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                                )
                        else:
                            # agg_method 미선택 => row별 그대로 geom_col
                            if group_col and group_col != "없음":
                                plot = (
                                    ggplot(filtered_df, aes(x=x_col, y=y_col, fill=group_col))
                                    + geom_col(position="dodge")
                                    + theme_minimal()
                                    + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                                )
                            else:
                                plot = (
                                    ggplot(filtered_df, aes(x=x_col, y=y_col))
                                    + geom_col(fill="steelblue")
                                    + theme_minimal()
                                    + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                                )
                    else:
                        st.error("막대그래프에서 Y축은 '개수' 또는 연속형 변수가 필요합니다.")
            else:
                st.error("막대그래프는 X축이 이산형이어야 합니다.")

        elif graph_type == "상자그림":
            # x 이산형, y 연속형
            if x_col != "사용안함" and not x_is_cont and y_col not in ["사용안함", "개수"] and y_is_cont:
                if group_col and group_col != "없음":
                    plot = (
                        ggplot(filtered_df, aes(x=x_col, y=y_col, fill=group_col))
                        + geom_boxplot()
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
                else:
                    plot = (
                        ggplot(filtered_df, aes(x=x_col, y=y_col))
                        + geom_boxplot()
                        + theme_minimal()
                        + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                    )
            else:
                st.error("상자그림은 X=이산형, Y=연속형 변수가 필요합니다.")

        elif graph_type == "선그래프":
            # (1) x_col != "사용안함" & x,y 모두 연속형 => 일반 라인
            # (2) x_col == "사용안함" & y_col 연속형 => 인덱스 vs y_col
            if x_col != "사용안함":
                if x_is_cont and y_is_cont:
                    if color_col and color_col != "없음":
                        plot = (
                            ggplot(filtered_df, aes(x=x_col, y=y_col, color=color_col, group=color_col))
                            + geom_line()
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                    else:
                        plot = (
                            ggplot(filtered_df, aes(x=x_col, y=y_col))
                            + geom_line(color="steelblue")
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                else:
                    st.error("선그래프(일반)는 x,y 모두 연속형일 때 사용하세요.")
            else:
                if y_col not in ["사용안함", "개수"] and y_is_cont:
                    tmp_df = filtered_df.reset_index(drop=False).rename(columns={"index": "IDX"})
                    if color_col and color_col != "없음":
                        plot = (
                            ggplot(tmp_df, aes(x="IDX", y=y_col, color=color_col, group=color_col))
                            + geom_line()
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                    else:
                        plot = (
                            ggplot(tmp_df, aes(x="IDX", y=y_col))
                            + geom_line(color="steelblue")
                            + theme_minimal()
                            + theme(figure_size=(10, 6),text=element_text(family='NanumGothic', size=20))
                        )
                else:
                    st.error("선그래프: x='사용안함'일 때는 Y축이 연속형 변수여야 합니다. (인덱스 vs y_col)")

        if plot is not None:
            fig = plot.draw()
            st.pyplot(fig)
    else:
        st.info("그래프 종류를 선택해주세요 (또는 데이터를 업로드하세요).")

if __name__ == "__main__":
    main()
