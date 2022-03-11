from functools import partial as partfunc
from itertools import chain
from math import inf
from pathlib import Path
from pprint import pprint
from re import search as re_search, split as re_split
from sys import exit
from time import perf_counter
from typing import Dict, Union, Tuple, List, Optional


class NoResultError(ValueError):
    """Signalizes that no result could be calculated.
    If the program cannot continue without the function's output, raise this."""


class ATG:

    def __init__(self, paths_file: str, nodes_file: str = None, costs_file: str = None):
        self.DEFAULT_DAGMN_VERSION = 2
        self.paths: Tuple[Tuple[int, ...], ...] = self.get_paths(paths_file)
        if nodes_file is None:
            self.nodes: Dict[int, str] = self.get_nodes_from_paths(self.paths)
        else:
            self.nodes: Dict[int, str] = self.get_nodes(nodes_file)
        if costs_file is not None:
            self.costs: Optional[Dict[int, int]] = dict(
                zip(self.nodes.keys(), self.get_paths(costs_file, single_column=True)))
        else:
            self.costs: Optional[Dict[int, int]] = None

    @staticmethod
    def get_paths(filename: str, single_column: bool = False) -> Tuple[Union[Tuple[int, ...], int], ...]:
        output: List[Union[Tuple[int, ...], int], ...] = []
        with open(filename, encoding='cp852') as file:
            i = 0
            for line in file:
                i += 1
                # noinspection RegExpSingleCharAlternation
                split_line = re_split("\t| |\n", line)
                line_list = []
                for part in split_line:
                    if part != '':
                        line_list.append(int(re_search("([-+]?[0-9]*\.?[0-9]+)", part).group(1)))
                if single_column:
                    output.append(line_list[0])
                else:
                    output.append(tuple(line_list))
        if single_column:
            return tuple(output)
        return tuple(sorted(output))

    @staticmethod
    def get_nodes(filename: str) -> Dict[int, str]:
        output = {}
        with open(filename, encoding='cp852') as file:
            for line in file:
                output[int(line[:5])] = line[5:-1]
        return output

    @staticmethod
    def get_nodes_from_paths(paths: tuple) -> Dict[int, str]:
        nodes = {}
        for path in paths:
            if path[0] not in nodes.keys():
                nodes[path[0]] = str(path[0])
            if path[1] not in nodes.keys():
                nodes[path[1]] = str(path[1])
        return {k: v for k, v in sorted(nodes.items(), key=lambda item: item[0])}

    def predecessors_to_output(self, input_: dict, source: int, dest: int = None):
        output: Dict[int, Dict[str, Union[int, List[int]]]] = {}
        for node in self.nodes.keys():
            if input_[node]["t"] == inf or input_[node]["t"] == -inf:
                continue
            if dest is not None and node != dest:
                continue
            if node not in output.keys():
                output[node] = {"cost": input_[node]["t"], "node_path": []}
            pred = node
            output[node]["node_path"].append(pred)
            while pred != source:
                pred = input_[pred]["x"]
                output[node]["node_path"].append(pred)
            output[node]["node_path"].reverse()
            if dest is not None:
                return output
        return output

    def basic_shortest_path(self, source: int):
        i: dict = self.nodes.copy()
        for key in i:
            i[key] = {"t": inf, "x": -1}
            if key == source:
                i[key]["t"] = 0
        cont = False
        while True:
            for path in self.paths:
                if i[path[1]]["t"] > i[path[0]]["t"] + path[2]:
                    i[path[1]]["t"] = i[path[0]]["t"] + path[2]
                    i[path[1]]["x"] = path[0]
                    cont = True
                    break
            if not cont:
                break
            cont = False
        return self.predecessors_to_output(i, source)

    def find_negative_cycle(self) -> Tuple[bool, list]:
        i: dict = self.nodes.copy()
        p = list(self.paths)
        test_node = 1
        while test_node in i.keys():
            test_node += 1
        i[test_node] = ""
        source = test_node
        for node in i.keys():
            if (test_node, node, 0) not in p:
                p.append((test_node, node, 0))
        for key in i:
            i[key] = {"t": inf, "x": -1}
            if key == source:
                i[key]["t"] = 0
        cont = False
        while True:
            for path in p:
                if i[path[1]]["t"] > i[path[0]]["t"] + path[2]:
                    i[path[1]]["t"] = i[path[0]]["t"] + path[2]
                    i[path[1]]["x"] = path[0]
                    x = i[path[1]]["x"]
                    x_to_check = x
                    possible_cycle = [x]
                    while x != source:
                        x = i[x]["x"]
                        possible_cycle.append(x)
                        if x == x_to_check:
                            possible_cycle.reverse()
                            return True, possible_cycle
                    cont = True
                    break
            if not cont:
                break
            cont = False
        return False, []

    def label_set(self, source: int, dest: int = None, track: bool = False):
        cycles = 0
        i: dict = self.nodes.copy()
        for key in i:
            i[key] = {"t": inf, "x": -1}
            if key == source:
                i[key]["t"] = 0
        e = [source]
        while True:
            r = -1
            m = inf
            for item in e:
                if i[item]["t"] <= m:
                    m = i[item]["t"]
                    r = item
            e.remove(r)
            if r == dest:
                break
            for path in self.paths:
                if path[0] != r:
                    continue
                if i[path[1]]["t"] > i[r]["t"] + path[2]:
                    i[path[1]]["t"] = i[r]["t"] + path[2]
                    i[path[1]]["x"] = r
                    e.append(path[1])
            cycles += 1
            if track and cycles % 100 == 0:
                print(cycles, len(e))
            if not e:
                break
        return self.predecessors_to_output(i, source, dest)

    def kruskal(self) -> Tuple[int, list]:
        paths: List[tuple] = sorted(list(self.paths), key=lambda tup: tup[2])
        nodes: dict = self.nodes.copy()
        skeleton = []
        for i in nodes.keys():
            nodes[i] = {"k": i}
        while True:
            r = paths.pop(0)
            if nodes[r[0]]["k"] != nodes[r[1]]["k"]:
                skeleton.append(r)
                r0k = nodes[r[0]]["k"]
                r1k = nodes[r[1]]["k"]
                for i in nodes.keys():
                    if nodes[i]["k"] == r1k:
                        nodes[i]["k"] = r0k
            if len(skeleton) == len(nodes.keys()) - 1 or len(paths) == 0:
                break
        cost = 0
        for item in skeleton:
            cost += item[2]
        return cost, skeleton

    def dag_ordering(self, version: int = None) -> tuple:
        if version is None:
            version = self.DEFAULT_DAGMN_VERSION
        if version not in (1, 2):
            raise ValueError("Nesprávna verzia zoradenia - musí byť 1 alebo 2.")

        nodes: Dict = self.nodes.copy()
        for node in nodes:
            nodes[node] = {"d": 0, "w": []}
        for path in self.paths:
            nodes[path[1]]["d"] += 1
            nodes[path[0]]["w"].append(path)
        p = []

        if version == 1:
            while len(nodes) != 0:
                ok = False
                for node in nodes:
                    if nodes[node]["d"] == 0:
                        for path in nodes[node]["w"]:
                            nodes[path[1]]["d"] -= 1
                        p.append(node)
                        nodes.pop(node)
                        ok = True
                        break
                if not ok:
                    raise NoResultError("Žiadne monotónne zoradenie nebolo nájdené.")
            return tuple(p)

        elif version == 2:
            for node in nodes:
                if nodes[node]["d"] == 0:
                    p.append(node)
            i = 0
            while True:
                vi = p[i]
                for path in nodes[vi]["w"]:
                    w = path[1]
                    if w == vi:
                        continue
                    nodes[w]["d"] -= 1
                    if nodes[w]["d"] == 0:
                        p.append(w)
                if len(p) >= len(nodes.keys()):
                    break
                else:
                    i += 1
                    if i > len(p):
                        raise NoResultError("Žiadne monotónne zoradenie nebolo nájdené.")
            return tuple(p)

    def dag_extreme_path(self, source, dest=None, inner_ordering: int = None, outer_ordering: tuple = None,
                         shortest=True):
        if outer_ordering is not None:
            p = outer_ordering
        else:
            p = self.dag_ordering(inner_ordering)
        i: int = p.index(source)
        nodes: Dict[int, Union[str, dict]] = self.nodes.copy()
        if shortest:
            sinf = inf
        else:
            sinf = -inf

        for node in nodes:
            if node == source:
                nodes[node] = {"t": 0, "x": 0, "w": []}
            else:
                nodes[node] = {"t": sinf, "x": 0, "w": []}
        for path in self.paths:
            nodes[path[0]]["w"].append(path)

        while True:
            for w in nodes[p[i]]["w"]:
                if w[0] == w[1]:
                    continue
                if (shortest and nodes[w[1]]["t"] > nodes[p[i]]["t"] + w[2]) or (
                        not shortest and nodes[w[1]]["t"] < nodes[p[i]]["t"] + w[2]):
                    nodes[w[1]]["t"] = nodes[p[i]]["t"] + w[2]
                    nodes[w[1]]["x"] = p[i]
            i += 1
            if i == len(p):
                break

        return self.predecessors_to_output(nodes, source, dest)

    def dag_cpm(self, inner_ordering: int = None, outer_ordering: tuple = None):
        if self.costs is None:
            raise NoResultError("Súbor s dĺžkami činností nebol načítaný.")
        nodes: dict = self.nodes.copy()
        paths = [[i, o] for i, o, *rest in self.paths]
        zero_l = [0]

        start_mutator = {node: [node] for node in nodes}
        end_mutator = {node: [node] for node in nodes}

        npaths = []
        for path in paths:
            npaths.append([end_mutator[path[0]], start_mutator[path[1]], zero_l])

        for node in nodes:
            nodes[node] = [True, True]
        for path in paths:
            nodes[path[0]][0] = False
            nodes[path[1]][1] = False
        starts = []
        ends = []
        for node in nodes:
            if nodes[node][1]:
                starts.append(start_mutator[node])
            if nodes[node][0]:
                ends.append(end_mutator[node])

        new_nodes = {1: "z", 2: "k"}
        n = 3
        extra_paths = []
        for node in self.nodes:
            new_nodes[n] = str(node) + 'a'
            start_mutator[node][0] = n
            n += 1
            new_nodes[n] = str(node) + 'b'
            end_mutator[node][0] = n
            extra_paths.append((n - 1, n, self.costs[node]))
            n += 1

        eap = extra_paths.append
        for node in starts:
            eap((1, node[0], 0))
        for node in ends:
            eap((node[0], 2, 0))

        new_paths = tuple(sorted([tuple(chain.from_iterable(path)) for path in npaths] + extra_paths))
        old_nodes = self.nodes
        old_paths = self.paths
        self.nodes = new_nodes
        self.paths = new_paths

        if outer_ordering is not None:
            mono = outer_ordering
        else:
            mono = self.dag_ordering(inner_ordering)

        t = self.dag_extreme_path(1, 2, outer_ordering=mono, shortest=False)
        t = t[2]['cost']
        critical_nodes: List[int] = []
        output = {"project_duration": t, "critical_nodes": critical_nodes, "cpm": {node: {} for node in old_nodes}}
        zk_set = {"z", "k"}

        for node in new_nodes:
            if new_nodes[node] in ("z", "k"):
                continue
            old_node = int(new_nodes[node][:-1])
            p: int = self.costs[old_node]
            output["cpm"][old_node]["p"] = p
            if new_nodes[node][-1:] == "a":
                z: int = self.dag_extreme_path(1, node, outer_ordering=mono, shortest=False)[node]['cost']
                output["cpm"][old_node]["z"] = z
            else:
                k: int = t - self.dag_extreme_path(node, 2, outer_ordering=mono, shortest=False)[2]['cost']
                output["cpm"][old_node]["k"] = k
            if zk_set.issubset(output["cpm"][old_node]):
                r: int = output["cpm"][old_node]["k"] - output["cpm"][old_node]["z"] - output["cpm"][old_node]["p"]
                output["cpm"][old_node]["r"] = r
                if r == 0:
                    critical_nodes.append(old_node)

        self.nodes = old_nodes
        self.paths = old_paths

        return output


