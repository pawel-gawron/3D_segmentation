from natsort import natsorted
import nibabel as nib
import glob
import os

## Create nonoverlapping quadrants



data_dir = os.path.join(os.getcwd(), 'AeroPath')

def create_overlapping_quadrants(image_shape, overlap_percentage=0.0):
    x, y, z = image_shape
    overlap_z = int(z * overlap_percentage)
    if z < 3 * overlap_z:
        return [(0, z)]
    mid_z = z // 2
    return [
        (0, mid_z + overlap_z),
        (mid_z - overlap_z, z)
    ]

def load_nifti_file(file_path):
    return nib.load(file_path)

def save_nifti_file(data, affine, file_path):
    img = nib.Nifti1Image(data, affine)
    nib.save(img, file_path)

def process_file(file_path, output_dir):
    img = load_nifti_file(file_path)
    data = img.get_fdata()
    print("input shape: ", data.shape)
    affine = img.affine
    quadrants = create_overlapping_quadrants(data.shape)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (start, end) in enumerate(quadrants):
        quadrant_data = data[:, :, start:end]
        quadrant_file_path = os.path.join(output_dir, f"quadrant_{i+1}_{os.path.basename(file_path)}")
        save_nifti_file(quadrant_data, affine, quadrant_file_path)
        print(f"Saved: {quadrant_file_path}")
        print(f'Quadrant {i} shape: {quadrant_data.shape}')


# Example Usage
pattern = os.path.join(data_dir, '**/*_CT_HR_label_airways.nii.gz')
train_labels = natsorted(glob.glob(pattern, recursive=True))

pattern = os.path.join(data_dir, '**/*_CT_HR.nii.gz')
train_images = natsorted(glob.glob(pattern, recursive=True))



for idx, (image_name, label_name) in enumerate(zip(train_images, train_labels)):
    output_dir = f'nonoverlapping_quadrants/{idx + 1}'
    process_file(image_name, output_dir)
    output_dir = f'nonoverlapping_labels/{idx + 1}'
    process_file(label_name, output_dir)
    
    print('')
    print('###########')
    print('')
