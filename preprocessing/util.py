"""
Helper functions for preprocessing
"""
from nipype.interfaces import fsl
from nipype.interfaces.ants import N4BiasFieldCorrection
from nipype.interfaces.dcm2nii import Dcm2niix
from HD_BET.run import run_hd_bet

import os
from nipype.interfaces.fsl import ApplyMask
import SimpleITK as sitk
import numpy as np


def pet_convert_to_nii(out_dir_path, input_file):
    cmd = f'ecat2nii -O={out_dir_path} {input_file}'
    os.system(cmd)

def reorient_2_std(input_file, output_file):
    reorient = fsl.Reorient2Std()
    reorient.inputs.out_file = input_file
    reorient.inputs.out_file = output_file
    reorient.run()

def mr_convert_to_nii(dicom_dir_path, out_dir_path, out_path):
    """
    Convert dir containing dicom series to nifti file. File will be compressed (out_filename.nii.gz).
    dcm2niix tool is used.
    :param dicom_dir_path: str or pathlike object | dir containing single dicom series
    :param out_dir_path: str or pathlike object | output dir
    :param out_path: str or pathlike object | output file name (without .nii.gz suffix!)
    :return: nifti file
    """
    converter = Dcm2niix()
    converter.inputs.source_dir = dicom_dir_path
    converter.inputs.bids_format = False
    converter.inputs.compress = 'y'
    converter.inputs.output_dir = out_dir_path
    converter.inputs.out_filename = f'{out_path}'
    converter.run()


def registration(in_path, ref_path, out_path):
    """
    Registration image to another image (for example T1-km to T1-native)
    :param in_path: str or pathlike object | nifti file that should be registered
    :param ref_path: str or pathlike object | nifti file that should be registered to
    :param out_path: str or pathlike object | output file name (without .nii.gz suffix!)
    :return: registered nifti file
    """
    flt = fsl.FLIRT(cost_func='mutualinfo',
                    dof=7,
                    searchr_x=[180, 180],
                    searchr_y=[180, 180],
                    searchr_z=[180, 180],
                    interp='trilinear')

    flt.inputs.in_file = in_path  # File that should be registered
    flt.inputs.reference = ref_path  # File that should be registered to
    flt.inputs.output_type = 'NIFTI_GZ'
    flt.inputs.out_file = out_path
    flt.run()


def brain_segmentation(in_path, out_path, device=0):
    """
    Brain segmentation using HD-BET
    :param in_path: str |
    :param out_path: str |
    :param device_id: either int for device id or 'cpu'
    :return: image crop to brain mask, brain mask
    """
    run_hd_bet(in_path, out_path, device=device)


def crop_to_mask(in_path, mask_path, out_path):
    """
    Use HD-BET brain segmentation mask for all sequences
    :param in_path:
    :param mask_path:
    :param out_path:
    :return:
    """
    mask = ApplyMask()
    mask.inputs.in_file = in_path
    mask.inputs.mask_file = mask_path
    mask.inputs.out_file = out_path
    mask.run()


def n4_bias_field_correction(in_path, out_path, brain_mask_path):
    """
    N4-bias-field correction unsing ANTS
    :param in_path:
    :param out_path:
    :param brain_mask_path:
    :return:
    """
    n4 = N4BiasFieldCorrection()
    n4.inputs.input_image = in_path
    n4.inputs.mask_image = brain_mask_path
    n4.inputs.output_image = out_path
    n4.run()


def mr_tumor_segmentation(in_dir_path, out_dir_path):
    """
    Perform HD-GLIO segmentation for complete folder with the following structure:
    t1_native: PATIENT_IDENTIFIER_0000.nii.gz
    t1_km: PATIENT_IDENTIFIER_0001.nii.gz
    t2: PATIENT_IDENTIFIER_0002.nii.gz
    flair: PATIENT_IDENTIFIER_0003.nii.gz
    :param in_dir_path: str or pathlike object |
    :param out_dir_path: str or pathlike object |
    :return: tumor segmentation
    """
    cmd = f'hd_glio_predict_folder -i {in_dir_path} -o {out_dir_path}'
    os.system(cmd)

def pet_tumor_segmentation(in_dir_path, out_dir_path):
    """
    Perform nnunet pet segmentation for complete folder with the following structure:
    pet: PATIENT_IDENTIFIER_0004.nii.gz
    :param in_dir_path: str or pathlike object |
    :param out_dir_path: str or pathlike object |
    :return: tumor segmentation
    """
    cmd = f'nnUNet_predict -i {in_dir_path} -o {out_dir_path} -t 070 -m 3d_fullres -tr nnUNetTrainerV2'
    os.system(cmd)


