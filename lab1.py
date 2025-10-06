# ortools_mcf_batch.py
import argparse
import os
import re
from typing import Dict, Tuple, List, Optional
import pandas as pd
import numpy as np
from ortools.linear_solver import pywraplp


def _read_instance(offices_csv: str, reqs_csv: str, distance_csv: str,
                   cost_column: str = "price") -> Tuple[List[int],
                                                        List[Tuple[int,int,float]],
                                                        List[Tuple[int,int]],
                                                        Dict[Tuple[int,int], float]]:
    """Читает один сценарий и готовит множества/параметры модели."""
    offices = pd.read_csv(offices_csv)
    reqs = pd.read_csv(reqs_csv)
    dist = pd.read_csv(distance_csv)

    nodes = sorted(offices['office_id'].astype(int).unique().tolist())

    # ориентированные рёбра без самопетель
    if 'src' not in dist.columns or 'dst' not in dist.columns:
        raise ValueError(f"Файл {distance_csv} должен содержать колонки 'src' и 'dst'")
    if cost_column not in dist.columns:
        raise ValueError(f"В файле {distance_csv} нет колонки стоимости '{cost_column}'")

    edges_df = dist[dist['src'] != dist['dst']].copy()
    edges_df = edges_df[['src', 'dst', cost_column]].rename(
        columns={'src': 'u', 'dst': 'v', cost_column: 'cost'}
    )
    edges_df['u'] = edges_df['u'].astype(int)
    edges_df['v'] = edges_df['v'].astype(int)
    edges: List[Tuple[int, int]] = list(map(tuple, edges_df[['u', 'v']].to_records(index=False)))
    cost = {(u, v): float(c) for u, v, c in edges_df[['u', 'v', 'cost']].itertuples(index=False, name=None)}

    # товары (коммодити)
    need_cols = {'src_office_id', 'dst_office_id', 'volume'}
    if not need_cols.issubset(set(reqs.columns)):
        raise ValueError(f"Файл {reqs_csv} должен содержать колонки {need_cols}")
    commodities: List[Tuple[int, int, float]] = []
    for _, r in reqs.iterrows():
        s = int(r['src_office_id']); t = int(r['dst_office_id']); d = float(r['volume'])
        if d > 0:
            commodities.append((s, t, d))

    return nodes, commodities, edges, cost


