Отвечаю по вашему конспекту (формулы в $…$ — для KaTeX).

# 1) GNN: основные архитектуры — GCN, GraphSAGE, GAT

## GCN (Graph Convolutional Network)

* **Идея:** спектральная свёртка на графе, реализуемая как нормализованное усреднение соседей с последующим линейным преобразованием и нелинейностью.
* **Обновление слоя:**
  $
  H^{(l+1)}=\sigma!\big(,\hat A, H^{(l)} \Theta^{(l)}\big),
  $
  где $\hat A = \tilde D^{-1/2}\tilde A,\tilde D^{-1/2}$ — нормализованная смежность с петлями, $\tilde A = A + I_N$, $\tilde D_{ii}=\sum_j \tilde A_{ij}$, $\Theta^{(l)}\in\mathbb{R}^{D_l\times D_{l+1}}$, $H^{(0)}=X$.
* **Интуиция:** это **message passing** с корректной нормализацией степеней, чтобы стабилизировать обучение и учитывать разную степень узлов.

## GraphSAGE (Sample and Aggregate)

* **Идея:** обучаемые/настраиваемые аггрегаторы соседей; работает как конструктор «сообщений» от $N(v)$.
* **Шаг 1 — агрегация соседей $v$:**
  $
  m_{N(v)}^{(l)}=\operatorname{AGGREGATE}^{(l)}!\big({h_u^{(l)}:u\in N(v)}\big)
  $
  Примеры:

  * Среднее: $; \displaystyle m_{N(v)}^{(l)}=\frac{1}{|N(v)|}\sum_{u\in N(v)} h_u^{(l)}$
  * Max-pooling: $; \displaystyle m_{N(v)}^{(l)}=\gamma!\big({,\operatorname{MLP}(h_u^{(l)}):u\in N(v)}\big)$, где $\gamma$ — поэлементный максимум.
* **Шаг 2 — объединение с самим узлом:**
  $
  h_v^{(l+1)}=\sigma!\big(\Theta^{(l)}\cdot \operatorname{CONCAT}(h_v^{(l)},, m_{N(v)}^{(l)})\big)
  $
* **Шаг 3 — нормализация (часто):**
  $
  h_v^{(l+1)}\leftarrow \frac{h_v^{(l+1)}}{|h_v^{(l+1)}|_2}
  $

## GAT (Graph Attention Networks)

* **Идея:** взвешивать вклад каждого соседа через механизм внимания, а не одинаково усреднять.
* **Энергия внимания (до softmax):**
  $
  e_{vu}=\operatorname{LeakyReLU}!\big(a^\top[,\Theta h_v^{(l)}\ \Vert\ \Theta h_u^{(l)},]\big),
  $
  где $\Theta\in\mathbb{R}^{D'\times D_l}$, $a\in\mathbb{R}^{2D'}$, $\Vert$ — конкатенация.
* **Нормализация softmax по соседям $u\in N(v)\cup{v}$:**
  $
  \alpha_{vu}=\frac{\exp(e_{vu})}{\sum_{k\in N(v)\cup{v}}\exp(e_{vk})}
  $
* **Агрегация:**
  $
  h_v^{(l+1)}=\sigma!\Big(\sum_{u\in N(v)\cup{v}} \alpha_{vu},\Theta h_u^{(l)}\Big)
  $
* **Многоголовое внимание ($K$ голов):**
  $
  h_v^{(l+1)}=\big\Vert_{k=1}^{K}\ \sigma!\Big(\sum_{u\in N(v)\cup{v}} \alpha_{vu}^{k},\Theta^{k} h_u^{(l)}\Big)
  $

---



