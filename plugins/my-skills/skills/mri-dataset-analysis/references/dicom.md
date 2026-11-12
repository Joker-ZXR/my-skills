# DICOM 转换与头信息

优先用 dcm2niix，记录本地版本和实际命令；参数先核对本地帮助，不盲目采用默认值。依赖缺失时按环境权限安装或申请，不绕过限制。

按患者/StudyInstanceUID/SeriesInstanceUID 索引，不按文件名拼接；识别重复 SOPInstanceUID 及冲突。筛除范围外定量图和定位像。一个序列可能输出多份 NIfTI，保留回波、时相、重建差异，不强制合并。已有可验证对应且完整的 NIfTI 可复用，但仍从 DICOM 提取可用头信息。无法确认对应时记录，不默认重复或同一序列。

脚本保存 `data_pre/<REGION>/<DATASET_NAME>/convert_dicom_to_nifti.py`，输入输出用 CLI 参数。一次启动处理全部待转换序列，在脚本内完成遍历、分组、转换和验证；不为每个病例或序列单独发起 Agent 工具调用。单项失败记录后继续其他独立项，详细转换日志保存文件，终端仅输出定期汇总进度和错误摘要；结合转换清单支持中断续跑。输出 .nii.gz 和同名 sidecar；DWI 另保存转换器实际生成的 .bval/.bvec。不创建伪造梯度文件。不额外裁剪、重采样、归一化。保留原始数据。

重复执行只跳过已成功、输出完整且输入及转换配置未变化的项。使用清单记录输入校验依据和工具/参数；至少检测文件新增、删除、大小或修改时间变化，疑似冲突再核对内容。新输出先验证再发布，失败不标成功；已有输出不匹配时写新的可区分结果或按已授权范围更新，不能静默覆盖无关数据。

## 三类信息分别保存

1. `<image>.json`：转换工具 sidecar，原有字段和单位不改。标准 meta 再换算单位，例如 sidecar 秒→ms，不能把原 DICOM ms 再乘1000。
2. `<METADATA_OUTPUT_DIR>/dicom_headers.json`：所需 DICOM 标签，不是完整头信息转储。记录序列、tag 编号/名称/VR/原值及单位依据。包括可获取的 PatientAge/Sex、厂商 Manufacturer (0008,0070)、扫描仪型号 ManufacturerModelName (0008,1090)、场强 MagneticFieldStrength (0018,0087)、TR/TE/TI/FA、序列、层厚、层间距、像素间距、方向位置、扩散参数等。检查关键标签跨实例变化，变化值附实例/帧映射；读取 Enhanced DICOM Shared/Per-frame Functional Groups。私有标签仅在有可靠定义时解码。无 PixelData，不额外导出无关直接身份信息。
3. `<METADATA_OUTPUT_DIR>/conversion_manifest.json`：输入相对路径/序列标识、校验依据、转换状态、工具版本与命令、所有输出及 sidecar/梯度/头记录映射、维度/间距/类型和错误原因。

## 验证

验证影像可读、空间信息有效、文件映射完整、sidecar 对应。按实际帧/回波/时相组织核对，不要求 DICOM 文件数等于 NIfTI 切片数。掩膜与影像检查形状/affine，说明容差；不直接复制 affine 掩盖问题。dcm2niix 不作为任意 DICOM SEG/RTSTRUCT 的通用标签转换器，遇到这些标注需按对应格式可靠处理，不能冒充普通序列输出。

记录检查深度和成功/失败/排除/待判定数量；报告脚本、命令、工具版本与失败清单。不把 header 可读称作全压缩流或像素内容已验证。

三类 JSON 均按元数据规范将数组单行显示、对象缩进。sidecar 仅改空白排版，不改变转换器的原字段和值。转换统计和解释写入 Markdown，不再另建通用 details.json。
