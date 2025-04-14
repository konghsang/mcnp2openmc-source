import re


def read_data_file(filename):
    data = {}
    current_key = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()

            # 修改正则表达式以允许字母+数字的组合（如SI2）
            if len(parts) >= 2 and len(parts[1]) == 1 and re.match(r"^[A-Za-z][A-Za-z0-9]*$", parts[0]):
                key = parts[0] + parts[1]
                current_key = key
                try:
                    values = list(map(float, parts[2:]))
                    data.setdefault(key, []).extend(values)
                except:
                    current_key = None
            else:
                # 处理数据行
                if current_key is not None:
                    try:
                        values = list(map(float, parts))
                        data[current_key].extend(values)
                    except:
                        pass
    return data
# 使用示例
data = read_data_file("mcnp_sdef.txt")
list = data.get("DS3Q", [])
# 筛选出奇数索引位置的元素
new_list_odd = list[::2]

# 筛选出偶数索引位置的元素，转换为整数并按照“SI数P”的规则组成新数组
new_list_even = ["SP" + str(int(num)) + "D" for num in list[1::2]]

a=data.get(new_list_even[1], [])
print(a)
