# -*- coding: utf-8 -*-
"""
岗位池分析：读取 05_报考信息/职位表/ 下的职位表，按个人条件筛选并汇总。

用法：
    python 99_工具/岗位池分析.py
输出：
    05_报考信息/岗位池_筛选结果.xlsx
    05_报考信息/岗位池_汇总.md
"""
import os
import re
import sys
import glob
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "05_报考信息", "职位表")
OUT_XLSX = os.path.join(ROOT, "05_报考信息", "岗位池_筛选结果.xlsx")
OUT_MD = os.path.join(ROOT, "05_报考信息", "岗位池_汇总.md")

# 可调的条件
KEYWORD_MAJOR = ["计算机类", "数字媒体技术", "不限"]
KEYWORD_DEGREE = ["本科", "本科及以上"]
MAX_PEOPLE = 99          # 招录人数上限（先不限）
REQUIRE_GRASSROOTS = False  # True 只保留要求基层经历的

COL_HINTS = {
    "unit": ["招录机关", "招录单位", "用人单位", "单位名称", "部门"],
    "post": ["职位名称", "岗位名称", "职位"],
    "code": ["职位代码", "岗位代码", "代码"],
    "num": ["招录人数", "招考人数", "人数"],
    "degree": ["学历", "学历要求"],
    "major": ["专业", "专业要求"],
    "grass": ["基层工作经历", "工作经历", "基层经历"],
    "area": ["地区", "工作地点", "所在地", "市（州）", "县（市、区）"],
}


def find_col(df, keys):
    for k in keys:
        for c in df.columns:
            if k in str(c):
                return c
    return None


def load_any(path):
    try:
        sheets = pd.read_excel(path, sheet_name=None, header=None)
    except Exception as e:
        print("  读取失败:", e)
        return None
    for name, raw in sheets.items():
        # 找到表头行：包含“招录”或“职位”的那一行
        header_row = None
        for i in range(min(8, len(raw))):
            row = " ".join(str(x) for x in raw.iloc[i].tolist())
            if ("招录" in row or "职位" in row) and ("学历" in row or "专业" in row):
                header_row = i
                break
        if header_row is None:
            continue
        df = raw.iloc[header_row + 1:].copy()
        df.columns = [str(c).strip() for c in raw.iloc[header_row].tolist()]
        df = df.dropna(how="all")
        if len(df) >= 5:
            print("  使用工作表:", name, "行数", len(df))
            return df
    return None


def main():
    os.makedirs(SRC_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.xlsx")) + glob.glob(os.path.join(SRC_DIR, "*.xls")))
    if not files:
        print("没有找到职位表。请把 .xlsx 放到：", SRC_DIR)
        return
    all_frames = []
    for f in files:
        print("读取:", os.path.basename(f))
        df = load_any(f)
        if df is None:
            continue
        df["来源文件"] = os.path.basename(f)
        all_frames.append(df)
    if not all_frames:
        print("没有可用工作表")
        return
    df = pd.concat(all_frames, ignore_index=True)

    cols = {k: find_col(df, v) for k, v in COL_HINTS.items()}
    print("识别到的列:", {k: v for k, v in cols.items() if v})

    major_col, degree_col = cols["major"], cols["degree"]
    if major_col is None or degree_col is None:
        print("缺少专业或学历列，无法筛选")
        return

    s = df.copy()
    s[major_col] = s[major_col].astype(str)
    s[degree_col] = s[degree_col].astype(str)

    cond_major = s[major_col].apply(lambda x: any(k in x for k in KEYWORD_MAJOR))
    cond_degree = s[degree_col].apply(lambda x: any(k in x for k in KEYWORD_DEGREE))
    s = s[cond_major & cond_degree]

    if REQUIRE_GRASSROOTS and cols["grass"]:
        s = s[s[cols["grass"]].astype(str).str.contains("两年|2年|基层")]

    # 排除乡镇、街道
    unit_col = cols["unit"]
    if unit_col:
        bad = s[unit_col].astype(str).str.contains("乡镇|街道")
        print("  排除乡镇/街道岗位:", int(bad.sum()))
        s = s[~bad]

    if cols["num"]:
        s[cols["num"]] = pd.to_numeric(s[cols["num"]], errors="coerce")
        s = s[(s[cols["num"]] >= 1) & (s[cols["num"]] <= MAX_PEOPLE)]

    keep = [c for c in [cols["code"], cols["unit"], cols["post"], cols["num"],
                        cols["degree"], cols["major"], cols["grass"], cols["area"]] if c]
    s = s[keep].rename(columns={colors: colors for colors in keep})

    s.to_excel(OUT_XLSX, index=False)
    lines = ["# 岗位池汇总", "", "条件：专业含「计算机类/数字媒体技术/不限」，学历含「本科」", ""]
    lines.append("筛选结果：**%d 个职位**" % len(s))
    if cols["num"]:
        lines.append("合计招录：**%s 人**" % int(s[cols["num"]].fillna(0).sum()))
    if cols["area"]:
        lines.append("")
        lines.append("## 地区分布")
        vc = s[cols["area"]].astype(str).value_counts().head(20)
        for k, v in vc.items():
            lines.append("- %s：%d" % (k, v))
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("完成：", OUT_XLSX)
    print("汇总：", OUT_MD)


if __name__ == "__main__":
    main()