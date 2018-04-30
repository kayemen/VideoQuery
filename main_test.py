import config as cfg
from tqdm import tqdm_gui, tqdm
import time
print(cfg.BASE_DIR)
# print(cfg.TEST_SETTING)
# print(cfg.OVERRIDE_SETTING)

for i in tqdm(range(3000), ascii=True):
    # pass
    time.sleep(0.001)
    # print(i)