def solve_mcf_ortools(offices_csv: str,
                      reqs_csv: str,
                      distance_csv: str,
                      vehicle_capacity: float = 100.0,
                      time_limit_sec: int = 0,
                      cost_column: str = "price"):
    nodes, commodities, edges, cost = _read_instance(offices_csv, reqs_csv, distance_csv, cost_column)
    K = len(commodities)
    V = len(nodes)
    node_set = set(nodes)

    outgoing = {v: [] for v in nodes}
    incoming = {v: [] for v in nodes}
    for (u, v) in edges:
        outgoing[u].append((u, v))
        incoming[v].append((u, v))

    solver = pywraplp.Solver.CreateSolver('CBC')
    if solver is None:
        raise RuntimeError("OR-Tools CBC solver недоступен. Установите ortools.")
    if time_limit_sec and time_limit_sec > 0:
        solver.SetTimeLimit(time_limit_sec * 1000)

    # Переменные
    y = {e: solver.IntVar(0.0, solver.infinity(), f"y_{e[0]}_{e[1]}") for e in edges}
    x = {(k, u, v): solver.NumVar(0.0, solver.infinity(), f"x_{k}_{u}_{v}")
         for k, _ in enumerate(commodities) for (u, v) in edges}

    # Цель
    obj = solver.Objective()
    for (u, v) in edges:
        obj.SetCoefficient(y[(u, v)], cost[(u, v)])
    obj.SetMinimization()

    # Балансы
    for k, (s, t, d) in enumerate(commodities):
        if s not in node_set or t not in node_set:
            raise ValueError(f"Коммодити {k} содержит неизвестный узел: ({s}->{t})")
        for v in nodes:
            out_expr = solver.Sum([x[(k, a, b)] for (a, b) in outgoing.get(v, [])])
            in_expr  = solver.Sum([x[(k, a, b)] for (a, b) in incoming.get(v, [])])
            rhs = d if v == s else (-d if v == t else 0.0)
            solver.Add(out_expr - in_expr == rhs)

    # Связь поток–ТС: sum_k x_{k,uv} ≤ C * y_{uv}
    for (u, v) in edges:
        flow_uv = solver.Sum([x[(k, u, v)] for k in range(K)])
        solver.Add(flow_uv <= vehicle_capacity * y[(u, v)])

    status = solver.Solve()
    status_map = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE (time/limits)",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }
    status_str = status_map.get(status, f"UNKNOWN({status})")
    obj_val = obj.Value() if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE) else float('nan')

    # Результаты
    import pandas as pd
    y_rows = []
    for (u, v) in edges:
        val = y[(u, v)].solution_value()
        if val > 1e-7:
            vehicles = int(round(val))
            y_rows.append({"u": u, "v": v, "vehicles": vehicles,
                           "cost_per_vehicle": cost[(u, v)],
                           "arc_cost": vehicles * cost[(u, v)]})
    y_df = pd.DataFrame(y_rows).sort_values("arc_cost", ascending=False)

    x_rows = []
    for k, (s, t, d) in enumerate(commodities):
        for (u, v) in edges:
            f = x[(k, u, v)].solution_value()
            if f > 1e-9:
                x_rows.append({"commodity_id": k, "src": s, "dst": t, "demand": d,
                               "u": u, "v": v, "flow": f})
    x_df = pd.DataFrame(x_rows)

    summary_df = pd.DataFrame([{
        "status": status_str,
        "objective_total_cost": obj_val,
        "vehicle_capacity": vehicle_capacity,
        "num_nodes": V,
        "num_edges": len(edges),
        "num_commodities": len(commodities),
        "active_arcs": int((y_df["vehicles"] > 0).sum()) if not y_df.empty else 0,
        "nonzero_flows": len(x_df),
        "wall_time_ms": solver.wall_time(),
        "iterations": solver.iterations(),
        "nodes": solver.nodes()
    }])

    return {"summary": summary_df, "y": y_df, "x": x_df}


# --------- Пакетный режим ---------
def _stem_key(fname: str) -> str:
    """
    Выделяем ключ сценария из имени.
    Примеры соответствий:
      offices.csv / reqs.csv / distance_matrix.csv  -> ключ "default"
      offices_A.csv / reqs_A.csv / distance_matrix_A.csv -> ключ "A"
      offices_01.csv / reqs_01.csv / distance_matrix_01.csv -> ключ "01"
    """
    base = os.path.basename(fname)
    name, _ = os.path.splitext(base)
    # Ищем суффикс после первого символа подчеркивания / дефиса
    m = re.match(r'^(offices|reqs|distance_matrix)[-_]?(.*)$', name)
    if not m:
        return "default"
    suffix = m.group(2)
    return suffix if suffix else "default"


def discover_triplets(input_dir: str) -> List[Tuple[str, str, str, str]]:
    """
    Сканирует папку и формирует наборы (ключ, offices, reqs, dist).
    Требуется, чтобы для каждого ключа были все три файла.
    """
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(".csv")]
    offices_map: Dict[str, str] = {}
    reqs_map: Dict[str, str] = {}
    dist_map: Dict[str, str] = {}

    for f in files:
        base = os.path.basename(f).lower()
        if base.startswith("offices"):
            offices_map[_stem_key(f)] = f
        elif base.startswith("reqs"):
            reqs_map[_stem_key(f)] = f
        elif base.startswith("distance_matrix"):
            dist_map[_stem_key(f)] = f

    keys = sorted(set(offices_map.keys()) | set(reqs_map.keys()) | set(dist_map.keys()))
    triplets: List[Tuple[str, str, str, str]] = []
    for k in keys:
        if k in offices_map and k in reqs_map and k in dist_map:
            triplets.append((k, offices_map[k], reqs_map[k], dist_map[k]))
    return triplets


