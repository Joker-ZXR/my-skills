# 目录与清单规范

本文件定义清单字段和目录候选样式；实际目录必须先在本次预案中展示并由用户确认。只规范 NIfTI 归档及必要索引，不替代来源元数据 JSON。

## 目录与文件名

先核对同一目标库的实际归档和当前清单，沿用可比数据集的命名与层级。以下仅是在没有既有约定时使用的候选结构：

```text
DATASET_ROOT/
  base/
    anat/sub-<id>/<name>.nii.gz
    dwi/sub-<id>/<name>.nii.gz
    swi/sub-<id>/<name>.nii.gz
    mask/sub-<id>/<name>.nii.gz
    label/sub-<id>/<name>.nii.gz
  manifests/v<version>/{subjects,images,pairs}.tsv
```

`anat`、`dwi`、`swi` 是影像类别；`mask` 指身体/前景范围掩膜（如 brain mask），`label` 指组织、病灶等分割标签，二值分割也按用途归 `label`。只创建当前有数据的类别目录，其他模态可增加相应类别。`base` 是本次选定的来源集合，来源已做的重采样、去颅骨、归一化等仍可放这里，在清单记录处理状态；仅需区别处理版本或已有命名约定要求时才写入文件名。归档后若有新处理，再创建 `derivatives/<pipeline>/<category>/sub-<id>/`；没有就不创建。跨数据集总库先加 `<dataset>/` 层，不在单数据集根目录下重复数据集名。预案中列出最终树和各类真实文件示例，而不是只给占位符。

文件名首先沿用参考归档。无既有约定时可采用 `sub-<id>[_ses-<id>]_<sequence>.nii.gz`，只在必要时增加期相、侧别或重复采集标识。已有文件名含患者和检查编号时应保留这一风格，不自行改成无身份短名。标签和派生结果须用文件名或子目录清楚区分，完整协议、来源名和精确参考图放在清单。每个数据集有独立 `sub` 命名空间；编号一次分配后不重排。仅有一次检查且无检查编号时，不必制造 `ses-01`。

影像、掩膜与分割标签要易于区分；来源已处理文件和归档后新处理文件都须在文件名或清单中标明处理来源和已知版本，不能臆造算法版本。`role=derived_image` 或 `auto_label` 可以出现在 `base`，表示来源文件已有处理，并不表示本库新生成了 `derivatives`。文件名中的 `gt`、`pred` 只按来源语义解释；例如“真实 MRI 的 SynthSeg 输出”仍是自动标签。若源影像为 `.nii`，目标可无损压缩为 `.nii.gz`，同时记录源与目标校验值；不要借压缩改写像素或 affine。

序列词表保留医学差别：T1w、T1ce、T2w、PDw、FLAIR、T2SPACE、DESS、FISP、IW 等分别编码；增强期相、左右侧、重复采集用独立实体。原名如 `T1c` 可映射到统一 `T1ce`，原值仍留在清单。对未知序列先标记待判定，不按宽泛字符串匹配猜测。

### 当前 Brain 目标库的参考示例

以下路径于 2026-10-28 从 `/mnt/hdd_data/Project_zxr/Open_source_datasets/Brain/` 实查，使用时仍需核对当前状态；它们是本项目参考，不是所有数据集的固定命名模板。

- 结构像与随访层级：`PKG-UPENN-GBM/ori/base/anat/sub-UPENN-GBM-00001/ses-11/sub-UPENN-GBM-00001_ses-11_T1ce.nii.gz`。
- 独立 SWI 类别：`UCSF-PDGM-v3/ori/base/swi/sub-UCSF-PDGM-0004/sub-UCSF-PDGM-0004_SWI.nii.gz`；SWAN 可归此类，原始实现名称放入清单。
- ADC：`UCSF-PDGM-v3/ori/base/dwi/sub-UCSF-PDGM-0004/sub-UCSF-PDGM-0004_ADC.nii.gz`。
- 带已知 b 值的 DWI：`ISLES-2022/ori/base/dwi/sub-0001/sub-0001_ses-0001_DWI_b800.nii.gz`。不能把某库的 `trace_b1000` 名称套给未确认 trace 类型或 b 值的影像。
- 分割：`PKG-UPENN-GBM/ori/base/label/sub-UPENN-GBM-00001/ses-11/sub-UPENN-GBM-00001_ses-11_tumor.nii.gz`。同次检查有多套分割时添加能区分含义的短后缀，不合并标签。
- 此库已有来源处理状态主要放在清单；不因已重采样、去颅骨而给每个文件追加 `src-preproc`。工作脚本可随版本保存在 `manifests/v1/`；不自动另增 `scripts/` 层。

