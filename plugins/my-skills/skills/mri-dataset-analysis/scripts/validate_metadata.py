#!/usr/bin/env python3
"""Validate this skill's metadata structure; no image/content validation."""
import argparse
import json
import math
from pathlib import PurePosixPath

BASE = 'Age Sex Region ImageContrast AcquisitionType AcquisitionPlane PulseSequence SequenceFamily MatrixSize VoxelSpacing_mm SliceThickness_mm Manufacturer ManufacturersModelName FieldStrength_T TR_ms-TE_ms-TI_ms-FA_degree ContrastPhase FatSuppression HealthStatus Disease TaskType'.split()
DWI = 'BValues_s_per_mm2 BVectors BVectorCoordinateSystem BValFile BVecFile DiffusionImageType'.split()

def number(v, minimum=0, positive=False):
    return v == 'NaN' or (type(v) in (int, float) and math.isfinite(v) and (v > minimum if positive else v >= minimum))

def path_ok(v):
    return isinstance(v, str) and bool(v) and not PurePosixPath(v).is_absolute() and '..' not in PurePosixPath(v).parts and '\\' not in v

def validate_label_definitions(value):
    errors = []
    if not isinstance(value, dict) or set(value) != {'Classification', 'Segmentation'}:
        return ['LabelDefinitions must contain Classification and Segmentation']
    for task, definition in value.items():
        schemes = isinstance(definition, dict) and 'Schemes' in definition
        if schemes:
            if set(definition) != {'Schemes'} or not isinstance(definition['Schemes'], dict) or not definition['Schemes']:
                errors.append(f'LabelDefinitions.{task}: invalid Schemes')
                continue
            items = definition['Schemes']
        else:
            items = {'default': definition}
        for name, entry in items.items():
            prefix = f'LabelDefinitions.{task}.{name}'
            if not isinstance(name, str) or not name or not isinstance(entry, dict):
                errors.append(f'{prefix}: expected named definition object')
                continue
            required = {'Status', 'Labels', 'Description'} | ({'Scope'} if schemes else set())
            if not required <= set(entry) or not set(entry) <= {'Status', 'Labels', 'Description', 'Scope'}:
                errors.append(f'{prefix}: unexpected or missing fields')
            status, labels = entry.get('Status'), entry.get('Labels')
            if status not in ('Available', 'NotAvailable', 'NotApplicable', 'Unknown'):
                errors.append(f'{prefix}: invalid Status')
            if not isinstance(labels, dict):
                errors.append(f'{prefix}: Labels must be an object')
            else:
                if (status == 'Available') != bool(labels):
                    errors.append(f'{prefix}: Available requires labels; other statuses require an empty mapping')
                for code, meaning in labels.items():
                    if not isinstance(code, str) or not code or not isinstance(meaning, str) or not meaning.strip():
                        errors.append(f'{prefix}: expected code strings mapped to nonempty English names')
                    if task == 'Segmentation':
                        try:
                            assert str(int(code)) == code
                        except (ValueError, TypeError, AssertionError):
                            errors.append(f'{prefix}: segmentation codes must be integer strings')
            for field in ['Description'] + (['Scope'] if 'Scope' in entry else []):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    errors.append(f'{prefix}: {field} must be a nonempty English string')
    return errors