def run_batch(input_dir: str,
              out_dir: str,
              vehicle_capacity: float,
              time_limit_sec: int,
              cost_column: str):
    os.makedirs(out_dir, exist_ok=True)
    triplets = discover_triplets(input_dir)
    if not triplets:
        raise RuntimeError(
            f"В {input_dir} не найдено ни одной полной тройки файлов "
            f"(offices*.csv, reqs*.csv, distance_matrix*.csv)."
        )

    all_rows = []
    for key, offices_csv, reqs_csv, dist_csv in triplets:
        print(f"\n=== Решаем сценарий: {key} ===")
        out_sub = os.path.join(out_dir, f"scenario_{key}")
        os.makedirs(out_sub, exist_ok=True)
        res = solve_mcf_ortools(offices_csv, reqs_csv, dist_csv,
                                vehicle_capacity=vehicle_capacity,
                                time_limit_sec=time_limit_sec,
                                cost_column=cost_column)
        res["summary"].insert(0, "scenario", key)
        res["summary"].to_csv(os.path.join(out_sub, "solution_summary.csv"), index=False)
        res["y"].to_csv(os.path.join(out_sub, "vehicles_on_arcs.csv"), index=False)
        res["x"].to_csv(os.path.join(out_sub, "flows_by_commodity.csv"), index=False)
        print(res["summary"].to_string(index=False))
        all_rows.append(res["summary"])

    # сводка по всем сценариям
    big = pd.concat(all_rows, ignore_index=True)
    big.to_csv(os.path.join(out_dir, "all_scenarios_summary.csv"), index=False)
    print(f"\nИтоговая сводка по {len(triplets)} сценариям сохранена в {os.path.join(out_dir, 'all_scenarios_summary.csv')}")


def main():
    ap = argparse.ArgumentParser()
    # Режим 1: явная тройка файлов
    ap.add_argument("--offices", help="offices*.csv")
    ap.add_argument("--reqs", help="reqs*.csv")
    ap.add_argument("--dist", help="distance_matrix*.csv")
    # Режим 2: пакетно по папке
    ap.add_argument("--input_dir", help="Папка с множеством CSV (offices*.csv, reqs*.csv, distance_matrix*.csv).")
    # Общие параметры
    ap.add_argument("--vehicle_capacity", type=float, default=100.0)
    ap.add_argument("--time_limit_sec", type=int, default=0)
    ap.add_argument("--out_dir", default="./out")
    ap.add_argument("--cost_column", default="price",
                    help="Имя колонки стоимости в distance_matrix (по умолчанию 'price').")
    args = ap.parse_args()

    # Выбор режима
    if args.offices and args.reqs and args.dist:
        # одиночный сценарий
        os.makedirs(args.out_dir, exist_ok=True)
        res = solve_mcf_ortools(args.offices, args.reqs, args.dist,
                                vehicle_capacity=args.vehicle_capacity,
                                time_limit_sec=args.time_limit_sec,
                                cost_column=args.cost_column)
        res["summary"].to_csv(os.path.join(args.out_dir, "solution_summary.csv"), index=False)
        res["y"].to_csv(os.path.join(args.out_dir, "vehicles_on_arcs.csv"), index=False)
        res["x"].to_csv(os.path.join(args.out_dir, "flows_by_commodity.csv"), index=False)
        print(res["summary"].to_string(index=False))
        print(f"\nSaved to: {os.path.abspath(args.out_dir)}")
    elif args.input_dir:
        run_batch(input_dir=args.input_dir,
                  out_dir=args.out_dir,
                  vehicle_capacity=args.vehicle_capacity,
                  time_limit_sec=args.time_limit_sec,
                  cost_column=args.cost_column)
    else:
        raise SystemExit("Укажите либо тройку файлов (--offices, --reqs, --dist), либо папку (--input_dir).")


if __name__ == "__main__":
    main()
