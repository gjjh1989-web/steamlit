import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정 (Wide 모드)
st.set_page_config(
    page_title='신경세포 활동 전위 탐구 발표',
    page_icon='⚡',
    layout='wide',
)

# 2. 사이드바 발표자 정보
with st.sidebar:
  st.header('📌 발표자 정보')
  st.markdown('---')
  st.markdown('**발표자:** 【지중호】')
  st.markdown('**분야:** 【생명과학】')
  st.markdown('**주제:** 【신경세포에서의 활동 전위 발생】')
  st.markdown('---')
  st.info('Streamlit과 Matplotlib을 활용한 과학 탐구 시뮬레이션 발표입니다.')


# 3. 시뮬레이션 표시 코드 (수정 없이 그대로 포함)
GLOWSCRIPT = 'https://www.glowscript.org'

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<link type="text/css" href="__GS__/css/redmond/2.1/jquery-ui.custom.css" rel="stylesheet" />
<link type="text/css" href="__GS__/css/ide.css" rel="stylesheet" />
<script src="__GS__/lib/jquery/2.1/jquery.min.js"></script>
<script src="__GS__/lib/jquery/2.1/jquery-ui.custom.min.js"></script>
<script src="__GS__/package/glow.3.2.min.js"></script>
<script src="__GS__/package/RScompiler.3.2.min.js"></script>
<script src="__GS__/package/RSrun.3.2.min.js"></script>
<style>
  body { background: white; margin: 0; padding: 8px; font-family: sans-serif; }
  #error { color: #c00; white-space: pre-wrap; font-family: monospace; }