def validate(data, require_label_definitions=False):
    if not isinstance(data, dict) or not data:
        return ['Expected a nonempty image-key dictionary']
    errors = []
    if 'LabelDefinitions' in data:
        errors.extend(validate_label_definitions(data['LabelDefinitions']))
        if next(iter(data)) != 'LabelDefinitions':
            errors.append('LabelDefinitions must be the first top-level field')
    elif require_label_definitions:
        errors.append('Missing top-level LabelDefinitions (required for schema v1.3)')
    if not any(key != 'LabelDefinitions' for key in data):
        errors.append('Expected at least one image record')
    for key, r in data.items():
        if key == 'LabelDefinitions':
            continue
        def check(ok, message):
            if not ok:
                errors.append(f'{key}: {message}')
        check(path_ok(key), 'key must be a relative image path')
        if not isinstance(r, dict):
            check(False, 'record must be an object')
            continue
        diffusion = r.get('ImageContrast') == 'DWI'
        check(set(r) == set(BASE + (DWI if diffusion else [])), 'unexpected or missing fields')
        if not set(BASE) <= set(r):
            continue
        for field in BASE:
            if field not in ['Age', 'MatrixSize', 'VoxelSpacing_mm', 'SliceThickness_mm', 'FieldStrength_T', 'TR_ms-TE_ms-TI_ms-FA_degree', 'Disease', 'TaskType']:
                check(isinstance(r[field], str) and bool(r[field]), f'{field}: expected nonempty string')
        for field, choices in {'Sex': ['M','F','Unknown'], 'AcquisitionType':['2D','3D','Unknown'], 'AcquisitionPlane':['Axial','Sagittal','Coronal','Oblique','Unknown'], 'HealthStatus':['Healthy','Diseased','Unknown']}.items():
            check(r[field] in choices, f'{field}: invalid category')
        check(number(r['Age']), 'Age must be nonnegative or "NaN"')
        for field in ['SliceThickness_mm', 'FieldStrength_T']:
            check(number(r[field], positive=True), f'{field}: expected positive number or "NaN"')
        shape = r['MatrixSize']
        shape_ok = isinstance(shape, list) and len(shape) >= 3 and all(type(x) is int and x > 0 for x in shape)
        check(shape_ok, 'MatrixSize must contain >=3 positive integers')
        for field, length in [('VoxelSpacing_mm', 3), ('TR_ms-TE_ms-TI_ms-FA_degree', 4)]:
            value = r[field]
            check(isinstance(value, list) and len(value) == length and all(number(x, positive=field=='VoxelSpacing_mm') for x in value), f'{field}: invalid numeric array')
        for field in ['Disease', 'TaskType']:
            check(isinstance(r[field], list) and all(isinstance(x,str) and x for x in r[field]), f'{field}: expected string list')
        if r['HealthStatus'] == 'Healthy':
            check(r['Disease'] == [], 'healthy record must have empty Disease')
        if r['HealthStatus'] != 'Healthy':
            check(bool(r['Disease']), 'non-healthy record needs Disease or Unknown')
        if not diffusion or not set(DWI) <= set(r):
            continue
        check(r['BVectorCoordinateSystem'] in ['FSL','Unknown'], 'invalid bvec coordinate convention')
        check(r['DiffusionImageType'] in ['Directional','Trace','Unknown'], 'invalid diffusion image type')
        for field in ['BValFile','BVecFile']:
            check(r[field] == 'Unknown' or path_ok(r[field]), f'{field}: expected relative path or Unknown')
        n = (shape[3] if len(shape)==4 else 1) if shape_ok and len(shape) in (3,4) else None
        for field in ['BValues_s_per_mm2', 'BVectors']:
            value = r[field]
            if value == 'NaN':
                continue
            if not isinstance(value,list) or not value:
                check(False, f'{field}: expected array or "NaN"')
                continue
            if n is not None:
                check(len(value) == n, f'{field}: count differs from NIfTI volumes')
            if field == 'BValues_s_per_mm2':
                check(all(number(x) for x in value), 'invalid b values')
            else:
                check(all(isinstance(v,list) and len(v)==3 and all(x=='NaN' or (type(x) in (int,float) and math.isfinite(x)) for x in v) for v in value), 'bvec must be N x 3 finite values or missing components')
    return errors

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError(f'Nonstandard JSON constant: {value}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata')
    parser.add_argument('--require-label-definitions', action='store_true', help='Require the v1.3 dataset-level label definitions')
    args = parser.parse_args()
    try:
        with open(args.metadata, encoding='utf-8') as stream:
            data = json.load(stream, object_pairs_hook=unique_object, parse_constant=reject_constant)
        errors = validate(data, args.require_label_definitions)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'PASS: {sum(k != "LabelDefinitions" for k in data)} image records; structure only (not image or gradient-content validation).')

if __name__ == '__main__':
    main()
