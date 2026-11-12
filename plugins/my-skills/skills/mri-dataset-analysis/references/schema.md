# 标准格式 v1.3

本文件为规范；原始参考文件仅用于理解既有格式：
- `/mnt/hdd_data2/Files/Open_source_datasets/Abdomen/atlas_dataset_T1/ori/meta_data/atlas_dataset_T1_meta.json`
- `/mnt/hdd_data2/Files/Open_source_datasets/metadata_template.md`
参考不存在也可依本文件执行，不猜测其内容。

顶层为 `{"LabelDefinitions": 标签定义对象, 影像键: 字段对象, ...}`，无 Records 包装。`LabelDefinitions` 固定序列化在最前，仅出现一次，不属于影像记录，不计入影像数。影像键用相对源根目录的路径；转换数据相对 NIfTI 输出目录。混合根目录用 `root_alias/relative/path`，在 Markdown 的“方法与溯源”部分 保存别名映射。一个实际影像文件一条，掩膜不计影像，配对的 DICOM 与 NIfTI 不重复纳入。

## 数据集级标签定义

`LabelDefinitions` 包含 `Classification` 和 `Segmentation`，字段名、类别名称及解释均用英文。每类包含：

- `Status`：`Available`、`NotAvailable`、`NotApplicable` 或 `Unknown`，分别表示有明确编码、未提供、不适用、尚无法确定。
- `Labels`：编码字符串 → 英文含义的对象。分类采用发布者的原始编码，不自行编号；分割采用实际交付 NIfTI 的整数体素值，包括有定义的背景值。没有可靠编码时为空对象。
- `Description`：英文简述标签任务及编码依据或缺失原因；文献链接和详细溯源放 Markdown。
- `Scope`（可选）：英文说明适用队列、序列或标签文件范围，避免误解为每个影像都有标签。

同类任务存在不兼容的多套编码时，不合并成一个含义冲突的映射：将该类对象改为 `{"Schemes": {"<EnglishSchemeName>": {Status, Labels, Description, Scope}, ...}}`，各方案必须有明确 `Scope`。`Classification` 和 `Segmentation` 均支持这种形式。不要把病例健康描述、影像对比类型、性别字段或数据划分自动当作分类任务标签。数据集级 `Available` 不表示每幅影像都有该任务，须在 `Scope` 说明部分覆盖范围，并按实际标签匹配填写逐影像 `TaskType`。仅有器官分割标签时，分割为 `Available`、未提供的分类为 `NotAvailable`，不能据此推断疾病标签。

示例仅展示独立标签定义，不代表所有数据集都有相同任务或编码：

```json
{
  "LabelDefinitions": {
    "Classification": {
      "Status": "NotAvailable",
      "Labels": {},
      "Description": "No subject-level classification labels are provided."
    },
    "Segmentation": {
      "Status": "Available",
      "Labels": {
        "0": "Background",
        "1": "Liver"
      },
      "Description": "Voxel values in the delivered segmentation files.",
      "Scope": "Training segmentation files only."
    }
  }
}
```

实际交付须在 `LabelDefinitions` 后附逐影像记录，每条仍仅使用下述基础字段及适用的 DWI 扩展。检查实际标签值均有定义；未观察到但发布者明确定义的类别可保留。v1.3 新增此顶层对象；校验器默认仍可读取旧格式，新的交付用 `--require-label-definitions` 强制检查，不自动改写历史文件。

## 20 个基础字段

