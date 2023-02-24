# Preprocessing MR data

## INPUT

### Folder structure (raw)
```bash
└── PROJECT_NAME
    ├── PID_1
    │   ├── flair
    │   │   ├── IM-0305-0001.dcm
    │   │   ├── IM-0305-0002.dcm
    │   │   └── IM-0305-0003.dcm
    │   ├── t1_km
    │   │   ├── IM-0309-0001.dcm
    │   │   ├── IM-0309-0002.dcm
    │   │   └── IM-0309-0003.dcm
    │   ├── t1_native
    │   │   ├── IM-0307-0001.dcm
    │   │   ├── IM-0307-0002.dcm
    │   │   └── IM-0307-0003.dcm
    │   └── t2
    │       ├── IM-0308-0001.dcm
    │       ├── IM-0308-0002.dcm
    │       └── IM-0308-0003.dcm
    └── PID_2
        ├── flair
        ├── t1_km
        ├── t1_native
        └── t2
```

define in main.py script\
`settings.init(run_from='btupc09', project_name='CETEG_PROGNOSE'`\
`number_of_processes = 8`\

## OUTPUT

### Folder structure (processed)

```bash
PROJECT_NAME/
├── 003
│   └── 20111207
│       ├── 003_0000.nii.gz
│       ├── 003_0000_std.nii.gz
│       ├── 003_0001.nii.gz
│       ├── 003_0001_std.nii.gz
│       ├── 003_0002.nii.gz
│       ├── 003_0002_std.nii.gz
│       ├── 003_0003.nii.gz
│       ├── 003_0003_std.nii.gz
│       ├── 003_brain_segmentation.nii.gz
│       └── 003_mr_segmentation.nii.gz
└── 005
    └── 20120320

```


| Sequence | File |
| ------ | ------ |
| T1_native | PID_0000.nii.gz  |
| T1_KM | PID_0001.nii.gz |
| T2 | PID_0002.nii.gz |
| FLAIR | PID_0003.nii.gz |



- brain_segmentation: HD-BET mask (0: background, 1: brain)
- mr_segmentation; HD-GLIO mask (0: background, 1: t2/flair abnormalities 2: t1-km signal)
