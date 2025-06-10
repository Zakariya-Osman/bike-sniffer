def clear_temp_files():
    import os
    from pathlib import Path

    temp_folder = Path('data/temp')
    
    if not temp_folder.exists():
        print("Temp folder does not exist.")
        return
    
    for temp_file in temp_folder.glob('*.json'):
        os.remove(temp_file)
        print(f"Deleted {temp_file.name} from temp folder.")
    
    print("All temp files cleared.")

def move_temp_files_to_cache():
    import os
    import shutil
    from pathlib import Path

    temp_folder = Path('data/temp')
    cache_folder = Path('data/cache')

    if not cache_folder.exists():
        cache_folder.mkdir(parents=True)

    for temp_file in temp_folder.glob('*.json'):
        shutil.move(temp_file, cache_folder / temp_file.name)
        print(f"Moved {temp_file.name} to cache.")