| 字段 | 类型及约定 |
| --- | --- |
| Age | 非负有限数值，岁；缺失 `"NaN"`。DICOM AS 保留原单位，换算方法写 Markdown 的“方法与溯源”部分 |
| Sex | M/F/Unknown；不猜测 CSV 编码 |
| Region | abdomen/brain/knee 等统一英文名；未知 Unknown |
| ImageContrast | T1/T2/FLAIR/DWI 等；未知 Unknown |
| AcquisitionType | 2D/3D/Unknown |
| AcquisitionPlane | Axial/Sagittal/Coronal/Oblique/Unknown |
| PulseSequence | 可靠序列名称或 Unknown |
| SequenceFamily | GRE/SE/TSE/EPI 等或 Unknown |
| MatrixSize | 正整数列表，保留完整存储维度；不可读取时不伪造，报告失败 |
| VoxelSpacing_mm | 三个正有限数，空间单位 mm；缺失分量为 `"NaN"` |
| SliceThickness_mm | 正数或 `"NaN"` |
| Manufacturer | 统一厂家名称或 Unknown |
| ManufacturersModelName | 扫描仪型号字符串，保留可靠来源中的具体型号；缺失 Unknown |
| FieldStrength_T | 正数或 `"NaN"` |
| TR_ms-TE_ms-TI_ms-FA_degree | 四项列表，依次 TR/TE/TI/FA，数值或逐项 `"NaN"` |
| ContrastPhase | Arterial/PortalVenous/Delayed/PreContrast/NoContrast/Unknown 等有依据的名称 |
| FatSuppression | None/FatSat/SPAIR/STIR/Dixon 等或 Unknown；None 表示确认无脂抑 |
| HealthStatus | Healthy/Diseased/Unknown |
| Disease | 名称列表；确认健康 []；未知 ["Unknown"] |
| TaskType | 该影像实际具有对应标签的任务列表，例如 ["Segmentation"]；没有对应标签时 [] |

数值缺失是字符串 `"NaN"`，不是非标准 JSON 浮点 NaN；分类缺失 Unknown。不要写 null。不要把 unknown/no/none 混用。数值单位：mm、ms、T、度；保留可靠精度。JSON 对象顺序不是语义要求，生成时按上述顺序便于阅读。

矩阵/间距从输出文件读取，不用论文模型输入尺寸。NIfTI z 间距不是采集层厚；存储 affine 平面不是已证实的采集平面；目录 3D 不等于 3D 采集；第四维间距不能自动当 TR。序列内部变化的采集参数不能以首值或均值填成统一值，基础字段缺失，在 Markdown 的“方法与溯源”部分汇总变化范围和受影响影像数，不展开逐帧明细。标准记录中不添加来源或临床分级字段。

## TR/TE/TI/FA 组合参数的缺失与覆盖率

`TR_ms-TE_ms-TI_ms-FA_degree` 始终保存四项列表，顺序固定为 TR、TE、TI、FA。已有数值逐项保留，只有对应参数缺失的位置写字符串 `"NaN"`；即使四项全缺失，也保留 `["NaN", "NaN", "NaN", "NaN"]`，不把整个字段改成单个 `"NaN"`。

Markdown 分开统计以下口径，分母均为本次纳入的影像数：

- **字段有信息/覆盖率**：至少一项有有效数值即计入；只有四项全缺失才计为整组缺失。不能使用 `all(...)` 的四项齐全判定代替这一口径。
- **单项有效/缺失**：分别列出 TR、TE、TI、FA 的有效数、缺失数及覆盖率。
- 如另外报告**四项齐全率**，明确使用这一名称；部分参数缺失不等于整组缺失。

例如 `[4000, 120, "NaN", 90]` 表示 TR、TE、FA 有值，只有 TI 缺失：整组计为“有信息”，TI 计为缺失，不计入“四项齐全”。缺失 TI 不补成 0；已有且符合参数语义的 0 也不能因真假值判断被误计为缺失。这一整组覆盖口径仅适用于该组合参数，不替代空间信息或 DWI 梯度的完整性校验。

## 扫描设备信息

逐影像填写 `Manufacturer`、`ManufacturersModelName`、`FieldStrength_T`，型号不与厂商或场强拼成一个字段。DICOM `ManufacturerModelName` (0008,1090) 映射到标准字段 `ManufacturersModelName`；sidecar 优先读取 `ManufacturersModelName`，兼容 `ManufacturerModelName`。厂商取 DICOM/sidecar `Manufacturer` (0008,0070)，场强取 `MagneticFieldStrength` (0018,0087)，单位 T。表格中的明确型号列（如 `Mfg Model`）按可靠影像/检查 ID 匹配，不将序列名称、线圈名称、站点名称或设备序列号当型号。