def atg_test() -> str:
    atg = ATG("data/pr1.hrn", "data/pr1.uzl")
    atg_zcd = ATG("data/CYKL_maxi.hrn")
    atg_kru = ATG("data/pr3.hrn")
    atg_dag = ATG("data/acdigraf.hrn")
    atg_cpm = ATG("data/CPM_mini.hrn", costs_file="data/CPM_mini.tim")

    atg_input = {
        "Základný algoritmus": partfunc(atg.basic_shortest_path, 1),
        "Label Set": partfunc(atg.label_set, 1),
        "Label Set u - v": partfunc(atg.label_set, 1, 56),
        "Záporný cyklus": partfunc(atg_zcd.find_negative_cycle),
        "Kruskalov algoritmus II": partfunc(atg_kru.kruskal),
        "Monotónne uspor. v DAG 1": partfunc(atg_dag.dag_ordering, 1),
        "Monotónne uspor. v DAG 2": partfunc(atg_dag.dag_ordering, 2),
        "cesta v DAG cez mon. usp.": partfunc(atg_dag.dag_extreme_path, 1, shortest=True),
        "cesta v DAG cez Label Set": partfunc(atg_dag.label_set, 1),
        "CPM metóda": partfunc(atg_cpm.dag_cpm)
    }

    print_width = len(max(atg_input.keys(), key=len)) + 2
    output = []
    for text in atg_input:
        t0 = perf_counter()
        res = atg_input[text]()
        td = perf_counter() - t0
        output.append(
            (text + ":").rjust(print_width - 1).ljust(print_width) + " | " + f'{td:.6f}' + "s | " + str(res)[:100] +
            ["..." if len(str(res)) > 100 else ""][0])
    return "\n".join(output)


