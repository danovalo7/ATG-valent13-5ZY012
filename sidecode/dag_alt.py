
# Kód, ktorý už nieje potrebný / je určený na testovanie / je napísaný bez úplného pochopenia zadania.
# Všetok plne funguje, preto nebol vymazaný; ale nieje časťou úlohy, preto je v osobitnom súbore.
# Je v docstringu preto, aby IDE neukazovalo chyby.

"""
    @staticmethod
    def output_to_nodes(output: dict, target: int) -> List[int]:
        # takes output of algorithm, returns only the nodes travelled in a list; for csp, therefore obsolete.
        if target not in output.keys():
            return []
        # nodes = [output[target]["path"][0][0]]
        nodes = []
        for item in output[target]["path"]:
            nodes.append(item[0])  # item[1]
        return nodes

    def custom_shortest_path(self, source: int) -> dict:
        def csp(path_to_follow, current_paths, current_cost, travelled_nodes):
            current_node = path_to_follow[1]
            if current_node in travelled_nodes:
                return
            travelled_nodes.append(current_node)
            current_paths.append(path_to_follow)
            current_cost += path_to_follow[2]
            if current_node in output.keys():
                if output[current_node]["cost"] > current_cost:
                    output[current_node]["cost"] = current_cost
                    output[current_node]["path"] = current_paths[:]
                else:
                    return
            else:
                output[current_node] = {"cost": current_cost, "path": current_paths[:]}
            for path_from_here in [filtered_path for filtered_path in self.paths if filtered_path[0] == current_node]:
                csp(path_from_here, current_paths[:], current_cost, travelled_nodes[:])

        if source not in self.nodes.keys():
            return {}
        output = {"source": source, source: {"cost": 0, "path": [(source, source, 0)]}}
        for starting_path in [starting_path for starting_path in self.paths if starting_path[0] == source]:
            # should really be 'for starting_path in self.paths if starting_path[0] == source:'
            # but it doesnt work that way for some reason;
            # see https://stackoverflow.com/questions/6981717#comment40282643_6981771
            csp(starting_path, [], 0, [source])

        return output

    def dag_earliest_start(self, inner_ordering: int = None, outer_ordering: tuple = None) -> Dict[
        str, Union[int, Dict[int, int]]]:
        if outer_ordering is not None:
            mono = outer_ordering
        else:
            mono = self.dag_ordering(inner_ordering)
        nodes: Dict[int, Union[dict, str]] = self.nodes.copy()
        for i, node in enumerate(nodes):
            nodes[node] = {'z': 0, 'x': 0, 'p': self.costs[node], 'w': []}
        nodes: Dict[int, Dict[str, Union[int, list]]]
        for path in self.paths:
            nodes[path[0]]['w'].append(path)
        for r in mono:
            for path_out in nodes[r]['w']:
                if r == path_out[1]:
                    continue
                w = path_out[1]
                if nodes[w]['z'] < nodes[r]['z'] + nodes[r]['p']:
                    nodes[w]['z'] = nodes[r]['z'] + nodes[r]['p']
                    nodes[w]['x'] = r
        output: Dict[str, Union[int, Dict[int, int]]] = {
            'project_duration': max([nodes[i]['z'] + nodes[i]['p'] for i in nodes.keys() if len(nodes[i]['w']) == 0]),
            'earliest_starts': {}}
        for node in nodes:
            output['earliest_starts'][node] = nodes[node]['z']
        return output


    def dag_latest_finish(self, duration: int, inner_ordering: int = None, outer_ordering: tuple = None) -> Dict[
        str, Union[int, Dict[int, int]]]:
        if outer_ordering is not None:
            mono = outer_ordering
        else:
            mono = self.dag_ordering(inner_ordering)
        nodes: Dict[int, Union[str, dict]] = self.nodes.copy()
        for i, node in enumerate(nodes):
            nodes[node] = {'k': duration, 'y': 0, 'p': self.costs[node], 'w': []}
        nodes: Dict[int, Dict[str, Union[int, list]]]
        for path in self.paths:
            nodes[path[0]]['w'].append(path)
        for r in mono:
            for path_out in nodes[r]['w']:
                if r == path_out[1]:
                    continue
                w = path_out[1]
                if nodes[r]['k'] > nodes[w]['k'] - nodes[w]['p']:
                    nodes[r]['k'] = nodes[w]['k'] - nodes[w]['p']
                    nodes[r]['y'] = w
        output: Dict[str, Union[int, Dict[int, int]]] = {
            'project_duration': duration,
            'latest_finishes': {}}
        for node in nodes:
            output['latest_finishes'][node] = nodes[node]['k']
        return output


    def dag_critical(self, inner_ordering: int = None, outer_ordering: tuple = None, earliest_starts: dict = None,
                     latest_finishes: dict = None):
        if earliest_starts is None or latest_finishes is None:
            if outer_ordering is not None:
                mono = outer_ordering
            else:
                mono = self.dag_ordering(inner_ordering)
            if earliest_starts is None:
                earliest_starts = self.dag_earliest_start(outer_ordering=mono)
            if latest_finishes is None:
                latest_finishes = self.dag_latest_finish(earliest_starts["project_duration"], outer_ordering=mono)
        critical_nodes = []
        output: Dict[str, Union[int, Dict[int, Dict[str, int]]]] = {
            "project_duration": earliest_starts["project_duration"], "critical_nodes": critical_nodes, "cpm": {}}
        nodes = tuple(self.nodes.keys())
        for node in nodes:
            p = self.costs[node]
            z = earliest_starts["earliest_starts"][node]
            k = latest_finishes["latest_finishes"][node]
            r = k - z - p
            output["cpm"][node] = {"p": p, "z": k, "k": z, "r": r}
            if r == 0:
                critical_nodes.append(node)


def atg_label_set_vs_monot():
    atg_dag = ATG("data/acdigraf.hrn")

    print(" - Usporiadanie")
    t0 = perf_counter()
    m1 = atg_dag.dag_ordering(1)
    td = perf_counter() - t0
    print("MONOTv1: " + f'{td:.6f}' + "s")
    t0 = perf_counter()
    m2 = atg_dag.dag_ordering(2)
    td = perf_counter() - t0
    print("MONOTv2: " + f'{td:.6f}' + "s")

    print("\n - Cesta")
    avg = 0
    for i in range(1, 6):
        t0 = perf_counter()
        res = atg_dag.dag_extreme_path(i, shortest=True, outer_ordering=m1)
        td = perf_counter() - t0
        print(str(i) + " MONOTv1: " + f'{td:.6f}' + "s")
        avg += td
    avg /= 5
    print("Average: " + f'{avg:.6f}', end="\n\n")

    avg = 0
    for i in range(1, 6):
        t0 = perf_counter()
        res = atg_dag.dag_extreme_path(i, shortest=True, outer_ordering=m2)
        td = perf_counter() - t0
        print(str(i) + " MONOTv2: " + f'{td:.6f}' + "s")
        avg += td
    avg /= 5
    print("Average: " + f'{avg:.6f}', end="\n\n")

    avg = 0
    for i in range(1, 6):
        t0 = perf_counter()
        res = atg_dag.label_set(i)
        td = perf_counter() - t0
        print(str(i) + " Label set: " + f'{td:.6f}' + "s")
        avg += td
    avg /= 5
    print("Average: " + f'{avg:.6f}', end="\n\n")"""