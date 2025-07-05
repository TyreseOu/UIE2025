from data_prepare import get_sorted_file_list

if __name__ == '__main__':
    sorted_list = get_sorted_file_list(base_dir='/data/clz/unziped_files')
    print(sorted_list)
