import csv
import os
import time
import timeit

import pandas as pd

from tqdm import tqdm
import metrics
import run_configs
import search_engine_best

first = True


def generate_var_options(var_options):
    output = [{}]
    for k in var_options.keys():
        new_output = []
        for out in output:
            for v in var_options[k]:
                new_o = out.copy()
                new_o[k] = v
                new_output.append(new_o)
        output = new_output
    return output


def save_to_csv(row):
    global first
    csv_file = open('outputs.csv', 'w' if first else 'a', newline='')
    fieldnames = row.keys()
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if first:
        writer.writeheader()
        first = False
    writer.writerow(row)
    csv_file.close()


def test(engine, options):
    queries = pd.read_csv(os.path.join('data', 'queries_train.tsv'), sep='\t')
    bench_lbls = pd.read_csv(os.path.join('data', 'benchmark_lbls_train.csv'),
                             dtype={'query': int, 'tweet': str, 'y_true': int})
    q2n_relevant = bench_lbls.groupby('query')['y_true'].sum().to_dict()
    queries_results = []
    q_times = []
    for i, row in queries.iterrows():
        q_id = row['query_id']
        q_keywords = row['keywords']
        start_time = time.time()
        q_n_res, q_res = engine.search(q_keywords, options['methods'])
        end_time = time.time()
        q_time = end_time - start_time
        q_times.append(q_time)
        queries_results.extend([(q_id, str(doc_id)) for doc_id in q_res])
        if q_time > 10:
            print(f'Query time exceeded: {options}')
    queries_results = pd.DataFrame(queries_results, columns=['query', 'tweet'])
    q_results_labeled = pd.merge(queries_results, bench_lbls, on=['query', 'tweet'], how='inner',
                                 suffixes=('_result', '_bench'))
    options['max_q_time'] = max(q_times)
    options['avg_q_time'] = sum(q_times) / len(q_times)
    options['MAP'] = metrics.map(q_results_labeled)
    options['precision'] = metrics.precision(q_results_labeled)
    options['precision@5'] = metrics.precision(q_results_labeled.groupby('query').head(5))
    options['precision@10'] = metrics.precision(q_results_labeled.groupby('query').head(10))
    options['precision@50'] = metrics.precision(q_results_labeled.groupby('query').head(50))
    options['recall'] = metrics.recall(q_results_labeled, q2n_relevant)
    save_to_csv(options)


if __name__ == '__main__':
    bench_data_path = r'data\benchmark_data_train.snappy.parquet'
    methods_opt = [{}, {1}, {2}, {3}, {1, 2}, {1, 3}, {2, 3}, {1, 2, 3}]
    v_options = {
        'stemming': [True, False],
        'ext_url': [True, False],
        'emoji': [True, False],
        'quotes': [True, False],
        'entity': [True, False],
        'less_more': [True, False],
        'hashtag': [True, False],
        'url': [True, False],
        'tag': [True, False],
        'capitals': [True, False],
        'cos_sym': [True, False],
        'min_length': [i for i in range(1, 5)],
        'min_relevant': [i for i in range(1, 5)],
        'the_count': [i for i in range(1, 10)],
        'wordnet_count': [i for i in range(1, 10)],
        'min_occurrence': [i for i in range(1, 5)],
        'ext_val': [i / 10 for i in range(1, 10)]
    }
    """
     min_length=3, min_relevant=1, the_count=5, wordnet_count=5, min_occurrence=2, ext_val=0.5
    """
    var_options_list = generate_var_options(v_options)
    print('a')
    progressbar = tqdm(total=len(var_options_list))
    for opt in var_options_list:
        config = run_configs.ConfigClass(**opt)
        opt_engine = search_engine_best.SearchEngine(config)
        opt['build_idx_time'] = timeit.timeit(
            "opt_engine.build_index_from_parquet(bench_data_path)",
            globals=globals(), number=1
        )
        if opt['build_idx_time'] > 60:
            print(f'Build time exceeded: {opt}')
        for methods_list in methods_opt:
            o = opt.copy()
            o['methods'] = methods_list
            test(opt_engine, o)
            progressbar.update(1 / len(methods_opt))
