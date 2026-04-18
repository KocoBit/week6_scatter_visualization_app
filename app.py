import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform
import numpy as np


# --------------------------------------------------
# 한글 폰트 설정 함수
# --------------------------------------------------
def set_korean_font():
    # 현재 사용 중인 운영체제 이름을 확인한다.
    # Windows, Darwin(Mac), Linux 등이 결과로 나올 수 있다.
    system_name = platform.system()

    # 운영체제에 따라 한글 폰트를 다르게 지정한다.
    # 그래프에서 한글이 깨지지 않도록 하기 위한 설정이다.
    if system_name == "Windows":
        plt.rc("font", family="Malgun Gothic")
    elif system_name == "Darwin":
        plt.rc("font", family="AppleGothic")
    else:
        # Streamlit Cloud(리눅스)에서는 packages.txt로 설치한 폰트를 사용한다.
        plt.rc("font", family="Nanum Gothic")

    # 음수 기호(-)가 네모나 이상한 문자로 깨지는 현상을 막는다.
    plt.rcParams["axes.unicode_minus"] = False


# --------------------------------------------------
# CSV 파일 읽기 함수
# --------------------------------------------------
def load_data(uploaded_file):
    # 업로드한 CSV 파일을 pandas의 DataFrame 형태로 읽는다.
    # DataFrame은 표 형태 데이터를 다루기 편한 자료구조이다.
    df = pd.read_csv(uploaded_file)

    # 산점도와 상관계수 계산에 사용할 숫자형 열 목록이다.
    number_columns = ["공부시간", "점수", "출석률", "게임시간", "스트레스지수"]

    # 위 열들을 숫자형으로 변환한다.
    # 혹시 숫자가 아닌 값이 섞여 있으면 errors="coerce"에 의해 NaN으로 처리된다.
    for col in number_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 정리한 DataFrame을 반환한다.
    return df


# --------------------------------------------------
# 데이터 미리보기 함수
# --------------------------------------------------
def show_data(df):
    # 화면에 소제목 출력
    st.subheader("데이터 미리보기")

    # 데이터의 앞쪽 5행만 표 형태로 출력
    # head()는 처음 5개 행을 보여주는 함수이다.
    st.dataframe(df.head())


# --------------------------------------------------
# 산점도와 추세선 출력 함수
# --------------------------------------------------
def draw_scatter(df, x_column, y_column):
    # 그래프를 그릴 도화지(fig)와 좌표축(ax)을 생성한다.
    fig, ax = plt.subplots(figsize=(8, 6))

    # 전공 열에서 비어 있지 않은 값만 모아서 전공 종류를 확인한다.
    major_list = df["전공"].dropna().unique()

    # 전공별로 데이터를 나누어 서로 다른 그룹처럼 표시한다.
    for major in major_list:
        # 현재 전공에 해당하는 데이터만 따로 추출한다.
        major_data = df[df["전공"] == major]

        # 산점도 점을 찍는다.
        # x_column에 해당하는 값을 X축에,
        # y_column에 해당하는 값을 Y축에 표시한다.
        ax.scatter(
            major_data[x_column],
            major_data[y_column],
            label=major,   # 범례에 표시할 이름
            alpha=0.7      # 점을 약간 투명하게 표시
        )

    # --------------------------------------------------
    # 추세선 계산 부분
    # --------------------------------------------------

    # 추세선을 계산하려면 X축과 Y축 값이 모두 있어야 하므로
    # 결측값(NaN)이 있는 행은 제거한다.
    trend_data = df[[x_column, y_column]].dropna()

    # 점이 2개 이상은 있어야 직선을 만들 수 있으므로 조건을 확인한다.
    if len(trend_data) >= 2:
        # X축 값만 따로 저장
        x_values = trend_data[x_column]

        # Y축 값만 따로 저장
        y_values = trend_data[y_column]

        # np.polyfit(x, y, 1)은 1차 직선의 기울기와 절편을 구해준다.
        # 1차 직선은 y = ax + b 형태이다.
        # 여기서 a는 기울기(slope), b는 절편(intercept)이다.
        slope, intercept = np.polyfit(x_values, y_values, 1)

        # 추세선을 부드럽게 그리기 위해 X축 최소값~최대값 사이를
        # 100개의 점으로 나누어 만든다.
        trend_x = np.linspace(x_values.min(), x_values.max(), 100)

        # 직선식 y = ax + b를 이용해 추세선의 Y값을 계산한다.
        trend_y = slope * trend_x + intercept

        # 계산한 점들을 이용해 추세선을 그래프 위에 그린다.
        ax.plot(
            trend_x,
            trend_y,
            linestyle="--",  # 점선 모양
            linewidth=2,     # 선 두께
            label="추세선"
        )

    # 그래프 제목 설정
    ax.set_title(f"{x_column}와 {y_column}의 관계")

    # X축 이름 설정
    ax.set_xlabel(x_column)

    # Y축 이름 설정
    ax.set_ylabel(y_column)

    # 범례 표시
    ax.legend(title="전공")

    # 격자 표시
    ax.grid(True)

    # 완성된 그래프를 Streamlit 화면에 출력
    st.pyplot(fig)


# --------------------------------------------------
# 상관계수 출력 함수
# --------------------------------------------------
def show_correlation(df, x_column, y_column):
    # corr()는 두 열 사이의 상관계수를 계산한다.
    # 값이 1에 가까우면 양의 상관관계가 강하고,
    # -1에 가까우면 음의 상관관계가 강하다.
    # 0에 가까우면 관계가 약하다고 볼 수 있다.
    correlation = df[x_column].corr(df[y_column])

    # 소수 셋째 자리까지 출력
    st.write(f"상관계수 : {correlation:.3f}")


# ==================================================
# 메인 부분
# ==================================================

# 웹 페이지 제목 출력
st.title("산점도 활용 프로그램")

# 한글 폰트 설정
set_korean_font()

# CSV 파일 업로드 입력창 생성
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요.", type=["csv"])

# 파일이 업로드되었을 때만 아래 코드 실행
if uploaded_file is not None:
    # CSV 파일을 읽어서 데이터프레임으로 저장
    df = load_data(uploaded_file)

    # 데이터 미리보기 출력
    show_data(df)

    # 사용자가 선택할 수 있는 숫자형 항목 목록
    number_columns = ["공부시간", "점수", "출석률", "게임시간", "스트레스지수"]

    # 항목 선택 소제목 출력
    st.subheader("항목 선택")

    # X축 항목 선택 상자
    x_column = st.selectbox(
        "X축 항목을 선택하세요.",
        number_columns
    )

    # Y축 항목 선택 상자
    # index=1은 처음 화면에서 두 번째 항목을 기본값으로 선택한다는 뜻이다.
    y_column = st.selectbox(
        "Y축 항목을 선택하세요.",
        number_columns,
        index=1
    )

    # 버튼을 눌렀을 때만 그래프와 상관계수를 출력한다.
    if st.button("산점도 생성"):
        # 산점도와 추세선 출력
        draw_scatter(df, x_column, y_column)

        # 상관계수 출력
        show_correlation(df, x_column, y_column)