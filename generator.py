import io
import os
import subprocess
import click
from datetime import datetime
from pathlib import Path
from cv2 import cv2


gallery_dir = Path("../stahlferro.github.io/src/static/gallery-videos/").resolve()
out_dir = Path("../stahlferro.github.io/src/static/gallery-thumbs/").resolve()
notes_path = out_dir.joinpath("wtg_log.txt")
pngquant_path = Path("bin/pngquant.exe").resolve()

size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def _read_filesize(nbytes: int) -> str:
    i = 0
    while nbytes >= 1024 and i < len(size_suffixes)-1:
        nbytes /= 1024.
        i += 1
    size = str(round(nbytes, 3)).rstrip('0').rstrip('.')
    return f"{size} {size_suffixes[i]}"

def _quantize_png(path: Path, quality: int):
    cmdlist = [str(pngquant_path), f"--quality={quality}", str(path), "--ext=.png", "--force"]
    cmd = ' '.join(cmdlist)
    subprocess.run(cmd, shell=True)
    return

def _generate_thumbnails(quality: int):
    if not Path.exists(gallery_dir):
        raise NotADirectoryError(f"Cannot find directory {gallery_dir}")
    if not Path.exists(out_dir):
        raise NotADirectoryError(f"Cannot find directory {out_dir}")
    
    gallery_collections = [d for d in Path(gallery_dir).glob("*") if Path.is_dir(d)]
    # for gc in gallery_collections:
    #     print(gc)
    total_size = 0
    genlog_descs = []
    for collection_dir in gallery_collections:
        colldir_txt = f"Collection dir\n{collection_dir}"
        print(colldir_txt)
        genlog_descs.append(f"{colldir_txt}\n")
        video_paths = [cd for cd in Path(collection_dir).glob("*")]

        thumbgroup_dir = Path.joinpath(out_dir, collection_dir.stem)
        if not os.path.exists(thumbgroup_dir):
            os.mkdir(thumbgroup_dir)
        savedir_txt = f"Save dir\n{thumbgroup_dir}\n"
        print(savedir_txt)
        genlog_descs.append(f"{savedir_txt}\n")
        for vidpath in video_paths:
            vidfile = vidpath.name
            print(vidfile)
            genlog_descs.append(f"{vidfile}\n")
            # print(f"{Path(*vidpath.parts[-2:])}")
            video = cv2.VideoCapture(str(vidpath))
            retval, frame = video.read()
            fname = f"{vidpath.stem}.png"
            save_path = Path.joinpath(thumbgroup_dir, fname)
            cv2.imwrite(str(save_path), frame)
            
            if quality:
                _quantize_png(save_path, quality)
            im_size = Path(save_path).stat().st_size
            total_size += im_size
            im_size_desc = _read_filesize(im_size)
            final_compressed_desc = f"[{im_size_desc}] {save_path.name}"
            print(final_compressed_desc)
            genlog_descs.append(f"{final_compressed_desc}\n")
            # print(f"\t\t[{im_size_desc}] {Path(*save_path.parts[-2:])}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            video.release()
            cv2.destroyAllWindows()
        print("\n")
        genlog_descs.append("\n\n")
    totalsize_desc = f"Total size   : {_read_filesize(total_size)}\n"
    print(totalsize_desc)
    print("Writing thumbgen.txt...")
    with open(notes_path, "w") as f:
        f.writelines([
            "=================================================\n",
            f"Website Thumbnail Generator v0.0.1 Log\n\n",
            f"Datetime     : {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} UTC\n",
            f"Quality      : {quality}\n",
            f"{totalsize_desc}",
            "=================================================\n\n"
            "==== Generation Log ====\n\n"])
        f.writelines(genlog_descs)
    print("Done writing.")
    print("All processes finished.")


@click.group()
def cli():
    pass

@cli.command()
@click.option("--quality", type=int)
def generate(quality):
    _generate_thumbnails(quality)


if __name__ == "__main__":
    cli()
