from re import sub
from pathlib import Path
from shutil import unpack_archive, ReadError
from hashlib import md5

FOLDERS = {
    "images": ("JPEG", "PNG", "JPG", "SVG"),
    "video": ("AVI", "MP4", "MOV", "MKV"),
    "documents": ("DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"),
    "audio": ("MP3", "OGG", "WAV", "AMR"),
    "archives": ("ZIP", "GZ", "TAR"),
}

CYR = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRN = (
    "a", "b", "v", "g", "d", "e", "e", "zh", "z", "i",
    "j", "k", "l", "m", "n", "o", "p", "r", "s", "t",
    "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "",
    "e", "yu", "ya", "je", "i", "ji", "g",
)
trn_dict = {}
for c, l in zip(CYR, TRN):
    trn_dict[ord(c)] = l
    trn_dict[ord(c.upper())] = l.upper()

# list of archives to unpack
archives = []
# counters
total: dict = {}
counters = [0, 0, 0, 0]


def normalize(string: str) -> str:
    return sub(r"\W", "_", string.translate(trn_dict))


def plural(number: int):
    return number, " was" if number == 1 else "s were"


def calc_hash(file_path: Path) -> str:
    BUF_SIZE = 128 * 1024
    md = md5()
    if file_path.is_file():
        with open(file_path, "rb") as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md.update(data)
    return md.hexdigest()


def get_unique_name(old_file: Path, new_name: str) -> Path:
    new_file = old_file.parent / (new_name + old_file.suffix)
    n = 0
    while new_file.exists():
        n += 1
        file_id = f"_renamed_{n:0>3}_"
        new_file = old_file.parent / (new_name + file_id + old_file.suffix)
    return new_file


def process_file(file_path: Path, target: Path):
    filename = normalize(file_path.stem)
    new_file = target / (filename + file_path.suffix)
    # duplicate name check (extended for archives)
    if (
        new_file.exists()
        or target.stem == "archives"
        and list(target.glob(filename + ".*"))
    ):
        md5_hash = calc_hash(file_path)
        # cycle to find a unique name (keep checking the hash)
        n = 0
        s = filename
        while (
            new_file.exists()
            or target.stem == "archives"
            and (list(target.glob(s + ".*")) or (target / s).exists())
        ):
            if (
                new_file.is_file()
                and new_file.stat().st_size == file_path.stat().st_size
                and calc_hash(new_file) == md5_hash
            ):
                # delete duplicate file (equal hash)
                file_path.unlink()
                counters[1] += 1
                return
            else:
                # filename pattern: "<old filename>_renamed_001_.<ext>"
                n += 1
                s = filename + f"_renamed_{n:0>3}_"
                new_file = target / (s + file_path.suffix)
        # renamed files counter
        counters[0] += 1
    else:
        # moved files counters
        total[target.stem] = total.get(target.stem, 0) + 1
        # check/create sort folder
        if not target.exists():
            target.mkdir()
            print(f"Folder '{target}' has been created.")
        # check if there is a file instead of a folder
        elif target.is_file():
            n = 1
            tmp = target.parent / (target.stem + str(n))
            while tmp.exists():
                n += 1
                tmp = target.parent / (target.stem + str(n))
            target.replace(tmp)
            target.mkdir()
            tmp.replace(target / target.stem)
            print(f"Folder '{target}' has been created.")
            print(f"Warning: the file '{target}' was moved into that folder.")
    # move the file
    file_path.replace(new_file)
    # add to unpack list
    if target.stem == "archives":
        archives.append(new_file)


def process_folder(folder: Path, level: int) -> bool:
    print(folder)
    delete_flag = bool(level)
    for x in folder.iterdir():
        if x.is_dir():
            if level or x.suffix or not x.stem.lower() in FOLDERS:
                delete_flag &= process_folder(x, level + 1)
        else:
            for name, ext in FOLDERS.items():
                if x.suffix[1:].upper() in ext:
                    process_file(x, x.parents[level] / name)
                    break
            else:
                # unlisted extention = do not move the file
                counters[2] += 1
                # mark folder as "not empty"
                delete_flag = False
                # normalize file name
                s = normalize(x.stem)
                if s != x.stem:
                    x.rename(get_unique_name(x, s))
    if delete_flag:
        # delete empty folder
        folder.rmdir()
        counters[3] += 1
    else:
        # normalize folder name
        s = normalize(folder.stem)
        if s != folder.stem:
            folder.rename(get_unique_name(folder, s))
    return delete_flag


def sort_files(folder: Path):
    # check the target folder
    if not folder.exists():
        raise ValueError(f"ERROR: '{folder}' does not exist.")
    if not folder.is_dir():
        raise ValueError(f"ERROR: '{folder}' is a file (not a folder).")
    # main procedure
    print(f"Processing folder '{folder.parent.resolve()}'...")
    process_folder(folder, 0)
    # process archives
    for archive in archives:
        try:
            unpack_archive(archive, folder / "archives" / archive.stem)
        except ReadError:
            print(f'Warning: could not unpack the file "{archive}".')
            archives.remove(archive)
        else:
            archive.unlink()
    # print counters
    b = bool(sum(counters)) or bool(len(archives))
    for f, n in total.items():
        if n and f != "archives":
            b = True
            print('{} file{} moved to the folder "{}".'.format(*plural(n), f))
    if len(archives):
        print("{} archive{} unpacked.".format(*plural(len(archives))))
    if counters[0]:
        print("{} file{} renamed (duplicate name).".format(*plural(counters[0])))
    if counters[1]:
        print("{} duplicate file{} deleted.".format(*plural(counters[1])))
    if counters[3]:
        print("{} empty folder{} deleted.".format(*plural(counters[3])))
    if counters[2]:
        print("{} file{} not moved (check extension).".format(*plural(counters[2])))
    elif not b:
        print("0 files found to process.")