## 三张 TSV

一行对应一个对象；使用 UTF-8、表头、相对规范根目录的保存路径。缺失值留空，状态用明确词表，不用文本 `NaN` 冒充事实。

| 文件 | 最少字段 | 作用 |
| --- | --- | --- |
| `subjects.tsv` | `dataset`, `subject_id`, `source_subject_id`, `global_subject_id`, `split`, `split_source` | 原患者 ID 与规范 ID 的稳定映射；跨发布重合者关联到同一全局身份；split 按患者冻结，尚未确定时写 `unassigned`。 |
| `images.tsv` | `image_id`, `dataset`, `subject_id`, `session_id`, `source_root`, `source_relpath`, `source_filename`, `stored_relpath`, `source_sha256`, `stored_sha256`, `storage_status`, `role`, `sequence`, `phase`, `side`, `run`, `parent_image_id`, `reference_image_id`, `pipeline_version`, `geometry_status`, `admission_status` | 每个基准 NIfTI、标签和派生 NIfTI 各占一行；原名和原路径可双向追溯。按需补 shape、spacing、affine、qform/sform code、dtype 和 metadata key。 |
| `pairs.tsv` | `pair_id`, `source_image_ids`, `target_image_id`, `anchor_image_id`, `registered_image_id`, `qc_status` | 记录合法源目标关系及配准质控；多源 IDs 用项目约定的可解析列表格式。 |

`image_id` 在所有数据集间唯一。`role` 至少区分 `image`、`source_label`、`derived_image`、`auto_label`、`prediction`；标签来源再记人工/发布者/算法。`storage_status` 区分 `planned`、`verified`、`failed`，表示是否已核对落盘；`admission_status` 区分 `unassessed`（尚未决定训练用途）、`included`、`hold`、`excluded`，表示实验准入，原因单列。只有 `storage_status=verified` 才能写 `admission_status=included` 和可用的 `stored_relpath`。源根目录和原相对路径共同定位旧文件；不能只记 basename，因为不同病例可能同名。来源 `.nii.gz` 的字节复制应保持哈希相同；`.nii` 压缩后用源/目标哈希加解码内容与几何比较核对。

执行时在暂存区维护映射和复制状态；中断后的暂存表不作为正式 `manifests/vN` 使用。完整校验后一次性发布该版本。若新建患者 split，同时保存 `split_config.json`，写明分层字段、层内配额、排序、随机种子、算法版本和实际名单哈希；配额说明本身不是冻结名单。

项目主方案还列 `checkpoints.tsv` 保存训练祖先与 manifest hash；它属于训练溯源，不必为纯 NIfTI 入库生成。已有 v1.1 逐影像 metadata JSON 保持原用途，`images.tsv` 通过 `metadata_key` 引用，不把采集参数写进影像文件名。

## 准入与特殊情况

- 校验影像完整读取、有限值、物理单位和有效空间变换；标签与对应影像检查 shape、affine 和标签集合。qform、sform 可表示不同坐标语义，有冲突时标 `hold` 并保留原头，不按一个固定优先级覆盖。
- 若发布者的归一化策略有意把无效信号写成 NaN，记录非有限体素数和策略文件；在确认下游处理方式之前，不标为 `included`。
- 同一患者不同检查、期相或侧别保持各自身份；相同 shape/affine 不证明解剖配准。只有通过检查的记录进入 `pairs.tsv` 可用状态。
- 若纳入 4D DWI，NIfTI 保持一幅影像身份，配套 `.bval/.bvec` 与 NIfTI 同 stem 放置；`images.tsv` 增加 `bval_relpath`、`bvec_relpath` 及各自的来源/目标校验值，梯度数与第四维相符。是否归档由用户确认的范围决定；是否进入训练另由 `admission_status` 决定。
- OAI 的 18m/30m 是访视；Prostate158 的训练划分来自 CSV 而非 `train/` 路径；LLD 的文件名类别码不是检查号；SynthSeg 输出不是人工真值。这些例子只提示检查点，实际准入以当前项目方案与源文件为准。