def get_brain_mask_no_tumor(brain_mask_path, tumor_mask_path):
    """

    :param brain_mask_path:
    :param tumor_mask_path:
    :return:
    """
    sitk_brain_mask = sitk.ReadImage(brain_mask_path)
    sitk_tumor_mask = sitk.ReadImage(tumor_mask_path)
    sitk_tumor_mask_array = sitk.GetArrayFromImage(sitk_tumor_mask).astype(dtype='uint8')
    sitk_brain_mask_array = sitk.GetArrayFromImage(sitk_brain_mask).astype(dtype='uint8')
    sitk_tumor_mask_array[sitk_tumor_mask_array == 2] = 1
    brain_mask_no_tumor = sitk_brain_mask_array - sitk_tumor_mask_array
    return brain_mask_no_tumor


def standardization(image_path, brain_mask, out_file):
    """

    :param image_path:
    :param brain_mask:
    :param out_file:
    :return:
    """
    sitk_image = sitk.ReadImage(image_path)
    sitk_image_array = sitk.GetArrayFromImage(sitk_image)
    brain_values = sitk_image_array[brain_mask == 1]
    mean = np.mean(brain_values)
    std = np.std(brain_values)
    sitk_image_array_std = (sitk_image_array - mean) / std
    sitk_img_std = sitk.GetImageFromArray(sitk_image_array_std)
    sitk_img_std.CopyInformation(sitk_image)
    sitk.WriteImage(sitk_img_std, out_file)


####################### DON'T TOUCH ####################################

# #%% 8) Resample (sitk-version, maybe switch to ANTS!)
#
# def get_rsmpl_params(sitk_img, spacing_out=1, size_out=224, is_mask=False):
#     spacing = np.array(sitk_img.GetSpacing())
#     resampled_pixel_spacing = np.array([spacing_out, spacing_out, spacing[2]])
#     size = np.array(sitk_img.GetSize())
#     output_size = (int(size[0]), int(size[1]), int(size[2]))
#     # output_size = (size_out, size_out, int(size[2]))
#     direction = np.array(sitk_img.GetDirection())
#     origin = sitk_img.GetOrigin()
#     image_pixel_type = sitk_img.GetPixelID()
#     if is_mask:
#         interpolator = sitk.sitkNearestNeighbor
#     else:
#         interpolator = sitk.sitkBSpline
#
#     params = {'file': sitk_img,
#               'output_spacing': resampled_pixel_spacing,
#               'output_size': output_size,
#               'output_direction': direction,
#               'output_origin': origin,
#               'output_pixel_type': image_pixel_type,
#               'interpolator': interpolator}
#
#     return params
#
#
# def get_rsmpl_image(params):
#     sitk_img = params['file']
#     output_spacing = params['output_spacing']
#     output_size = params['output_size']
#     output_direction = params['output_direction']
#     output_origin = params['output_origin']
#     output_pixel_type = params['output_pixel_type']
#     interpolator = params['interpolator']
#
#     rif = sitk.ResampleImageFilter()
#     rif.SetOutputSpacing(output_spacing)
#     rif.SetSize(output_size)
#     rif.SetOutputDirection(output_direction)
#     rif.SetOutputOrigin(output_origin)  # Not sure if this is valid for every case
#     rif.SetOutputPixelType(output_pixel_type)
#     rif.SetInterpolator(interpolator)
#     resampled_image = rif.Execute(sitk_img)
#     return resampled_image
#
# #%% 9) Discretization
#
#
# def bin_image(sitk_image, sitk_mask, output_path, bin_width=None, bin_counts=None):
#     """
#     Discretize image intensity values. Either to a bin_width or bin_counts.
#     For example: Values range from -3 to +3. Bin_width of 0.15 results in 40 intensity values (gray values).
#     Values range from -3 to +10. Bin_width of 0.15 results in 86 intensity values.
#     Literature for discretization: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4525145/
#     Python Code: https://github.com/AIM-Harvard/pyradiomics/blob/ad5b2de5b42701c7d80f2579335b0f2b574d2fab/radiomics/imageoperations.py#L56
#     :param sitk_image:
#     :param sitk_mask:
#     :param bin_width:
#     :param bin_counts:
#     :return:
#     """
#     array_img = sitk.GetArrayFromImage(sitk_image)
#     array_mask = sitk.GetArrayFromImage(sitk_mask)
#
#     values = array_img[array_mask == 1].flatten()
#     if bin_counts:
#         bin_edges = np.histogram(values, bin_counts)[1]
#         bin_edges[-1] += 1
#     else:
#         minimum = min(values)
#         maximum = max(values)
#         low_Bound = minimum - (minimum % bin_width)
#         high_Bound = maximum + 2 * bin_width
#         bin_edges = np.arange(low_Bound, high_Bound, bin_width)
#
#     array_img_bin = np.digitize(array_img, bin_edges)
#     sitk_img_bin = sitk.GetImageFromArray(array_img_bin.astype(float))
#     sitk_img_bin.CopyInformation(sitk_image)
#     sitk.WriteImage(sitk_img_bin, str(output_path))
#


