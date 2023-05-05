import sys
import os
from txt2img import TextToImage

src = "money.txt"
dst = "output.txt"


def show_exception_and_pause(exc_type, exc_value, tb):
    import traceback

    traceback.print_exception(exc_type, exc_value, tb)
    input("发生错误...")
    sys.exit(-1)


sys.excepthook = show_exception_and_pause


def init_config(path: str, string: list, break_text: list):
    def preprocess(s):
        r = ""
        f = 0.0
        try:
            f = float(s)
        except:
            r = s
            f = sum(map(lambda v: float(v.strip()), s.split("+")))
        return f, r

    config = []
    comment = []
    with open(path, encoding="utf-8") as file:
        for line in file.readlines():
            if line.startswith("#"):
                comment.append(line.removeprefix("#").strip())
                continue
            c = {}
            first = line.split("#")
            if len(first) > 1:
                c["comment"] = first[1].strip()
            else:
                c["comment"] = ""
            second = first[0].strip().split(maxsplit=2)
            assert len(second) >= 2
            c["name"] = second[0]
            c["weight"] = float(second[1])
            if len(second) >= 3:
                c["money"], c["raw_money"] = preprocess(second[2])
            else:
                c["raw_money"] = ""
                c["money"] = 0
            config.append(c)
    print("comment: ", comment)
    print("config: ", config)
    string.append("配置：\n")

    sum_w = sum(map(lambda i: i["weight"], config))

    def to_string(i):
        c = i["comment"]
        n = i["name"]
        w = i["weight"]
        m = i["money"]
        r = i["raw_money"]
        if len(c) > 0:
            if len(r) > 0:
                return f"    {n}（{w:.1f}/{sum_w:.1f}）：{m} [{r}]    “{c}”\n"
            else:
                return f"    {n}（{w:.1f}/{sum_w:.1f}）：{m}    “{c}”\n"
        else:
            return f"    {n}（{w:.1f}/{sum_w:.1f}）：{m}\n"

    string.extend(map(to_string, config))
    string.append("注释：\n")
    string.extend(map(lambda c: f"    {c}\n", comment))
    string.append("\n")
    return config, comment


def calculate(config, string: list, break_text: list):
    s = sum(map(lambda i: i["money"], config))
    w = sum(map(lambda i: i["weight"], config))
    pw = s / w
    avg = dict(map(lambda i: (i["name"], pw * i["weight"]), config))
    diff = dict(map(lambda i: (i["name"], i["money"] - avg[i["name"]]), config))
    r = {
        "sum": s,
        "weight": w,
        "money_per_weight": pw,
        "average": avg,
        "difference": diff,
    }
    print("result: ", r)
    break_text.append("合计")
    string.append(f"合计：{s:.2f}\n")
    string.append(f"总权重：{w:.1f}\n")
    string.append(f"每权重均值：{pw:.2f}\n")

    def to_string_avg(i):
        n = i[0]
        m = i[1]
        return f"    {n} 负担 {m:.2f}\n"

    string.append("每人负担：\n")
    string.extend(map(to_string_avg, avg.items()))
    string.append("每人离平均值差异：\n")

    def to_string_diff(i):
        n = i[0]
        d = i[1]
        if d <= 0:
            return f"    {n} 需给出 {-d:.2f}\n"
        else:
            return f"    {n} 将接收 {d:.2f}\n"

    string.extend(map(to_string_diff, diff.items()))
    return r


def gen_left_right(result, string: list, break_text: list):
    diff = result["difference"]
    left = dict(filter(lambda i: i[1] < 0, diff.items()))
    right = dict(filter(lambda i: i[1] > 0, diff.items()))
    print("left: ", left)
    print("right: ", right)
    return left, right


def gen_edges(left: dict, right: dict, string: list, break_text: list):
    r = []
    for a in left.keys():
        for b in right.keys():
            if a == b:
                continue
            r.append((a, b))
    print("edges: ", r)
    return r


def find(result, edges: list, string: list, break_text: list):
    MAX = result["sum"]
    diff = result["difference"]
    r = []
    while True:
        m = [MAX, -1]
        for i in range(len(edges)):
            edge = edges[i]
            for j in range(2):
                if abs(diff[edge[j]]) < m[0]:
                    m[0] = abs(diff[edge[j]])
                    m[1] = i
        if m[1] >= 0:
            edge = edges[m[1]]
            r.append([edge, m[0]])
            diff[edge[0]] = diff[edge[0]] + m[0]
            diff[edge[1]] = diff[edge[1]] - m[0]
            for i in range(2):
                if diff[edge[i]] == 0:
                    for j in range(len(edges) - 1, -1, -1):
                        if edges[j][i] == edge[i]:
                            edges.pop(j)
        else:
            break
    print("find: ", r)
    return r


def arrange(results: list, string: list, break_text: list):
    results.sort(key=lambda v: v[0][0])
    new = []
    # [(from, [(to, money)])]
    for r in results:
        if len(new) == 0 or (len(new) > 0 and new[-1][0] != r[0][0]):
            new.append((r[0][0], []))
        new[-1][1].append((r[0][1], r[1]))
    print("arrange: ", new)
    i = 0
    for r in new:
        s = []
        for t in r[1]:
            n = t[0]
            m = t[1]
            s.append(f"给 {n} {m:.2f}")
        string.insert(i, f"{r[0]}：{'， '.join(s)}\n")
        i = i + 1
    break_text.insert(0, "详细过程信息")
    string.insert(i, "\n详细过程信息：\n")
    return new


def generate(result, string: list, break_text: list):
    left, right = gen_left_right(result, string, break_text)
    edges = gen_edges(left, right, string, break_text)
    r = find(result, edges, string, break_text)
    return arrange(r, string, break_text)


def output(string, path, comment, break_text: list):
    with open(path, mode="w", encoding="utf-8") as file:
        file.writelines(string)
    TextToImage(string, break_text, comment[0]).to_image().save("output.jpg")


def main():
    path = src
    if os.path.exists(f"{path}"):
        pass
    elif os.path.exists(f"../{path}"):
        path = f"../{path}"
    string = []
    break_text = []
    config, comment = init_config(path, string, break_text)
    calc = calculate(config, string, break_text)
    _ = generate(calc, string, break_text)
    output(string, dst, comment, break_text)


main()
