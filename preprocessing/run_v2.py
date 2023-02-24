
from preprocessing.util import mr_convert_to_nii, pet_convert_to_nii, registration, brain_segmentation, crop_to_mask, n4_bias_field_correction,\
    mr_tumor_segmentation, pet_tumor_segmentation, get_brain_mask_no_tumor, standardization, reorient_2_std
import shutil
from preprocessing import settings
import os
# import SimpleITK as sitk
import nibabel as nib

def run_preprocessing(pid, queue, configurer):
    """
    Preprocessing steps:
    1) Convert to nifti (dcm2niix)
    2) Registration to t1-native
    3) Brain Segmentation (HD-BET)
    4) Tumor Segmentation (HD-GLIO)

    5) N4BiasFieldCorrection (ANTS)
    6) Resample
    7) Standardization (Reference: Brain mask)

    :param pid: patient unique identifier
    :param queue: process queue
    :param configurer: logging configurer for one single process
    :return: preprocess images, brain segmentation and tumor segmentation
    """

    configurer(queue)

#     #%% 1) Convert to Nifti
#     # MRI
#     sequences = ['t1_native', 't1_km', 't2', 'flair']
#     for sequence in sequences:
#         dicom_dir = settings.raw_path.joinpath(settings.project, pid, sequence)
#         out_dir = settings.intermediate_path.joinpath(settings.project, pid)
#         out_file = f'{sequence}'
#
#         if not out_dir.is_dir():
#             out_dir.mkdir(parents=True)
#
#         print(f'PID: {pid}. convert {sequence} to nifti')
#
#         mr_convert_to_nii(dicom_dir, out_dir, out_file)
#
#         try:
#             file = [x for x in out_dir.glob(f'{sequence}*')][0]
#         except IndexError:
#             print(f'{pid}, {sequence} | Nifti file not generated')
#             continue
#         file.rename(out_dir.joinpath(f'{sequence}.nii.gz'))
#
#         print(f'PID: {pid}. convert {sequence} to nifti completed')
#
#     # PET
#     input_file = [x for x in settings.raw_path.joinpath(settings.project, pid, 'pet').glob('*.v')][0]
#     out_dir = settings.intermediate_path.joinpath(settings.project, pid)
#
#     pet_convert_to_nii(out_dir, input_file)
#
#     # GZIP
#     out_file = [x for x in out_dir.glob('*.nii')][0]
#     out_file.rename(out_file.parent.joinpath('pet.nii'))
#     out_file = out_file.parent.joinpath('pet.nii')
#     cmd = f'gzip {out_file}'
#     os.system(cmd)
#
#     # Origin
#     reference = nib.load(settings.intermediate_path.joinpath(settings.project, pid, 't1_native.nii.gz'))
#     image = nib.load(settings.intermediate_path.joinpath(settings.project, pid, 'pet.nii.gz'))
#     array = image.get_fdata()
#     if len(array.shape) == 4:
#         array = array[..., 0]
#     nifti = nib.Nifti1Image(array, reference.affine)
#     nib.save(nifti, settings.intermediate_path.joinpath(settings.project, pid, 'pet.nii.gz'))
#
#     # Orientation (R und L + A und P müssen getauscht werden)
#     # pet_file_in = settings.intermediate_path.joinpath(settings.project, pid, 'pet.nii.gz')
#     # pet_file_out = settings.intermediate_path.joinpath(settings.project, pid, 'pet_v2.nii.gz')
#     #
#     # cmd = f'fslswapdim {pet_file_in} x y -z {pet_file_out}'
#     # os.system(cmd)
#
# #%% ### VERSUCHE ###
# # import matplotlib.pyplot as plt
# #
# # # xform = np.eye(4)
# # # x, y, z
# #
# # nifti = nib.Nifti1Image(array, reference.affine)
# # # nifti = nib.funcs.as_closest_canonical(nifti)
# #
# # nib.save(nifti, intermediate_path.joinpath('test.nii.gz'))
# #
# #
# #     # cmd = f'fslswapdim {out_file} x y -z {out_file}'
# #     # os.system(cmd)
# #
# # # import torchio as tio
# # # import SimpleITK as sitk
# # # from pathlib import Path
# # # import numpy as np
# # # import nibabel as nib
# #
# # intermediate_path = Path('/Volumes/btu-ai/data/intermediate/TEMP_V1/FE2BP896F-BI')
# #
# # sitk_img_t1 = sitk.ReadImage(intermediate_path.joinpath('t1_native.nii.gz'))
# # sitk_img_pet = sitk.ReadImage(intermediate_path.joinpath('pet.nii.gz'))
# #
# # # direction = np.array(sitk_img_t1.GetDirection())
# # # origin = sitk_img_t1.GetOrigin()
# # # image_pixel_type = sitk_img_t1.GetPixelID()
# # # tio.Image()
# #
# # # array = sitk.GetArrayFromImage(sitk_img_t1)
# # reference = nib.load(intermediate_path.joinpath('t1_native.nii.gz'))
# # # reference = nib.funcs.as_closest_canonical(reference)
# # image = nib.load(intermediate_path.joinpath('pet.nii.gz'))
# # array = image.get_fdata()
# # if len(array.shape) == 4:
# #     array = array[..., 0]
# # import numpy as np
# # # x = np.transpose(array, (1, 0, 2))
# # # x = np.rot90(array)
# # x = array[256:0, 256:0, :]
# # nifti = nib.Nifti1Image(x, reference.affine)
# #
# # nib.save(nifti, intermediate_path.joinpath('test_5.nii.gz'))
# # import matplotlib.pyplot as plt
# #
# # # xform = np.eye(4)
# # # x, y, z
# #
# # nifti = nib.Nifti1Image(array, reference.affine)
# # # nifti = nib.funcs.as_closest_canonical(nifti)
# #
# # nib.save(nifti, intermediate_path.joinpath('test.nii.gz'))
#     # origin = sitk.ReadImage(str(settings.intermediate_path.joinpath(settings.project, pid, 't1_native.nii.gz'))).GetOrigin()
#     # direction = sitk.ReadImage(str(settings.intermediate_path.joinpath(settings.project, pid, 't1_native.nii.gz'))).GetDirection()
#
#
#     # origin = sitk.ReadImage(str(settings.intermediate_path.joinpath(settings.project, pid, 't1_native.nii.gz'))).GetOrigin()
#     # direction = sitk.ReadImage(str(settings.intermediate_path.joinpath(settings.project, pid, 't1_native.nii.gz'))).GetDirection()
#     #
#     # sequences = ['t1_km', 't2', 'flair', 'pet']
#     # for sequence in sequences:
#     #     in_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}.nii.gz')
#     #     sitk_img = sitk.ReadImage(str(in_file))
#     #     sitk_img.SetOrigin(origin)
#     #     sitk_img.SetDirection(direction)
#     #     sitk.WriteImage(sitk_img, str(in_file.parent.joinpath(f'{sequence}_origin_t1_native.nii.gz')))
#
#     # x = sitk.ReadImage(str('/Volumes/btu-ai/data/intermediate/TEMP_V1/FE2BP896F-BI/t1_native.nii.gz'))
#     # y = sitk.ReadImage(str('/Volumes/btu-ai/data/intermediate/TEMP_V1/FE2BP896F-BI/pet.nii.gz'))
#     # origin = x.GetOrigin()
#     # direction = x.GetDirection()
#     # y.SetOrigin(origin)
#     # y.SetDirection(direction)
#     # sitk.WriteImage(y, str('/Volumes/btu-ai/data/intermediate/TEMP_V1/FE2BP896F-BI/test.nii.gz'))
#
# ### PROBLEM - ORIENTATION PET ###
#     # cmd = f'fslswapdim {out_file} x y -z {out_file}'
#     # os.system(cmd)
#
#     # # Reorient to STD Space  (### Läuft nicht ###)
#     # # sequences = ['t1_native', 't1_km', 't2', 'flair', 'pet']
#     # # for sequence in sequences:
#     # #     in_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}.nii.gz')
#     # #     out_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}_reorient.nii.gz')
#     # #     reorient_2_std(in_file, out_file)
#
#     #%% 2) Registration
#     sequences = ['t1_km', 't2', 'flair', 'pet']
#
#     for sequence in sequences:
#         print(f'PID: {pid}. Registration for: {sequence}')
#
#         in_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}.nii.gz')
#         ref_file = settings.intermediate_path.joinpath(settings.project, pid, f't1_native.nii.gz')
#         out_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}_co.nii.gz')
#         registration(in_file, ref_file, out_file)
#
#     print(f'PID: {pid}. Registration for: {sequence} done')
#
#     #%% 3) Brain Segmentation
#     print(f'PID: {pid}. Brain segmentation')
#
#     in_file = str(settings.intermediate_path.joinpath(settings.project, pid, f't1_native.nii.gz'))
#     out_file = settings.intermediate_path.joinpath(settings.project, pid, f't1_native_hdbet.nii.gz')
#     brain_segmentation(in_file, str(out_file), device=0)
#     out_file.rename(out_file.parent.joinpath(f'{pid}_0000.nii.gz'))
#
#     out_file.parent.joinpath(f't1_native_hdbet_mask.nii.gz').rename(out_file.parent.joinpath(f'brain_segmentation.nii.gz'))
#     print(f'PID: {pid}. Brain segmentation and renaming done.')
#
#
#     #%% 4) Multiply brain segmentation with images
#     print(f'PID: {pid}. Apply brain segmentation mask')
#
#     out_dir = settings.processed_path.joinpath(settings.project, pid)
#     if not out_dir.is_dir():
#         out_dir.mkdir(parents=True)
#
#     for i, sequence in enumerate(sequences):
#         mask_file = settings.intermediate_path.joinpath(settings.project, pid, f'brain_segmentation.nii.gz')
#         in_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}_co.nii.gz')
#         out_file = settings.intermediate_path.joinpath(settings.project, pid, f'{sequence}_hdbet.nii.gz')
#         crop_to_mask(in_file, mask_file, out_file)
#         out_file.rename(out_file.parent.joinpath(f'{pid}_000{i + 1}.nii.gz'))
#     print(f'PID: {pid}. Application brain segmentation mask done')
#
#     #%% 5) Move MRI files to processed directory
#     for i in range(4):
#         shutil.move(str(settings.intermediate_path.joinpath(settings.project, pid, f'{pid}_000{i}.nii.gz')), str(out_dir))
#
#     #%% 6) HD-GLIO tumor segmentation
#
#     print(f'PID: {pid}. MR tumor segmentation')
#
#     mr_tumor_segmentation(str(out_dir), str(out_dir))
#
#     out_dir.joinpath(f'{pid}.nii.gz').rename(out_dir.joinpath(f'{pid}_mr_segmentation.nii.gz'))
#
#     shutil.move(str(
#         settings.intermediate_path.joinpath(settings.project, pid, f'brain_segmentation.nii.gz')),
#                 out_dir)
#
#     out_dir.joinpath(f'brain_segmentation.nii.gz').rename(out_dir.joinpath(f'{pid}_brain_segmentation.nii.gz'))
#
#     to_remove = ['plans.pkl', 'postprocessing.json']
#     for remove in to_remove:
#         out_dir.joinpath(remove).unlink()
#
#     print(f'PID: {pid}. MR tumor segmentation done')

