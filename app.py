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


# 3. Streamlit용 Matplotlib 애니메이션 렌더링 함수
def show_matplotlib_animation():
  num_na = 120
  num_k = 120
  width, height = 12.0, 10.0
  total_frames = 150  # 웹에서 부드럽게 구동되도록 프레임 수 조정

  np.random.seed(42)

  x_na = np.random.uniform(-5.5, 5.5, num_na)
  y_na = np.random.uniform(1.0, 4.5, num_na)
  vx_na = np.random.normal(0, 0.03, num_na)
  vy_na = np.random.normal(0, 0.03, num_na)

  x_k = np.random.uniform(-5.5, 5.5, num_k)
  y_k = np.random.uniform(-4.5, -1.0, num_k)
  vx_k = np.random.normal(0, 0.03, num_k)
  vy_k = np.random.normal(0, 0.03, num_k)

  fig, (ax_sim, ax_graph) = plt.subplots(
      2, 1, figsize=(9, 8), gridspec_kw={'height_ratios': [2, 1]}
  )

  time_steps = np.linspace(0, 15, total_frames)
  membrane_potential = (
      -70
      + 100 * np.exp(-(((time_steps % 5) - 1.5) ** 2) / 0.15)
      - 20 * np.exp(-(((time_steps % 5) - 2.5) ** 2) / 0.3)
  )
  membrane_potential[
      (time_steps % 5 > 2.0) & (time_steps % 5 < 3.5)
  ] -= 10

  ax_sim.set_xlim(-width / 2, width / 2)
  ax_sim.set_ylim(-height / 2, height / 2)
  ax_sim.set_aspect('equal')
  ax_sim.set_title(
      'Neuron Action Potential Simulation', fontsize=12, fontweight='bold'
  )
  ax_sim.set_ylabel('Y Position (nm)')
  ax_sim.axhline(0, color='dimgray', linewidth=6, label='Cell Membrane')

  scat_na = ax_sim.scatter([], [], c='crimson', s=30, edgecolor='k', label='Na+')
  scat_k = ax_sim.scatter(
      [], [], c='dodgerblue', s=30, edgecolor='k', label='K+'
  )
  ax_sim.legend(loc='upper right', fontsize=8)

  ax_graph.set_xlim(0, 15)
  ax_graph.set_ylim(-90, 50)
  ax_graph.set_xlabel('Time (ms)')
  ax_graph.set_ylabel('Membrane Potential (mV)')
  ax_graph.axhline(-70, color='gray', linestyle='--', label='Resting (-70mV)')
  ax_graph.grid(True, linestyle=':', alpha=0.6)

  (line_vm,) = ax_graph.plot(
      [], [], color='purple', linewidth=2, label='Action Potential ($V_m$)'
  )
  (point_vm,) = ax_graph.plot([], [], 'ro', markersize=6)
  phase_text = ax_graph.text(
      0.5,
      30,
      '',
      fontsize=10,
      fontweight='bold',
      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
  )
  ax_graph.legend(loc='lower right', fontsize=8)
  plt.tight_layout()

  # Streamlit st.pyplot과 연동을 위한 컨테이너 생성
  placeholder = st.empty()

  # 애니메이션 대신 Streamlit 루프를 통해 실시간 렌더링 (Streamlit Cloud 최적화)
  import time

  if st.button('시뮬레이션 재생 / 재시작'):
    for frame_idx in range(total_frames):
      t = time_steps[frame_idx]
      cycle_t = t % 5.0

      is_na_open = 1.0 if (1.0 < cycle_t < 2.0) else 0.1
      is_k_open = 1.0 if (2.0 < cycle_t < 3.5) else 0.1

      # Na+ 업데이트
      vx_na += np.random.normal(0, 0.02, num_na)
      vy_na += np.random.normal(0, 0.02, num_na)
      vx_na *= 0.94
      vy_na *= 0.94
      x_na_new = x_na + vx_na
      y_na_new = y_na + vy_na

      crossing_na = y_na * y_na_new < 0
      in_na_pore = (x_na > -3.0) & (x_na < -2.0)
      if 1.0 < cycle_t < 2.0:
        pull_na = in_na_pore & (y_na > 0)
        vy_na[pull_na] = -0.15
      reflect_na = crossing_na & (~in_na_pore | (is_na_open < 0.5))
      vy_na[reflect_na] = -vy_na[reflect_na]
      y_na_new[reflect_na] = y_na[reflect_na] + vy_na[reflect_na]

      # K+ 업데이트
      vx_k += np.random.normal(0, 0.02, num_k)
      vy_k += np.random.normal(0, 0.02, num_k)
      vx_k *= 0.94
      vy_k *= 0.94
      x_k_new = x_k + vx_k
      y_k_new = y_k + vy_k

      crossing_k = y_k * y_k_new < 0
      in_k_pore = (x_k > 2.0) & (x_k < 3.0)
      if 2.0 < cycle_t < 3.5:
        push_k = in_k_pore & (y_k < 0)
        vy_k[push_k] = 0.15
      reflect_k = crossing_k & (~in_k_pore | (is_k_open < 0.5))
      vy_k[reflect_k] = -vy_k[reflect_k]
      y_k_new[reflect_k] = y_k[reflect_k] + vy_k[reflect_k]

      # 펌프
      pump_na = (np.abs(x_na) < 0.6) & (y_na < 0)
      y_na_new[pump_na] += 0.08
      pump_k = (np.abs(x_k) < 0.6) & (y_k > 0)
      y_k_new[pump_k] -= 0.08

      x_na[:], y_na[:] = (
          np.clip(x_na_new, -5.8, 5.8),
          np.clip(y_na_new, -4.8, 4.8),
      )
      x_k[:], y_k[:] = np.clip(x_k_new, -5.8, 5.8), np.clip(
          y_k_new, -4.8, 4.8
      )

      scat_na.set_offsets(np.c_[x_na, y_na])
      scat_k.set_offsets(np.c_[x_k, y_k])

      line_vm.set_data(time_steps[:frame_idx], membrane_potential[:frame_idx])
      point_vm.set_data([t], [membrane_potential[frame_idx]])

      if cycle_t <= 1.0:
        phase_text.set_text('Phase: Resting State (-70 mV)')
      elif 1.0 < cycle_t <= 2.0:
        phase_text.set_text('Phase: Depolarization (Na+ Influx)')
      elif 2.0 < cycle_t <= 3.5:
        phase_text.set_text('Phase: Repolarization (K+ Efflux)')
      else:
        phase_text.set_text('Phase: Hyperpolarization & Recovery')

      placeholder.pyplot(fig)
      time.sleep(0.03)
  else:
    placeholder.pyplot(fig)


# 4. 메인 타이틀
st.title('⚡ 신경세포에서의 활동 전위 발생 탐구')
st.markdown('지중호 학생의 생명과학 탐구 발표 웹앱입니다.')

# 5. 6개 탭 구성
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
      '아래의 **[시뮬레이션 재생 / 재시작]** 버튼을 누르면 이온의 이동과 막전위'
      ' 그래프가 실시간으로 구동됩니다.'
  )
  show_matplotlib_animation()

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
