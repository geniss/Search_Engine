import run_configs
import search_engine_best

if __name__ == '__main__':
    engine = search_engine_best.SearchEngine(run_configs.ConfigClass())
    path = r'data\benchmark_data_train.snappy.parquet'
    engine.build_index_from_parquet(path)
    print(engine.search('Herd immunity has been reached'))
