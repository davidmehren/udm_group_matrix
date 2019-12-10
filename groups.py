#!/bin/env python3
import re
from typing import List
import numpy as np
import matplotlib.pyplot as plt

filtered_users = ["join-backup", "join-slave", "ucs-sso"]


class LDAPUser:
    name: str

    def __init__(self, name):
        self.name = name

    def __eq__(self, o: 'LDAPUser') -> bool:
        return self.name == o.name

    def __hash__(self) -> int:
        return self.name.__hash__()


class LDAPGroupList:
    content: List['LDAPGroup']

    def __init__(self):
        self.content = []

    def add(self, group):
        self.content.append(group)

    def get_by_name(self, name):
        for _group in self.content:
            if _group.name == name:
                return _group
        return None

    def get_max_users(self):
        _max = 0
        for group in self.content:
            _max = max(len(group.members), _max)
        return _max

    def get_user_list(self):
        user_list = set()
        for group in self.content:
            user_list.update(group.members)
        return list(user_list)

    def tidy(self):
        new_content = []
        for group in self.content:
            if group.samba_rid < 1000:
                continue
            if len(group.members) > 0:
                new_content.append(group)
        self.content = new_content


class LDAPGroup:
    name: str
    samba_rid: int
    subgroups: List[str]
    members: List[LDAPUser]

    def __str__(self) -> str:
        _repr = f"{self.name}\n  Mitglieder:\n"
        for member in self.members:
            _repr = _repr + f"    {member.name}\n"
        _repr = _repr + "  Untergruppen:\n"
        for _group in self.subgroups:
            _repr = _repr + f"    {_group}\n"
        return _repr

    def __init__(self, name: str):
        self.name = name.lower()
        self.subgroups = []
        self.members = []

    def add_subgroup(self, group: str):
        self.subgroups.append(group.lower())

    def parse_subgroups(self, global_groups: LDAPGroupList):
        for group_name in self.subgroups:
            ldap_group = global_groups.get_by_name(group_name)
            if ldap_group is None:
                print(f"can't find group '{group_name}'")
            else:
                for member in ldap_group.members:
                    if member not in self.members:
                        self.members.append(member)

    def add_member(self, member):
        if member.name not in filtered_users:
            self.members.append(member)


def read_groupdump():
    _group_list = LDAPGroupList()
    with open("groupdump.txt", "r") as file:
        current_group = None
        for line in file:
            if line == "\n":
                continue
            if line.startswith("DN"):
                current_group = LDAPGroup(re.findall(r"cn=(.*?),", line)[0])
                _group_list.add(current_group)
                # print(current_user)
            if current_group.name.startswith("dns-") or current_group.name.startswith(
                    "ucs-") or current_group.name.startswith("join-"):
                continue
            if line.startswith("  users"):
                user = LDAPUser(re.findall(r"uid=(.*?),", line)[0])
                # print("  ", group)
                current_group.add_member(user)
            if line.startswith("  nestedGroup"):
                subgroup = re.findall(r"cn=(.*?),", line)[0]
                # print("  ", group)
                current_group.add_subgroup(subgroup)
            if line.startswith("  sambaRID:"):
                rid = re.findall(r"([0-9]{1,4})", line)[0]
                current_group.samba_rid = int(rid)
    return _group_list


def paint_matrix(groups: LDAPGroupList):
    user_list = groups.get_user_list()
    x_count = len(groups.content)
    y_count = len(user_list)
    matrix = np.zeros((x_count, y_count))

    for g_index, group in enumerate(groups.content):
        for user in group.members:
            matrix[g_index][user_list.index(user)] = 1
    plt.pcolor(matrix.T, edgecolors='k', cmap="Greys", vmin=0, vmax=1)
    x_locations = [x + 0.5 for x in range(x_count)]
    y_locations = [x + 0.5 for x in range(y_count)]
    plt.xticks(x_locations, [group.name for group in groups.content], rotation=45, fontsize=4, ha="right")
    plt.yticks(y_locations, [user.name for user in user_list], fontsize=4)
    plt.tight_layout()
    plt.savefig("groups.png", dpi=300)


if __name__ == '__main__':
    groups = read_groupdump()
    for group in groups.content:
        group.parse_subgroups(groups)
    groups.tidy()
    paint_matrix(groups)
