import datetime
import pathlib
import time

import numpy as np


def main():
    sample_dir = pathlib.Path(__file__).parent / 'samples'
    sample_dir.mkdir(exist_ok=True)
    t = np.linspace(0., 10., 1024)
    try:
        while True:
            stamp = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
            sample_npy = sample_dir / f'{stamp}.npy'
            with open(sample_npy, 'wb') as npy_file:
                np.save(npy_file, np.sin(t + np.pi * time.time() / 30.))
            time.sleep(0.1)
    except KeyboardInterrupt:
        return 0
    except Exception:
        return 1


if __name__ == '__main__':
    main()