</style>
</head><body>
<div id="error"></div>
<div id="glowscript" class="glowscript"></div>
<script>
function showError(msg) {
  document.getElementById("error").textContent = "시뮬레이션 오류: " + msg;
}
window.onerror = function (msg) { showError(msg); };
try {
  var source = __SOURCE__;
  var js = glowscript_compile(source, {lang: "vpython", version: "3.2"});
  window.__context = { glowscript_container: $("#glowscript").removeAttr("id") };
  (0, eval)(js + ";window.__main = __main__;");
  var result = window.__main();
  if (result && result.catch) result.catch(function (e) { showError(e); });
} catch (e) {
  showError(e);
}
</script>
</body></html>
"""


def show_vpython(code, height=800):
  source_js = json.dumps(code.strip()).replace('</', '<\\/')
  html = PAGE.replace('__GS__', GLOWSCRIPT).replace('__SOURCE__', source_js)
  components.html(html, height=height, scrolling=True)


# 4. 원본 VPython 코드 문자열 (한 글자도 수정하지 않고 그대로 삽입)
VPYTHON_CODE = r'''
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# --- 시뮬레이션 파라미터 설정 ---
num_na = 120  # 나트륨 이온 개수
num_k = 120  # 칼륨 이온 개수
width, height = 12.0, 10.0
total_frames = 300

np.random.seed(42)

# 초기 농도 설정: Na+는 세포 밖(y > 0)에 많고, K+는 세포 안(y < 0)에 많음
x_na = np.random.uniform(-5.5, 5.5, num_na)
y_na = np.random.uniform(1.0, 4.5, num_na)
vx_na = np.random.normal(0, 0.03, num_na)
vy_na = np.random.normal(0, 0.03, num_na)

x_k = np.random.uniform(-5.5, 5.5, num_k)
y_k = np.random.uniform(-4.5, -1.0, num_k)
vx_k = np.random.normal(0, 0.03, num_k)
vy_k = np.random.normal(0, 0.03, num_k)

# --- 서브플롯 구성 (위: 입자 시뮬레이션, 아래: 막전위 그래프) ---
fig, (ax_sim, ax_graph) = plt.subplots(
    2, 1, figsize=(10, 9), gridspec_kw={'height_ratios': [2, 1]}
)

# 막전위 그래프 데이터 미리 계산 (시간에 따른 mV 변화)
time_steps = np.linspace(0, 15, total_frames)
# 활동 전위 파형 모델링 함수
membrane_potential = (
    -70
    + 100 * np.exp(-(((time_steps % 5) - 1.5) ** 2) / 0.15)
    - 20 * np.exp(-(((time_steps % 5) - 2.5) ** 2) / 0.3)
)
# 과분극 표현 조정
membrane_potential[
    (time_steps % 5 > 2.0) & (time_steps % 5 < 3.5)
] -= 10  # 임시 조정


def init():
  # 1. 상단 세포막 시뮬레이션 초기화
  ax_sim.set_xlim(-width / 2, width / 2)
  ax_sim.set_ylim(-height / 2, height / 2)
  ax_sim.set_aspect('equal')
  ax_sim.set_title(
      'Neuron Action Potential Simulation', fontsize=13, fontweight='bold'
  )
  ax_sim.set_ylabel('Y Position (nm)')

  # 세포막 구조 그리기 (통로 및 펌프 위치 비워둠)
  ax_sim.axhline(
      0, xmin=0.0, xmax=1.0, color='dimgray', linewidth=7, label='Cell Membrane'
  )

  global scat_na, scat_k, line_vm, point_vm, phase_text
  scat_na = ax_sim.scatter(
      [], [], c='crimson', s=35, edgecolor='k', label='Na+ (Extracellular Rich)'
  )
  scat_k = ax_sim.scatter(
      [], [], c='dodgerblue', s=35, edgecolor='k', label='K+ (Intracellular Rich)'
  )
  ax_sim.legend(loc='upper right', framealpha=0.9, fontsize=9)

  # 2. 하단 막전위 그래프 초기화
  ax_graph.set_xlim(0, 15)
  ax_graph.set_ylim(-90, 50)
  ax_graph.set_xlabel('Time (ms)')
  ax_graph.set_ylabel('Membrane Potential (mV)')
  ax_graph.axhline(-70, color='gray', linestyle='--', label='Resting (-70mV)')
  ax_graph.grid(True, linestyle=':', alpha=0.6)

  (line_vm,) = ax_graph.plot(
      [], [], color='purple', linewidth=2.5, label='Action Potential ($V_m$)'
  )
  (point_vm,) = ax_graph.plot([], [], 'ro', markersize=8)
  phase_text = ax_graph.text(
      0.5,
      30,
      '',
      fontsize=11,
      fontweight='bold',
      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
  )
  ax_graph.legend(loc='lower right', fontsize=9)

  return scat_na, scat_k, line_vm, point_vm, phase_text


# --- 애니메이션 업데이트 함수 ---
def update(frame_idx):
  global x_na, y_na, vx_na, vy_na, x_k, y_k, vx_k, vy_k

  t = time_steps[frame_idx % total_frames]
  cycle_t = t % 5.0  # 5초 주기로 활동 전위 반복

  # 활동 전위 단계별 상태 정의
  # 0~1초: 휴지기 (Resting)
  # 1~2초: 탈분극 (Depolarization - Na+ 채널 열림)
  # 2~3.5초: 재분극 (Repolarization - K+ 채널 열림)
  # 3.5~5초: 과분극 및 회복 (Hyperpolarization & Pump)

  is_na_open = 1.0 if (1.0 < cycle_t < 2.0) else 0.1
  is_k_open = 1.0 if (2.0 < cycle_t < 3.5) else 0.1

  # --- 나트륨(Na+) 업데이트 ---
  vx_na += np.random.normal(0, 0.02, num_na)
  vy_na += np.random.normal(0, 0.02, num_na)
  vx_na *= 0.94
  vy_na *= 0.94

  x_na_new = x_na + vx_na
  y_na_new = y_na + vy_na

  # Na+ 통로 (x: -3.0 ~ -2.0)
  crossing_na = y_na * y_na_new < 0
  in_na_pore = (x_na > -3.0) & (x_na < -2.0)

  # 탈분극 시 Na+가 세포 안(y < 0)으로 대거 유입
  if 1.0 < cycle_t < 2.0:
    pull_na = in_na_pore & (y_na > 0)
    vy_na[pull_na] = -0.15  # 아래로 강제 이동

  reflect_na = crossing_na & (~in_na_pore | (is_na_open < 0.5))
  vy_na[reflect_na] = -vy_na[reflect_na]
  y_na_new[reflect_na] = y_na[reflect_na] + vy_na[reflect_na]

  # --- 칼륨(K+) 업데이트 ---
  vx_k += np.random.normal(0, 0.02, num_k)
  vy_k += np.random.normal(0, 0.02, num_k)
  vx_k *= 0.94
  vy_k *= 0.94

  x_k_new = x_k + vx_k
  y_k_new = y_k + vy_k

  # K+ 통로 (x: 2.0 ~ 3.0)
  crossing_k = y_k * y_k_new < 0
  in_k_pore = (x_k > 2.0) & (x_k < 3.0)

  # 재분극 시 K+가 세포 밖(y > 0)으로 대거 유출
  if 2.0 < cycle_t < 3.5:
    push_k = in_k_pore & (y_k < 0)
    vy_k[push_k] = 0.15  # 위로 강제 이동

  reflect_k = crossing_k & (~in_k_pore | (is_k_open < 0.5))
  vy_k[reflect_k] = -vy_k[reflect_k]
  y_k_new[reflect_k] = y_k[reflect_k] + vy_k[reflect_k]

  # --- 나트륨-칼륨 펌프 (중앙 x: -0.6 ~ 0.6, 항상 작동하여 농도 유지) ---
  pump_na = (np.abs(x_na) < 0.6) & (y_na < 0)
  y_na_new[pump_na] += 0.08  # 밖으로 밀어냄
  pump_k = (np.abs(x_k) < 0.6) & (y_k > 0)
  y_k_new[pump_k] -= 0.08  # 안으로 끌어들임

  # 영역 제한
  x_na_new = np.clip(x_na_new, -5.8, 5.8)
  y_na_new = np.clip(y_na_new, -4.8, 4.8)
  x_k_new = np.clip(x_k_new, -5.8, 5.8)
  y_k_new = np.clip(y_k_new, -4.8, 4.8)

  x_na[:], y_na[:] = x_na_new, y_na_new
  x_k[:], y_k[:] = x_k_new, y_k_new

  scat_na.set_offsets(np.c_[x_na, y_na])
  scat_k.set_offsets(np.c_[x_k, y_k])

  # --- 하단 그래프 업데이트 ---
  current_idx = frame_idx % total_frames
  line_vm.set_data(time_steps[:current_idx], membrane_potential[:current_idx])
  point_vm.set_data([t], [membrane_potential[current_idx]])

  # 단계별 텍스트 표시
  if cycle_t <= 1.0:
    phase_text.set_text('Phase: Resting State (-70 mV)')
  elif 1.0 < cycle_t <= 2.0:
    phase_text.set_text('Phase: Depolarization (Na+ Influx -> +30 mV)')
  elif 2.0 < cycle_t <= 3.5:
    phase_text.set_text('Phase: Repolarization (K+ Efflux -> Down)')
  else:
    phase_text.set_text('Phase: Hyperpolarization & Pump Recovery')

  return scat_na, scat_k, line_vm, point_vm, phase_text


# 애니메이션 실행
ani = FuncAnimation(
    fig, update, frames=total_frames, init_func=init, interval=40, blit=True
)

plt.tight_layout()
plt.show()
'''

# 5. 메인 타이틀
st.title('⚡ 신경세포에서의 활동 전위 발생 탐구')
st.markdown('지중호 학생의 생명과학 탐구 발표 웹앱입니다.')

# 6. 6개 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    '① 탐구 질문',
    '② 시뮬레이션',
    '③ 원리',
    '④ 결과 분석',
    '⑤ 결론과 한계',
    '⑥ 퀴즈',
])

# --- 탭 ①: 탐구 질문 ---
with tab1:
  st.header('탐구 질문 및 가설')
  st.markdown("""
    * **탐구 질문:** 신경세포에서 활동 전위는 어떤 메커니즘으로 발생하며, 이온의 이동과 막전위는 어떻게 변화하는가?
    * **가설 설정:** 
        1. 자극이 주어지면 나트륨($Na^+$) 통로가 열려 세포 밖의 나트륨 이온이 안으로 유입되며 탈분극(막전위 상승)이 일어날 것이다.
        2. 이어서 칼륨($K^+$) 통로가 열려 세포 안의 칼륨 이온이 밖으로 유출되며 재분극(막전위 하강)이 일어날 것이다.
    """)

# --- 탭 ②: 시뮬레이션 ---
with tab2:
  st.header('이온 투과 및 활동 전위 시뮬레이션')
  st.write(
      '아래 시뮬레이션 화면에서 재생 버튼 등을 활용해 이온의 이동과 막전위 그래프의 변화를 관찰하세요.'
  )
  show_vpython(VPYTHON_CODE, height=900)

# --- 탭 ③: 원리 ---
with tab3:
  st.header('핵심 과학 원리')
  st.markdown(
      '신경세포의 흥분 전파 과정에서 일어나는 막전위 변화 수식과 원리입니다.'
  )

  st.subheader('1. 휴지 전위 (Resting Potential)')
  st.markdown(
      '세포막을 경계로 이온의 농도 차이가 존재할 때, 안정 상태의 막전위는 다음과 같이 표현됩니다.'
  )
  st.latex(r'V_{m} \approx -70\text{ mV}')

  st.subheader('2. 탈분극 (Depolarization)')
  st.markdown(
      '나트륨 이온 통로가 열리며 $Na^+$ 이온이 세포 내로 급격히 유입되어 전위가 상승합니다.'
  )
  st.latex(r'Na^{+} \text{ influx} \implies V_{m} \text{ increases up to } +30\text{ mV}')

  st.subheader('3. 재분극 (Repolarization)')
  st.markdown(
      '칼륨 이온 통로가 열리며 $K^+$ 이온이 세포 외로 유출되어 전위가 하강합니다.'
  )
  st.latex(r'K^{+} \text{ efflux} \implies V_{m} \text{ decreases / hyperpolarizes}')

# --- 탭 ④: 결과 분석 ---
with tab4:
  st.header('실험 및 측정값 결과 분석')
  st.markdown('시뮬레이션 구동 시 측정된 시간에 따른 대표적인 막전위 변화 데이터입니다.')

  # 측정값 데이터프레임 구성
  data = {
      '시간 (ms)': [0.0, 1.5, 2.5, 4.0, 5.0],
      '막전위 (mV)': [-70.0, +30.0, -85.0, -72.0, -70.0],
      '단계 상태': [
          '휴지기',
          '탈분극 피크',
          '재분극/과분극',
          '회복기',
          '휴지기 복귀',
      ],
  }
  df_results = pd.DataFrame(data)

  st.dataframe(df_results, use_container_width=True)

  st.markdown('---')
  st.subheader('시간에 따른 막전위 변화 추세')

  # 시각화용 데이터로 선 그래프 제공
  chart_data = pd.DataFrame(
      {
          '막전위 (mV)': [
              -70,
              -50,
              0,
              30,
              0,
              -50,
              -85,
              -75,
              -70,
          ]
      },
      index=[
          '0.0ms',
          '0.8ms',
          '1.2ms',
          '1.5ms',
          '2.0ms',
          '2.3ms',
          '2.5ms',
          '3.5ms',
          '5.0ms',
      ],
  )
  st.line_chart(chart_data)

# --- 탭 ⑤: 결론과 한계 ---
with tab5:
  st.header('탐구 결론 및 한계점')
  st.markdown("""
    ### 📌 결론
    * 신경세포의 활동 전위는 나트륨 이온과 칼륨 이온의 순차적인 통로 개폐에 따른 확산 및 농도 변화로 설명될 수 있습니다.
    * 탈분극 시기에는 $Na^+$ 이온의 안쪽 유입이 주도하며, 재분극 시기에는 $K^+$ 이온의 바깥쪽 유출이 막전위를 원래 상태로 되돌립니다.

    ### ⚠️ 한계점
    * 실제 신경세포의 복잡한 전압 개폐성 이온 채널의 확률적 개폐 거동을 완벽하게 재현하기에는 모델이 단순화되어 있습니다.
    * 세포막 전압-시간 관계가 수학적 수식과 근사된 랜덤 워크 모델 기반이므로 실제 생체 전기 생리학적 수치와 미세한 오차가 존재할 수 있습니다.
    """)

# --- 탭 ⑥: 퀴즈 ---
with tab6:
  st.header('발표 확인 퀴즈')
  st.markdown('오늘 발표 내용과 관련된 간단한 퀴즈를 풀어보세요!')

  answer = st.radio(
      'Q. 신경세포에서 활동 전위가 발생할 때, 탈분극(Depolarization) 단계에서 주로 세포 안으로 유입되는 이온은 무엇인가요?',
      (
          '1. 칼륨 이온 (K+)',
          '2. 나트륨 이온 (Na+)',
          '3. 염화물 이온 (Cl-)',
          '4. 칼슘 이온 (Ca2+)',
      ),
      index=0,
  )

  if st.button('정답 확인'):
    if answer.startswith('2'):
      st.success('정답입니다! 탈분극 시에는 나트륨 이온(Na+)이 세포 안으로 유입됩니다.')
    else:
      st.error(
          '오답입니다. 다시 생각해 보세요! (정답: 2. 나트륨 이온 (Na+))'
      )
