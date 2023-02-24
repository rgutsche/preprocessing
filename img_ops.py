import SimpleITK as sitk
import numpy as np





def get_bbox_from_mask(mask, outside_value=0):
    mask_voxel_coords = np.where(mask != outside_value)
    minzidx = int(np.min(mask_voxel_coords[0]))  # Anterior
    maxzidx = int(np.max(mask_voxel_coords[0])) + 1  # Posterior
    minxidx = int(np.min(mask_voxel_coords[1]))  # Right
    maxxidx = int(np.max(mask_voxel_coords[1])) + 1  # Left
    return [[minzidx, maxzidx], [minxidx, maxxidx]]


def crop_to_bbox(image, bbox):
    image = image[bbox[0][0]:bbox[0][1], bbox[1][0]:bbox[1][1], :]
    return image



def get_min_max_for_slicing(bb):
    """
    Slicing parameters for image 168 x 168 x z
    :param bb: xstart, ystart, zstart, xsize, ysize, zsize
    :return: slicing_params: xmin, xmax, ymin, ymax
    """
    slicing_params = []
    for i in range(2):
        center = bb[i] + int((bb[i + 3]/2))
        min_ = center - 84
        max_ = center + 84
        slicing_params.append(min_)
        slicing_params.append(max_)

    return slicing_params


def crop_image(sitk_img, sitk_brain_mask, sitk_tum_mask):
    """

    :return: centered (to brain mask) and cropped image and masks to 168x168xz dimension
    """
    lsif = sitk.LabelShapeStatisticsImageFilter()
    lsif.Execute(sitk_brain_mask)
    # [xstart, ystart, zstart, xsize, ysize, zsize]
    bb = lsif.GetBoundingBox(label=1)
    params = get_min_max_for_slicing(bb)
    crop_sitk_img = sitk_img[params[0]:params[1], params[2]:params[3], bb[2]:bb[2] + bb[5]]
    crop_brain_mask = sitk_brain_mask[params[0]:params[1], params[2]:params[3], bb[2]:bb[2] + bb[5]]
    crop_tum_mask = sitk_tum_mask[params[0]:params[1], params[2]:params[3], bb[2]:bb[2] + bb[5]]
    return crop_sitk_img, crop_brain_mask, crop_tum_mask



# Get index of biggest slice
# fg_mask = sitk_tumor_mask_array != 0
# fg_mask = sitk_tumor_mask_array == 2
# fg_per_slice = fg_mask.sum((1, 2))
# selected_slice = np.argmax(fg_per_slice)



def get_bbox_from_mask(mask, outside_value=0):
    mask_voxel_coords = np.where(mask != outside_value)
    minzidx = int(np.min(mask_voxel_coords[0]))  # Anterior
    maxzidx = int(np.max(mask_voxel_coords[0])) + 1  # Posterior
    minxidx = int(np.min(mask_voxel_coords[1]))  # Right
    maxxidx = int(np.max(mask_voxel_coords[1])) + 1  # Left
    minyidx = int(np.min(mask_voxel_coords[2]))  # Inferior
    maxyidx = int(np.max(mask_voxel_coords[2])) + 1  # Superior
    return [[minzidx, maxzidx], [minxidx, maxxidx], [minyidx, maxyidx]]


# sitk_tumor_mask_array.shape
#
# get_bbox_from_mask(sitk_tumor_mask_array)



def crop_to_bbox(image, bbox):
    assert len(image.shape) == 3, "only supports 3d images"
    resizer = (slice(bbox[0][0], bbox[0][1]), slice(bbox[1][0], bbox[1][1]), slice(bbox[2][0], bbox[2][1]))
    return image[resizer]