from collections import OrderedDict
import tarfile

import pandas as pd

# The RXCUI to ATC mapping was created using RxMix
# (https://mor.nlm.nih.gov/RxMix/):
# - Fuction getClassByRxNormDrugId (relaSource=ATC)
# - Input: batch, all RxNorm RXCUIs ("check all")
RXCUI_ATC_TAR_FILE = '../../data/raw/rxcui_atc_map.tar.gz'
RXCUI_ATC_FILE_NAME = 'rxcui_atc_map.text'
RXCUI_ATC_CSV_OUTPUT = '../../data/intermediate/rxcui_atc_map.csv'

tar = tarfile.open(RXCUI_ATC_TAR_FILE, mode="r:gz")
map_file = tar.extractfile(RXCUI_ATC_FILE_NAME).read()
map_file_lines = map_file.decode(encoding='UTF-8').split('\n')

rxcuids = []
generic_rxcuids = []
atc_classes = []
atc_descs = []

for line in map_file_lines:
    line_parts = line.split('|')
    if len(line_parts) < 10:
        continue
    rxcuids.append(line_parts[3])
    generic_rxcuids.append(line_parts[5])
    atc_classes.append(line_parts[7])
    atc_descs.append(line_parts[9])

map_df = pd.DataFrame.from_dict(OrderedDict({
    'RXCUID': rxcuids,
    'GENERIC_RXCUID': generic_rxcuids,
    'ATC_CLASS': atc_classes,
    'ATC_DESC': atc_descs
}))

map_df.to_csv(RXCUI_ATC_CSV_OUTPUT, index=False)