#%% PET Segmentation
    temp_dir = settings.intermediate_path.joinpath(settings.project, pid, 'temp')
    if not temp_dir.is_dir():
        temp_dir.mkdir(parents=True)
    in_file = str(settings.intermediate_path.joinpath(settings.project, pid, f'{pid}_0004.nii.gz'))
    shutil.move(str(in_file), str(temp_dir))
    # out_file = str(settings.intermediate_path.joinpath(settings.project, pid, f'pet_segmentation.nii.gz'))
    pet_tumor_segmentation(temp_dir, temp_dir)

#%%
# #%% 5) N4BiasFieldCorrection
#
# # logger.warning(f'PID: {pid}. Perform N4BiasFieldCorrection')
# print(f'PID: {pid}. Perform N4BiasFieldCorrection')
#
# sequences = ['t1_native', 't1_km', 't2', 'flair']
#
# for i, sequence in enumerate(sequences):
#     out_dir = settings.processed_path.joinpath(settings.project, pid, study)
#     if not out_dir.is_dir():
#         out_dir.mkdir(parents=True)
#     in_file = str(settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}_hdbet.nii.gz'))
#     out_file = settings.processed_path.joinpath(settings.project, pid, study, f'{sequence}_hdbet_n4.nii.gz')
#     brain_mask = str(
#         settings.intermediate_path.joinpath(settings.project, pid, study, f'brain_segmentation.nii.gz'))
#     n4_bias_field_correction(in_file, str(out_file), brain_mask)
#
#     # 6) Rename files to nnU-Net format
#     out_file.rename(out_file.parent.joinpath(f'{pid}_000{i}.nii.gz'))
#
# # logger.warning(f'PID: {pid}. N4BiasFieldCorrection and renaming done')
# print(f'PID: {pid}. N4BiasFieldCorrection and renaming done')

    # logger.warning(f'PID: {pid}. MR tumor segmentation done')
    #
    # #%% 8) Standardization
    #
    # sequences = ['0000', '0001', '0002', '0003']
    #
    # brain_mask_path = in_dir_path.joinpath(f'{pid}_brain_segmentation.nii.gz')
    # tumor_mask_path = in_dir_path.joinpath(f'{pid}_mr_segmentation.nii.gz')
    # brain_mask_array = get_brain_mask_no_tumor(str(brain_mask_path), str(tumor_mask_path))
    #
    # # logger.warning(f'PID: {pid}. Doing standardization')
    # print(f'PID: {pid}. Doing standardization')
    #
    # for sequence in sequences:
    #     image_path = in_dir_path.joinpath(f'{pid}_{sequence}.nii.gz')
    #     out_file = in_dir_path.joinpath(f'{pid}_{sequence}_std.nii.gz')
    #     standardization(str(image_path), brain_mask_array, str(out_file))
    # # logger.warning(f'PID: {pid}. Standardization done')
    # # logger.warning(f'PID: {pid}. Preprocessing finished!')
    # print(f'PID: {pid}. Standardization done')
    # print(f'PID: {pid}. Preprocessing finished!')