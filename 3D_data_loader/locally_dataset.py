from datasets import load_dataset

import nibabel as nib

import numpy as np

from nibabel.processing import resample_to_output
from concurrent.futures import ThreadPoolExecutor
from patchify import patchify

# @profile
def load_aeropath():

    ct_dataset = load_dataset("andreped/AeroPath")
    print('len dataset', ct_dataset['test'].num_rows)

    print(ct_dataset)

    all_ct_scan_patches = []
    all_ct_mask_patches = []

    for index, img in enumerate(range(len(ct_dataset['test']))):
        print(index)     #just stop here to see all file names printed
                
        large_image = ct_dataset['test'][img]

        scan_name = str(large_image['ct']).split('/')[-1].split('.')[0]

        ct_image = nib.load(large_image["ct"])
        print("Type1: ", type(ct_image))
        ct_image = resample_to_output(ct_image, order=1)
        print("Type2: ", type(ct_image))

        # nib.save(ct_image, 'test.nii.gz')
        
        ct_data_scan = ct_image.get_fdata().astype("int16")
        print("Type3: ", type(ct_data_scan))
        ct_data_scan[ct_data_scan < -1024] = -1024
        ct_data_scan[ct_data_scan > 400] = 400

        print("FINISH LOADING CT SCAN")
        # ct_data_scan = (ct_data_scan - np.min(ct_data_scan)) / (np.max(ct_data_scan) - np.min(ct_data_scan))

        # ct_data_scan = ct_data_scan.astype(np.float16)
        # ct_data_scan = np.clip(ct_data_scan, 0, 255).astype("uint8")

        # print("max: ", np.max(ct_data_scan))
        # print("min: ", np.min(ct_data_scan))
        # print("type:", ct_data_scan[0].dtype)

        ct_data_scan = ct_data_scan + 1024
        # print('shape: ', ct_data_scan.shape)

        # print('image: ', ct_data_scan)

        # break

        ct_mask = nib.load(large_image["airways"])
        ct_mask = resample_to_output(ct_mask, order=1)
        ct_data_mask = ct_mask.get_fdata().astype("uint8")

        print("FINISH LOADING CT MASK")

        percent_size_x = 0.5  # Przykładowo 20% w osi X
        percent_size_y = 0.5  # Przykładowo 20% w osi Y
        fixed_size_z = 50  # Stała liczba sliców w osi Z

        scan_shape = ct_data_scan.shape

        patch_size_x = min(int(round(scan_shape[0] * percent_size_x)), scan_shape[0])
        patch_size_y = min(int(round(scan_shape[1] * percent_size_y)), scan_shape[1])

        patch_size = (patch_size_x, patch_size_y, fixed_size_z)

        print("patch_size", patch_size)

        step = patch_size

        patches_scan = patchify(ct_data_scan, patch_size, step=step)
        patches_mask = patchify(ct_data_mask, patch_size, step=step)

        # print(patches_scan.shape)
        # print(type(patches_scan))

        # Pętle do iteracji przez otrzymane fragmenty danego skanu
        for i in range(patches_scan.shape[0]):
            for j in range(patches_scan.shape[1]):
                for k in range(patches_scan.shape[2]):
                    patch_scan = patches_scan[i, j, k, :, :, :]
                    patch_mask = patches_mask[i, j, k, :, :, :]

                    # nib.save(patch_scan, 'test_scan.nii.gz')
                    # print(type(patch_scan))

                    # np.save('./dataset/scans/'+scan_name + f'_{i}_{j}_{k}' + '.npy', patch_scan)
                    # np.save('./dataset/airways/'+scan_name + f'_{i}_{j}_{k}' + '.npy', patch_mask)

                    # print(patch_mask.shape)
                    print(patch_scan.shape)
                        
        #             all_ct_scan_patches.append(patch_scan)
        #             all_ct_mask_patches.append(patch_mask)

        # print(np.shape(all_ct_scan_patches))
        # print(type(all_ct_scan_patches))

if __name__ == '__main__':
    load_aeropath()