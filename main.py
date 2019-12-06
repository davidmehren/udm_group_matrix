import re
from collections import defaultdict
import matplotlib.pyplot as plt

users = defaultdict(lambda: [])
groups = set()
matrix = []


def read_dump():
    with open("userdump.txt", "r") as file:
        current_user = ""
        for line in file:
            if line == "":
                continue
            if line.startswith("DN"):
                current_user = re.findall(r"uid=(.*?),", line)[0]
                # print(current_user)
            if current_user.startswith("dns-") or current_user.startswith("ucs-") or current_user.startswith("join-"):
                continue
            if line.startswith("  groups"):
                group = re.findall(r"cn=(.*?),", line)[0]
                # print("  ", group)
                groups.add(group)
                users[current_user].append(group)


def generate_line(user, u_index):
    user_line = user
    matrix.append([])
    for g_index, group in enumerate(groups):
        matrix[u_index].append([])
        if group in users[user]:
            user_line = user_line + ", X"
            matrix[u_index][g_index] = 1
        else:
            user_line = user_line + ","
            matrix[u_index][g_index] = 0
    return user_line


def generate_header():
    header = ","
    for group in groups:
        header = header + group + ","
    return header


if __name__ == '__main__':
    read_dump()
    user_names = sorted(users.keys(), reverse=True)
    groups = sorted(groups)
    print(generate_header())
    for u_index, user in enumerate(user_names):
        print(generate_line(user, u_index))
    plt.pcolor(matrix, edgecolors='k', cmap="Greys", vmin=0, vmax=1)
    x_locations = [x + 0.5 for x in range(len(matrix[0]))]
    y_locations = [x + 0.5 for x in range(len(matrix))]
    plt.xticks(x_locations, list(groups), rotation=45, fontsize=4, ha="right")
    plt.yticks(y_locations, user_names, fontsize=4)
    plt.tight_layout()
    plt.savefig("matrix.png", dpi=300)