只清理型号首尾空白；合并型号别名须有依据，并在 Markdown 说明映射、保留原值来源。DICOM、sidecar 或表格值冲突且无法判断时填 `Unknown`，报告冲突数量与代表性记录。文献列出多种设备或“主要使用某型号”不能代填逐例；明确适用于全部纳入影像或可可靠匹配队列/站点/检查的型号才可补充，注明文献来源和适用范围。仅有 NIfTI 几何信息时不能推断型号。

报告厂商×型号×场强组合的影像数及可确定的患者数，患者跨设备时可出现在多个组合中，注明计数口径；单独报告三个设备字段的有效/缺失数。v1.2 新增必需的 `ManufacturersModelName`，旧 v1.1 结果需补采型号（确认无可靠来源时填 `Unknown`）后再按新规范校验，不自动改写历史结果。

字段对应参考：[DICOM General Equipment](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.5.html)、[BIDS MRI hardware information](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetic-resonance-imaging-data.html#hardware-information)。

## DWI 的 6 个扩展字段

所有 `ImageContrast="DWI"` 记录额外包含以下字段，普通影像只用基础字段。ADC 等定量图在范围筛选阶段排除，不生成标准记录。

| 字段 | 约定 |
| --- | --- |
| BValues_s_per_mm2 | 按输出体积顺序排列的非负有限数列表；未知分量或整体 `"NaN"` |
| BVectors | 同顺序 N×3 数组；未知分量或整体 `"NaN"` |
| BVectorCoordinateSystem | 确认符合 FSL 约定才填 FSL，否则 Unknown |
| BValFile | 相对对应影像根目录的路径；不存在 Unknown |
| BVecFile | 相对对应影像根目录的路径；不存在 Unknown |
| DiffusionImageType | Directional/Trace/Unknown |

JSON BVectors 为 N×3，FSL bvec 文件为 3×N，bval 一行 N 值。bval/bvec 与输出体积对应，不独立排序、不用唯一 b 值替代完整数组。普通 3D N=1，普通 4D N=第四维；更高维需显式映射和另外验证。

保留转换器给出的输出梯度，不直接用 DICOM 患者坐标向量当 FSL bvec。影像轴置换/翻转/旋转必须用可靠工具同步处理梯度。确认 b=0 可以用零向量；缺失方向不能补零。Trace/方向平均 DWI 常无有效单方向，此时 BVectors 为 "NaN"，Markdown 的“方法与溯源”部分 标为不适用而非提取失败。不得从名称猜测 b 值。

核对数组与梯度文件一致、数量与体积匹配、数值有限、b 值非负、非零方向范数；异常记录，不自动归一化。源信息和缺失/不适用/提取失败原因写 Markdown 的“方法与溯源”部分。报告 b 值频数、b0 定义、方向完整性；b-shell 分组说明容差，原始 bval 不改精度。

## JSON 排版

所有数组整体单行显示，包括 MatrixSize、VoxelSpacing_mm、组合参数、Disease、TaskType、BValues_s_per_mm2 以及完整 BVectors 嵌套数组；不截断长数组。字典逐字段换行、缩进 2 空格。只调整空白，不改变字段、顺序、数值、类型或单位。示例：

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "MAGNETOM Skyra",
  "FieldStrength_T": 3,
  "MatrixSize": [256, 256, 80],
  "TR_ms-TE_ms-TI_ms-FA_degree": [4000, 120, "NaN", 90],
  "BVectors": [[0, 0, 0], [1, 0, 0]]
}
```

使用技能的 `scripts/format_json.py`；交付前重新解析核对内容一致。该示例仅说明排版，并非完整记录。
