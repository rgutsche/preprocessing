from preprocessing.util import convert_to_nii, registration, brain_segmentation, crop_to_mask, n4_bias_field_correction,\
    tumor_segmentation, get_brain_mask_no_tumor, standardization
from multiprocessing import current_process
import logging
import shutil
from preprocessing import settings


def run_preprocessing(pid, queue, configurer):
    """
    Preprocessing steps:
    1) Convert to nifti (dcm2niix)
    2) Registration to t1-native
    3) Brain Segmentation (HD-BET)
    4) N4BiasFieldCorrection (ANTS)
    5) Tumor Segmentation (HD-GLIO)
    6) Standardization (Reference: Brain mask without tumor region)
    :param pid: patient unique identifier
    :param queue: process queue
    :param configurer: logging configurer for one single process
    :return: preprocess images, brain segmentation and tumor segmentation
    """

    configurer(queue)

    logger = logging.getLogger()
    logger.warning(f'Process: {current_process().name}, pid: {pid}')

    studies = [x.name for x in settings.raw_path.joinpath(settings.project, pid).iterdir() if x.is_dir()]

    # Problems with @eaDir. Remove these dirs before execution.
    # if you have this problem run this block and change line 25 to:
    # studies = [x for x in settings.raw_path.joinpath(settings.project, pid).iterdir() if x.is_dir()]
    # if len(studies) > 1:
    #     logger.warning(f'Studies: {pid}: {studies[-1]}')
    #     if studies[-1].name == '@eaDir':
    #         logger.warning(f'Removing Directory: {studies[-1]}')
    #         shutil.rmtree(studies[-1])
    #         studies = [x for x in settings.raw_path.joinpath(settings.project, pid).iterdir() if x.is_dir()]
    #         assert len(studies) == 1

    for study in studies:
        sequences = ['t1_native', 't1_km', 't2', 'flair']
        for sequence in sequences:
            dicom_dir = settings.raw_path.joinpath(settings.project, pid, study, sequence)
            out_dir = settings.intermediate_path.joinpath(settings.project, pid, study)
            out_file = f'{sequence}'

            if not out_dir.is_dir():
                out_dir.mkdir(parents=True)

            logger.warning(f'PID: {pid}. convert {sequence} to nifti')

            convert_to_nii(dicom_dir, out_dir, out_file)

            try:
                file = [x for x in out_dir.glob(f'{sequence}*')][0]
            except IndexError:
                logger.error(f'{pid}, {sequence}. Nifti file not generated.')
                continue
            file.rename(out_dir.joinpath(f'{sequence}.nii.gz'))

            logger.warning(f'PID: {pid}. convert {sequence} to nifti completed')

        #%% 2) Registration
        sequences = ['t1_km', 't2', 'flair']

        for sequence in sequences:
            logger.warning(f'PID: {pid}. Registration for: {sequence}')

            in_file = settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}.nii.gz')
            ref_file = settings.intermediate_path.joinpath(settings.project, pid, study, f't1_native.nii.gz')
            out_file = settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}_co.nii.gz')
            registration(in_file, ref_file, out_file)

        logger.warning(f'PID: {pid}. Registration for: {sequence} done')

        #%% 3) Brain Segmentation
        logger.warning(f'PID: {pid}. Brain segmentation')
        in_file = str(settings.intermediate_path.joinpath(settings.project, pid, study, f't1_native.nii.gz'))
        out_file = settings.intermediate_path.joinpath(settings.project, pid, study, f't1_native_hdbet.nii.gz')
        brain_segmentation(in_file, str(out_file), device=0)

        out_file.parent.joinpath(f't1_native_hdbet_mask.nii.gz').rename(out_file.parent.joinpath(f'brain_segmentation.nii.gz'))
        logger.warning(f'PID: {pid}. Brain segmentation and renaming done.')

        #%% 4) Multiply brain segmentation with images
        logger.warning(f'PID: {pid}. Apply brain segmentation mask')

        for sequence in sequences:
            mask_file = settings.intermediate_path.joinpath(settings.project, pid, study, f'brain_segmentation.nii.gz')
            in_file = settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}_co.nii.gz')
            out_file = settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}_hdbet.nii.gz')
            crop_to_mask(in_file, mask_file, out_file)

        logger.warning(f'PID: {pid}. Application brain segmentation mask done')

        #%% 5) N4BiasFieldCorrection

        logger.warning(f'PID: {pid}. Perform N4BiasFieldCorrection')

        sequences = ['t1_native', 't1_km', 't2', 'flair']

        for i, sequence in enumerate(sequences):
            out_dir = settings.processed_path.joinpath(settings.project, pid, study)
            if not out_dir.is_dir():
                out_dir.mkdir(parents=True)
            in_file = str(settings.intermediate_path.joinpath(settings.project, pid, study, f'{sequence}_hdbet.nii.gz'))
            out_file = settings.processed_path.joinpath(settings.project, pid, study, f'{sequence}_hdbet_n4.nii.gz')
            brain_mask = str(
                settings.intermediate_path.joinpath(settings.project, pid, study, f'brain_segmentation.nii.gz'))
            n4_bias_field_correction(in_file, str(out_file), brain_mask)

            # 6) Rename files to nnU-Net format
            out_file.rename(out_file.parent.joinpath(f'{pid}_000{i}.nii.gz'))

        logger.warning(f'PID: {pid}. N4BiasFieldCorrection and renaming done')

        #%% 7) HD-GLIO tumor segmentation

        logger.warning(f'PID: {pid}. MR tumor segmentation')
        in_dir_path = settings.processed_path.joinpath(settings.project, pid, study)

        tumor_segmentation(str(in_dir_path), str(in_dir_path))

        in_dir_path.joinpath(f'{pid}.nii.gz').rename(in_dir_path.joinpath(f'{pid}_mr_segmentation.nii.gz'))

        shutil.move(str(
            settings.intermediate_path.joinpath(settings.project, pid, study, f'brain_segmentation.nii.gz')),
                    in_dir_path)

        in_dir_path.joinpath(f'brain_segmentation.nii.gz').rename(in_dir_path.joinpath(f'{pid}_brain_segmentation.nii.gz'))

        to_remove = ['plans.pkl', 'postprocessing.json']
        for remove in to_remove:
            in_dir_path.joinpath(remove).unlink()

        logger.warning(f'PID: {pid}. MR tumor segmentation done')

        #%% 8) Standardization

        sequences = ['0000', '0001', '0002', '0003']

        brain_mask_path = in_dir_path.joinpath(f'{pid}_brain_segmentation.nii.gz')
        tumor_mask_path = in_dir_path.joinpath(f'{pid}_mr_segmentation.nii.gz')
        brain_mask_array = get_brain_mask_no_tumor(str(brain_mask_path), str(tumor_mask_path))

        logger.warning(f'PID: {pid}. Doing standardization')
        for sequence in sequences:
            image_path = in_dir_path.joinpath(f'{pid}_{sequence}.nii.gz')
            out_file = in_dir_path.joinpath(f'{pid}_{sequence}_std.nii.gz')
            standardization(str(image_path), brain_mask_array, str(out_file))
        logger.warning(f'PID: {pid}. Standardization done')
        logger.warning(f'PID: {pid}. Preprocessing finished!')