def atg_long_test():
    long_test = ATG("data/SlovRep.hrn")
    yield "Súbor načítaný, spúšťam algoritmus..."
    tx = perf_counter()
    long_test_result = long_test.label_set(1, track=True)
    ty = perf_counter()
    yield str(ty - tx)
    yield long_test_result


def atg_cli():
    def number_prompt(format_string, question_list):
        out = []
        for i, item in enumerate(question_list):
            out.append(format_string.format(i + 1, item))
        out = "\n".join(out)
        print(out)
        try:
            _inp = int(input("input: ")) - 1
        except ValueError:
            _inp = -1
        while _inp not in range(len(question_list)):
            print("Nesprávny vstup.")
            print(out)
            try:
                _inp = int(input("input: ")) - 1
            except ValueError:
                _inp = -1
        print()
        return _inp

    def get_valid_paths():
        def get_valid_file():
            file_path = Path(input("Zadajte cestu: "))
            print()
            try:
                path_valid = file_path.is_file()
            except OSError:
                path_valid = False
            while not path_valid:
                print("Nesprávna cesta. Skúsiť znova?")
                _input = number_prompt(" [{}] {}", ["áno", "nie"])
                if _input == 0:
                    file_path = Path(input("Zadajte cestu: "))
                    print()
                    try:
                        path_valid = file_path.is_file()
                    except OSError:
                        path_valid = False
                else:
                    break
            if not path_valid:
                return None
            else:
                return file_path

        path_to_paths = get_valid_file()
        if path_to_paths is None:
            return None
        print("Vybrať súbor pre časy elementárnych operácii v metóde CPM?")
        _inp = number_prompt(" [{}] {}", ["áno", "nie"])
        if _inp == 1:
            return path_to_paths
        path_to_costs = get_valid_file()
        if path_to_costs is None:
            print("Pokračovať len so súborom ciest?")
            _inp = number_prompt(" [{}] {}", ["áno", "nie"])
            if _inp == 0:
                return path_to_paths
            else:
                return None
        else:
            return path_to_paths, path_to_costs

    def get_int(prompt):
        try:
            _inp = int(input(prompt))
        except ValueError:
            _inp = None
        while _inp is None:
            print("Nezadali ste číslo v správnom formáte.")
            try:
                _inp = int(input(prompt))
            except ValueError:
                _inp = None
        return _inp

    def pick_algorithm():
        if atg is None:
            print("CHYBA: Nie je vybratý súbor.")
            return
        print("Vyberte algoritmus na otestovanie:")
        _inp = number_prompt(" [{}] pre {}", ["Základný algoritmus",
                                              "Label Set",
                                              "Label Set u - v",
                                              "Algoritmus na hľadanie záporného cyklu",
                                              "Kruskalov algoritmus II",
                                              "Algoritmus na monotónne usporiadanie digrafu I.",
                                              "Algoritmus na monotónne usporiadanie digrafu II.",
                                              "Algoritmus pre cestu v DAG cez monotónne usporiadanie",
                                              "Algoritmus pre cestu v DAG cez Label Set",
                                              "CPM metóda"])
        beginning = 0
        ending = 0
        short_or_long = True
        if _inp in (0, 1, 2, 7, 8):
            beginning = get_int("Zadajte začiatočný bod algoritmu: ")
            while beginning not in atg.nodes.keys():
                print("Zadaný začiatočný bod neexistuje.")
                beginning = get_int("Zadajte začiatočný bod algoritmu: ")
        if _inp == 2:
            ending = get_int("Zadajte konečný bod algoritmu: ")
            while ending not in atg.nodes.keys():
                print("Zadaný konečný bod neexistuje.")
                ending = get_int("Zadajte konečný bod algoritmu: ")
        if _inp == 7:
            print("Najkratšiu či najdlhšiu cestu?")
            short_or_long = not bool(number_prompt(" {}: {}", ["najkratšiu", "najdlhšiu"]))

        func = (partfunc(atg.basic_shortest_path, beginning),
                partfunc(atg.label_set, beginning),
                partfunc(atg.label_set, beginning, ending),
                partfunc(atg.find_negative_cycle),
                partfunc(atg.kruskal),
                partfunc(atg.dag_ordering, 1),
                partfunc(atg.dag_ordering, 2),
                partfunc(atg.dag_extreme_path, beginning, shortest=short_or_long),
                partfunc(atg.label_set, beginning),
                partfunc(atg.dag_cpm))[_inp]
        print("Spúšťam...")
        tb = perf_counter()
        output = func()
        ta = perf_counter()
        print("Hotovo, t={}, zobraziť výstup?".format(ta - tb))
        _inp = number_prompt(" [{}] {}", ["áno, celý", "iba prvých 150 znakov", "zapísať do súboru output.txt", "nie"])
        if _inp == 0:
            pprint(output, sort_dicts=False, compact=True)
        elif _inp == 1:
            print(str(output)[:150])
        elif _inp == 2:
            with open("output.txt", "w+t") as output_file:
                print("Začínam zápis...")
                output_file.write(str(output))
                print("Hotovo - výstup zapísaný do output.txt")

    print("ATG úloha - Daniel Valent 5ZY012")
    while True:
        atg = None
        print("\nStlačte:")
        inp = number_prompt(" [{}] pre {}", ["rýchly test všetkých algoritmov,", "pomalý test,", "vlastný test,",
                                             "ukončenie programu."])
        if inp == 0:
            print(atg_test())
        elif inp == 1:
            lt = atg_long_test()
            print(next(lt))
            print("Hotovo, čas: " + next(lt))
            print("Zapisujem výsledok do súboru longtest.txt...")
            with open("longtest.txt", "w+t") as long_test_file:
                pprint(next(lt), stream=long_test_file, width=140, compact=True, sort_dicts=False)
            print("Hotovo.")
        elif inp == 2:
            print("Stlačte:")
            inp = number_prompt(" [{}] ak chcete {}",
                                ["vybrať súbor zo zoznamu,", "vybrať súbor podľa cesty,", "íst späť."])
            if inp == 0:
                print("Vyberte súbor:")
                inp = number_prompt(" [{}]: súbor {}",
                                    ["pr1.hrn", "pr3.hrn", "AcDigr.hrn", "acdigraf.hrn", "CPM_mini.hrn + .tim"])
                if inp == 0:
                    atg = ATG("data/pr1.hrn")
                elif inp == 1:
                    atg = ATG("data/pr3.hrn")
                elif inp == 2:
                    atg = ATG("data/AcDigr.hrn")
                elif inp == 3:
                    atg = ATG("data/acdigraf.hrn")
                elif inp == 4:
                    atg = ATG("data/CPM_mini.hrn", costs_file="data/CPM_mini.tim")
                pick_algorithm()
            elif inp == 1:
                file_paths = get_valid_paths()
                if file_paths is None:
                    continue
                elif isinstance(file_paths, Path):
                    atg = ATG(str(file_paths))
                else:
                    atg = ATG(str(file_paths[0]), costs_file=str(file_paths[1]))
                pick_algorithm()
        elif inp == 3:
            exit(0)


if __name__ == '__main__':
    # noinspection PyBroadException
    while True:
        try:
            atg_cli()
        except KeyboardInterrupt:
            input("Program prerušený; stlačte enter pre zatvorenie okna.")
            exit()
        except NoResultError as err:
            print("CHYBA: výsledok neexistuje - " + str(err))
        except Exception as err:
            print("\n\n [CHYBA]")
            print(repr(err))
            input("\nProgram prerušený; stlačte enter pre zatvorenie okna.\n")
            exit(1)
