import search_engine_best

if __name__ == '__main__':
   # search_engine_best.main()
    path = r'C:\Users\roik2\PycharmProjects\data\benchmark_data_train.snappy.parquet'

    search_engine_best.SearchEngine.build_index_from_parquet(path)
